"""
Registry of project generators.
Manages the registration and access to different types of generators.
"""
from typing import Dict, Type
from core.src.generators.base_generator import BaseProjectGenerator
from core.src.generators.cookiecutter_flask_generator import CookiecutterFlaskGenerator
from core.src.generators.cookiecutter_django_generator import CookiecutterDjangoGenerator
from core.src.generators.node_generator import NodeProjectGenerator
from core.src.generators.react_generator import ReactProjectGenerator


class GeneratorRegistry:
    """Registry to manage the different types of available generators."""
    
    def __init__(self):
        self._generators: Dict[str, Type[BaseProjectGenerator]] = {}
        self._register_default_generators()
    
    def _register_default_generators(self):
        """Registers the default generators."""
        self.register("flask", CookiecutterFlaskGenerator)
        self.register("django", CookiecutterDjangoGenerator)  # Use cookiecutter as default
        self.register("node", NodeProjectGenerator)
        self.register("react", ReactProjectGenerator)
    
    def register(self, project_type: str, generator_class: Type[BaseProjectGenerator]):
        """
        Registers a new generator.
        
        Args:
            project_type: Project type (e.g.: 'flask', 'fastapi')
            generator_class: Generator class
        """
        self._generators[project_type] = generator_class
    
    def get_generator(self, project_type: str, project_name: str, output_dir: str, **kwargs) -> BaseProjectGenerator:
        """
        Gets a generator instance for the specified type.
        
        Args:
            project_type: Project type
            project_name: Project name
            output_dir: Output directory
            **kwargs: Additional generator-specific parameters
            
        Returns:
            BaseProjectGenerator: Generator instance
            
        Raises:
            ValueError: If the project type is not registered
        """
        if project_type not in self._generators:
            raise ValueError(f"Project type '{project_type}' is not registered. "
                           f"Available types: {list(self._generators.keys())}")
        
        generator_class = self._generators[project_type]
        
        # For cookiecutter generators, pass additional parameters
        if (project_type == "flask" and generator_class == CookiecutterFlaskGenerator) or \
           (project_type == "django" and generator_class == CookiecutterDjangoGenerator):
            return generator_class(
                project_name, 
                output_dir, 
                template_url=kwargs.get('template_url'),
                interactive=kwargs.get('interactive', False)
            )
        elif project_type == "react" and generator_class == ReactProjectGenerator:
            return generator_class(
                project_name, 
                output_dir,
                use_typescript=kwargs.get('use_typescript', False),
                port=kwargs.get('port', 3000)
            )
        else:
            return generator_class(project_name, output_dir)
    
    def get_available_types(self) -> list:
        """
        Returns the list of available project types.
        
        Returns:
            list: List of registered project types
        """
        return list(self._generators.keys())


# Global instance of the registry
generator_registry = GeneratorRegistry()
