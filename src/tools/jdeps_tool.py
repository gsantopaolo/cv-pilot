import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Type, List

from pydantic import BaseModel, Field, PrivateAttr
from crewai.tools.base_tool import BaseTool

BUILD_OUTPUT_CANDIDATES = [
    "build/classes/java/main",  # Gradle default
    "target/classes",           # Maven default
]

def resolve_target_path(base_path: Optional[str] = None) -> str:
    """
    Resolve where to point jdeps:
      1) If base_path is a .jar → use it.
      2) Otherwise, if any of the standard build output dirs exist under the root → use the first one found.
      3) Otherwise, if there are any .class files anywhere under the root → use the root itself.
      4) If still nothing, error.
    """
    # Determine project root (explicit, CODE_PATH, or cwd)
    root = Path(base_path or os.getenv("CODE_PATH") or os.getcwd())

    # 1) Direct JAR?
    if root.is_file() and root.suffix.lower() == ".jar":
        return str(root)

    # Must be a directory from here on
    if not root.is_dir():
        raise RuntimeError(f"'{root}' is not a directory or JAR.")

    # 2) Look for standard build output dirs first
    for candidate in BUILD_OUTPUT_CANDIDATES:
        for path in root.rglob(candidate):
            if path.is_dir():
                return str(path)

    # 3) Fallback: if any .class files exist under root, use root itself
    if any(root.rglob("*.class")):
        return str(root)

    # 4) Give up
    raise RuntimeError(
        f"Could not locate any of {BUILD_OUTPUT_CANDIDATES} under {root}. "
        "Did you compile your code? Please build first or point --base-path at the class output."
    )

class JDepsInput(BaseModel):
    base_path: Optional[str] = Field(
        None,
        description="Filesystem path to compiled class files or JAR"
    )

class JDepsTool(BaseTool):
    name: str = "jdeps"
    description: str = "Analyze Java dependencies via jdeps"
    args_schema: Type[JDepsInput] = JDepsInput

    _base_path: str = PrivateAttr()
    _jdeps_cmd: str = PrivateAttr()

    def __init__(self, base_path: str, java_home: Optional[str] = None):
        super().__init__()
        self._jdeps_cmd = os.path.join(java_home, "bin", "jdeps") if java_home else "jdeps"
        self._base_path = base_path

    def _run(self, base_path: Optional[str] = None) -> dict:
        # Determine which path to use (runtime override or constructor default)
        real_base = base_path or self._base_path
        # Resolve to actual class directory or JAR
        # target = resolve_target_path(real_base)
        # todo: hardcoded path
        target = resolve_target_path("/Users/gp/Developer/java-samples/reforge-ai/src/temp_codebase/")


        # Build jdeps invocation (no -s so we get full detail)
        cmd: List[str] = [self._jdeps_cmd, "-R", target]

        # Execute jdeps
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"jdeps failed (exit {result.returncode}): {result.stderr.strip()}")

        output = result.stdout
        issues = [
            line.strip()
            for line in output.splitlines()
            if "not found" in line
               or "JDK internal API" in line
               or line.startswith("jdeps:")
        ]

        return {"jdeps_output": output, "identified_issues": issues}
