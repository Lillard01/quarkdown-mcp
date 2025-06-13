#!/usr/bin/env python3
"""Quarkdown MCP Server - Main server implementation.

This module implements the MCP server that provides Quarkdown document processing
capabilities through various tools for compilation, conversion, and preview.
"""

import asyncio
import logging
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.lowlevel import NotificationOptions
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListResourcesRequest,
    ReadResourceRequest,
    ReadResourceResult,
)

from .core.config import QuarkdownConfig
from .tools.compile import CompileDocumentTool
from .tools.create_project import CreateProjectTool
from .tools.validate import ValidateMarkdownTool
from .tools.preview import PreviewServerTool
from .tools.batch import ConvertBatchTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize configuration and server
config = QuarkdownConfig()
server = Server("quarkdown-mcp")

# Initialize tools
compile_tool = CompileDocumentTool(config)
create_tool = CreateProjectTool(config)
validate_tool = ValidateMarkdownTool(config)
preview_tool = PreviewServerTool(config)
convert_tool = ConvertBatchTool(config)


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Return the list of available tools."""
    return [
        compile_tool.get_tool_definition(),
        create_tool.get_tool_definition(),
        validate_tool.get_tool_definition(),
        preview_tool.get_tool_definition(),
        convert_tool.get_tool_definition(),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls."""
    if arguments is None:
        arguments = {}
    
    if name == "compile_document":
        return await compile_tool.execute(arguments)
    elif name == "create_project":
        return await create_tool.execute(arguments)
    elif name == "validate_markdown":
        return await validate_tool.execute(arguments)
    elif name == "preview_server":
        return await preview_tool.execute(arguments)
    elif name == "convert_batch":
        return await convert_tool.execute(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


def get_capabilities():
    """Return server capabilities."""
    return {
        "tools": {
            "compile_document": compile_tool.get_tool_definition(),
            "create_project": create_tool.get_tool_definition(),
            "validate_markdown": validate_tool.get_tool_definition(),
            "preview_server": preview_tool.get_tool_definition(),
            "convert_batch": convert_tool.get_tool_definition(),
        }
    }


def create_server() -> Server:
    """Create and return the configured server instance."""
    return server


async def main():
    """Main entry point for the MCP server."""
    # Create notification options
    notification_options = NotificationOptions(
        tools_changed=True,
        resources_changed=True,
        prompts_changed=True
    )
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="quarkdown-mcp",
                server_version="1.0.0",
                capabilities=get_capabilities(),
                notification_options=notification_options,
                experimental_capabilities={}
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())