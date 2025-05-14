import os
import re
import subprocess
import json
from typing import Type

from pydantic import BaseModel, Field, PrivateAttr
from crewai.tools.base_tool import BaseTool


class DBParserInput(BaseModel):
    """
    Input arguments for DBParserTool.
    """
    code_path: str = Field(
        ..., description="Filesystem path to the Java codebase root"
    )


class DBParserTool(BaseTool):
    """
    CrewAI tool to detect and parse SQL usage in a Java codebase.

    It scans .java files for SQL query strings and, if a helper JAR is
    provided, uses it to parse queries into structured output.
    """
    name: str = "db-parser"
    description: str = (
        "Detect and extract database usage patterns from Java code by scanning for SQL strings "
        "and optionally parsing them with a helper JAR using JSqlParser."
    )
    args_schema: Type[DBParserInput] = DBParserInput

    # Private attributes for internal use only
    _java_cmd: str = PrivateAttr()
    _helper_jar: str | None = PrivateAttr()

    def __init__(self, java_cmd: str = "java", java_helper_jar: str | None = None):
        super().__init__()
        self._java_cmd = java_cmd
        self._helper_jar = java_helper_jar

    def _run(self, code_path: str) -> dict:
        """
        Scan the codebase for SQL queries and parse each.

        Returns:
            A dictionary with a list of queries and their parsed details.
        """
        # Heuristic for finding SQL strings in Java code
        sql_pattern = re.compile(r'"(SELECT|INSERT|UPDATE|DELETE).*?"', re.IGNORECASE)
        parsed_results = []

        # Walk the codebase and collect query strings
        for root, _, files in os.walk(code_path):
            for file in files:
                if not file.endswith('.java'):
                    continue
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except OSError:
                    continue

                for match in sql_pattern.finditer(content):
                    raw_query = match.group(0).strip('"')
                    # Parse the query (naive or via helper JAR)
                    parsed = self._parse_sql(raw_query)
                    entry = {"query": raw_query}
                    entry.update(parsed)
                    parsed_results.append(entry)

        return {"sql_queries": parsed_results}

    def _parse_sql(self, sql_query: str) -> dict:
        """
        Parse a single SQL query using the provided helper JAR or a simple regex fallback.
        """
        # If no helper JAR, fallback to naive table extraction
        if not self._helper_jar:
            tables = re.findall(r'FROM\s+([\w\.]+)', sql_query, flags=re.IGNORECASE)
            return {"tables": list(set(tables))} if tables else {}

        # Use the helper JAR for robust parsing
        cmd = [self._java_cmd, '-jar', self._helper_jar, sql_query]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"SQL parse failed (exit {e.returncode}): {e.stderr.strip()}")

        # Expect JSON output from the helper JAR
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            # If JSON parsing fails, return raw output
            return {"raw_output": result.stdout.strip()}
