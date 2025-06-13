"""Preview server tool for Quarkdown MCP server.

This module provides the preview_server tool that starts a local development
server for previewing Quarkdown documents in real-time.
"""

import asyncio
import os
import tempfile
from typing import Any, Dict, List

from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from .base import BaseTool


class PreviewServerTool(BaseTool):
    """Tool for starting a preview server for Quarkdown documents.
    
    This tool creates a local development server that allows users to
    preview their Quarkdown documents in a web browser with live updates.
    """
    
    def get_tool_definition(self) -> Tool:
        """Get the MCP tool definition for preview server.
        
        Returns:
            Tool definition object for MCP registration
        """
        return Tool(
            name="preview_server",
            description="Start a local preview server for Quarkdown documents with live reload",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_content": {
                        "type": "string",
                        "description": "The Quarkdown source content to preview"
                    },
                    "port": {
                        "type": "integer",
                        "default": 8080,
                        "minimum": 1024,
                        "maximum": 65535,
                        "description": "Port number for the preview server"
                    },
                    "auto_reload": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable automatic reload when source content changes"
                    },
                    "theme": {
                        "type": "string",
                        "default": "default",
                        "enum": ["default", "dark", "light", "academic", "minimal"],
                        "description": "Theme for the preview interface"
                    },
                    "watch_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Additional files to watch for changes (optional)"
                    },
                    "open_browser": {
                        "type": "boolean",
                        "default": False,
                        "description": "Automatically open the preview in default browser"
                    }
                },
                "required": ["source_content"]
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent | ImageContent | EmbeddedResource]:
        """Execute the preview server tool.
        
        Args:
            arguments: Tool arguments from MCP client
            
        Returns:
            List of content items with execution results
        """
        try:
            # Clean and validate parameters
            cleaned_kwargs = self._clean_and_validate_params(arguments)
            
            # Extract parameters with defaults
            source_content = cleaned_kwargs.get('source_content')
            port = cleaned_kwargs.get('port', 8080)
            auto_reload = cleaned_kwargs.get('auto_reload', True)
            theme = cleaned_kwargs.get('theme', 'default')
            open_browser = cleaned_kwargs.get('open_browser', False)
            
            # Validate required parameters
            if not source_content:
                return [TextContent(
                    type="text",
                    text="Error: Missing required parameter 'source_content'"
                )]
            
            # Validate parameter types and values
            validation_result = self._validate_parameters(
                source_content, port, auto_reload, theme, open_browser
            )
            if not validation_result["valid"]:
                return [TextContent(
                    type="text",
                    text=f"Error: {validation_result['error']}"
                )]
            
            # Execute the preview server
            result = await self.wrapper.start_preview_server(
                content=source_content,
                port=port,
                auto_reload=auto_reload,
                theme=theme,
                open_browser=open_browser
            )
            
            # Format response based on result
            if result.get('success'):
                success_message = f"Preview server started successfully!\n\n"
                success_message += f"🌐 URL: {result.get('url', f'http://localhost:{port}')}\n"
                success_message += f"📁 Compiled output: {result.get('compiled_output', 'N/A')}\n"
                success_message += f"🔧 Process ID: {result.get('process_id', 'N/A')}\n\n"
                
                if result.get('instructions'):
                    success_message += "📋 Instructions:\n"
                    for instruction in result['instructions']:
                        success_message += f"  • {instruction}\n"
                
                return [TextContent(
                    type="text",
                    text=success_message
                )]
            else:
                error_message = f"Failed to start preview server\n\n"
                error_message += f"❌ Error: {result.get('error', 'Unknown error')}\n"
                if result.get('return_code'):
                    error_message += f"🔢 Return code: {result['return_code']}\n"
                if result.get('exception_type'):
                    error_message += f"🐛 Exception type: {result['exception_type']}\n"
                
                return [TextContent(
                    type="text",
                    text=error_message
                )]
                
        except Exception as e:
            logger.error(f"Preview server execution failed: {e}", exc_info=True)
            return [TextContent(
                type="text",
                text=f"Unexpected error starting preview server: {str(e)}"
            )]

    def _clean_and_validate_params(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate input parameters.
        
        Args:
            kwargs: Raw input parameters
            
        Returns:
            Cleaned parameters dictionary
        """
        # Remove any unexpected parameters that might be added by MCP framework
        unwanted_params = ['source_file', 'input_file', 'file_path']
        cleaned = {k: v for k, v in kwargs.items() if k not in unwanted_params}
        
        # Normalize parameter names
        if 'content' in cleaned and 'source_content' not in cleaned:
            cleaned['source_content'] = cleaned.pop('content')
        
        return cleaned
    
    def _validate_parameters(self, source_content: str, port: int, auto_reload: bool, 
                           theme: str, open_browser: bool) -> Dict[str, Any]:
        """Validate parameter types and values.
        
        Args:
            source_content: Document content
            port: Server port
            auto_reload: Auto-reload flag
            theme: Theme name
            open_browser: Open browser flag
            
        Returns:
            Validation result dictionary
        """
        # Validate source_content
        if not isinstance(source_content, str):
            return {"valid": False, "error": "source_content must be a string"}
        
        if len(source_content.strip()) == 0:
            return {"valid": False, "error": "source_content cannot be empty"}
        
        # Validate port
        if not isinstance(port, int):
            try:
                port = int(port)
            except (ValueError, TypeError):
                return {"valid": False, "error": "port must be an integer"}
        
        if not (1024 <= port <= 65535):
            return {"valid": False, "error": "port must be between 1024 and 65535"}
        
        # Validate boolean parameters
        if not isinstance(auto_reload, bool):
            return {"valid": False, "error": "auto_reload must be a boolean"}
        
        if not isinstance(open_browser, bool):
            return {"valid": False, "error": "open_browser must be a boolean"}
        
        # Validate theme
        valid_themes = ['default', 'dark', 'light', 'academic', 'minimal']
        if theme not in valid_themes:
            return {"valid": False, "error": f"theme must be one of: {', '.join(valid_themes)}"}
        
        return {"valid": True}
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format.
        
        Returns:
            ISO formatted timestamp string
        """
        from datetime import datetime
        return datetime.now().isoformat()
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent | ImageContent | EmbeddedResource]:
        """Execute the preview server startup.
        
        Args:
            arguments: Tool execution arguments containing source content and server options
            
        Returns:
            List containing the server startup results and access information
        """
        try:
            # Debug: Print all received arguments
            print(f"DEBUG preview.py: execute called with arguments:")
            print(f"  arguments keys: {list(arguments.keys())}")
            print(f"  arguments: {arguments}")
            
            # Remove any unwanted parameters that might be added by MCP framework
            if 'source_file' in arguments:
                print(f"DEBUG: Removing unwanted 'source_file' parameter: {arguments['source_file']}")
                arguments = {k: v for k, v in arguments.items() if k != 'source_file'}
                print(f"DEBUG: Filtered arguments: {arguments}")
            
            # Validate required arguments
            self._validate_required_args(arguments, ["source_content"])
            
            source_content = arguments["source_content"]
            port = arguments.get("port", 8080)
            auto_reload = arguments.get("auto_reload", True)
            theme = arguments.get("theme", "default")
            watch_files = arguments.get("watch_files", [])
            open_browser = arguments.get("open_browser", False)
            
            # Create temporary directory for preview files
            temp_dir = tempfile.mkdtemp(prefix="quarkdown_preview_")
            source_file = os.path.join(temp_dir, "document.qmd")
            
            # Write source content to temporary file
            with open(source_file, 'w', encoding='utf-8') as f:
                f.write(source_content)
                
            # Check if port is available
            if not await self._is_port_available(port):
                # Try to find an available port
                port = await self._find_available_port(port)
                
            # Debug: Print the actual arguments being passed
            print(f"DEBUG: About to call start_preview_server with:")
            print(f"  content type: {type(source_content)}")
            print(f"  content length: {len(source_content)}")
            print(f"  port: {port}")
            print(f"  port type: {type(port)}")
            
            # Start the preview server
            try:
                # Filter out any unwanted parameters that might be passed by MCP framework
                server_params = {
                    'content': source_content,
                    'port': port
                }
                print(f"DEBUG: Calling start_preview_server with filtered params: {server_params}")
                server_result = await self.wrapper.start_preview_server(**server_params)
            except Exception as e:
                print(f"DEBUG: Exception details: {e}")
                print(f"DEBUG: Exception type: {type(e)}")
                import traceback
                print(f"DEBUG: Traceback: {traceback.format_exc()}")
                raise
            
            # Debug: Log the server result for troubleshooting
            logger.debug(f"Preview server result: {server_result}")
            
            # Check if server_result is None or empty
            if server_result is None:
                return [
                    self._create_error_content(
                        "Preview server returned null result. This may indicate a configuration issue with the Quarkdown JAR file or Java environment."
                    )
                ]
            
            # Check if server started successfully
            if server_result.get("success"):
                server_url = server_result.get("url", f"http://localhost:{port}")
                
                # Optionally open browser
                if open_browser:
                    await self._open_browser(server_url)
                    
                response_parts = [
                    self._create_success_content(
                        f"Preview server started successfully on port {port}"
                    ),
                    self._create_text_content(
                        f"**Server Information**:\n"
                        f"- **URL**: {server_url}\n"
                        f"- **Port**: {port}\n"
                        f"- **Auto-reload**: {'Enabled' if auto_reload else 'Disabled'}\n"
                        f"- **Theme**: {theme}\n"
                        f"- **Source content**: Provided content"
                    )
                ]
                
                # Add watch files information if any
                if watch_files:
                    watch_info = "\n".join([f"  - {file}" for file in watch_files])
                    response_parts.append(self._create_text_content(
                        f"**Watching additional files**:\n{watch_info}"
                    ))
                    
                return response_parts
            else:
                error_msg = server_result.get('error', 'Unknown error')
                if error_msg == 'Unknown error' and not server_result.get('success'):
                    error_msg = "Failed to start preview server. Please check that Java is installed and the Quarkdown JAR file is accessible."
                
                return [
                    self._create_error_content(
                        f"Failed to start preview server: {error_msg}"
                    )
                ]
                
        except Exception as e:
            return [self._create_error_content(f"Error starting preview server: {str(e)}")]
            
    async def _is_port_available(self, port: int) -> bool:
        """Check if a port is available for use.
        
        Args:
            port: Port number to check
            
        Returns:
            True if port is available
        """
        import socket
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(('localhost', port))
                return True
        except OSError:
            return False
            
    async def _find_available_port(self, start_port: int) -> int:
        """Find an available port starting from the given port.
        
        Args:
            start_port: Starting port number
            
        Returns:
            Available port number
        """
        for port in range(start_port, start_port + 100):
            if await self._is_port_available(port):
                return port
                
        # If no port found in range, try random high port
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(('localhost', 0))
            return sock.getsockname()[1]
            
    async def _open_browser(self, url: str) -> None:
        """Open the preview URL in the default browser.
        
        Args:
            url: URL to open
        """
        import webbrowser
        try:
            webbrowser.open(url)
        except Exception:
            # Silently fail if browser can't be opened
            pass
            
    def _generate_usage_instructions(self, server_url: str, temp_dir: str) -> str:
        """Generate usage instructions for the preview server.
        
        Args:
            server_url: Server URL
            temp_dir: Temporary directory path
            
        Returns:
            Formatted instructions string
        """
        instructions = [
            f"1. **Open your browser** and navigate to: {server_url}",
            "2. **Edit your document** by modifying the source content",
            "3. **Save changes** to see live updates (if auto-reload is enabled)",
            f"4. **Source file location**: {temp_dir}",
            "5. **Stop the server** using the management commands below"
        ]
        
        return "\n".join(instructions)
        
    def _generate_management_info(self, process_id: int) -> str:
        """Generate server management information.
        
        Args:
            process_id: Server process ID
            
        Returns:
            Formatted management information
        """
        management_info = [
            f"- **Process ID**: {process_id}",
            f"- **Stop server**: `kill {process_id}` (Unix/macOS) or use Task Manager (Windows)",
            "- **Check status**: Use `ps aux | grep quarkdown` (Unix/macOS)",
            "- **View logs**: Check the terminal where the server was started",
            "- **Restart**: Stop the current server and run this tool again"
        ]
        
        return "\n".join(management_info)
        
    async def stop_server(self, process_id: int) -> bool:
        """Stop a running preview server.
        
        Args:
            process_id: Process ID of the server to stop
            
        Returns:
            True if server was stopped successfully
        """
        try:
            import os
            import signal
            
            # Send SIGTERM to gracefully stop the server
            os.kill(process_id, signal.SIGTERM)
            
            # Wait a moment for graceful shutdown
            await asyncio.sleep(1)
            
            # Check if process is still running
            try:
                os.kill(process_id, 0)  # Check if process exists
                # If we reach here, process is still running, force kill
                os.kill(process_id, signal.SIGKILL)
            except ProcessLookupError:
                # Process already terminated
                pass
                
            return True
            
        except Exception:
            return False
            
    async def list_running_servers(self) -> List[Dict[str, Any]]:
        """List all running Quarkdown preview servers.
        
        Returns:
            List of server information dictionaries
        """
        try:
            import psutil
            
            servers = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'quarkdown' in proc.info['name'].lower():
                        cmdline = ' '.join(proc.info['cmdline'])
                        if 'preview' in cmdline or 'server' in cmdline:
                            servers.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cmdline': cmdline
                            })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            return servers
            
        except ImportError:
            # psutil not available, return empty list
            return []
        except Exception:
            return []