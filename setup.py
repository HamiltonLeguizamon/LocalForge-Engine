"""
Setup script for LocalForge CI/CD Engine.
Allows installation as a Python package.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="localforge-cicd",
    version="1.0.0",
    author="LocalForge Engine",
    description="Modern CI/CD engine with web interface and project generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_dir={"": "."},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-html>=4.1.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "localforge-pipeline=core.src.main:main",
            "localforge-ui=core.src.web.web_ui:main",
            "localforge-generate=core.src.project_generator:main",
        ],
    },
    include_package_data=True,
    package_data={
        "core.src.web": ["templates/*", "static/**/*"],
        "core.src.generators": ["templates/**/*"],
    },
)
