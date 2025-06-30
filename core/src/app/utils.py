"""
Utility functions for the web UI: pipeline discovery, statistics, etc.
"""
import os
import glob
from datetime import datetime
import yaml

def discover_pipeline_files():
    """Automatically discovers available pipeline files in the project."""
    # Search from the project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
    pipeline_files = []
    projects = {}
    
    # Search for all pipeline*.yml files in any subdirectory of examples/
    pipeline_patterns = [
        os.path.join(project_root, "examples", "**", "pipeline.yml"),
        os.path.join(project_root, "examples", "**", "pipeline-*.yml")
    ]
    
    for pattern in pipeline_patterns:
        for file_path in glob.glob(pattern, recursive=True):
            relative_path = os.path.relpath(file_path, project_root)
            relative_path = relative_path.replace(os.sep, '/')
            
            # Extract project name and environment from path
            path_parts = relative_path.split('/')
            if len(path_parts) >= 3 and path_parts[0] == 'examples':
                project_name = path_parts[1]
                file_name = os.path.basename(file_path)
                
                # Determine environment type from filename
                if file_name == 'pipeline.yml':
                    environment = 'development'
                    env_suffix = ''
                elif file_name.startswith('pipeline-'):
                    env_suffix = file_name.replace('pipeline-', '').replace('.yml', '')
                    environment = env_suffix
                else:
                    environment = 'unknown'
                    env_suffix = ''
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                        name = config.get('name', f"{project_name} - {environment.title()}")
                        description = config.get('description', 'No description')
                        steps_count = 0
                        if 'pipeline' in config:
                            steps_count += len(config['pipeline'])
                        if 'parallel_steps' in config:
                            steps_count += len(config['parallel_steps'])
                except Exception as e:
                    name = f"{project_name} - {environment.title()}"
                    description = f'Pipeline file (Read error: {str(e)})'
                    steps_count = 0
                
                # Group by project
                if project_name not in projects:
                    projects[project_name] = {
                        'project_name': project_name,
                        'environments': {}
                    }
                
                # Add environment details
                projects[project_name]['environments'][environment] = {
                    'path': relative_path,
                    'name': name,
                    'description': description,
                    'directory': os.path.dirname(relative_path),
                    'steps_count': steps_count,
                    'size': os.path.getsize(file_path),
                    'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                    'environment': environment,
                    'env_suffix': env_suffix,
                    'file_name': file_name
                }
                
                # Also add to flat list for backward compatibility
                pipeline_files.append({
                    'path': relative_path,
                    'name': name,
                    'description': description,
                    'directory': os.path.dirname(relative_path),
                    'steps_count': steps_count,
                    'size': os.path.getsize(file_path),
                    'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                    'environment': environment,
                    'project_name': project_name,
                    'env_suffix': env_suffix
                })
    
    return {
        'flat_list': sorted(pipeline_files, key=lambda x: x['modified'], reverse=True),
        'grouped_by_project': projects
    }

def discover_pipeline_files_legacy():
    """Legacy function for backward compatibility - returns flat list only."""
    result = discover_pipeline_files()
    return result['flat_list']

def count_existing_projects():
    """Counts the number of existing projects in the examples folder."""
    try:
        # Search from the project root
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
        examples_dir = os.path.join(project_root, "examples")
        
        if not os.path.exists(examples_dir):
            return 0
        
        # Count directories that contain project files
        # A valid project must have at least one of these files
        project_indicators = [
            'pipeline.yml',
            'package.json',
            'requirements.txt',
            'Dockerfile',
            'main.py',
            'app.py',
            'index.html',
            'README.md'
        ]
        
        project_count = 0
        
        # Iterate over all subdirectories in examples
        for item in os.listdir(examples_dir):
            item_path = os.path.join(examples_dir, item)
            
            # Only count directories
            if os.path.isdir(item_path):
                # Check if it contains any project indicator file
                has_project_file = False
                for indicator in project_indicators:
                    if os.path.exists(os.path.join(item_path, indicator)):
                        has_project_file = True
                        break
                
                if has_project_file:
                    project_count += 1
        
        return project_count
        
    except Exception as e:
        print(f"Error counting projects: {e}")
        return 0
