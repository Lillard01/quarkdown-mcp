"""Document compilation tool for Quarkdown MCP server.

This module provides the compile_document tool that converts Quarkdown
source content to various output formats like HTML, PDF, and LaTeX.
"""

from pathlib import Path
from typing import Any, Dict, List

from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from .base import BaseTool


class CompileDocumentTool(BaseTool):
    """Tool for compiling Quarkdown documents to various formats.
    
    This tool takes Quarkdown source content and compiles it to the specified
    output format, supporting HTML, PDF, LaTeX, and Markdown outputs.
    """
    
    def get_tool_definition(self) -> Tool:
        """Get the MCP tool definition for document compilation.
        
        Returns:
            Tool definition object for MCP registration
        """
        return Tool(
            name="compile_document",
            description="Compile Quarkdown source content to various output formats (HTML, PDF, LaTeX, Markdown)",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_content": {
                        "type": "string",
                        "description": "The Quarkdown source content to compile"
                    },
                    "input_file": {
                        "type": "string",
                        "description": "Path to input file containing Quarkdown source content"
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["html", "pdf", "tex", "md"],
                        "default": "html",
                        "description": "Output format for the compiled document"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Optional output file path. If not provided, returns content directly"
                    },
                    "pretty_output": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to generate pretty formatted output"
                    },
                    "wrap_output": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to wrap the output in a complete document structure"
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Working directory for relative path resolution"
                    }
                },
                "anyOf": [
                    {"required": ["source_content"]},
                    {"required": ["input_file"]}
                ]
            }
        )
        
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent | ImageContent | EmbeddedResource]:
        """Execute the document compilation.
        
        Args:
            arguments: Tool execution arguments containing source content and options
            
        Returns:
            List containing the compilation results
        """
        try:
            # Get source content from either direct content or input file
            source_content = None
            input_file = arguments.get("input_file")
            direct_content = arguments.get("source_content")
            
            if direct_content:
                source_content = direct_content
            elif input_file:
                try:
                    input_path = Path(input_file)
                    if not input_path.exists():
                        return [self._create_error_content(f"Input file not found: {input_file}")]
                    source_content = input_path.read_text(encoding='utf-8')
                except Exception as e:
                    return [self._create_error_content(f"Failed to read input file: {e}")]
            else:
                return [self._create_error_content("Either source_content or input_file must be provided")]
            
            output_format = arguments.get("output_format", "html")
            output_path = arguments.get("output_path")
            pretty_output = arguments.get("pretty_output", True)
            wrap_output = arguments.get("wrap_output", True)
            working_directory = arguments.get("working_directory")
            
            # Validate output format
            valid_formats = ["html", "pdf", "tex", "md"]
            if output_format not in valid_formats:
                return [self._create_error_content(f"Unsupported output format: {output_format}")]
                
            # Prepare compilation options
            options = {}
            if pretty_output is not None:
                options["pretty"] = pretty_output
            if wrap_output is not None:
                options["wrap"] = wrap_output
            if working_directory:
                options["working-directory"] = working_directory
                
            # Convert output_path to Path object if provided
            output_file_path = Path(output_path) if output_path else None
            
            # Execute compilation
            result = await self.wrapper.compile_document(
                content=source_content,
                output_format=output_format,
                output_path=output_file_path,
                config_options=options
            )
            
            # Check if compilation was successful
            if not result.get("success", False):
                errors = result.get("errors", ["Unknown compilation error"])
                error_msg = "\n".join(errors) if isinstance(errors, list) else str(errors)
                return [self._create_error_content(f"Compilation failed: {error_msg}")]
                
            result_content = result.get("output", "")
            output_file = output_file_path
            
            # Prepare response
            response_parts = []
            
            # Add success message
            response_parts.append(self._create_success_content(
                f"Document compiled successfully to {output_format.upper()} format"
            ))
            
            # Add output file information if saved to file
            if output_path and output_file:
                response_parts.append(self._create_text_content(
                    f"**Output saved to**: `{output_file}`"
                ))
                
            # Add compiled content
            if result_content:
                # Determine language for syntax highlighting
                language_map = {
                    "html": "html",
                    "tex": "latex",
                    "md": "markdown",
                    "pdf": ""  # PDF is binary, don't show content
                }
                
                if output_format == "pdf":
                    response_parts.append(self._create_text_content(
                        "**PDF Content**: Binary PDF file generated successfully. "
                        "Content cannot be displayed as text."
                    ))
                else:
                    language = language_map.get(output_format, "")
                    formatted_content = self._format_file_content(
                        result_content[:2000] + ("..." if len(result_content) > 2000 else ""),
                        f"output.{output_format}",
                        language
                    )
                    response_parts.append(self._create_text_content(formatted_content))
                    
            return response_parts
            
        except Exception as e:
            return [self._create_error_content(str(e))]