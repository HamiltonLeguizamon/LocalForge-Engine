#!/usr/bin/env python3
"""
Shortcut script to run the web UI from the project root.
Improved version that doesn't manipulate sys.path.
"""
import subprocess
import sys
import os
from pathlib import Path


def main():
    """Main function that runs the web UI using the installed package."""
    try:
        # Try to use the installed package first
        result = subprocess.run([
            sys.executable, "-m", "core.src.web.web_ui"
        ], cwd=Path(__file__).parent)
        sys.exit(result.returncode)
    except Exception:
        # Fallback: use direct import for development
        import sys
        import os
        
        # Only add to path if we're in development
        if not __package__:
            core_src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core', 'src')
            sys.path.insert(0, core_src_path)

        try:
            # Import and run web_ui
            from core.src.web.web_ui import app
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
            app.run(host='0.0.0.0', port=port, debug=True)
            
        except Exception as e:
            print(f"Error running the web UI: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()
