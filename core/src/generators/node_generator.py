"""
Specific generator for Node.js (Express) projects.
Implements the logic to create Node.js projects with a complete structure.
"""
from core.src.generators.base_generator import BaseProjectGenerator
from core.src.generators.templates.node_templates import (
    DOCKERFILE_TEMPLATE,
    PACKAGE_JSON_TEMPLATE,
    DOCKER_COMPOSE_TEMPLATE,
    PIPELINE_DEV_TEMPLATE,
    PIPELINE_TEST_TEMPLATE,
    PIPELINE_PROD_TEMPLATE,
    APP_TEMPLATE,
    TEST_APP_TEMPLATE,
    README_TEMPLATE,
    GITIGNORE_TEMPLATE
)

class NodeProjectGenerator(BaseProjectGenerator):
    """Specific generator for Node.js (Express) projects."""
    
    # Node.js-specific reserved words (common ones are in ProjectValidator.COMMON_RESERVED_NAMES)
    NODE_RESERVED_NAMES = {
        'express', 'middleware', 'router', 'routes', 'controllers',
        'models', 'views', 'bin', 'www', 'server', 'app.js'
    }

    def __init__(self, project_name: str, output_dir: str):
        """Initialize the Node.js generator."""
        # Use centralized validation with Node.js-specific reserved words
        super().__init__(project_name, output_dir, self.NODE_RESERVED_NAMES)

    def get_project_type(self) -> str:
        """Returns the project type."""
        return "node"

    def get_directory_structure(self) -> list:
        """Defines the directory structure for a Node.js project."""
        return [
            "src",
            "src/tests",
            "logs",
            "reports",
            "test-reports"
        ]

    def get_project_files(self) -> dict:
        """Defines all files to be generated for the Node.js project."""
        return {
            # Docker configuration files
            "Dockerfile": DOCKERFILE_TEMPLATE,
            "docker-compose.yml": DOCKER_COMPOSE_TEMPLATE,

            # Node.js dependencies
            "package.json": PACKAGE_JSON_TEMPLATE,            # CI/CD Pipelines - Multiple modes
            "pipeline-dev.yml": PIPELINE_DEV_TEMPLATE,
            "pipeline-test.yml": PIPELINE_TEST_TEMPLATE,
            "pipeline-prod.yml": PIPELINE_PROD_TEMPLATE,
            
            # Default pipeline for backward compatibility
            "pipeline.yml": PIPELINE_DEV_TEMPLATE,

            # Application source code
            "src/app.js": APP_TEMPLATE,

            # Tests
            "src/tests/test_app.js": TEST_APP_TEMPLATE,
            "src/tests/test_app.spec.js": TEST_APP_TEMPLATE,

            # Documentation
            "README.md": README_TEMPLATE,

            # Version control
            ".gitignore": GITIGNORE_TEMPLATE,

            # Placeholder files for directories
            "logs/.gitkeep": "# Directory for application logs\n",
            "reports/.gitkeep": "# Directory for code analysis reports\n",
            "test-reports/.gitkeep": "# Directory for test reports\n"
        }
