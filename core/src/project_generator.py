#!/usr/bin/env python
"""
Improved script for generating projects in LocalForge Engine.
Uses a modular architecture with generators specific to each project type.
"""
import argparse
import logging
import sys
from pathlib import Path

# Import generator registry
from core.src.generators.registry import generator_registry
# Import centralized logging
from core.src.utils.log_manager import setup_logging


def setup_logging_legacy():
    """Backward compatibility function - uses the centralized handler."""
    setup_logging(log_file="project_generator.log", level=logging.INFO)


def print_next_steps_and_tree(project_type, project_name, project_path):
    """Prints next steps and the full directory tree for the generated project."""
    print("\n📋 Next steps:")
    print(f"   1. cd {project_name}")
    print("   2. Review the README.md file for detailed instructions")
    print("   3. Execute the pipeline: python ../../run_pipeline.py --pipeline pipeline.yml")
    print("\n📁 Project structure:")
    print_directory_tree(project_path)

def print_directory_tree(root_path, prefix=""):
    """Recursively prints the directory tree starting from root_path."""
    import os
    root_path = str(root_path)
    entries = sorted(os.listdir(root_path))
    for idx, entry in enumerate(entries):
        path = os.path.join(root_path, entry)
        connector = "└── " if idx == len(entries) - 1 else "├── "
        print(prefix + connector + entry)
        if os.path.isdir(path):
            extension = "    " if idx == len(entries) - 1 else "│   "
            print_directory_tree(path, prefix + extension)


def create_project(project_type: str, project_name: str, output_dir: str = ".", 
                  template_url: str = None, interactive: bool = False) -> bool:
    """
    Creates a new project of the specified type.
    
    Args:
        project_type: Type of project to create
        project_name: Project name
        output_dir: Directory where to create the project
        template_url: URL of cookiecutter template (only for flask)
        interactive: Whether to use interactive mode (only for flask)
        
    Returns:
        bool: True if the project was created successfully, False otherwise
    """
    try:
        # Get the appropriate generator
        generator = generator_registry.get_generator(
            project_type, 
            project_name, 
            output_dir,
            template_url=template_url,
            interactive=interactive
        )
        
        # Create the project
        success = generator.create_project()
        
        if success:
            project_path = Path(output_dir) / project_name
            print(f"\n✅ Project '{project_name}' successfully created!")
            print(f"📁 Location: {project_path.absolute()}")
            print(f"🚀 Type: {project_type}")
            print_next_steps_and_tree(project_type, project_name, project_path)
            
        return success
        
    except ValueError as e:
        logging.error(f"Configuration error: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return False


def list_available_types():
    """Lists the available project types."""
    types = generator_registry.get_available_types()
    print("🛠️  Available project types:")
    for project_type in types:
        print(f"   • {project_type}")


def main():
    """Main function of the script."""
    setup_logging_legacy()
    
    parser = argparse.ArgumentParser(
        description='Improved LocalForge Engine project generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  %(prog)s --type flask --name my_api
  %(prog)s --type flask --name my_project --output ./projects
  %(prog)s --type flask --name my_app --interactive
  %(prog)s --type flask --name my_app --template https://github.com/my-template.git
  %(prog)s --list-types
        """
    )
    
    parser.add_argument(
        '--type', '-t',
        help='Type of project to create'
    )
    
    parser.add_argument(
        '--name', '-n',
        help='Project name'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='.',
        help='Output directory (default: current directory)'
    )
    
    parser.add_argument(
        '--template', 
        help='Cookiecutter template URL (only for Flask)'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Cookiecutter interactive mode (only for Flask)'
    )
    
    parser.add_argument(
        '--list-types', '-l',
        action='store_true',
        help='List available project types'
    )
    
    args = parser.parse_args()
    
    # Show available types
    if args.list_types:
        list_available_types()
        return
    
    # Validate required arguments
    if not args.type or not args.name:
        parser.error("--type and --name are required (use --list-types to see available types)")
    
    # Validate that the project name is valid
    if not args.name.replace('_', '').replace('-', '').isalnum():
        parser.error("The project name must contain only letters, numbers, hyphens and underscores")
    
    # Create the project
    success = create_project(
        args.type, 
        args.name, 
        args.output,
        template_url=args.template,
        interactive=args.interactive
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

