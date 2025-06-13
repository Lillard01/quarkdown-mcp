"""Project creation tool for Quarkdown MCP server.

This module provides the create_project tool that creates new Quarkdown
projects with proper directory structure and template files.
"""

from pathlib import Path
from typing import Any, Dict, List

from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from .base import BaseTool


class CreateProjectTool(BaseTool):
    """Tool for creating new Quarkdown projects.
    
    This tool creates a new Quarkdown project directory with the proper
    structure and template files to get started with document authoring.
    """
    
    def get_tool_definition(self) -> Tool:
        """Get the MCP tool definition for project creation.
        
        Returns:
            Tool definition object for MCP registration
        """
        return Tool(
            name="create_project",
            description="Create a new Quarkdown project with proper directory structure and template files",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path where the new project should be created"
                    },
                    "project_name": {
                        "type": "string",
                        "description": "Name of the project (used for default files)"
                    },
                    "template": {
                        "type": "string",
                        "enum": ["basic", "presentation", "book", "article"],
                        "default": "basic",
                        "description": "Project template to use"
                    },
                    "include_examples": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to include example files and documentation"
                    },
                    "initialize_git": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether to initialize a Git repository"
                    }
                },
                "required": ["project_path", "project_name"]
            }
        )
        
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent | ImageContent | EmbeddedResource]:
        """Execute the project creation.
        
        Args:
            arguments: Tool execution arguments containing project details
            
        Returns:
            List containing the project creation results
        """
        try:
            # Validate required arguments
            self._validate_required_args(arguments, ["project_path", "project_name"])
            
            project_path = Path(arguments["project_path"])
            project_name = arguments["project_name"]
            template = arguments.get("template", "basic")
            include_examples = arguments.get("include_examples", True)
            initialize_git = arguments.get("initialize_git", False)
            
            # Check if project directory already exists
            if project_path.exists() and any(project_path.iterdir()):
                return [self._create_error_content(
                    f"Directory {project_path} already exists and is not empty"
                )]
                
            # Create project directory
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Create basic project structure
            await self._create_project_structure(project_path, project_name, template, include_examples)
            
            # Initialize Git repository if requested
            if initialize_git:
                await self._initialize_git_repo(project_path)
                
            # Prepare response
            response_parts = []
            
            response_parts.append(self._create_success_content(
                f"Quarkdown project '{project_name}' created successfully"
            ))
            
            response_parts.append(self._create_text_content(
                f"**Project Location**: `{project_path.absolute()}`\n"
                f"**Template**: {template}\n"
                f"**Examples Included**: {'Yes' if include_examples else 'No'}\n"
                f"**Git Initialized**: {'Yes' if initialize_git else 'No'}"
            ))
            
            # List created files
            created_files = self._list_project_files(project_path)
            if created_files:
                files_list = "\n".join([f"- `{file}`" for file in created_files])
                response_parts.append(self._create_text_content(
                    f"**Created Files**:\n{files_list}"
                ))
                
            # Add getting started instructions
            response_parts.append(self._create_text_content(
                self._get_getting_started_instructions(project_path, project_name)
            ))
            
            return response_parts
            
        except Exception as e:
            return [self._create_error_content(str(e))]
            
    async def _create_project_structure(self, project_path: Path, project_name: str, 
                                       template: str, include_examples: bool) -> None:
        """Create the basic project directory structure and files.
        
        Args:
            project_path: Path to the project directory
            project_name: Name of the project
            template: Project template to use
            include_examples: Whether to include example files
        """
        # Create subdirectories
        (project_path / "src").mkdir(exist_ok=True)
        (project_path / "assets").mkdir(exist_ok=True)
        (project_path / "output").mkdir(exist_ok=True)
        
        if include_examples:
            (project_path / "examples").mkdir(exist_ok=True)
            
        # Create main document file
        main_content = self._get_template_content(template, project_name)
        (project_path / "src" / f"{project_name}.qmd").write_text(main_content, encoding="utf-8")
        
        # Create configuration file
        config_content = self._get_config_content(project_name, template)
        (project_path / "quarkdown.yaml").write_text(config_content, encoding="utf-8")
        
        # Create README
        readme_content = self._get_readme_content(project_name, template)
        (project_path / "README.md").write_text(readme_content, encoding="utf-8")
        
        # Create .gitignore
        gitignore_content = self._get_gitignore_content()
        (project_path / ".gitignore").write_text(gitignore_content, encoding="utf-8")
        
        # Create example files if requested
        if include_examples:
            await self._create_example_files(project_path, template)
            
    async def _create_example_files(self, project_path: Path, template: str) -> None:
        """Create example files for the project.
        
        Args:
            project_path: Path to the project directory
            template: Project template being used
        """
        examples_dir = project_path / "examples"
        
        # Basic example
        basic_example = self._get_basic_example_content()
        (examples_dir / "basic_example.qmd").write_text(basic_example, encoding="utf-8")
        
        # Template-specific examples
        if template == "presentation":
            presentation_example = self._get_presentation_example_content()
            (examples_dir / "presentation_example.qmd").write_text(presentation_example, encoding="utf-8")
        elif template == "book":
            book_example = self._get_book_example_content()
            (examples_dir / "book_example.qmd").write_text(book_example, encoding="utf-8")
            
    async def _initialize_git_repo(self, project_path: Path) -> None:
        """Initialize a Git repository in the project directory.
        
        Args:
            project_path: Path to the project directory
        """
        import subprocess
        
        try:
            subprocess.run(["git", "init"], cwd=project_path, check=True, capture_output=True)
            subprocess.run(["git", "add", "."], cwd=project_path, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], 
                         cwd=project_path, check=True, capture_output=True)
        except subprocess.CalledProcessError:
            # Git initialization failed, but don't fail the entire operation
            pass
            
    def _list_project_files(self, project_path: Path) -> List[str]:
        """List all files created in the project.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            List of relative file paths
        """
        files = []
        for file_path in project_path.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(project_path)
                files.append(str(relative_path))
        return sorted(files)
        
    def _get_template_content(self, template: str, project_name: str) -> str:
        """Get the main document content for the specified template.
        
        Args:
            template: Template type
            project_name: Name of the project
            
        Returns:
            Template content string
        """
        if template == "presentation":
            return f"""---
title: {project_name}
author: Your Name
date: {{{{ date }}}}
type: presentation
---

# {project_name}

Welcome to your Quarkdown presentation!

---

## Slide 2

This is your second slide.

- Point 1
- Point 2
- Point 3

---

## Slide 3

Add your content here.
"""
        elif template == "book":
            return f"""---
title: {project_name}
author: Your Name
date: {{{{ date }}}}
type: book
---

# {project_name}

## Chapter 1: Introduction

Welcome to your Quarkdown book!

## Chapter 2: Getting Started

Add your content here.
"""
        elif template == "article":
            return f"""---
title: {project_name}
author: Your Name
date: {{{{ date }}}}
type: article
---

# {project_name}

## Abstract

This is the abstract of your article.

## Introduction

Welcome to your Quarkdown article!

## Conclusion

Add your conclusions here.
"""
        else:  # basic
            return f"""---
title: {project_name}
author: Your Name
date: {{{{ date }}}}
---

# {project_name}

Welcome to your Quarkdown document!

This is a basic Quarkdown document. You can:

- Write **bold** and *italic* text
- Create lists and tables
- Add code blocks
- Include mathematical expressions: $E = mc^2$
- Use Quarkdown functions and variables

## Getting Started

Edit this file to create your document content.
"""
            
    def _get_config_content(self, project_name: str, template: str) -> str:
        """Get configuration file content.
        
        Args:
            project_name: Name of the project
            template: Template type
            
        Returns:
            Configuration content string
        """
        return f"""# Quarkdown Project Configuration
project:
  name: {project_name}
  template: {template}
  
output:
  directory: output
  formats:
    - html
    - pdf
    
build:
  source_directory: src
  assets_directory: assets
  
settings:
  pretty_output: true
  wrap_output: true
"""
        
    def _get_readme_content(self, project_name: str, template: str) -> str:
        """Get README file content.
        
        Args:
            project_name: Name of the project
            template: Template type
            
        Returns:
            README content string
        """
        return f"""# {project_name}

A Quarkdown {template} project.

## Getting Started

1. Edit the source files in the `src/` directory
2. Add any assets (images, etc.) to the `assets/` directory
3. Build your document using Quarkdown
4. Output files will be generated in the `output/` directory

## Building

To build this project:

```bash
quarkdown c src/{project_name}.qmd -o output/{project_name}.html
```

## Project Structure

- `src/` - Source Quarkdown files
- `assets/` - Images, stylesheets, and other assets
- `output/` - Generated output files
- `examples/` - Example files and documentation
- `quarkdown.yaml` - Project configuration
"""
        
    def _get_gitignore_content(self) -> str:
        """Get .gitignore file content.
        
        Returns:
            .gitignore content string
        """
        return """# Quarkdown output files
output/
*.html
*.pdf
*.tex

# Temporary files
.tmp/
*.tmp

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Editor files
.vscode/
.idea/
*.swp
*.swo
*~
"""
        
    def _get_basic_example_content(self) -> str:
        """Get basic example file content.
        
        Returns:
            Basic example content string
        """
        return """---
title: Basic Quarkdown Example
author: Example Author
---

# Basic Quarkdown Features

## Text Formatting

You can use **bold**, *italic*, and `code` formatting.

## Lists

- Item 1
- Item 2
  - Nested item
  - Another nested item

## Code Blocks

```python
def hello_world():
    print("Hello, Quarkdown!")
```

## Mathematics

Inline math: $E = mc^2$

Block math:
$$
\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}
$$

## Tables

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |
"""
        
    def _get_presentation_example_content(self) -> str:
        """Get presentation example content.
        
        Returns:
            Presentation example content string
        """
        return """---
title: Presentation Example
author: Example Author
type: presentation
---

# Title Slide

This is a presentation example.

---

## Content Slide

- Point 1
- Point 2
- Point 3

---

## Code Slide

```javascript
function example() {
    console.log("Hello from a presentation!");
}
```

---

## Thank You

Questions?
"""
        
    def _get_book_example_content(self) -> str:
        """Get book example content.
        
        Returns:
            Book example content string
        """
        return """---
title: Book Example
author: Example Author
type: book
---

# Preface

This is an example book structure.

# Chapter 1: Introduction

Welcome to the first chapter.

## Section 1.1

Content for the first section.

## Section 1.2

Content for the second section.

# Chapter 2: Advanced Topics

This chapter covers advanced topics.

## Section 2.1

Advanced content here.
"""
        
    def _get_getting_started_instructions(self, project_path: Path, project_name: str) -> str:
        """Get getting started instructions.
        
        Args:
            project_path: Path to the project directory
            project_name: Name of the project
            
        Returns:
            Getting started instructions string
        """
        return f"""**Getting Started**:

1. **Navigate to your project**:
   ```bash
   cd {project_path.absolute()}
   ```

2. **Edit your main document**:
   ```bash
   # Edit the main source file
   nano src/{project_name}.qmd
   ```

3. **Build your document**:
   ```bash
   # Compile to HTML
   quarkdown c src/{project_name}.qmd -o output/{project_name}.html
   
   # Compile to PDF
   quarkdown c src/{project_name}.qmd -o output/{project_name}.pdf
   ```

4. **Start a preview server**:
   ```bash
   quarkdown start src/{project_name}.qmd
   ```

For more information, check the examples in the `examples/` directory!
"""