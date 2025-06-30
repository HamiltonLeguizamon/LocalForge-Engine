import os
import sys
import glob
import json
import time
import logging
import yaml
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from core.src.app.utils import discover_pipeline_files, count_existing_projects
from core.src.app.form_configs import get_flask_cookiecutter_config, get_django_cookiecutter_config

# Make sure the project root is in the path to import modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

try:
    from core.src.main import PipelineRunner
    from core.src.utils.log_manager import setup_logging
    from core.src.project_generator import create_project
    from core.src.generators.registry import generator_registry
except ImportError as e:
    print(f"Error: Could not import required modules: {e}")
    print(f"Python path: {sys.path}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"Project root: {project_root}")
    sys.exit(1)

from core.src.app.pipeline_manager import PipelineManager
from core.src.app.project_manager import ProjectManager, get_available_project_types

app = Flask(
    __name__,
    template_folder='../web/templates',
    static_folder='../web/static'
)

app.config['SECRET_KEY'] = 'your_secret_key_here_improved_2025!'
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")

# Instantiate managers
pipeline_manager = PipelineManager(socketio)
project_manager = ProjectManager(socketio)

@app.route('/')
def index():
    """Serves the landing page."""
    return render_template('landing.html')

@app.route('/pipelines')
def pipelines():
    """Serves the pipelines view."""
    pipeline_data = discover_pipeline_files()
    available_pipelines = pipeline_data['flat_list']  # For backward compatibility
    grouped_pipelines = pipeline_data['grouped_by_project']
    stats = pipeline_manager.get_stats()
    
    return render_template('pipelines.html', 
                         status=pipeline_manager.status, 
                         pipelines=available_pipelines,
                         grouped_pipelines=grouped_pipelines,
                         stats=stats,
                         history=pipeline_manager.history[-5:])  # Last 5 runs

@app.route('/projects')
def projects():
    """Serves the projects management view."""
    available_types = get_available_project_types()
    
    # Make sure project creation state is clean when the page loads
    if not project_manager.status["creating"]:
        project_manager.reset_status()
    
    return render_template('projects.html', 
                         project_types=available_types,
                         creation_status=project_manager.status)

@app.route('/api/pipelines')
def get_pipelines():
    """API endpoint to get the list of available pipelines."""
    return jsonify(discover_pipeline_files())

@app.route('/api/pipelines/flat')
def get_pipelines_flat():
    """API endpoint to get the flat list of pipelines (legacy format)."""
    pipeline_data = discover_pipeline_files()
    return jsonify(pipeline_data['flat_list'])

@app.route('/api/pipelines/grouped')
def get_pipelines_grouped():
    """API endpoint to get pipelines grouped by project."""
    pipeline_data = discover_pipeline_files()
    return jsonify(pipeline_data['grouped_by_project'])

@app.route('/api/stats')
def get_stats():
    """API endpoint to get statistics."""
    return jsonify(pipeline_manager.get_stats())

@app.route('/api/history')
def get_history():
    """API endpoint to get execution history."""
    return jsonify(pipeline_manager.history)

@app.route('/api/status')
def get_status():
    """API endpoint to get the current pipeline status."""
    return jsonify(pipeline_manager.status)

@app.route('/api/project-types')
def get_project_types():
    """API endpoint to get available project types."""
    try:
        project_types = get_available_project_types()
        return jsonify({"types": project_types})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/create-project', methods=['POST'])
def api_create_project():
    """API endpoint to create a new project."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        project_type = data.get('type')
        project_name = data.get('name')
        output_dir = data.get('output_dir', 'examples')
        
        if not project_type or not project_name:
            return jsonify({"error": "'type' and 'name' are required"}), 400
        
        # Validate that there's no creation in progress
        if project_manager.status["creating"]:
            return jsonify({"error": "There's already a project creation in progress"}), 409
          # Validate project type
        available_types = get_available_project_types()
        valid_types = [t['name'] for t in available_types]
        if project_type not in valid_types:
            return jsonify({
                "error": f"Project type '{project_type}' not available",
                "available_types": available_types
            }), 400
        
        project_manager.create_project_in_background(project_type, project_name, output_dir)
        
        return jsonify({
            "message": "Project creation started",
            "project_name": project_name,
            "project_type": project_type,
            "output_dir": output_dir
        })
        
    except Exception as e:
        logging.exception("Error in api_create_project")
        return jsonify({"error": str(e)}), 500

@app.route('/api/project-creation-status')
def get_project_creation_status():
    """API endpoint to get the project creation status."""
    # If there is no active creation, reset the status to avoid
    # showing success/error messages from previous creations
    if not project_manager.status["creating"]:
        project_manager.reset_status()
    return jsonify(project_manager.status)

@app.route('/api/projects/count')
def get_projects_count():
    """API endpoint to get the number of existing projects."""
    try:
        count = count_existing_projects()
        return jsonify({
            "count": count,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        })
    except Exception as e:
        logging.exception("Error in get_projects_count")
        return jsonify({
            "error": str(e),
            "count": 0,
            "status": "error"
        }), 500

@socketio.on('connect')
def handle_connect():
    """Handles the connection of a new client."""
    print('🔌 Client connected')
    # Send the current status and statistics to the newly connected client
    emit('pipeline_update', pipeline_manager.status)
    emit('stats_update', pipeline_manager.get_stats())
    
    # If there is no active project creation, reset the status to avoid
    # showing success/error messages from previous creations
    if not project_manager.status["creating"]:
        project_manager.reset_status()
    
    # Send the updated status (or the current status if there is an ongoing creation)
    emit('project_creation_update', project_manager.status)
    
    # Send available project types
    try:
        project_types = get_available_project_types()
        emit('project_types', {"types": project_types})
    except Exception as e:
        emit('project_types', {"error": str(e)})

@socketio.on('disconnect')
def handle_disconnect():
    """Handles the disconnection of a client."""
    print('🔌 Client disconnected')

@socketio.on('start_pipeline')
def handle_start_pipeline(data):
    """Starts the pipeline execution in the background."""
    pipeline_file = data.get('pipeline_file')
    if not pipeline_file:
        emit('pipeline_update', {"error": "You must select a pipeline to run."})
        return
    if not pipeline_manager.status["running"]:
        print("🚀 Request to start pipeline received.")
        pipeline_manager.run_pipeline_in_background(pipeline_file)
    else:
        print("⚠️ Pipeline is already running.")
        emit('pipeline_update', {"error": "Pipeline is already running."})

@socketio.on('clear_logs')
def handle_clear_logs(data):
    """Clears the logs of the current pipeline."""
    pipeline_manager.clear_logs()

@socketio.on('clear_steps')
def handle_clear_steps(data):
    """Clears the steps of the current pipeline."""
    pipeline_manager.clear_steps()

@socketio.on('stop_pipeline')
def handle_stop_pipeline(data):
    """Stops the currently running pipeline."""
    print("⏹️ Request to stop pipeline received.")
    if pipeline_manager.status["running"]:
        success = pipeline_manager.stop_pipeline()
        if success:
            print("✅ Pipeline stopped successfully.")
            emit('pipeline_update', {"message": "Pipeline stopped by the user", "stopped": True})
        else:
            print("❌ Error stopping the pipeline.")
            emit('pipeline_update', {"error": "Error stopping the pipeline"})
    else:
        print("⚠️ No pipeline is running.")
        emit('pipeline_update', {"error": "No pipeline is running to stop."})

@socketio.on('create_project')
def handle_create_project(data):
    """Handles the request to create a new project via SocketIO."""
    print(f"🔨 Creation request received: {data}")
    if project_manager.status["creating"]:
        print("⚠️ A creation is already in progress")
        emit('project_creation_update', {"error": "A project creation is already in progress."})
        return
    
    project_type = data.get('project_type')
    project_name = data.get('project_name')
    output_dir = data.get('output_dir', 'examples')
    
    # Extract React-specific parameters
    react_language = data.get('react_language', 'javascript')
    react_port = data.get('react_port', 3000)
    
    print(f"📝 Parameters: type={project_type}, name={project_name}, dir={output_dir}")
    if project_type == 'react':
        print(f"⚛️ React Parameters: language={react_language}, port={react_port}")
    
    if not project_type or not project_name:
        print("❌ Missing required parameters")
        emit('project_creation_update', {"error": "Both 'project_type' and 'project_name' are required"})
        return
    
    # Validate the project type
    available_types_info = get_available_project_types() # This function returns a list of dictionaries
    available_types = [pt_info['name'] for pt_info in available_types_info] # Extract just the names
    if project_type not in available_types:
        print(f"❌ Invalid project type: {project_type}")
        emit('project_creation_update', {
            "error": f"Project type '{project_type}' not available. Available types: {[t['display_name'] for t in available_types_info]}"
        })
        return
    
    print(f"🚀 Starting project creation in separate thread...")
    
    # Pass specific parameters if it's a React project
    if project_type == 'react':
        project_manager.create_project_in_background(
            project_type, project_name, output_dir, 
            react_language=react_language, react_port=react_port
        )
    else:
        project_manager.create_project_in_background(project_type, project_name, output_dir)
    
    print(f"🧵 Creation thread started")

@socketio.on('get_project_types')
def handle_get_project_types():
    """Sends the available project types."""
    try:
        project_types_info = get_available_project_types()
        print(f"📋 Sending project types: {[pt['name'] for pt in project_types_info]}")
        emit('project_types_update', {"types": project_types_info})
    except Exception as e:
        print(f"❌ Error sending project types: {e}")
        emit('project_types_update', {"error": str(e)})

@socketio.on('get_cookiecutter_config')
def handle_get_cookiecutter_config(data):
    """Gets the cookiecutter configuration for a project type."""
    try:
        project_type = data.get('project_type')
        template_url = data.get('template_url')
        
        if project_type == 'flask':
            # Specific configuration for Flask
            config_fields = get_flask_cookiecutter_config(template_url)
            emit('cookiecutter_config_response', {
                "success": True,
                "project_type": project_type,
                "fields": config_fields
            })
        elif project_type == 'django':
            # Specific configuration for Django
            config_fields = get_django_cookiecutter_config(template_url)
            emit('cookiecutter_config_response', {
                "success": True,
                "project_type": project_type,
                "fields": config_fields
            })
        else:
            emit('cookiecutter_config_response', {
                "success": False,
                "error": f"Cookiecutter configuration not available for {project_type}"
            })
    except Exception as e:
        print(f"❌ Error getting cookiecutter configuration: {e}")
        emit('cookiecutter_config_response', {
            "success": False,
            "error": str(e)
        })

@socketio.on('create_project_advanced')
def handle_create_project_advanced(data):
    """Creates a project with advanced cookiecutter configuration."""
    project_type = data.get('project_type')
    project_name = data.get('project_name') 
    output_dir = data.get('output_dir', './examples')
    cookiecutter_config = data.get('custom_config', {})
    template_url = data.get('template_url')
    
    # Basic validations
    if not project_type or not project_name:
        emit('project_creation_update', {
            "error": "Project type and name are required"
        })
        return
        
    if project_manager.status["creating"]:
        emit('project_creation_update', {
            "error": "A project is already being created"
        })
        return
    
    # Validate the project type
    available_types_info = get_available_project_types()
    available_types = [pt_info['name'] for pt_info in available_types_info]
    if project_type not in available_types:
        emit('project_creation_update', {
            "error": f"Project type '{project_type}' not available"
        })
        return
    
    print(f"🚀 Starting advanced project creation in separate thread...")
    project_manager.create_project_advanced_in_background(project_type, project_name, output_dir, cookiecutter_config, template_url)

def main():
    """Main function to run the web UI."""
    from core.src.utils.log_manager import setup_logging
    import logging
    
    # Configure logging
    setup_logging(log_file="ci_cd_ui.log", level=logging.INFO)
    
    # Get port from environment variable or use default
    port = int(os.environ.get('FLASK_PORT', 5001))
    
    print("🚀 Starting CI/CD web interface...")
    print(f"📱 The interface will be available at: http://localhost:{port}")
    print("⏹️  To stop the server press Ctrl+C")
    
    # Start the Flask app
    socketio.run(app, debug=True, port=port, host='0.0.0.0')


if __name__ == '__main__':
    main()
