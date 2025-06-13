"""Configuration module for Quarkdown MCP server.

This module provides configuration management for the Quarkdown MCP server,
including JAR path, temporary directory settings, and execution options.
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class QuarkdownConfig:
    """Configuration class for Quarkdown MCP server.
    
    This class manages all configuration settings needed to run Quarkdown
    operations, including JAR file location, temporary directories, and
    execution parameters.
    """
    
    def __init__(self, jar_path: Optional[str] = None, temp_dir: Optional[str] = None, log_level: str = "INFO"):
        """Initialize Quarkdown configuration.
        
        Args:
            jar_path: Path to the Quarkdown JAR file. If None, uses default location.
            temp_dir: Temporary directory for file operations. If None, uses system temp.
            log_level: Logging level for operations. Defaults to INFO.
        """
        # Set JAR path - default to the built JAR in the project
        if jar_path is None:
            project_root = Path(__file__).parent.parent.parent.parent
            jar_path_obj = project_root / "quarkdown" / "build" / "libs" / "quarkdown.jar"
        else:
            jar_path_obj = Path(jar_path)
            
        # Validate JAR file exists
        if not jar_path_obj.exists():
            raise FileNotFoundError(f"JAR file not found at: {jar_path_obj}")
            
        # Store as string for API consistency
        self.jar_path = str(jar_path_obj)
            
        # Set temporary directory
        if temp_dir is None:
            temp_dir_obj = Path(tempfile.gettempdir()) / "quarkdown_mcp"
            # Store as string for API consistency
            self.temp_dir = str(temp_dir_obj)
            # Ensure temp directory exists when using default
            Path(self.temp_dir).mkdir(parents=True, exist_ok=True)
        else:
            temp_dir_obj = Path(temp_dir)
            # Validate that explicitly provided temp directory exists
            if not temp_dir_obj.exists():
                raise FileNotFoundError(f"Temporary directory not found: {temp_dir_obj}")
            # Store as string for API consistency
            self.temp_dir = str(temp_dir_obj)
        
        # Set log level with validation
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level not in valid_log_levels:
            raise ValueError(f"Invalid log level: {log_level}. Must be one of {valid_log_levels}")
        self.log_level = log_level
        
        # Java executable path
        self.java_executable = "java"
        
        # Default timeout for operations (in seconds)
        self.timeout = 300
        
        # Default encoding
        self.encoding = "utf-8"
        
        # Track temporary files for cleanup
        self._temp_files = []
        
    def create_temp_file(self, content: str | bytes = "", suffix: str = ".qmd") -> Path:
        """Create a temporary file with the given content.
        
        Args:
            content: Content to write to the file (str or bytes)
            suffix: File extension/suffix
            
        Returns:
            Path to the created temporary file
        """
        import uuid
        # Use shorter UUID to avoid "File name too long" error
        short_uuid = str(uuid.uuid4())[:8]
        temp_file = Path(self.temp_dir) / f"temp_{short_uuid}{suffix}"
        
        if content:
            if isinstance(content, bytes):
                temp_file.write_bytes(content)
            else:
                temp_file.write_text(content, encoding=self.encoding)
        
        # Track the file for cleanup
        self._temp_files.append(temp_file)
            
        return temp_file
        
    def create_temp_dir(self, prefix: str = "quarkdown_") -> Path:
        """Create a temporary directory.
        
        Args:
            prefix: Prefix for the temporary directory name
            
        Returns:
            Path to the created temporary directory
        """
        import uuid
        # Use shorter UUID to avoid "Directory name too long" error
        short_uuid = str(uuid.uuid4())[:8]
        temp_dir = Path(self.temp_dir) / f"{prefix}{short_uuid}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        return temp_dir
        
    def cleanup_temp_file(self, file_path: Path) -> None:
        """Clean up a temporary file.
        
        Args:
            file_path: Path to the file to remove
        """
        try:
            if file_path.exists() and file_path.is_relative_to(Path(self.temp_dir)):
                file_path.unlink()
        except Exception:
            # Ignore cleanup errors
            pass
            
    def get_output_formats(self) -> list[str]:
        """Get list of supported output formats.
        
        Returns:
            List of supported output format extensions
        """
        return ["html", "pdf", "tex", "md"]
        
    def validate_output_format(self, format_name: str) -> bool:
        """Validate if the given output format is supported.
        
        Args:
            format_name: Output format to validate
            
        Returns:
            True if format is supported, False otherwise
        """
        return format_name.lower() in self.get_output_formats()
        
    def validate(self) -> None:
        """Validate the configuration settings.
        
        Raises:
            FileNotFoundError: If JAR file or temp directory doesn't exist
        """
        # Validate JAR file exists
        jar_path_obj = Path(self.jar_path)
        if not jar_path_obj.exists():
            raise FileNotFoundError(f"JAR file not found: {jar_path_obj}")
            
        # Validate temp directory exists
        temp_dir_obj = Path(self.temp_dir)
        if not temp_dir_obj.exists():
            raise FileNotFoundError(f"Temporary directory not found: {temp_dir_obj}")
    
    @classmethod
    def from_env(cls) -> "QuarkdownConfig":
        """Create configuration from environment variables.
        
        Environment variables:
            QUARKDOWN_JAR_PATH: Path to the Quarkdown JAR file (required)
            QUARKDOWN_TEMP_DIR: Temporary directory path (optional)
            QUARKDOWN_LOG_LEVEL: Log level (optional, defaults to INFO)
            
        Returns:
            QuarkdownConfig instance
            
        Raises:
            ValueError: If required environment variables are missing
        """
        jar_path = os.environ.get("QUARKDOWN_JAR_PATH")
        if jar_path is None:
            raise ValueError("QUARKDOWN_JAR_PATH environment variable is required")
            
        temp_dir = os.environ.get("QUARKDOWN_TEMP_DIR")
        if temp_dir is None:
            # When no temp_dir is specified in env, use system temp directly
            temp_dir = tempfile.gettempdir()
            
        log_level = os.environ.get("QUARKDOWN_LOG_LEVEL", "INFO")
        
        return cls(jar_path=jar_path, temp_dir=temp_dir, log_level=log_level)
    
    @classmethod
    def from_dict(cls, config_data: dict) -> "QuarkdownConfig":
        """Create configuration from dictionary.
        
        Args:
            config_data: Dictionary containing configuration data
            
        Returns:
            QuarkdownConfig instance
            
        Raises:
            ValueError: If required fields are missing
            TypeError: If field types are invalid
        """
        jar_path = config_data.get("jar_path")
        if jar_path is None:
            raise ValueError("jar_path is required")
            
        temp_dir = config_data.get("temp_dir")
        if temp_dir is not None and not isinstance(temp_dir, str):
            raise TypeError("temp_dir must be a string")
            
        log_level = config_data.get("log_level", "INFO")
        
        return cls(jar_path=jar_path, temp_dir=temp_dir, log_level=log_level)
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary.
        
        Returns:
            Dictionary containing configuration values
        """
        return {
            "jar_path": self.jar_path,
            "temp_dir": self.temp_dir,
            "log_level": self.log_level
        }
    
    def __repr__(self) -> str:
        """String representation of configuration.
        
        Returns:
            String representation
        """
        return f"QuarkdownConfig(jar_path='{self.jar_path}', temp_dir='{self.temp_dir}', log_level='{self.log_level}')"
    
    def __eq__(self, other) -> bool:
        """Check equality with another configuration.
        
        Args:
            other: Another QuarkdownConfig instance
            
        Returns:
            True if configurations are equal
        """
        if not isinstance(other, QuarkdownConfig):
            return False
        return (
            self.jar_path == other.jar_path and
            self.temp_dir == other.temp_dir and
            self.log_level == other.log_level
        )
    
    def __hash__(self) -> int:
        """Hash function for configuration.
        
        Returns:
            Hash value based on configuration attributes
        """
        return hash((self.jar_path, self.temp_dir, self.log_level))
    
    def copy(self) -> "QuarkdownConfig":
        """Create a copy of the configuration.
        
        Returns:
            New QuarkdownConfig instance with same values
        """
        return QuarkdownConfig(
            jar_path=self.jar_path,
            temp_dir=self.temp_dir,
            log_level=self.log_level
        )
    
    def update(self, **kwargs) -> None:
        """Update configuration attributes.
        
        Args:
            **kwargs: Configuration attributes to update
            
        Raises:
            AttributeError: If invalid field is provided
            ValueError: If invalid log level is provided
        """
        valid_fields = {"jar_path", "temp_dir", "log_level"}
        
        for key, value in kwargs.items():
            if key not in valid_fields:
                raise AttributeError(f"Invalid configuration field: {key}")
            
            if key == "log_level":
                valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
                if value not in valid_levels:
                    raise ValueError(f"Invalid log level: {value}. Must be one of {valid_levels}")
            
            setattr(self, key, value)
    
    def is_valid(self) -> bool:
        """Check if configuration is valid.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            self.validate()
            return True
        except (FileNotFoundError, ValueError):
            return False
    
    def get_java_command(self, jvm_options: list = None) -> list:
        """Get Java command for executing Quarkdown.
        
        Args:
            jvm_options: Optional JVM options to include
            
        Returns:
            List of command arguments
        """
        command = ["java"]
        
        if jvm_options:
            command.extend(jvm_options)
            
        command.extend(["-jar", self.jar_path])
        
        return command
    
    def cleanup_temp_files(self) -> None:
        """Clean up all temporary files created by this config instance."""
        for temp_file in self._temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
                    logger.debug(f"Cleaned up temporary file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {temp_file}: {e}")
        self._temp_files.clear()
        
    def cleanup_temp_file(self, file_path: Path) -> None:
        """Clean up a specific temporary file.
        
        Args:
            file_path: Path to the temporary file to clean up
        """
        try:
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Cleaned up temporary file: {file_path}")
            if file_path in self._temp_files:
                self._temp_files.remove(file_path)
        except Exception as e:
            logger.warning(f"Failed to clean up temporary file {file_path}: {e}")
    
    def get_log_config(self) -> dict:
        """Get logging configuration dictionary.
        
        Returns:
            Dictionary containing logging configuration
        """
        return {
            "level": self.log_level,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "handlers": [
                {
                    "class": "logging.StreamHandler",
                    "level": self.log_level,
                    "formatter": "default"
                }
            ]
        }