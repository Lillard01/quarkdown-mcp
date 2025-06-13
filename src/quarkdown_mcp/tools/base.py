"""Base tool class for Quarkdown MCP tools.

This module provides a base class that all Quarkdown MCP tools inherit from,
offering common functionality and interface definitions.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from ..core.config import QuarkdownConfig
from ..core.wrapper import QuarkdownWrapper


class BaseTool(ABC):
    """Base class for all Quarkdown MCP tools.
    
    This abstract base class provides common functionality and interface
    definitions that all Quarkdown tools should implement.
    """
    
    def __init__(self, config: QuarkdownConfig):
        """Initialize the base tool.
        
        Args:
            config: Quarkdown configuration object
        """
        self.config = config
        self.wrapper = QuarkdownWrapper(config)
        
    @abstractmethod
    def get_tool_definition(self) -> Tool:
        """Get the MCP tool definition.
        
        Returns:
            Tool definition object for MCP registration
        """
        pass
        
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent | ImageContent | EmbeddedResource]:
        """Execute the tool with given arguments.
        
        Args:
            arguments: Tool execution arguments
            
        Returns:
            List of content objects representing the tool output
        """
        pass
        
    def _create_text_content(self, text: str) -> TextContent:
        """Create a text content object.
        
        Args:
            text: Text content
            
        Returns:
            TextContent object
        """
        return TextContent(type="text", text=text)
        
    def _create_error_content(self, error: str) -> TextContent:
        """Create an error content object.
        
        Args:
            error: Error message
            
        Returns:
            TextContent object with error formatting
        """
        return TextContent(
            type="text",
            text=f"❌ **Error**: {error}"
        )
        
    def _create_success_content(self, message: str) -> TextContent:
        """Create a success content object.
        
        Args:
            message: Success message
            
        Returns:
            TextContent object with success formatting
        """
        return TextContent(
            type="text",
            text=f"✅ **Success**: {message}"
        )
        
    def _validate_required_args(self, arguments: Dict[str, Any], required_keys: List[str]) -> None:
        """Validate that required arguments are present.
        
        Args:
            arguments: Tool arguments
            required_keys: List of required argument keys
            
        Raises:
            ValueError: If any required argument is missing
        """
        missing_keys = [key for key in required_keys if key not in arguments or arguments[key] is None]
        if missing_keys:
            raise ValueError(f"Missing required arguments: {', '.join(missing_keys)}")
            
    def _format_file_content(self, content: str, file_path: str, language: str = "") -> str:
        """Format file content for display.
        
        Args:
            content: File content
            file_path: Path to the file
            language: Programming language for syntax highlighting
            
        Returns:
            Formatted content string
        """
        return f"**File**: `{file_path}`\n\n```{language}\n{content}\n```"
        
    def _format_validation_results(self, is_valid: bool, errors: List[str]) -> str:
        """Format validation results for display.
        
        Args:
            is_valid: Whether validation passed
            errors: List of validation errors
            
        Returns:
            Formatted validation results
        """
        if is_valid:
            return "✅ **Validation Passed**: Document syntax is valid."
        else:
            error_list = "\n".join([f"- {error}" for error in errors])
            return f"❌ **Validation Failed**: Found {len(errors)} error(s):\n\n{error_list}"