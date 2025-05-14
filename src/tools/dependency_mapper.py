# crewai_tools/dependency_mapper.py

import os
import subprocess
from pathlib import Path
from typing import Optional, Type, Dict

from pydantic import BaseModel, Field
from crewai.tools.base_tool import BaseTool

def resolve_build_file(base_path: Optional[str] = None) -> Path:
    """
    Resolve the path to 'pom.xml' or 'build.gradle':
      1) Look recursively under the provided root directory or current working directory.
      2) If 'pom.xml' is found, return its path.
      3) Else if 'build.gradle' is found, return its path.
      4) If neither is found, raise an error.
    """
    root = Path(base_path or os.getenv("CODE_PATH") or os.getcwd())

    if not root.is_dir():
        raise RuntimeError(f"'{root}' is not a directory.")

    # Search for 'pom.xml' first
    pom_files = list(root.rglob("pom.xml"))
    if pom_files:
        return pom_files[0]

    # If 'pom.xml' not found, search for 'build.gradle'
    gradle_files = list(root.rglob("build.gradle"))
    if gradle_files:
        return gradle_files[0]

    raise RuntimeError(
        f"Could not locate 'pom.xml' or 'build.gradle' under {root}. "
        "Please check your path or ensure the build file exists."
    )

class DependencyMapperInput(BaseModel):
    code_path: Optional[str] = Field(
        None,
        description="Root directory of the Java project (with pom.xml or build.gradle)."
    )

class DependencyMapperTool(BaseTool):
    name: str = "dependency_mapper"
    description: str = "Map all Maven/Gradle dependencies into a structured JSON graph."
    args_schema: Type[DependencyMapperInput] = DependencyMapperInput

    def _run(self, code_path: Optional[str] = None) -> Dict:

        root = resolve_build_file("/Users/gp/Developer/java-samples/reforge-ai/src/temp_codebase/")

        # Resolve the build file path
        # build_file = resolve_build_file(code_path)
        build_file = resolve_build_file("/Users/gp/Developer/java-samples/reforge-ai/src/temp_codebase/")

        # Determine the build tool based on the file name
        if build_file.name == "pom.xml":
            cmd = [
                "mvn", "-f", str(build_file),
                "dependency:tree", "-DoutputType=dot"
            ]
        elif build_file.name == "build.gradle":
            cmd = [
                "gradle", "--quiet",
                "dependencies", "--configuration", "runtimeClasspath"
            ]
        else:
            raise RuntimeError(f"Unsupported build file: {build_file.name}")

        # Execute the command
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Dependency command failed: {result.stderr.strip()}")

        tree_output = result.stdout
        # TODO: parse DOT or plain-text into structured JSON if desired
        return {"dependency_tree": tree_output}

