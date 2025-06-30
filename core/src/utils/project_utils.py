"""
Utility functions for project creation and validation.
Centralizes common functionality across all generators.
"""
import os
import re
import stat
import shutil
import logging
from pathlib import Path
from typing import Tuple, List, Set, Optional


class ProjectValidator:
    """Centralized project name validation and sanitization."""
    
    # Common reserved words across different frameworks
    COMMON_RESERVED_NAMES = {
        # Python built-ins
        'python', 'sys', 'os', 'json', 'http', 'test', 'tests', 'src', 'lib',
        'main', 'setup', 'config', 'utils', 'helpers', 'common', 'base',
        
        # Django reserved
        'django', 'settings', 'models', 'views', 'forms', 'admin', 'urls', 'manage',
        'migrations', 'static', 'templates', 'locale', 'fixtures',
        
        # Flask reserved  
        'flask', 'app', 'application', 'blueprints', 'api', 'auth', 'database',
        
        # Node.js/React reserved
        'node', 'npm', 'yarn', 'react', 'index', 'package', 'public', 'build',
        'dist', 'components', 'pages', 'hooks', 'context', 'store',
        
        # General development
        'project', 'demo', 'example', 'sample', 'template', 'scaffold',
        'dev', 'prod', 'staging', 'local', 'docker', 'kubernetes', 'k8s'
    }
    
    @classmethod
    def sanitize_project_name(cls, project_name: str, additional_reserved: Optional[Set[str]] = None) -> str:
        """
        Sanitize project name to avoid conflicts and ensure validity.
        
        Args:
            project_name: Original project name
            additional_reserved: Additional reserved words specific to the generator
            
        Returns:
            str: Sanitized project name
        """
        # Combine common reserved words with additional ones
        reserved_names = cls.COMMON_RESERVED_NAMES.copy()
        if additional_reserved:
            reserved_names.update(additional_reserved)
        
        # Basic cleanup: lowercase, replace non-alphanumeric with underscore
        slug = re.sub(r'[^a-z0-9_]', '_', project_name.lower())
        slug = re.sub(r'_+', '_', slug).strip('_')
        
        # Handle edge cases
        if not slug or slug[0].isdigit():
            slug = f"project_{slug}" if slug else "my_project"
            logging.info(f"🔧 Project name '{project_name}' renamed to '{slug}' (invalid identifier)")
        
        # Check reserved words
        if slug in reserved_names:
            slug = f"{slug}_app"
            logging.info(f"🔧 Project name '{project_name}' renamed to '{slug}' (reserved word)")
        
        return slug
    
    @classmethod
    def validate_project_name(cls, project_name: str, additional_reserved: Optional[Set[str]] = None) -> Tuple[str, List[str]]:
        """
        Validate project name and return sanitized version with log messages.
        
        Args:
            project_name: Original project name
            additional_reserved: Additional reserved words specific to the generator
            
        Returns:
            tuple: (sanitized_name, log_messages)
        """
        logs = []
        original_slug = re.sub(r'[^a-z0-9_]', '_', project_name.lower())
        original_slug = re.sub(r'_+', '_', original_slug).strip('_')
        
        sanitized_name = cls.sanitize_project_name(project_name, additional_reserved)
        
        if sanitized_name != original_slug:
            if sanitized_name.startswith('project_') or sanitized_name == "my_project":
                logs.append(f"⚠️  Project name '{project_name}' starts with number or is invalid - renamed to '{sanitized_name}'")
            elif sanitized_name.endswith('_app'):
                logs.append(f"⚠️  Project name '{project_name}' conflicts with reserved word - renamed to '{sanitized_name}'")
            else:
                logs.append(f"⚠️  Project name '{project_name}' sanitized to '{sanitized_name}'")
        
        return sanitized_name, logs


class FileSystemUtils:
    """Utility functions for file system operations."""
    
    @staticmethod
    def handle_remove_readonly(func, path, exc):
        """
        Error handler for Windows permission issues when removing files.
        
        Args:
            func: Function that was called
            path: Path that caused the error
            exc: Exception info
        """
        if os.path.exists(path):
            # Make the file writable and try again
            os.chmod(path, stat.S_IWRITE)
            func(path)
    
    @staticmethod
    def safe_rmtree(path: str) -> bool:
        """
        Safely remove a directory tree, handling Windows permission issues.
        
        Args:
            path: Path to directory to remove
            
        Returns:
            bool: True if successfully removed, False otherwise
        """
        if not os.path.exists(path):
            return True
            
        try:
            shutil.rmtree(path)
            return True
        except (OSError, PermissionError):
            # Try again with error handler for Windows
            try:
                shutil.rmtree(path, onerror=FileSystemUtils.handle_remove_readonly)
                return True
            except Exception as e:
                logging.warning(f"Could not remove directory {path}: {e}")
                return False
    
    @staticmethod
    def ensure_directory_exists(path: str) -> bool:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            path: Directory path to ensure exists
            
        Returns:
            bool: True if directory exists or was created successfully
        """
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            logging.error(f"Failed to create directory {path}: {e}")
            return False
    
    @staticmethod
    def check_directory_conflicts(project_path: Path) -> Tuple[bool, List[str]]:
        """
        Check for potential conflicts in the destination directory.
        
        Args:
            project_path: Path where project will be created
            
        Returns:
            tuple: (has_conflicts, conflict_messages)
        """
        conflicts = []
        has_conflicts = False
        
        if project_path.exists():
            if project_path.is_file():
                conflicts.append(f"❌ Cannot create project: '{project_path}' exists as a file")
                has_conflicts = True
            elif project_path.is_dir():
                # Check if directory is empty
                try:
                    contents = list(project_path.iterdir())
                    if contents:
                        conflicts.append(f"⚠️  Directory '{project_path}' already exists and is not empty")
                        conflicts.append(f"   Contents: {', '.join([item.name for item in contents[:5]])}")
                        if len(contents) > 5:
                            conflicts.append(f"   ... and {len(contents) - 5} more items")
                        has_conflicts = True
                except PermissionError:
                    conflicts.append(f"❌ Cannot access directory '{project_path}' - permission denied")
                    has_conflicts = True
        
        return has_conflicts, conflicts
    
    @staticmethod
    def get_cache_directory(app_name: str = "localforge") -> str:
        """
        Get or create a cache directory for the application.
        
        Args:
            app_name: Name of the application for cache directory
            
        Returns:
            str: Path to cache directory
        """
        if os.name == 'nt':  # Windows
            cache_base = os.path.expanduser(f"~/AppData/Local/{app_name}")
        else:  # Unix-like (Linux, macOS)
            cache_base = os.path.expanduser(f"~/.cache/{app_name}")
        
        cache_dir = os.path.join(cache_base, "templates")
        FileSystemUtils.ensure_directory_exists(cache_dir)
        return cache_dir


class ProjectCleaner:
    """Utility for cleaning up failed project creations."""
    
    @staticmethod
    def cleanup_failed_project(project_path: Path, keep_logs: bool = True) -> bool:
        """
        Clean up a failed project creation.
        
        Args:
            project_path: Path to the failed project
            keep_logs: Whether to preserve log files
            
        Returns:
            bool: True if cleanup was successful
        """
        if not project_path.exists():
            return True
        
        try:
            if keep_logs:
                # Move log files to a temporary location before cleanup
                log_backup = project_path.parent / f"{project_path.name}_logs_backup"
                if log_backup.exists():
                    FileSystemUtils.safe_rmtree(str(log_backup))
                
                log_backup.mkdir(exist_ok=True)
                
                # Look for common log file patterns
                log_patterns = ['*.log', '*.out', '*.err', 'logs/*']
                for pattern in log_patterns:
                    for log_file in project_path.glob(pattern):
                        if log_file.is_file():
                            try:
                                shutil.copy2(log_file, log_backup / log_file.name)
                            except Exception as e:
                                logging.warning(f"Could not backup log file {log_file}: {e}")
            
            # Remove the project directory
            success = FileSystemUtils.safe_rmtree(str(project_path))
            
            if success:
                logging.info(f"🧹 Cleaned up failed project at {project_path}")
                if keep_logs and log_backup.exists():
                    logging.info(f"📋 Log files backed up to {log_backup}")
            
            return success
            
        except Exception as e:
            logging.error(f"Failed to cleanup project {project_path}: {e}")
            return False
