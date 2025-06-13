"""Syntax validation tool for Quarkdown MCP server.

This module provides the validate_markdown tool that checks Quarkdown
source content for syntax errors and provides detailed error reporting.
"""

from typing import Any, Dict, List

from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from .base import BaseTool


class ValidateMarkdownTool(BaseTool):
    """Tool for validating Quarkdown document syntax.
    
    This tool analyzes Quarkdown source content and reports any syntax
    errors, helping users identify and fix issues in their documents.
    """
    
    def get_tool_definition(self) -> Tool:
        """Get the MCP tool definition for syntax validation.
        
        Returns:
            Tool definition object for MCP registration
        """
        return Tool(
            name="validate_markdown",
            description="Validate Quarkdown document syntax and report any errors or warnings",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_content": {
                        "type": "string",
                        "description": "The Quarkdown source content to validate"
                    },
                    "strict_mode": {
                        "type": "boolean",
                        "default": False,
                        "description": "Enable strict validation mode for more rigorous checking"
                    },
                    "check_functions": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to validate Quarkdown function syntax"
                    },
                    "check_variables": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to validate variable references"
                    },
                    "check_links": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether to validate external links (requires network access)"
                    }
                },
                "required": ["source_content"]
            }
        )
        
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent | ImageContent | EmbeddedResource]:
        """Execute the syntax validation.
        
        Args:
            arguments: Tool execution arguments containing source content and validation options
            
        Returns:
            List containing the validation results
        """
        try:
            # Validate required arguments
            self._validate_required_args(arguments, ["source_content"])
            
            source_content = arguments["source_content"]
            strict_mode = arguments.get("strict_mode", False)
            check_functions = arguments.get("check_functions", True)
            check_variables = arguments.get("check_variables", True)
            check_links = arguments.get("check_links", False)
            
            # Perform basic syntax validation using Quarkdown compiler
            validation_result = await self.wrapper.validate_syntax(source_content, strict_mode)
            
            is_valid = validation_result["valid"]
            errors = validation_result["errors"]
            warnings = validation_result["warnings"]
            
            # Perform additional validation checks if requested
            additional_warnings = []
            if check_functions:
                function_warnings = await self._validate_functions(source_content)
                additional_warnings.extend(function_warnings)
                
            if check_variables:
                variable_warnings = await self._validate_variables(source_content)
                additional_warnings.extend(variable_warnings)
                
            if check_links:
                link_warnings = await self._validate_links(source_content)
                additional_warnings.extend(link_warnings)
            
            # Combine all warnings
            all_warnings = warnings + additional_warnings
                
            # Prepare response
            response_parts = []
            
            # Add validation summary
            if is_valid and not all_warnings:
                response_parts.append(self._create_success_content(
                    "Document validation passed - no syntax errors found"
                ))
            elif is_valid and all_warnings:
                response_parts.append(self._create_text_content(
                    "✅ **Syntax Valid** but found warnings"
                ))
            else:
                response_parts.append(self._create_text_content(
                    f"❌ **Validation Failed** - found {len(errors)} error(s)"
                ))
                
            # Add detailed error information
            if errors:
                error_details = self._format_errors(errors)
                response_parts.append(self._create_text_content(
                    f"**Syntax Errors**:\n{error_details}"
                ))
                
            # Add warnings if any
            if all_warnings:
                warning_details = self._format_warnings(all_warnings)
                response_parts.append(self._create_text_content(
                    f"**Warnings**:\n{warning_details}"
                ))
                
            # Add validation statistics
            stats = await self._generate_validation_stats(source_content)
            response_parts.append(self._create_text_content(
                f"**Document Statistics**:\n{stats}"
            ))
            
            # Add suggestions if there are issues
            if errors or all_warnings:
                suggestions = self._generate_suggestions(errors, all_warnings)
                if suggestions:
                    response_parts.append(self._create_text_content(
                        f"**Suggestions**:\n{suggestions}"
                    ))
                    
            return response_parts
            
        except Exception as e:
            return [self._create_error_content(str(e))]
            
    async def _validate_functions(self, source_content: str) -> List[str]:
        """Validate Quarkdown function syntax.
        
        Args:
            source_content: Source content to validate
            
        Returns:
            List of function-related warnings
        """
        warnings = []
        lines = source_content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check for function calls
            if '{{' in line and '}}' in line:
                # Basic function syntax check
                function_calls = self._extract_function_calls(line)
                for func_call in function_calls:
                    if not self._is_valid_function_syntax(func_call):
                        warnings.append(f"Line {line_num}: Invalid function syntax: {func_call}")
                        
        return warnings
        
    async def _validate_variables(self, source_content: str) -> List[str]:
        """Validate variable references.
        
        Args:
            source_content: Source content to validate
            
        Returns:
            List of variable-related warnings
        """
        warnings = []
        lines = source_content.split('\n')
        
        # Extract variable definitions
        defined_vars = set()
        used_vars = set()
        
        for line_num, line in enumerate(lines, 1):
            # Check for variable definitions (simplified)
            if line.strip().startswith('$') and '=' in line:
                var_name = line.split('=')[0].strip().lstrip('$')
                defined_vars.add(var_name)
                
            # Check for variable usage
            var_uses = self._extract_variable_uses(line)
            for var_use in var_uses:
                used_vars.add(var_use)
                
        # Check for undefined variables
        undefined_vars = used_vars - defined_vars
        for var in undefined_vars:
            warnings.append(f"Undefined variable referenced: ${var}")
            
        return warnings
        
    async def _validate_links(self, source_content: str) -> List[str]:
        """Validate external links.
        
        Args:
            source_content: Source content to validate
            
        Returns:
            List of link-related warnings
        """
        warnings = []
        
        # Extract links from markdown
        import re
        link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        links = re.findall(link_pattern, source_content)
        
        for link_text, link_url in links:
            if link_url.startswith('http'):
                # This would require actual HTTP requests to validate
                # For now, just check basic URL format
                if not self._is_valid_url_format(link_url):
                    warnings.append(f"Invalid URL format: {link_url}")
                    
        return warnings
        
    def _extract_function_calls(self, line: str) -> List[str]:
        """Extract function calls from a line.
        
        Args:
            line: Line of text to analyze
            
        Returns:
            List of function call strings
        """
        import re
        pattern = r'\{\{([^}]+)\}\}'
        return re.findall(pattern, line)
        
    def _is_valid_function_syntax(self, func_call: str) -> bool:
        """Check if a function call has valid syntax.
        
        Args:
            func_call: Function call string to validate
            
        Returns:
            True if syntax appears valid
        """
        # Basic validation - function name should be valid identifier
        func_call = func_call.strip()
        if not func_call:
            return False
            
        # Check for basic function name pattern
        import re
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*'
        return bool(re.match(pattern, func_call.split('(')[0].strip()))
        
    def _extract_variable_uses(self, line: str) -> List[str]:
        """Extract variable uses from a line.
        
        Args:
            line: Line of text to analyze
            
        Returns:
            List of variable names
        """
        import re
        pattern = r'\$([a-zA-Z_][a-zA-Z0-9_]*)'
        return re.findall(pattern, line)
        
    def _is_valid_url_format(self, url: str) -> bool:
        """Check if URL has valid format.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL format appears valid
        """
        import re
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))
        
    def _format_errors(self, errors: List[str]) -> str:
        """Format error messages for display.
        
        Args:
            errors: List of error messages
            
        Returns:
            Formatted error string
        """
        if not errors:
            return "No errors found."
            
        formatted_errors = []
        for i, error in enumerate(errors, 1):
            formatted_errors.append(f"{i}. {error}")
            
        return "\n".join(formatted_errors)
        
    def _format_warnings(self, warnings: List[str]) -> str:
        """Format warning messages for display.
        
        Args:
            warnings: List of warning messages
            
        Returns:
            Formatted warning string
        """
        if not warnings:
            return "No warnings found."
            
        formatted_warnings = []
        for i, warning in enumerate(warnings, 1):
            formatted_warnings.append(f"{i}. ⚠️ {warning}")
            
        return "\n".join(formatted_warnings)
        
    async def _generate_validation_stats(self, source_content: str) -> str:
        """Generate document statistics.
        
        Args:
            source_content: Source content to analyze
            
        Returns:
            Formatted statistics string
        """
        lines = source_content.split('\n')
        
        stats = {
            "Total lines": len(lines),
            "Non-empty lines": len([line for line in lines if line.strip()]),
            "Characters": len(source_content),
            "Words": len(source_content.split()),
            "Function calls": len(self._extract_all_function_calls(source_content)),
            "Variable uses": len(self._extract_all_variable_uses(source_content))
        }
        
        formatted_stats = []
        for key, value in stats.items():
            formatted_stats.append(f"- **{key}**: {value}")
            
        return "\n".join(formatted_stats)
        
    def _extract_all_function_calls(self, content: str) -> List[str]:
        """Extract all function calls from content.
        
        Args:
            content: Content to analyze
            
        Returns:
            List of all function calls
        """
        all_calls = []
        for line in content.split('\n'):
            all_calls.extend(self._extract_function_calls(line))
        return all_calls
        
    def _extract_all_variable_uses(self, content: str) -> List[str]:
        """Extract all variable uses from content.
        
        Args:
            content: Content to analyze
            
        Returns:
            List of all variable uses
        """
        all_vars = []
        for line in content.split('\n'):
            all_vars.extend(self._extract_variable_uses(line))
        return all_vars
        
    def _generate_suggestions(self, errors: List[str], warnings: List[str]) -> str:
        """Generate helpful suggestions based on errors and warnings.
        
        Args:
            errors: List of error messages
            warnings: List of warning messages
            
        Returns:
            Formatted suggestions string
        """
        suggestions = []
        
        if any("function" in error.lower() for error in errors):
            suggestions.append("- Check function syntax: ensure proper `{{ function_name() }}` format")
            
        if any("variable" in warning.lower() for warning in warnings):
            suggestions.append("- Define variables before using them: `$variable_name = value`")
            
        if any("url" in warning.lower() for warning in warnings):
            suggestions.append("- Verify URL formats and accessibility")
            
        if not suggestions:
            suggestions.append("- Review the Quarkdown documentation for syntax guidelines")
            suggestions.append("- Check for missing closing brackets or parentheses")
            suggestions.append("- Ensure proper indentation and formatting")
            
        return "\n".join(suggestions)