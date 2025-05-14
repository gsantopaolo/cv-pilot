# tools/langchain_fs_tool.py
from typing import Any, Type, cast
from crewai.tools import BaseTool
from pydantic import Field, BaseModel, PrivateAttr  # Import PrivateAttr


# Define a default empty schema
class _EmptyArgsSchema(BaseModel):
    """Placeholder args schema if none provided by the wrapped lc_tool."""
    pass


class LangChainFSWrapper(BaseTool):
    # name and description will be set by __init__ and passed to super()
    # args_schema will also be set by __init__ and passed to super()

    # Use PrivateAttr for instance variables not intended as Pydantic model fields
    # directly passed to super(), but rather configured by __init__
    _lc_tool_internal: Any = PrivateAttr()

    def __init__(self, *, name: str, description: str, lc_tool: Any, **kwargs: Any):
        # Determine args_schema first
        if hasattr(lc_tool, 'args_schema') and lc_tool.args_schema is not None:
            args_schema_to_use = cast(Type[BaseModel], lc_tool.args_schema)
        else:
            args_schema_to_use = _EmptyArgsSchema

        # Initialize BaseTool with all required Pydantic fields
        # name, description, and args_schema are fields of BaseTool
        super().__init__(name=name, description=description, args_schema=args_schema_to_use, **kwargs)

        # Set our custom instance attribute AFTER super().__init__
        self._lc_tool_internal = lc_tool

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """
        Synchronous run: delegate to the LangChain tool's run method.
        """
        # Pass through kwargs, as they are already validated against args_schema by BaseTool
        return self._lc_tool_internal.run(kwargs if kwargs else (args[0] if args else {}))

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        """
        Asynchronous run: delegate if the LangChain tool supports async.
        """
        run_fn = getattr(self._lc_tool_internal, 'arun', self._lc_tool_internal.run)
        # Pass through kwargs
        output = await run_fn(kwargs if kwargs else (args[0] if args else {}))
        return output