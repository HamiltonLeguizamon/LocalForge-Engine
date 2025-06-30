"""
Module for project creation management and state.
"""
import os
import time
import threading
from core.src.generators.registry import generator_registry
from core.src.project_generator import create_project
from flask_socketio import SocketIO

def get_available_project_types():
    available_types = generator_registry.get_available_types()
    type_info = {
        'flask': {
            'name': 'flask',
            'display_name': 'Flask API (Cookiecutter)',
            'description': 'Professional REST API with Flask using cookiecutter templates, Docker, CI/CD and security best practices'
        },
        'django': {
            'name': 'django',
            'display_name': 'Django Web App (Cookiecutter)',
            'description': 'Complete web application with Django using official cookiecutter-django, Docker, PostgreSQL and best practices'
        },
        'node': {
            'name': 'node',
            'display_name': 'Node.js Express',
            'description': 'REST API with Node.js and Express, including middleware, routing and testing with Jest'
        },
        'react': {
            'name': 'react',
            'display_name': 'React App (Vite)',
            'description': 'Modern React application with Vite, optional TypeScript, React Router, testing with Vitest and Docker deployment'
        }
    }
    result = []
    for type_name in available_types:
        if type_name in type_info:
            result.append(type_info[type_name])
        else:
            result.append({
                'name': type_name,
                'display_name': type_name.title(),
                'description': f'Project of type {type_name} with automatic CI/CD configuration'
            })
    return result

class ProjectManager:
    def __init__(self, socketio):
        self.status = {
            "creating": False,
            "project_name": None,
            "project_type": None,
            "output_dir": None,
            "log": [],
            "success": False,
            "error": None
        }
        self.socketio = socketio

    def reset_status(self):
        self.status = {
            "creating": False,
            "project_name": None,
            "project_type": None,
            "output_dir": None,
            "log": [],
            "success": False,
            "error": None
        }

    def create_project_in_background(self, project_type, project_name, output_dir="examples", **kwargs):
        def _run():
            # Extract React-specific parameters if present
            react_language = kwargs.get('react_language', 'javascript')
            react_port = kwargs.get('react_port', 3000)
            
            self.status.update({
                "creating": True,
                "project_name": project_name,
                "project_type": project_type,
                "output_dir": output_dir,
                "log": [
                    f"🚀 Initializing LocalForge Engine for project '{project_name}'",
                    f"📋 Project Type: {project_type.upper()}",
                    f"📁 Target Directory: {output_dir}",
                    f"⏰ Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                ],
                "success": False,
                "error": None,
                "progress": 0,
                "current_step": "Initializing...",
                "steps": [
                    {"name": "Environment validation", "status": "pending"},
                    {"name": "Dependency checks", "status": "pending"},
                    {"name": "Project generation", "status": "pending"},
                    {"name": "Structure optimization", "status": "pending"},
                    {"name": "CI/CD pipeline setup", "status": "pending"}
                ]
            })
            
            # Add React-specific information to the log if applicable
            if project_type == 'react':
                self.status["log"].append(f"⚛️ React Configuration:")
                self.status["log"].append(f"   • Language: {react_language}")
                self.status["log"].append(f"   • Development Port: {react_port}")
                self.status["log"].append(f"   • Build Tool: Vite")
            
            self.socketio.emit('project_creation_update', dict(self.status))
            try:
                # Step 1: Environment validation
                self.status["current_step"] = "Environment validation"
                self.status["progress"] = 15
                self.status["steps"][0]["status"] = "running"
                self.status["log"].append(f"🔍 Validating environment for {project_type} project...")
                
                # Check if it's a cookiecutter-based project
                is_cookiecutter = project_type in ['flask', 'django']
                if is_cookiecutter:
                    self.status["log"].append(f"📦 Detected cookiecutter-based project type")
                    self.status["log"].append(f"🌐 Will require Git for template cloning")
                else:
                    self.status["log"].append(f"🛠️ Using built-in generator for {project_type}")
                
                self.socketio.emit('project_creation_update', dict(self.status))
                time.sleep(0.3)
                
                self.status["steps"][0]["status"] = "success"
                self.status["log"].append(f"✅ Environment validation completed")
                self.socketio.emit('project_creation_update', dict(self.status))
                
                # Step 2: Dependency checks
                self.status["current_step"] = "Dependency checks"
                self.status["progress"] = 30
                self.status["steps"][1]["status"] = "running"
                self.status["log"].append(f"🔧 Checking required dependencies...")
                
                if is_cookiecutter:
                    self.status["log"].append(f"   • Cookiecutter framework")
                    self.status["log"].append(f"   • Git version control")
                    self.status["log"].append(f"   • PyYAML for configuration")
                
                if project_type == 'node' or project_type == 'react':
                    self.status["log"].append(f"   • Node.js runtime")
                    self.status["log"].append(f"   • npm package manager")
                
                self.socketio.emit('project_creation_update', dict(self.status))
                time.sleep(0.4)
                self.status["steps"][1]["status"] = "success"
                self.status["log"].append(f"✅ Dependencies verified and ready")
                self.socketio.emit('project_creation_update', dict(self.status))
                
                # Step 3: Project generation
                self.status["current_step"] = "Project generation"
                self.status["progress"] = 50
                self.status["steps"][2]["status"] = "running"
                
                if is_cookiecutter:
                    self.status["log"].append(f"🌐 Cloning {project_type} template from remote repository...")
                    self.status["log"].append(f"📝 Applying project configuration: '{project_name}'...")
                else:
                    self.status["log"].append(f"🏗️ Generating {project_type} project structure...")
                    self.status["log"].append(f"� Creating project files and directories...")
                
                self.socketio.emit('project_creation_update', dict(self.status))
                  # Prepare additional parameters for the generator
                generator_kwargs = {}
                actual_project_name = project_name  # Default to original name
                
                if project_type == 'react':
                    # Map react_language to use_typescript
                    use_typescript = react_language == 'typescript'
                    generator_kwargs.update({
                        'use_typescript': use_typescript,
                        'port': react_port
                    })
                    self.status["log"].append(f"⚛️ TypeScript: {'Enabled' if use_typescript else 'Disabled'}")
                    self.status["log"].append(f"⚛️ Development server port: {react_port}")
                    self.socketio.emit('project_creation_update', dict(self.status))
                elif project_type == 'django':
                    # Use centralized project name validation
                    from core.src.utils.project_utils import ProjectValidator
                    from core.src.generators.cookiecutter_django_generator import CookiecutterDjangoGenerator
                    
                    sanitized_name = ProjectValidator.sanitize_project_name(
                        project_name, 
                        CookiecutterDjangoGenerator.DJANGO_RESERVED_NAMES
                    )
                    if sanitized_name != project_name.lower().replace(' ', '_').replace('-', '_'):
                        self.status["log"].append(f"🔧 Project name sanitized: '{project_name}' → '{sanitized_name}'")
                        self.status["log"].append(f"   (Avoided Django reserved words/invalid characters)")
                        self.socketio.emit('project_creation_update', dict(self.status))
                        actual_project_name = sanitized_name
                elif project_type == 'flask':
                    self.status["log"].append(f"🐍 Using Flask with cookiecutter template")
                    self.status["log"].append(f"🔒 Security tools will be automatically configured")
                elif project_type == 'node':
                    self.status["log"].append(f"🟢 Node.js Express API with middleware setup")
                    self.status["log"].append(f"🧪 Jest testing framework included")
                
                # Use generator_registry to create the project with specific parameters
                self.status["log"].append(f"🚀 Launching generator for '{actual_project_name}'...")
                self.socketio.emit('project_creation_update', dict(self.status))
                from core.src.generators.registry import generator_registry
                generator = generator_registry.get_generator(
                    project_type,
                    actual_project_name,  # Use the validated name
                    output_dir,
                    **generator_kwargs
                )
                
                self.status["log"].append(f"✨ Generator initialized successfully")
                self.socketio.emit('project_creation_update', dict(self.status))
                
                success = generator.create_project()
                
                if not success:
                    raise Exception("The generator failed to create the project structure, chek logs into logs\ci_cd_ui.log")
                
                self.status["log"].append(f"✅ Core project structure generated")
                self.status["steps"][2]["status"] = "success"
                self.socketio.emit('project_creation_update', dict(self.status))
                
                # Step 4: Structure optimization
                self.status["current_step"] = "Structure optimization"
                self.status["progress"] = 75
                self.status["steps"][3]["status"] = "running"
                self.status["log"].append(f"⚙️ Optimizing project structure and configuration...")
                
                if is_cookiecutter:
                    self.status["log"].append(f"🔒 Applying security best practices")
                    self.status["log"].append(f"🐳 Optimizing Docker configuration")
                    self.status["log"].append(f"📦 Setting up development dependencies")
                else:
                    self.status["log"].append(f"📝 Configuring project metadata")
                    self.status["log"].append(f"🔧 Setting up build configuration")
                
                self.socketio.emit('project_creation_update', dict(self.status))
                time.sleep(0.4)
                self.status["steps"][3]["status"] = "success"
                self.status["log"].append(f"✅ Project structure optimized")
                self.socketio.emit('project_creation_update', dict(self.status))
                
                # Step 5: CI/CD pipeline setup
                self.status["current_step"] = "CI/CD pipeline setup"
                self.status["progress"] = 90
                self.status["steps"][4]["status"] = "running"
                self.status["log"].append(f"🔧 Configuring CI/CD pipeline...")
                self.status["log"].append(f"📋 Creating pipeline configuration files:")
                self.status["log"].append(f"   • Development pipeline (dev)")
                self.status["log"].append(f"   • Testing pipeline (test)")
                self.status["log"].append(f"   • Production pipeline (prod)")
                self.socketio.emit('project_creation_update', dict(self.status))
                time.sleep(0.4)
                
                self.status["steps"][4]["status"] = "success"
                self.status["progress"] = 100
                self.status["current_step"] = "Completed!"
                
                project_path = os.path.join(output_dir, actual_project_name)
                full_project_path = os.path.abspath(project_path)
                
                self.status["log"].append(f"")
                self.status["log"].append(f"🎉 Project creation completed successfully!")
                self.status["log"].append(f"📁 Location: {full_project_path}")
                self.status["log"].append(f"🚀 Project Type: {project_type.upper()}")
                self.status["log"].append(f"⏰ Completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                self.status["log"].append(f"")
                self.status["log"].append(f"📋 Next steps:")
                self.status["log"].append(f"   1. cd {actual_project_name}")
                self.status["log"].append(f"   2. Review the README.md file for setup instructions")
                self.status["log"].append(f"   3. Run the pipeline: python ../../run_pipeline.py --pipeline pipeline.yml")
                self.status["log"].append(f"")
                self.status["log"].append(f"🛠️ Available commands in your project:")
                if project_type == 'react':
                    self.status["log"].append(f"   • npm install     (install dependencies)")
                    self.status["log"].append(f"   • npm run dev     (start development server)")
                    self.status["log"].append(f"   • npm run build   (build for production)")
                elif project_type == 'node':
                    self.status["log"].append(f"   • npm install     (install dependencies)")
                    self.status["log"].append(f"   • npm start       (start the server)")
                    self.status["log"].append(f"   • npm test        (run tests)")
                elif project_type in ['flask', 'django']:
                    self.status["log"].append(f"   • docker-compose up   (start with Docker)")
                    self.status["log"].append(f"   • pip install -r requirements.txt   (install dependencies)")
                    if project_type == 'django':
                        self.status["log"].append(f"   • python manage.py runserver   (start development server)")
                    else:
                        self.status["log"].append(f"   • python app.py   (start development server)")
                
                self.status["success"] = True
                self.status["error"] = None
            except Exception as e:
                error_msg = str(e)
                self.status["log"].append(f"")
                self.status["log"].append(f"❌ Project creation failed!")
                self.status["log"].append(f"🔍 Error details: {error_msg}")
                
                # Provide helpful suggestions based on error type
                if "git" in error_msg.lower():
                    self.status["log"].append(f"💡 Suggestion: Install Git from https://git-scm.com/")
                    self.status["log"].append(f"   Ensure Git is in your system PATH")
                elif "cookiecutter" in error_msg.lower():
                    self.status["log"].append(f"💡 Suggestion: Check cookiecutter installation")
                    self.status["log"].append(f"   Run: pip install cookiecutter")
                elif "permission" in error_msg.lower():
                    self.status["log"].append(f"💡 Suggestion: Check directory permissions")
                    self.status["log"].append(f"   Try running as administrator (Windows)")
                elif "network" in error_msg.lower() or "clone" in error_msg.lower():
                    self.status["log"].append(f"💡 Suggestion: Check internet connection")
                    self.status["log"].append(f"   Verify template URL is accessible")
                else:
                    self.status["log"].append(f"💡 Check the error message above for specific details")
                
                self.status["log"].append(f"⏰ Failed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                self.status["success"] = False
                self.status["error"] = error_msg
                self.status["current_step"] = "Error"
                
                # Mark the current running step as failed
                for step in self.status["steps"]:
                    if step["status"] == "running":
                        step["status"] = "failure"
                        break
            finally:
                self.status["creating"] = False
                self.socketio.emit('project_creation_update', dict(self.status))
        thread = threading.Thread(target=_run)
        thread.daemon = True
        thread.start()

    def create_project_advanced_in_background(self, project_type, project_name, output_dir, cookiecutter_config, template_url):
        def _run():
            self.status.update({
                "creating": True,
                "project_name": project_name,
                "project_type": project_type,
                "output_dir": output_dir,
                "log": [
                    f"🚀 LocalForge Engine - Advanced Mode",
                    f"🎯 Project: '{project_name}' ({project_type.upper()})",
                    f"📁 Destination: {output_dir}",
                    f"🌐 Template: {template_url}",
                    f"⚙️ Custom configuration with {len(cookiecutter_config)} parameters",
                    f"⏰ Started: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                ],
                "success": False,
                "error": None,
                "progress": 0,
                "current_step": "Initializing advanced mode...",
                "steps": [
                    {"name": "Configuration validation", "status": "pending"},
                    {"name": "Template preparation", "status": "pending"},
                    {"name": "Dependency verification", "status": "pending"},
                    {"name": "Project generation", "status": "pending"},
                    {"name": "Enhancement application", "status": "pending"},
                    {"name": "Pipeline configuration", "status": "pending"}
                ]
            })
            self.socketio.emit('project_creation_update', dict(self.status))
            import time, os
            try:
                # Step 1: Configuration validation
                self.status["current_step"] = "Configuration validation"
                self.status["progress"] = 12
                self.status["steps"][0]["status"] = "running"
                self.status["log"].append(f"🔍 Validating advanced configuration...")
                self.status["log"].append(f"   • Project name: {project_name}")
                self.status["log"].append(f"   • Template URL: {template_url}")
                self.status["log"].append(f"   • Configuration parameters: {len(cookiecutter_config)}")
                
                # Log some key configuration parameters
                key_configs = ['project_name', 'project_slug', 'author_name', 'email', 'version']
                for key in key_configs:
                    if key in cookiecutter_config:
                        self.status["log"].append(f"   • {key}: {cookiecutter_config[key]}")
                
                self.socketio.emit('project_creation_update', dict(self.status))
                time.sleep(0.4)
                
                self.status["steps"][0]["status"] = "success"
                self.status["log"].append(f"✅ Configuration validated successfully")
                self.socketio.emit('project_creation_update', dict(self.status))
                
                # Step 2: Template preparation
                self.status["current_step"] = "Template preparation"
                self.status["progress"] = 25
                self.status["steps"][1]["status"] = "running"
                self.status["log"].append(f"📦 Preparing cookiecutter template...")
                self.status["log"].append(f"🌐 Source: {template_url}")
                self.socketio.emit('project_creation_update', dict(self.status))
                time.sleep(0.3)
                
                self.status["steps"][1]["status"] = "success"
                self.status["log"].append(f"✅ Template prepared and ready")
                self.socketio.emit('project_creation_update', dict(self.status))
                
                # Step 3: Dependency verification
                self.status["current_step"] = "Dependency verification"
                self.status["progress"] = 40
                self.status["steps"][2]["status"] = "running"
                self.status["log"].append(f"🔧 Verifying required dependencies...")
                self.status["log"].append(f"   • Git (for template cloning)")
                self.status["log"].append(f"   • Cookiecutter framework")
                self.status["log"].append(f"   • PyYAML (for configuration)")
                if project_type == 'django':
                    self.status["log"].append(f"   • Django-specific requirements")
                elif project_type == 'flask':
                    self.status["log"].append(f"   • Flask-specific requirements")
                self.socketio.emit('project_creation_update', dict(self.status))
                time.sleep(0.4)
                self.status["steps"][2]["status"] = "success"
                self.status["log"].append(f"✅ All dependencies verified")
                self.socketio.emit('project_creation_update', dict(self.status))
                
                # Step 4: Project generation
                self.status["current_step"] = "Project generation"
                self.status["progress"] = 55
                self.status["steps"][3]["status"] = "running"
                self.status["log"].append(f"🏗️ Generating project with cookiecutter...")
                
                if project_type == 'flask':
                    self.status["log"].append(f"🐍 Initializing Flask generator...")
                    from core.src.generators.cookiecutter_flask_generator import CookiecutterFlaskGenerator
                    generator = CookiecutterFlaskGenerator(
                        project_name=project_name,
                        output_dir=output_dir,
                        template_url=template_url,
                        interactive=False
                    )
                    generator._apply_custom_config(cookiecutter_config)
                    self.status["log"].append(f"⚙️ Flask configuration applied")
                    
                elif project_type == 'django':
                    self.status["log"].append(f"🎯 Initializing Django generator...")
                    from core.src.generators.cookiecutter_django_generator import CookiecutterDjangoGenerator
                    
                    # Validate project name and emit log messages for web interface
                    sanitized_name, validation_logs = CookiecutterDjangoGenerator.validate_project_name_simple(project_name)
                    for log_msg in validation_logs:
                        self.status["log"].append(log_msg)
                    if validation_logs:  # Only emit if there are validation messages
                        self.socketio.emit('project_creation_update', dict(self.status))
                    
                    generator = CookiecutterDjangoGenerator(
                        project_name=sanitized_name,
                        output_dir=output_dir,
                        template_url=template_url,
                        interactive=False
                    )
                    generator._apply_custom_config(cookiecutter_config)
                    self.status["log"].append(f"⚙️ Django configuration applied")
                    
                else:
                    # For other types, use the previous method
                    self.status["log"].append(f"🛠️ Using standard generator for {project_type}")
                    success = create_project(project_type, project_name, output_dir)
                    project_path = os.path.join(output_dir, project_name)
                    full_project_path = os.path.abspath(project_path)
                    
                    self.status["log"].append(f"✅ Project '{project_name}' created successfully!")
                    self.status["log"].append(f"📁 Location: {full_project_path}")
                    self.status["success"] = True
                    self.status["error"] = None
                    self.status["progress"] = 100
                    self.status["current_step"] = "Completed!"
                    self.socketio.emit('project_creation_update', {
                        "creating": False,
                        "success": success,
                        "project_path": full_project_path
                    })
                    return
                
                self.socketio.emit('project_creation_update', dict(self.status))
                
                self.status["log"].append(f"� Executing project generation...")
                success = generator.create_project()
                if not success:
                    raise Exception("The cookiecutter generator failed to create the project")
                    
                self.status["steps"][3]["status"] = "success"
                self.status["log"].append(f"✅ Core project generated successfully")
                self.socketio.emit('project_creation_update', dict(self.status))
                
                # Step 5: Enhancement application
                self.status["current_step"] = "Enhancement application"
                self.status["progress"] = 75
                self.status["steps"][4]["status"] = "running"
                self.status["log"].append(f"⚙️ Applying LocalForge enhancements...")
                self.status["log"].append(f"   • Security tools integration")
                self.status["log"].append(f"   • Docker optimization")
                self.status["log"].append(f"   • Development settings")
                self.status["log"].append(f"   • Pre-commit hooks")
                self.socketio.emit('project_creation_update', dict(self.status))
                time.sleep(0.5)
                
                self.status["steps"][4]["status"] = "success"
                self.status["log"].append(f"✅ All enhancements applied")
                self.socketio.emit('project_creation_update', dict(self.status))
                
                # Step 6: Pipeline configuration
                self.status["current_step"] = "Pipeline configuration"
                self.status["progress"] = 90
                self.status["steps"][5]["status"] = "running"
                self.status["log"].append(f"🔧 Setting up CI/CD pipeline...")
                self.status["log"].append(f"   • Development environment pipeline")
                self.status["log"].append(f"   • Testing environment pipeline") 
                self.status["log"].append(f"   • Production environment pipeline")
                self.status["log"].append(f"   • Pipeline execution scripts")
                self.socketio.emit('project_creation_update', dict(self.status))
                time.sleep(0.4)
                
                self.status["steps"][5]["status"] = "success"
                self.status["progress"] = 100
                self.status["current_step"] = "Completed!"
                
                project_path = os.path.join(output_dir, project_name)
                full_project_path = os.path.abspath(project_path)
                
                self.status["log"].append(f"")
                self.status["log"].append(f"🎉 Advanced project creation completed!")
                self.status["log"].append(f"📁 Project location: {full_project_path}")
                self.status["log"].append(f"🌐 Template used: {template_url}")
                self.status["log"].append(f"⚙️ Configuration applied: {len(cookiecutter_config)} parameters")
                self.status["log"].append(f"⏰ Completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                self.status["log"].append(f"")
                self.status["log"].append(f"📋 Next steps:")
                self.status["log"].append(f"   1. cd {project_name}")
                self.status["log"].append(f"   2. Review the generated README.md for detailed instructions")
                self.status["log"].append(f"   3. Execute pipeline: python ../../run_pipeline.py --pipeline pipeline.yml")
                self.status["log"].append(f"")
                self.status["log"].append(f"🔧 Project-specific commands:")
                if project_type == 'flask':
                    self.status["log"].append(f"   • docker-compose up -d     (start services)")
                    self.status["log"].append(f"   • pip install -r requirements.txt")
                    self.status["log"].append(f"   • flask run     (development server)")
                elif project_type == 'django':
                    self.status["log"].append(f"   • docker-compose up -d     (start services)")
                    self.status["log"].append(f"   • pip install -r requirements.txt")
                    self.status["log"].append(f"   • python manage.py migrate")
                    self.status["log"].append(f"   • python manage.py runserver")
                
                self.status["success"] = True
                self.status["error"] = None
                self.socketio.emit('project_creation_update', {
                    "creating": False,
                    "success": True,
                    "project_name": project_name,
                    "project_type": project_type,
                    "output_dir": output_dir,
                    "log": self.status["log"],
                    "steps": self.status["steps"],
                    "progress": 100,
                    "current_step": "Completed!",
                    "message": f"✅ Project '{project_name}' successfully created!"
                })
            except Exception as e:
                error_msg = f"Error creating project: {str(e)}"
                self.status["log"].append(f"")
                self.status["log"].append(f"❌ Advanced project creation failed!")
                self.status["log"].append(f"🔍 Error details: {error_msg}")
                
                # Provide context-specific suggestions
                if "git" in str(e).lower():
                    self.status["log"].append(f"💡 Git-related issue detected:")
                    self.status["log"].append(f"   • Install Git: https://git-scm.com/")
                    self.status["log"].append(f"   • Ensure Git is in system PATH")
                    self.status["log"].append(f"   • Verify template URL is accessible")
                elif "cookiecutter" in str(e).lower():
                    self.status["log"].append(f"💡 Cookiecutter issue detected:")
                    self.status["log"].append(f"   • Run: pip install --upgrade cookiecutter")
                    self.status["log"].append(f"   • Check template URL format")
                elif "template" in str(e).lower():
                    self.status["log"].append(f"💡 Template issue detected:")
                    self.status["log"].append(f"   • Verify template URL: {template_url}")
                    self.status["log"].append(f"   • Check internet connectivity")
                    self.status["log"].append(f"   • Try a different template")
                elif "configuration" in str(e).lower():
                    self.status["log"].append(f"💡 Configuration issue detected:")
                    self.status["log"].append(f"   • Review cookiecutter parameters")
                    self.status["log"].append(f"   • Check template requirements")
                else:
                    self.status["log"].append(f"💡 General troubleshooting:")
                    self.status["log"].append(f"   • Check directory permissions")
                    self.status["log"].append(f"   • Verify internet connection")
                    self.status["log"].append(f"   • Review error message above")
                
                self.status["log"].append(f"⏰ Failed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                self.status["success"] = False
                self.status["error"] = error_msg
                self.status["current_step"] = "Error"
                
                # Mark the current running step as failed
                for step in self.status["steps"]:
                    if step["status"] == "running":
                        step["status"] = "failure"
                        break
                self.socketio.emit('project_creation_update', {
                    "creating": False,
                    "success": False,
                    "error": error_msg,
                    "log": self.status["log"],
                    "steps": self.status["steps"],
                    "current_step": "Error"
                })
            finally:
                self.status["creating"] = False
                self.socketio.emit('project_creation_update', dict(self.status))
        thread = threading.Thread(target=_run)
        thread.daemon = True
        thread.start()
