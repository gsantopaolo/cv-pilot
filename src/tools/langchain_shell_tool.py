# tools/langchain_shell_tool.py
from typing import Any, Type, List, Optional  # Added Optional
from crewai.tools import BaseTool
from pydantic import Field, BaseModel, PrivateAttr  # Import PrivateAttr
from langchain_community.tools import ShellTool  # Keep this import


# Define a default empty schema if needed, or use ShellTool's
class _DefaultShellArgsSchema(BaseModel):
    """Default args schema if ShellTool doesn't provide one or for simple list of commands."""
    commands: List[str] = Field(..., description="A list of shell commands to execute.")
    # LangChain's ShellTool actually expects a single string command or a list of commands
    # under the key 'commands' if multiple are passed as a list in a dict.
    # Let's make the input schema expect a list of commands for clarity for the agent.
    # The _run method will then format it as needed for the lc_tool.


class LangChainShellWrapper(BaseTool):
    # name, description, args_schema will be set in __init__ and passed to super()

    _lc_tool_internal: ShellTool = PrivateAttr()  # For the wrapped LangChain tool instance

    def __init__(self,
                 *,  # Make subsequent arguments keyword-only
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 lc_tool: Optional[ShellTool] = None,  # Allow passing a pre-configured ShellTool
                 **kwargs: Any):

        resolved_name = name or "shell_tool"  # Default name if not provided
        resolved_description = description or (
            "Executes a list of shell commands using the underlying LangChain ShellTool. "
            "Use with caution. Input should be a list of strings, where each string is a command."
        )

        # Instantiate the lc_tool if not provided
        # This ensures _lc_tool_internal is always a ShellTool instance
        self._lc_tool_internal = lc_tool or ShellTool()

        # Determine args_schema
        # LangChain's ShellTool has a specific args_schema
        args_schema_to_use: Type[BaseModel]
        if hasattr(self._lc_tool_internal, 'args_schema') and self._lc_tool_internal.args_schema is not None:
            args_schema_to_use = self._lc_tool_internal.args_schema
        else:
            # Fallback if ShellTool's args_schema isn't readily available or for more control
            args_schema_to_use = _DefaultShellArgsSchema

        super().__init__(
            name=resolved_name,
            description=resolved_description,
            args_schema=args_schema_to_use,
            **kwargs
        )

    def _run(self, commands: List[str]) -> str:  # Parameter name matches _DefaultShellArgsSchema
        """
        Synchronously run shell commands via the LangChain ShellTool.
        The 'commands' argument comes from the validated args_schema.
        """
        if not isinstance(commands, list):
            return "Error: Input 'commands' must be a list of command strings."

        # LangChain's ShellTool.run can take a single string or a list of strings (as dict value).
        # If args_schema forces a list, we adapt.
        # If multiple commands, ShellTool often expects them as one string 'cmd1 && cmd2' or
        # it processes a list if passed within a dict like `{"commands": ["echo hello", "echo world"]}`.
        # Let's try to pass it as a single string first if it's a list, or pass the dict.

        tool_input: Any
        if len(commands) == 1:
            tool_input = commands[0]  # Pass single command as string
        else:
            # If ShellTool's args_schema is `ShellToolInput` (which expects `commands: list[str] | str`),
            # passing a dict `{"commands": commands}` is correct.
            # If our _DefaultShellArgsSchema is used, the input `commands` is already a list.
            tool_input = {"commands": commands}

        try:
            # The actual lc_tool.run might take *args or **kwargs or a specific model.
            # We need to ensure the input matches what lc_tool.args_schema expects.
            # If our args_schema_to_use is _DefaultShellArgsSchema, then CrewAI will pass commands=List[str]
            # If ShellTool's own args_schema is used, CrewAI will pass what that schema defines.
            # The ShellTool.run expects a string or List[str] passed to a 'commands' key in a dict.
            # Or a single string command if called as tool.run("ls -l")

            # Assuming our _DefaultShellArgsSchema, 'commands' is a List[str].
            # The ShellTool itself, when run with a dict, expects `{"commands": ["cmd1", "cmd2"]}`
            # or `{"commands": "cmd1 && cmd2"}`.
            # If 'commands' is already a list from our args_schema:
            return self._lc_tool_internal.run(tool_input)

        except Exception as e:
            logger.error(f"Error executing shell command with LangChainShellWrapper: {e}")
            return f"Error during shell command execution: {e}"

    async def _arun(self, commands: List[str]) -> str:
        """
        Asynchronously run shell commands via the LangChain ShellTool.
        """
        if not isinstance(commands, list):
            return "Error: Input 'commands' must be a list of command strings."

        tool_input: Any
        if len(commands) == 1:
            tool_input = commands[0]
        else:
            tool_input = {"commands": commands}

        try:
            run_fn = getattr(self._lc_tool_internal, 'arun', self._lc_tool_internal.run)
            # Ensure awaiting if arun was found and is async
            if run_fn.__name__ == 'arun' and hasattr(run_fn, '__call__'):  # Basic check if it's callable
                return await run_fn(tool_input)
            else:  # Fallback to sync run if arun is not proper async or not found
                return run_fn(tool_input)  # This might be an issue if run_fn is async but not awaited
        except Exception as e:
            logger.error(f"Error executing async shell command with LangChainShellWrapper: {e}")
            return f"Error during async shell command execution: {e}"