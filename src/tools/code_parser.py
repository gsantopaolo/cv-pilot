# crewai_tools/custom_tools.py

import os
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Type

import javalang
from pydantic import BaseModel, Field, PrivateAttr
from mdutils.mdutils import MdUtils

from crewai.tools.base_tool import BaseTool
class CodeParserInput(BaseModel):
    code_path: Optional[str] = Field(
        None, description="Root directory of Java source files."
    )

class CodeParserTool(BaseTool):
    name: str = "code_parser"
    description: str = "Parse Java source into AST and extract class/method signatures."
    args_schema: Type[CodeParserInput] = CodeParserInput

    def _run(self, code_path: Optional[str] = None) -> Dict:
        root = Path(code_path or os.getenv("CODE_PATH") or ".").resolve()
        signatures: List[str] = []
        for java_file in root.rglob("*.java"):
            source = java_file.read_text(encoding="utf-8", errors="ignore")
            tree = javalang.parse.parse(source)
            pkg = tree.package.name if tree.package else ""
            for type_decl in tree.types:
                cls = type_decl.name
                for method in getattr(type_decl, "methods", []):
                    params = ", ".join(param.type.name for param in method.parameters)
                    signatures.append(f"{pkg}.{cls}.{method.name}({params})")
        return {"signatures": signatures}