"""
Centralized module for command line interface (CLI) management.
Avoids code duplication for argument parsing between scripts.
"""
import argparse
import logging
import sys
from typing import Dict, Any


class CLIManager:
    """Centralized manager for command line arguments."""
    
    @staticmethod
    def create_pipeline_parser() -> argparse.ArgumentParser:
        """Creates the argument parser for pipelines."""
        parser = argparse.ArgumentParser(description='Executes a CI/CD pipeline')
        parser.add_argument('--pipeline', '-p', default="pipeline.yml", 
                          help='Pipeline file to execute')
        parser.add_argument('--env', '-e', action='append', 
                          help='Environment variables in KEY=VALUE format')
        parser.add_argument('--parallel', action='store_true', 
                          help='Run parallel steps if defined')
        parser.add_argument('--continue', dest='continue_on_error', action='store_true', 
                          help='Continue execution even if there are errors')
        parser.add_argument('--log-level', default='INFO', 
                          choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                          help='Logging level')
        return parser
    
    @staticmethod
    def parse_env_vars(env_args: list) -> Dict[str, str]:
        """Parses environment variables from command line arguments."""
        env_vars = {}
        if env_args:
            for env_var in env_args:
                try:
                    key, value = env_var.split('=', 1)
                    env_vars[key] = value
                except ValueError:
                    logging.error(f"Invalid environment variable: {env_var}. Use KEY=VALUE format.")
                    sys.exit(1)
        return env_vars
    
    @staticmethod
    def get_log_level(level_str: str) -> int:
        """Converts log level string to logging constant."""
        return getattr(logging, level_str.upper())
