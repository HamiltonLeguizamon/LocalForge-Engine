"""
Centralized module for logging configuration.
Provides consistent log configuration across the project.
"""
import logging
import os
from pathlib import Path
from typing import Optional, Union


class LogManager:
    """Centralized manager for logging configuration."""
    
    _initialized = False
    _log_dir = None
    
    @classmethod
    def setup_logging(cls, 
                     log_file: Optional[str] = None, 
                     level: Union[int, str] = logging.INFO,
                     log_dir: Optional[str] = None) -> None:
        """
        Sets up the logging system centrally.
        
        Args:
            log_file: Log file name (optional)
            level: Logging level
            log_dir: Base directory for logs (optional, uses project directory)
        """
        if cls._initialized:
            return
            
        # Determine logs directory
        if log_dir:
            cls._log_dir = Path(log_dir)
        else:
            # Use logs directory at the project root
            project_root = cls._get_project_root()
            cls._log_dir = project_root / "logs"
        
        # Create logs directory if it doesn't exist
        cls._log_dir.mkdir(exist_ok=True)
        
        # Configure level
        if isinstance(level, str):
            level = getattr(logging, level.upper())
        
        # Configure basic logging
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        # Configure log file if specified
        if log_file:
            log_path = cls._log_dir / log_file
            logging.basicConfig(
                filename=str(log_path),
                level=level,
                format=log_format,
                filemode='a'
            )
        else:
            logging.basicConfig(
                level=level,
                format=log_format
            )
        
        # Also add logging to console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        formatter = logging.Formatter(log_format)
        console_handler.setFormatter(formatter)
        
        # Avoid duplicate handlers
        root_logger = logging.getLogger()
        if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
            root_logger.addHandler(console_handler)
        
        cls._initialized = True
        
        logging.info(f"Logging configured. Directory: {cls._log_dir}")
        if log_file:
            logging.info(f"Log file: {log_path}")
    
    @classmethod
    def _get_project_root(cls) -> Path:
        """Gets the CI/CD project root."""
        current = Path(__file__).parent
        # Navigate up until finding the project root
        while current.parent != current:
            if (current / "requirements.txt").exists() or (current / "README.md").exists():
                return current
            current = current.parent
        
        # Fallback: use parent directory of core
        return Path(__file__).parent.parent.parent.parent
    
    @classmethod
    def get_log_dir(cls) -> Path:
        """Returns the configured logs directory."""
        if not cls._log_dir:
            cls.setup_logging()
        return cls._log_dir
    
    @classmethod
    def get_log_file_path(cls, filename: str) -> Path:
        """Gets the full path for a log file."""
        return cls.get_log_dir() / filename


# Backward compatibility function
def setup_logging(log_file: Optional[str] = None, level: Union[int, str] = logging.INFO) -> None:
    """
    Backward compatibility function for setup_logging.
    Redirects to LogManager.setup_logging().
    """
    LogManager.setup_logging(log_file=log_file, level=level)
