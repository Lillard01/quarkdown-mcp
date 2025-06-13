"""Batch conversion tool for Quarkdown MCP server.

This module provides the convert_batch tool that processes multiple
Quarkdown documents in batch mode for efficient bulk operations.
"""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from .base import BaseTool


class ConvertBatchTool(BaseTool):
    """Tool for batch processing multiple Quarkdown documents.
    
    This tool allows users to convert multiple documents at once,
    apply consistent formatting, and generate reports on the conversion process.
    """
    
    def get_tool_definition(self) -> Tool:
        """Get the MCP tool definition for batch conversion.
        
        Returns:
            Tool definition object for MCP registration
        """
        return Tool(
            name="convert_batch",
            description="Convert multiple Quarkdown documents in batch mode with consistent settings",
            inputSchema={
                "type": "object",
                "properties": {
                    "documents": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Document name or identifier"
                                },
                                "content": {
                                    "type": "string",
                                    "description": "Quarkdown source content"
                                },
                                "output_name": {
                                    "type": "string",
                                    "description": "Custom output filename (optional)"
                                }
                            },
                            "required": ["name", "content"]
                        },
                        "description": "List of documents to process"
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["html", "pdf", "latex", "markdown", "docx"],
                        "default": "html",
                        "description": "Output format for all documents"
                    },
                    "output_directory": {
                        "type": "string",
                        "description": "Directory to save converted files (optional, uses temp dir if not specified)"
                    },
                    "template": {
                        "type": "string",
                        "description": "Template to apply to all documents (optional)"
                    },
                    "parallel_processing": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable parallel processing for faster conversion"
                    },
                    "max_workers": {
                        "type": "integer",
                        "default": 4,
                        "minimum": 1,
                        "maximum": 16,
                        "description": "Maximum number of parallel workers"
                    },
                    "continue_on_error": {
                        "type": "boolean",
                        "default": True,
                        "description": "Continue processing other documents if one fails"
                    },
                    "generate_index": {
                        "type": "boolean",
                        "default": False,
                        "description": "Generate an index file listing all converted documents"
                    },
                    "common_variables": {
                        "type": "object",
                        "description": "Common variables to apply to all documents"
                    }
                },
                "required": ["documents"]
            }
        )
        
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent | ImageContent | EmbeddedResource]:
        """Execute the batch conversion.
        
        Args:
            arguments: Tool execution arguments containing documents and conversion options
            
        Returns:
            List containing the batch conversion results and summary
        """
        try:
            # Validate required arguments
            self._validate_required_args(arguments, ["documents"])
            
            documents = arguments["documents"]
            output_format = arguments.get("output_format", "html")
            output_directory = arguments.get("output_directory")
            template = arguments.get("template")
            parallel_processing = arguments.get("parallel_processing", True)
            max_workers = arguments.get("max_workers", 4)
            continue_on_error = arguments.get("continue_on_error", True)
            generate_index = arguments.get("generate_index", False)
            common_variables = arguments.get("common_variables", {})
            
            # Validate documents
            if not documents or len(documents) == 0:
                return [self._create_error_content("No documents provided for batch conversion")]
                
            # Setup output directory
            if output_directory:
                output_dir = Path(output_directory)
                output_dir.mkdir(parents=True, exist_ok=True)
            else:
                output_dir = Path(tempfile.mkdtemp(prefix="quarkdown_batch_"))
                
            # Initialize conversion tracking
            conversion_results = []
            successful_conversions = []
            failed_conversions = []
            
            # Start batch conversion
            start_time = asyncio.get_event_loop().time()
            
            if parallel_processing and len(documents) > 1:
                # Parallel processing
                conversion_results = await self._process_documents_parallel(
                    documents, output_dir, output_format, template, 
                    common_variables, max_workers, continue_on_error
                )
            else:
                # Sequential processing
                conversion_results = await self._process_documents_sequential(
                    documents, output_dir, output_format, template, 
                    common_variables, continue_on_error
                )
                
            end_time = asyncio.get_event_loop().time()
            total_time = end_time - start_time
            
            # Categorize results
            for result in conversion_results:
                if result["success"]:
                    successful_conversions.append(result)
                else:
                    failed_conversions.append(result)
                    
            # Generate index file if requested
            index_file = None
            if generate_index and successful_conversions:
                index_file = await self._generate_index_file(
                    successful_conversions, output_dir, output_format
                )
                
            # Prepare response
            response_parts = []
            
            # Add summary
            summary = self._generate_conversion_summary(
                len(documents), len(successful_conversions), 
                len(failed_conversions), total_time
            )
            response_parts.append(self._create_text_content(f"**Batch Conversion Summary**\n{summary}"))
            
            # Add successful conversions details
            if successful_conversions:
                success_details = self._format_successful_conversions(successful_conversions)
                response_parts.append(self._create_success_content(
                    f"**Successful Conversions ({len(successful_conversions)})**\n{success_details}"
                ))
                
            # Add failed conversions details
            if failed_conversions:
                failure_details = self._format_failed_conversions(failed_conversions)
                response_parts.append(self._create_error_content(
                    f"**Failed Conversions ({len(failed_conversions)})**\n{failure_details}"
                ))
                
            # Add output directory information
            response_parts.append(self._create_text_content(
                f"**Output Directory**: {output_dir}\n"
                f"**Total Files Created**: {len(successful_conversions) + (1 if index_file else 0)}"
            ))
            
            # Add index file information
            if index_file:
                response_parts.append(self._create_text_content(
                    f"**Index File**: {index_file}\n"
                    "Open this file to navigate between all converted documents."
                ))
                
            # Add performance statistics
            perf_stats = self._generate_performance_stats(
                conversion_results, total_time, parallel_processing
            )
            response_parts.append(self._create_text_content(
                f"**Performance Statistics**\n{perf_stats}"
            ))
            
            return response_parts
            
        except Exception as e:
            return [self._create_error_content(f"Batch conversion error: {str(e)}")]
            
    async def _process_documents_parallel(
        self, documents: List[Dict], output_dir: Path, output_format: str,
        template: Optional[str], common_variables: Dict, max_workers: int,
        continue_on_error: bool
    ) -> List[Dict[str, Any]]:
        """Process documents in parallel.
        
        Args:
            documents: List of documents to process
            output_dir: Output directory
            output_format: Target format
            template: Template to use
            common_variables: Common variables
            max_workers: Maximum parallel workers
            continue_on_error: Whether to continue on errors
            
        Returns:
            List of conversion results
        """
        semaphore = asyncio.Semaphore(max_workers)
        
        async def process_single_document(doc: Dict) -> Dict[str, Any]:
            async with semaphore:
                return await self._convert_single_document(
                    doc, output_dir, output_format, template, common_variables
                )
                
        # Create tasks for all documents
        tasks = [process_single_document(doc) for doc in documents]
        
        if continue_on_error:
            # Use gather with return_exceptions to continue on errors
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Convert exceptions to error results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        "name": documents[i]["name"],
                        "success": False,
                        "error": str(result),
                        "output_file": None
                    })
                else:
                    processed_results.append(result)
                    
            return processed_results
        else:
            # Use gather without return_exceptions to fail fast
            return await asyncio.gather(*tasks)
            
    async def _process_documents_sequential(
        self, documents: List[Dict], output_dir: Path, output_format: str,
        template: Optional[str], common_variables: Dict, continue_on_error: bool
    ) -> List[Dict[str, Any]]:
        """Process documents sequentially.
        
        Args:
            documents: List of documents to process
            output_dir: Output directory
            output_format: Target format
            template: Template to use
            common_variables: Common variables
            continue_on_error: Whether to continue on errors
            
        Returns:
            List of conversion results
        """
        results = []
        
        for doc in documents:
            try:
                result = await self._convert_single_document(
                    doc, output_dir, output_format, template, common_variables
                )
                results.append(result)
            except Exception as e:
                error_result = {
                    "name": doc["name"],
                    "success": False,
                    "error": str(e),
                    "output_file": None
                }
                results.append(error_result)
                
                if not continue_on_error:
                    break
                    
        return results
        
    async def _convert_single_document(
        self, document: Dict, output_dir: Path, output_format: str,
        template: Optional[str], common_variables: Dict
    ) -> Dict[str, Any]:
        """Convert a single document.
        
        Args:
            document: Document to convert
            output_dir: Output directory
            output_format: Target format
            template: Template to use
            common_variables: Common variables
            
        Returns:
            Conversion result dictionary
        """
        try:
            doc_name = document["name"]
            doc_content = document["content"]
            output_name = document.get("output_name", f"{doc_name}.{output_format}")
            
            # Apply common variables to content
            if common_variables:
                doc_content = self._apply_variables(doc_content, common_variables)
                
            # Convert the document
            converted_content = await self.wrapper.compile_document(
                source_content=doc_content,
                output_format=output_format,
                template=template
            )
            
            # Save to output file
            output_file = output_dir / output_name
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(converted_content)
                
            return {
                "name": doc_name,
                "success": True,
                "output_file": str(output_file),
                "size": len(converted_content),
                "error": None
            }
            
        except Exception as e:
            return {
                "name": document["name"],
                "success": False,
                "output_file": None,
                "size": 0,
                "error": str(e)
            }
            
    def _apply_variables(self, content: str, variables: Dict) -> str:
        """Apply variables to document content.
        
        Args:
            content: Document content
            variables: Variables to apply
            
        Returns:
            Content with variables applied
        """
        for key, value in variables.items():
            placeholder = f"${{{key}}}"
            content = content.replace(placeholder, str(value))
            
        return content
        
    async def _generate_index_file(
        self, successful_conversions: List[Dict], output_dir: Path, output_format: str
    ) -> str:
        """Generate an index file for all converted documents.
        
        Args:
            successful_conversions: List of successful conversion results
            output_dir: Output directory
            output_format: Output format
            
        Returns:
            Path to the generated index file
        """
        index_content = self._create_index_content(successful_conversions, output_format)
        
        if output_format == "html":
            index_file = output_dir / "index.html"
        else:
            index_file = output_dir / "index.md"
            
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)
            
        return str(index_file)
        
    def _create_index_content(self, conversions: List[Dict], output_format: str) -> str:
        """Create content for the index file.
        
        Args:
            conversions: List of conversion results
            output_format: Output format
            
        Returns:
            Index file content
        """
        if output_format == "html":
            return self._create_html_index(conversions)
        else:
            return self._create_markdown_index(conversions)
            
    def _create_html_index(self, conversions: List[Dict]) -> str:
        """Create HTML index content.
        
        Args:
            conversions: List of conversion results
            
        Returns:
            HTML index content
        """
        html_content = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "    <meta charset='UTF-8'>",
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            "    <title>Quarkdown Batch Conversion Index</title>",
            "    <style>",
            "        body { font-family: Arial, sans-serif; margin: 40px; }",
            "        h1 { color: #333; }",
            "        .document-list { list-style-type: none; padding: 0; }",
            "        .document-item { margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }",
            "        .document-link { text-decoration: none; color: #0066cc; font-weight: bold; }",
            "        .document-link:hover { text-decoration: underline; }",
            "        .document-size { color: #666; font-size: 0.9em; }",
            "    </style>",
            "</head>",
            "<body>",
            "    <h1>Quarkdown Batch Conversion Index</h1>",
            f"    <p>Generated on {asyncio.get_event_loop().time()}</p>",
            "    <ul class='document-list'>"
        ]
        
        for conv in conversions:
            filename = os.path.basename(conv["output_file"])
            size_kb = conv["size"] / 1024
            html_content.extend([
                "        <li class='document-item'>",
                f"            <a href='{filename}' class='document-link'>{conv['name']}</a>",
                f"            <div class='document-size'>Size: {size_kb:.1f} KB</div>",
                "        </li>"
            ])
            
        html_content.extend([
            "    </ul>",
            "</body>",
            "</html>"
        ])
        
        return "\n".join(html_content)
        
    def _create_markdown_index(self, conversions: List[Dict]) -> str:
        """Create Markdown index content.
        
        Args:
            conversions: List of conversion results
            
        Returns:
            Markdown index content
        """
        md_content = [
            "# Quarkdown Batch Conversion Index",
            "",
            f"Generated on {asyncio.get_event_loop().time()}",
            "",
            "## Converted Documents",
            ""
        ]
        
        for conv in conversions:
            filename = os.path.basename(conv["output_file"])
            size_kb = conv["size"] / 1024
            md_content.append(f"- [{conv['name']}]({filename}) ({size_kb:.1f} KB)")
            
        return "\n".join(md_content)
        
    def _generate_conversion_summary(
        self, total: int, successful: int, failed: int, time_taken: float
    ) -> str:
        """Generate conversion summary.
        
        Args:
            total: Total documents
            successful: Successful conversions
            failed: Failed conversions
            time_taken: Time taken in seconds
            
        Returns:
            Formatted summary string
        """
        success_rate = (successful / total * 100) if total > 0 else 0
        
        summary = [
            f"- **Total Documents**: {total}",
            f"- **Successful**: {successful}",
            f"- **Failed**: {failed}",
            f"- **Success Rate**: {success_rate:.1f}%",
            f"- **Time Taken**: {time_taken:.2f} seconds",
            f"- **Average Time per Document**: {time_taken/total:.2f} seconds" if total > 0 else "- **Average Time**: N/A"
        ]
        
        return "\n".join(summary)
        
    def _format_successful_conversions(self, conversions: List[Dict]) -> str:
        """Format successful conversion details.
        
        Args:
            conversions: List of successful conversions
            
        Returns:
            Formatted details string
        """
        details = []
        for conv in conversions:
            size_kb = conv["size"] / 1024
            details.append(f"✅ **{conv['name']}** → {conv['output_file']} ({size_kb:.1f} KB)")
            
        return "\n".join(details)
        
    def _format_failed_conversions(self, conversions: List[Dict]) -> str:
        """Format failed conversion details.
        
        Args:
            conversions: List of failed conversions
            
        Returns:
            Formatted details string
        """
        details = []
        for conv in conversions:
            details.append(f"❌ **{conv['name']}**: {conv['error']}")
            
        return "\n".join(details)
        
    def _generate_performance_stats(
        self, results: List[Dict], total_time: float, parallel: bool
    ) -> str:
        """Generate performance statistics.
        
        Args:
            results: Conversion results
            total_time: Total processing time
            parallel: Whether parallel processing was used
            
        Returns:
            Formatted performance statistics
        """
        total_size = sum(r.get("size", 0) for r in results if r.get("success"))
        total_size_mb = total_size / (1024 * 1024)
        
        stats = [
            f"- **Processing Mode**: {'Parallel' if parallel else 'Sequential'}",
            f"- **Total Output Size**: {total_size_mb:.2f} MB",
            f"- **Processing Speed**: {total_size_mb/total_time:.2f} MB/s" if total_time > 0 else "- **Processing Speed**: N/A",
            f"- **Documents per Second**: {len(results)/total_time:.2f}" if total_time > 0 else "- **Documents per Second**: N/A"
        ]
        
        return "\n".join(stats)