# Contributing to LocalForge Engine

Thank you for your interest in contributing to LocalForge Engine! We welcome contributions from the community.

## How to Contribute

### Reporting Issues

- Use GitHub Issues to report bugs or request features
- Include detailed information about your environment
- Provide steps to reproduce the issue
- Include relevant logs from the `logs/` directory

### Development Setup

1. Fork the repository
2. Clone your fork locally
3. Run the installation script: `bash install.sh`
4. Make your changes
5. Test your changes thoroughly
6. Submit a pull request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Include appropriate error handling

### Testing

Before submitting a pull request:

- Test the CLI commands
- Test the web interface
- Test project generation for all supported types
- Ensure all existing functionality still works

### Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update version numbers if needed
3. Ensure your code passes all tests
4. Your pull request will be reviewed by maintainers

## Development Guidelines

### Adding New Project Generators

1. Create a new generator class in `core/src/generators/`
2. Register it in `core/src/generators/registry.py`
3. Add appropriate templates if needed
4. Update documentation

### Extending the Web Interface

- Follow the existing CSS structure
- Use responsive design principles
- Test on different browsers
- Maintain real-time functionality with SocketIO

## Questions?

Feel free to open an issue for questions about contributing!
