"""
Base class for all project template generators.
Defines the common interface and shared functionality.
"""
from abc import ABC, abstractmethod
from pathlib import Path
import os
import logging
from typing import Optional, Set
from core.src.utils.project_utils import ProjectValidator, FileSystemUtils, ProjectCleaner
from core.src.utils.generator_utils import ProjectCreateManager


class BaseProjectGenerator(ABC):
    """Abstract base class for project generators."""
    
    def __init__(self, project_name: str, output_dir: str, additional_reserved: Optional[Set[str]] = None):
        """
        Initializes the base generator.
        
        Args:
            project_name: Name of the project to generate
            output_dir: Directory where the project will be created
            additional_reserved: Additional reserved words specific to the generator
        """
        # Validate and sanitize project name
        self.original_project_name = project_name
        self.project_name, validation_logs = ProjectValidator.validate_project_name(
            project_name, additional_reserved
        )
        
        # Log validation messages
        for log_msg in validation_logs:
            logging.info(log_msg)
        
        self.output_dir = Path(output_dir)
        self.project_path = self.output_dir / self.project_name
    def create_project(self) -> bool:
        """
        Creates the complete project with validation and cleanup.
        Uses centralized project creation logic with enhanced validation.
        
        Returns:
            bool: True if the project was created successfully, False otherwise
        """
        try:
            # 1. Check for directory conflicts with detailed reporting
            has_conflicts, conflict_messages = FileSystemUtils.check_directory_conflicts(self.project_path)
            
            if has_conflicts:
                for msg in conflict_messages:
                    logging.warning(msg)
                
                # If directory exists and is not empty, check if we should proceed
                if self.project_path.exists() and any(self.project_path.iterdir()):
                    logging.error(f"Cannot create project in non-empty directory: {self.project_path}")
                    logging.info("💡 Tip: Choose a different name or clean the existing directory")
                    return False
            
            # 2. Check available disk space (basic check)
            if not self._check_disk_space():
                return False
            
            # 3. Create project directory with proper permissions
            if not FileSystemUtils.ensure_directory_exists(str(self.project_path)):
                logging.error(f"Failed to create project directory: {self.project_path}")
                return False
            
            # 4. Create directory structure
            logging.info(f"📁 Creating directory structure...")
            self._create_directory_structure()
            
            # 5. Generate files
            logging.info(f"📝 Generating project files...")
            self._generate_files()
            
            # 6. Verify project integrity
            if not self._verify_project_integrity():
                logging.warning("⚠️  Project creation completed but some issues were detected")
            
            logging.info(f"✅ Project '{self.project_name}' successfully created in {self.project_path}")
            
            # 7. Show final name if it was changed
            if self.project_name != self.original_project_name:
                logging.info(f"📝 Original name '{self.original_project_name}' was sanitized to '{self.project_name}'")
            
            # 8. Show next steps
            self._show_next_steps()
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Error creating project: {e}")
            
            # Enhanced cleanup for failed project
            if self.project_path.exists():
                logging.info(f"🧹 Cleaning up failed project creation...")
                cleanup_success = ProjectCleaner.cleanup_failed_project(self.project_path, keep_logs=True)
                if cleanup_success:
                    logging.info("✅ Cleanup completed successfully")
                else:
                    logging.warning("⚠️  Cleanup may be incomplete - manual intervention may be required")
            
            return False
    
    def _check_disk_space(self) -> bool:
        """
        Check if there's sufficient disk space for project creation.
        
        Returns:
            bool: True if sufficient space is available
        """
        try:
            # Get free space in output directory
            stat = os.statvfs(str(self.output_dir)) if hasattr(os, 'statvfs') else None
            if stat:
                free_bytes = stat.f_frsize * stat.f_bavail
                # Require at least 100MB free space
                min_required = 100 * 1024 * 1024  # 100MB
                if free_bytes < min_required:
                    logging.error(f"Insufficient disk space. Required: {min_required // (1024*1024)}MB, Available: {free_bytes // (1024*1024)}MB")
                    return False
        except (AttributeError, OSError):
            # On Windows or if check fails, proceed anyway
            pass
        
        return True
    
    def _verify_project_integrity(self) -> bool:
        """
        Verify that the project was created correctly.
        
        Returns:
            bool: True if project appears to be valid
        """
        if not self.project_path.exists():
            logging.error("Project directory was not created")
            return False
        
        # Check if project has any content
        try:
            contents = list(self.project_path.iterdir())
            if not contents:
                logging.warning("Project directory is empty")
                return False
                
            # Basic file checks
            essential_files = self._get_essential_files()
            missing_files = []
            
            for file_path in essential_files:
                full_path = self.project_path / file_path
                if not full_path.exists():
                    missing_files.append(file_path)
            
            if missing_files:
                logging.warning(f"Missing essential files: {', '.join(missing_files)}")
                return False
                
        except Exception as e:
            logging.warning(f"Could not verify project integrity: {e}")
            return False
        
        return True
    
    def _get_essential_files(self) -> list:
        """
        Get list of essential files that should exist in the project.
        Override in subclasses to specify project-specific essential files.
        
        Returns:
            list: List of essential file paths relative to project root
        """
        return []  # Default: no essential files required
    
    def _show_next_steps(self):
        """
        Show next steps to the user after project creation.
        Override in subclasses to provide project-specific guidance.
        """
        logging.info(f"")
        logging.info(f"🎉 Next steps:")
        logging.info(f"   1. cd {self.project_name}")
        logging.info(f"   2. Review the README.md file")
        logging.info(f"   3. Set up your development environment")
        logging.info(f"")
    
    @classmethod
    def create_project_safe(
        cls,
        project_name: str,
        output_dir: str,
        **kwargs
    ) -> tuple:
        """
        Class method for safe project creation with comprehensive error handling.
        
        Args:
            project_name: Name of the project
            output_dir: Output directory
            **kwargs: Additional arguments for the generator
            
        Returns:
            tuple: (success: bool, final_project_name: str, error_message: str or None)
        """
        return ProjectCreateManager.create_project_with_validation(
            cls, project_name, output_dir, **kwargs
        )
    
    def _create_directory_structure(self):
        """Creates the basic directory structure."""
        directories = self.get_directory_structure()
        for directory in directories:
            (self.project_path / directory).mkdir(parents=True, exist_ok=True)
    
    def _generate_files(self):
        """Generates all project files."""
        files = self.get_project_files()
        for file_path, content in files.items():
            full_path = self.project_path / file_path
            try:
                # Only format if there's {project_name}
                if '{project_name}' in content:
                    formatted_content = content.format(project_name=self.project_name)
                else:
                    formatted_content = content
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(formatted_content)
                logging.info(f"File generated: {full_path}")
            except Exception as e:
                logging.error(f"Error generating file {file_path}: {e}")
                print(f"[DEBUG] Error generating file {file_path}: {e}")
    
    @abstractmethod
    def get_directory_structure(self) -> list:
        """
        Returns the list of directories to create.
        
        Returns:
            list: List of directory paths relative to the project
        """
        pass
    
    @abstractmethod
    def get_project_files(self) -> dict:
        """
        Returns a dictionary with the files to generate.
        
        Returns:
            dict: Dictionary where keys are file paths and values are their content
        """
        pass
    
    @abstractmethod
    def get_project_type(self) -> str:
        """
        Returns the project type.
        
        Returns:
            str: Project type (e.g.: 'flask', 'fastapi', etc.)
        """
        pass
