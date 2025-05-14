import os
import subprocess
from pathlib import Path
from typing import Optional, Type

from pydantic import BaseModel, Field
from crewai.tools.base_tool import BaseTool

# Hardcoded default project path
DEFAULT_CODEBASE_PATH = "/Users/gp/Developer/java-samples/reforge-ai/src/1-codegen-work/code/code"

class MavenBuildInput(BaseModel):
    base_path: Optional[str] = Field(
        None,
        description="Filesystem path to the Maven/Gradle project to build"
    )

class MavenBuildTool(BaseTool):
    name: str = "maven-build"
    description: str = "Build a Java project using Maven (or Gradle if no pom.xml)"
    args_schema: Type[MavenBuildInput] = MavenBuildInput

    def __init__(self, base_path: Optional[str] = None):
        super().__init__()

        # Allow overriding the default path
        # todo: hardcoded for now
        # self._base_path = base_path or DEFAULT_CODEBASE_PATH
        self._base_path = DEFAULT_CODEBASE_PATH

    def _run(self, base_path: Optional[str] = None) -> dict:
        # Determine which path to build
        project_path = Path(self._base_path)

        # Validate directory exists
        if not project_path.is_dir():
            raise FileNotFoundError(f"📁 Directory '{project_path}' not found.")

        # Prepare environment (inherit yours, or override JAVA_HOME/PATH here)
        env = os.environ.copy()
        # env["JAVA_HOME"] = "/path/to/jdk-21"
        # env["PATH"] = f"{env['JAVA_HOME']}/bin:" + env["PATH"]

        # todo this tool assumes you have java 21 set as default
        # sdk default java 21.0.7-tem
        # test with sdk current java
        # debug versions
        print("******* DEBUG INFO *******")
        print(subprocess.run(["java", "-version"], capture_output=True, text=True).stderr)
        print(subprocess.run(["javac", "-version"], capture_output=True, text=True).stdout)
        print("******* END DEBUG INFO *******")

        # Determine build tool
        pom = project_path / "pom.xml"
        gradle = project_path / "build.gradle"

        if pom.exists():
            cmd = ["mvn", "-f", str(pom), "clean", "compile"]
            tool_used = "maven"
        elif gradle.exists():
            cmd = ["gradle", "-p", str(project_path), "build"]
            tool_used = "gradle"
        else:
            return {"message": "ℹ️  No build file found; skipping compile."}

        # Execute build
        result = subprocess.run(cmd, capture_output=True, text=True)

        return {
            "tool": tool_used,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
