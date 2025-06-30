"""
Centralized utilities for project generators.
Contains shared functionality that can be used across all generators.
"""
import os
import sys
import stat
import json
import shutil
import logging
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


def _get_command_executable(command: str) -> str:
    """
    Get the correct executable name for the current platform.
    
    Args:
        command: Base command name (e.g., 'git', 'npm', 'node')
        
    Returns:
        str: Platform-appropriate executable name
    """
    if os.name == 'nt' and not command.endswith('.exe'):
        # On Windows, try to find the .exe version
        exe_command = f"{command}.exe"
        if shutil.which(exe_command):
            return exe_command
        # Fallback to original command
        return command
    return command


def _run_command_safe(cmd_list: List[str], **kwargs) -> subprocess.CompletedProcess:
    """
    Run a command safely without shell=True.
    
    Args:
        cmd_list: List of command components
        **kwargs: Additional keyword arguments for subprocess
        
    Returns:
        subprocess.CompletedProcess: Result of the command execution
    """
    # Ensure the first command is properly resolved
    if cmd_list:
        cmd_list[0] = _get_command_executable(cmd_list[0])
    
    # Remove shell=True if present in kwargs
    kwargs.pop('shell', None)
    
    return subprocess.run(cmd_list, **kwargs)


def _check_command_availability(command: str) -> bool:
    """
    Check if a command is available in the system PATH.
    
    Args:
        command: Command to check
        
    Returns:
        bool: True if command is available
    """
    return shutil.which(_get_command_executable(command)) is not None


class DependencyManager:
    """Manages checking and installation of dependencies across all generators."""
    
    @staticmethod
    def ensure_python_package(package_name: str, import_name: str = None) -> bool:
        """
        Ensure a Python package is installed.
        
        Args:
            package_name: Name of the package for pip install
            import_name: Name to use for import check (defaults to package_name)
            
        Returns:
            bool: True if package is available, False otherwise
        """
        import_name = import_name or package_name.split('[')[0]  # Handle extras like 'bandit[toml]'
        
        try:
            __import__(import_name)
            return True
        except ImportError:
            logging.info(f"📦 Installing {package_name}...")
            try:
                result = _run_command_safe([
                    sys.executable, '-m', 'pip', 'install', package_name
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
                
                if result.returncode == 0:
                    return True
                else:
                    logging.error(f"❌ Failed to install {package_name}: exit code {result.returncode}")
                    return False
            except subprocess.TimeoutExpired:
                logging.error(f"❌ Pip install timed out for {package_name}")
                return False
            except Exception as e:
                logging.error(f"❌ Failed to install {package_name}: {e}")
                return False
    
    @staticmethod
    def ensure_cookiecutter() -> bool:
        """Ensure cookiecutter is installed."""
        return DependencyManager.ensure_python_package('cookiecutter')
    
    @staticmethod
    def ensure_pyyaml() -> bool:
        """Ensure PyYAML is installed."""
        return DependencyManager.ensure_python_package('PyYAML', 'yaml')
    
    @staticmethod
    def ensure_git() -> bool:
        """
        Check if Git is available on the system and provide installation guidance.
        
        Returns:
            bool: True if Git is available, False otherwise
        """
        if DependencyManager.check_system_command('git'):
            return True
        
        logging.error("❌ Git is not installed or not available in PATH")
        logging.error("📥 Git is required to clone cookiecutter templates")
        
        if os.name == 'nt':  # Windows
            logging.error("💡 Install Git from: https://git-scm.com/download/win")
            logging.error("💡 Or use Git for Windows: https://gitforwindows.org/")
            logging.error("💡 Alternative: Install GitHub Desktop which includes Git")
        else:  # Unix-like
            logging.error("💡 Install Git using your package manager:")
            logging.error("   • Ubuntu/Debian: sudo apt-get install git")
            logging.error("   • CentOS/RHEL: sudo yum install git")
            logging.error("   • macOS: brew install git")
        
        return False
    
    @staticmethod
    def check_system_command(command: str) -> bool:
        """
        Check if a system command is available.
        
        Args:
            command: Command to check
            
        Returns:
            bool: True if command is available
        """
        try:
            # Use different version flags for different commands
            version_flag = '--version'
            if command == 'npm':
                version_flag = '--version'
            elif command == 'node':
                version_flag = '--version'
            elif command == 'docker':
                version_flag = '--version'
                
            result = _run_command_safe(
                [command, version_flag], 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL,
                timeout=10  # Add timeout to prevent hanging
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    @staticmethod
    def ensure_node_npm() -> Tuple[bool, bool]:
        """
        Check if Node.js and npm are available.
        
        Returns:
            tuple: (node_available, npm_available)
        """
        node_available = DependencyManager.check_system_command('node')
        npm_available = DependencyManager.check_system_command('npm')
        
        if not node_available:
            logging.warning("⚠️  Node.js is not installed. Please install Node.js from https://nodejs.org/")
        if not npm_available:
            logging.warning("⚠️  npm is not installed. Please install npm.")
            
        return node_available, npm_available
    
    @staticmethod
    def ensure_docker() -> bool:
        """
        Check if Docker is available.
        
        Returns:
            bool: True if Docker is available
        """
        docker_available = DependencyManager.check_system_command('docker')
        
        if not docker_available:
            logging.warning("⚠️  Docker is not installed. Some features may not work properly.")
            
        return docker_available
    
    @staticmethod
    def install_npm_dependencies(project_path: str) -> bool:
        """
        Install npm dependencies in the given project path.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            bool: True if dependencies were installed successfully
        """
        try:
            if not _check_command_availability('npm'):
                logging.error("❌ npm is not available")
                return False
            
            result = _run_command_safe(
                ['npm', 'install'], 
                cwd=project_path,
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL,
                timeout=300  # 5 minute timeout for npm install
            )
            
            if result.returncode == 0:
                logging.info("✅ npm dependencies installed")
                return True
            else:
                logging.error(f"❌ npm install failed with exit code {result.returncode}")
                return False
            
        except subprocess.TimeoutExpired:
            logging.error("❌ npm install timed out")
            return False
        except Exception as e:
            logging.error(f"❌ Error installing npm dependencies: {e}")
            return False


class FileOperations:
    """Common file operations used across generators."""
    
    @staticmethod
    def handle_remove_readonly(func, path, exc):
        """Error handler for Windows permission issues when removing files."""
        if os.path.exists(path):
            os.chmod(path, stat.S_IWRITE)
            func(path)
    
    @staticmethod
    def safe_rmtree(path: str) -> bool:
        """
        Safely remove a directory tree, handling Windows permission issues.
        
        Args:
            path: Path to directory to remove
            
        Returns:
            bool: True if successfully removed
        """
        if not os.path.exists(path):
            return True
            
        try:
            shutil.rmtree(path)
            return True
        except (OSError, PermissionError):
            try:
                shutil.rmtree(path, onerror=FileOperations.handle_remove_readonly)
                return True
            except Exception as e:
                logging.warning(f"Could not remove directory {path}: {e}")
                return False
    
    @staticmethod
    def fix_shell_script_line_endings(script_path: str) -> bool:
        """
        Fix line endings in shell scripts for cross-platform compatibility.
        
        Args:
            script_path: Path to the shell script
            
        Returns:
            bool: True if fixed successfully
        """
        if not os.path.exists(script_path):
            return False
            
        try:
            with open(script_path, 'rb') as f:
                content = f.read()
            
            # Convert CRLF to LF
            if b'\r\n' in content:
                content = content.replace(b'\r\n', b'\n')
                
                with open(script_path, 'wb') as f:
                    f.write(content)
                    
                logging.info(f"✅ Fixed line endings in {script_path}")
            
            return True
        except Exception as e:
            logging.warning(f"Failed to fix line endings in {script_path}: {e}")
            return False


class DockerUtils:
    """Docker-related utilities used across generators."""
    
    @staticmethod
    def optimize_dockerfile_pip_cache(dockerfile_path: str) -> bool:
        """
        Optimize Dockerfile to use pip cache for faster builds.
        
        Args:
            dockerfile_path: Path to the Dockerfile
            
        Returns:
            bool: True if optimized successfully
        """
        if not os.path.exists(dockerfile_path):
            return False
            
        try:
            with open(dockerfile_path, 'r') as f:
                content = f.read()
            
            original_content = content
            
            # Remove --no-cache flags to enable pip caching
            content = content.replace('pip install --no-cache -r', 'pip install -r')
            content = content.replace('pip install --no-cache ', 'pip install ')
            
            if content != original_content:
                with open(dockerfile_path, 'w') as f:
                    f.write(content)
                logging.info(f"✅ Dockerfile optimized: {os.path.relpath(dockerfile_path)}")
                return True
                
        except Exception as e:
            logging.warning(f"Failed to optimize Dockerfile {dockerfile_path}: {e}")
            
        return False
    
    @staticmethod
    def add_cache_volumes_to_compose(compose_file: str, services: List[str] = None) -> bool:
        """
        Add cache volumes to docker-compose file for better performance.
        
        Args:
            compose_file: Path to docker-compose file
            services: List of service names to update (auto-detect if None)
            
        Returns:
            bool: True if updated successfully
        """
        if not os.path.exists(compose_file):
            return False
        
        # Try with yq first, then fallback to Python YAML
        if DependencyManager.check_system_command('yq'):
            return DockerUtils._update_compose_with_yq(compose_file, services)
        else:
            return DockerUtils._update_compose_with_python(compose_file, services)
    
    @staticmethod
    def _update_compose_with_yq(compose_file: str, services: List[str]) -> bool:
        """Update docker-compose using yq command."""
        try:
            # Auto-detect services if not provided
            if not services:
                services = ['django', 'web', 'app', 'flask', 'node', 'react']
            
            for service in services:
                # Check if service exists
                check_cmd = ['yq', f'.services.{service}', compose_file]
                result = subprocess.run(check_cmd, capture_output=True, text=True)
                
                if result.returncode == 0 and result.stdout.strip() != 'null':
                    # Add pip cache volume
                    volume_cmd = [
                        'yq', '-i', 
                        f'.services.{service}.volumes += ["pip-cache:/root/.cache/pip"]',
                        compose_file
                    ]
                    subprocess.run(volume_cmd, check=True)
                    
                    # Add volume definition
                    volumes_cmd = [
                        'yq', '-i', 
                        '.volumes.pip-cache = {"driver": "local"}',
                        compose_file
                    ]
                    subprocess.run(volumes_cmd, check=True)
                    
                    logging.info(f"✅ Added cache volume to service '{service}'")
                    return True
                    
        except subprocess.CalledProcessError as e:
            logging.warning(f"Failed to update docker-compose with yq: {e}")
            return False
        
        return False
    
    @staticmethod
    def _update_compose_with_python(compose_file: str, services: List[str]) -> bool:
        """Update docker-compose using Python YAML."""
        try:
            if not DependencyManager.ensure_pyyaml():
                return False
                
            import yaml
            
            with open(compose_file, 'r') as f:
                compose_data = yaml.safe_load(f)
            
            if not compose_data or 'services' not in compose_data:
                return False
            
            # Auto-detect services if not provided
            if not services:
                services = list(compose_data['services'].keys())
            
            updated = False
            for service in services:
                if service in compose_data['services']:
                    service_config = compose_data['services'][service]
                    
                    # Add volumes if they don't exist
                    if 'volumes' not in service_config:
                        service_config['volumes'] = []
                    
                    cache_volume = "pip-cache:/root/.cache/pip"
                    if cache_volume not in service_config['volumes']:
                        service_config['volumes'].append(cache_volume)
                        updated = True
            
            if updated:
                # Add volume definition
                if 'volumes' not in compose_data:
                    compose_data['volumes'] = {}
                compose_data['volumes']['pip-cache'] = {'driver': 'local'}
                
                with open(compose_file, 'w') as f:
                    yaml.dump(compose_data, f, default_flow_style=False, indent=2)
                
                logging.info(f"✅ Added cache volumes to {compose_file}")
                return True
                
        except Exception as e:
            logging.warning(f"Failed to update docker-compose with Python: {e}")
            
        return False


class SecurityTools:
    """Security tools management for projects."""
    
    @staticmethod
    def add_security_tools_to_requirements(
        requirements_file: str, 
        tools: List[str] = None,
        framework: str = "python"
    ) -> bool:
        """
        Add security tools to requirements file.
        
        Args:
            requirements_file: Path to requirements file
            tools: List of security tools to add (uses defaults if None)
            framework: Framework type for appropriate tools
            
        Returns:
            bool: True if tools were added successfully
        """
        if not os.path.exists(requirements_file):
            return False
        
        # Default security tools by framework
        default_tools = {
            "python": [
                'bandit[toml]>=1.7.0',  # Security analysis
                'safety>=2.3.0',       # Vulnerable dependency checker
            ],
            "django": [
                'bandit[toml]>=1.7.0',
                'safety>=2.3.0',
                'django-debug-toolbar>=4.0.0',
                'django-extensions>=3.2.0',
            ],
            "flask": [
                'bandit[toml]>=1.7.0',
                'safety>=2.3.0',
            ]
        }
        
        tools = tools or default_tools.get(framework, default_tools["python"])
        
        try:
            with open(requirements_file, 'r+') as f:
                content = f.read()
                added_tools = []
                
                for tool in tools:
                    tool_name = tool.split('>=')[0].split('[')[0]
                    if tool_name not in content:
                        f.write(f"\n{tool}\n")
                        added_tools.append(tool_name)
                
                if added_tools:
                    logging.info(f"✅ Security tools added: {', '.join(added_tools)}")
                    return True
                    
        except Exception as e:
            logging.warning(f"Failed to add security tools to {requirements_file}: {e}")
            
        return False


class TemplateManager:
    """Manages cookiecutter template operations."""
    
    @staticmethod
    def get_cache_dir(app_name: str = "localforge") -> str:
        """Get or create cache directory for templates."""
        if os.name == 'nt':  # Windows
            cache_base = os.path.expanduser(f"~/AppData/Local/{app_name}")
        else:  # Unix-like
            cache_base = os.path.expanduser(f"~/.cache/{app_name}")
        
        cache_dir = os.path.join(cache_base, "templates")
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir
    
    @staticmethod
    def prepare_cookiecutter_template(template_url: str) -> str:
        """
        Prepare cookiecutter template for use (clone if URL).
        
        Args:
            template_url: URL or path to cookiecutter template
            
        Returns:
            str: Path to prepared template
            
        Raises:
            Exception: If git is not available or cloning fails
        """
        if template_url.startswith(('http://', 'https://', 'git@')) or template_url.endswith('.git'):
            # It's a URL, need git to clone
            if not DependencyManager.ensure_git():
                raise Exception(
                    "Git is required to clone cookiecutter templates but is not available. "
                    "Please install Git and ensure it's in your PATH."
                )
            
            cache_dir = TemplateManager.get_cache_dir()
            template_name = template_url.split('/')[-1].replace('.git', '')
            cached_template = os.path.join(cache_dir, template_name)
            
            if os.path.exists(cached_template):
                logging.info(f"📋 Using cached template: {template_name}")
                return cached_template
            
            logging.info(f"📥 Cloning template: {template_url}")
            try:
                result = _run_command_safe([
                    'git', 'clone', template_url, cached_template
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
                
                if result.returncode == 0:
                    return cached_template
                else:
                    raise subprocess.CalledProcessError(result.returncode, 'git clone')
                    
            except subprocess.TimeoutExpired:
                logging.error(f"Git clone timed out for {template_url}")
                raise Exception(f"Git clone timed out for {template_url}")
            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to clone template: {e}")
                raise Exception(f"Failed to clone template from {template_url}: {e}")
        else:
            # It's a local path
            if os.path.exists(template_url):
                return template_url
            else:
                raise FileNotFoundError(f"Template not found: {template_url}")
    
    @staticmethod
    def apply_cookiecutter_config(template_dir: str, output_dir: str, config: Dict) -> str:
        """
        Apply cookiecutter configuration and generate project.
        
        Args:
            template_dir: Path to cookiecutter template
            output_dir: Output directory for generated project
            config: Configuration dictionary
            
        Returns:
            str: Path to generated project
        """
        if not DependencyManager.ensure_cookiecutter():
            raise RuntimeError("Cookiecutter is required but not available")
        
        # Create temporary config file
        config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(config, config_file, indent=2)
        config_file.close()
        
        try:
            cmd = [
                'cookiecutter', template_dir,
                '--output-dir', output_dir,
                '--config-file', config_file.name,
                '--overwrite-if-exists',
                '--no-input'
            ]
            
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Find generated project directory
            entries = [d for d in os.listdir(output_dir) if not d.startswith('.')]
            if not entries:
                raise RuntimeError("No project was generated")
            
            return os.path.join(output_dir, entries[0])
            
        finally:
            # Clean up temp config file
            try:
                os.unlink(config_file.name)
            except OSError:
                pass


class PipelineGenerator:
    """Generates CI/CD pipeline configurations."""
    
    @staticmethod
    def create_pipeline_files(
        project_path: str,
        project_name: str,
        templates: Dict[str, str]
    ) -> bool:
        """
        Create pipeline files for different environments.
        
        Args:
            project_path: Path to the project
            project_name: Name of the project
            templates: Dictionary mapping environment to template content
            
        Returns:
            bool: True if files were created successfully
        """
        try:
            for env, template in templates.items():
                pipeline_file = os.path.join(project_path, f'pipeline-{env}.yml')
                
                # Format template with project name
                content = template.format(project_name=project_name)
                
                with open(pipeline_file, 'w') as f:
                    f.write(content)
                
                logging.info(f"✅ Created pipeline-{env}.yml")
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to create pipeline files: {e}")
            return False


class ProjectCreateManager:
    """Enhanced project creation manager with validation and cleanup."""
    
    @staticmethod
    def create_project_with_validation(
        generator_class,
        project_name: str,
        output_dir: str,
        **kwargs
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Create a project with comprehensive validation and cleanup.
        
        Args:
            generator_class: Generator class to use
            project_name: Name of the project
            output_dir: Output directory
            **kwargs: Additional arguments for the generator
            
        Returns:
            tuple: (success, final_project_name, error_message)
        """
        try:
            # Create generator instance
            generator = generator_class(project_name, output_dir, **kwargs)
            
            # Check if destination already exists
            project_path = Path(output_dir) / generator.project_name
            
            if project_path.exists():
                contents = list(project_path.iterdir())
                if contents:
                    return False, generator.project_name, f"Directory {project_path} already exists and is not empty"
            
            # Create the project
            success = generator.create_project()
            
            if success:
                return True, generator.project_name, None
            else:
                # Cleanup failed creation
                if project_path.exists():
                    FileOperations.safe_rmtree(str(project_path))
                return False, generator.project_name, "Project creation failed"
                
        except Exception as e:
            logging.error(f"Project creation error: {e}")
            return False, project_name, str(e)


class GitManager:
    """Git repository management utilities."""
    
    @staticmethod
    def initialize_repository(project_path: str, initial_commit_message: str = "Initial commit") -> bool:
        """
        Initialize a Git repository and create an initial commit.
        
        Args:
            project_path: Path to the project directory
            initial_commit_message: Message for the initial commit
            
        Returns:
            bool: True if repository was initialized successfully
        """
        try:
            # Check if git is available
            if not _check_command_availability('git'):
                logging.warning("⚠️  Git is not installed. Skipping repository initialization.")
                return False
            
            # Initialize git repository
            result = _run_command_safe(
                ['git', 'init'], 
                cwd=project_path,
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL,
                timeout=30
            )
            
            if result.returncode != 0:
                logging.warning("⚠️ Failed to initialize git repository")
                return False
            
            # Add all files
            result = _run_command_safe(
                ['git', 'add', '.'], 
                cwd=project_path,
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL,
                timeout=60
            )
            
            if result.returncode != 0:
                logging.warning("⚠️ Failed to add files to git repository")
                return False
            
            # Create initial commit
            result = _run_command_safe(
                ['git', 'commit', '-m', initial_commit_message], 
                cwd=project_path,
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL,
                timeout=30
            )
            
            if result.returncode != 0:
                logging.warning("⚠️ Failed to create initial commit")
                return False
            
            logging.info(f"✅ Git repository initialized in {project_path}")
            return True
            
        except subprocess.TimeoutExpired:
            logging.warning("⚠️ Git operations timed out")
            return False
        except Exception as e:
            logging.warning(f"⚠️ Error initializing Git repository: {e}")
            return False
    
    @staticmethod
    def check_git_available() -> bool:
        """Check if Git is available on the system."""
        return _check_command_availability('git')
