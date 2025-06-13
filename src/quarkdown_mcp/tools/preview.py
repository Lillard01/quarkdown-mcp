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
        """Execute the preview server startup.
        
        Args:
            arguments: Tool execution arguments containing source content and server options
            
        Returns:
            List containing the server startup results and access information
        """
        try:
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
                
            # Start the preview server
            server_process = await self.wrapper.start_preview_server(
                source_file=source_file,
                port=port,
                auto_reload=auto_reload,
                theme=theme,
                watch_files=watch_files
            )
            
            # Wait a moment for server to start
            await asyncio.sleep(2)
            
            # Check if server started successfully
            if server_process and server_process.poll() is None:
                server_url = f"http://localhost:{port}"
                
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
                        f"- **Source file**: {source_file}\n"
                        f"- **Process ID**: {server_process.pid}"
                    )
                ]
                
                # Add watch files information if any
                if watch_files:
                    watch_info = "\n".join([f"  - {file}" for file in watch_files])
                    response_parts.append(self._create_text_content(
                        f"**Watching additional files**:\n{watch_info}"
                    ))
                    
                # Add usage instructions
                instructions = self._generate_usage_instructions(server_url, temp_dir)
                response_parts.append(self._create_text_content(
                    f"**Usage Instructions**:\n{instructions}"
                ))
                
                # Add server management commands
                management_info = self._generate_management_info(server_process.pid)
                response_parts.append(self._create_text_content(
                    f"**Server Management**:\n{management_info}"
                ))
                
                return response_parts
                
            else:
                return [self._create_error_content(
                    "Failed to start preview server. Check if the port is available and try again."
                )]
                
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