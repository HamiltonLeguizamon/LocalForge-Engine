"""
React pipeline templates for different deployment modes.
Includes development, testing, and production pipeline configurations.
"""

# Development pipeline - local dev with full structure
REACT_PIPELINE_DEV_TEMPLATE = '''# pipeline.yml automatically generated for React (Development)
name: "Local development {project_name}"
description: "Pipeline for local React development using Docker containers"

environment:
  PROJECT_NAME: "{project_name}"
  NODE_ENV: "development"
  PORT: "{port}"

pipeline:
  - step: install_dependencies
    description: "Install npm dependencies"
    commands:
      - docker-compose run --rm node npm install

  - step: code_analysis
    description: "Code analysis (lint and format)"
    commands:
      - docker-compose run --rm node npm run lint
      - docker-compose run --rm node npm run format

  - step: dev_server
    description: "Start Vite development server"
    commands:
      - docker-compose up -d react-dev

  - step: health_check
    description: "Check that the dev server is running"
    commands:
      - python -c "import time; time.sleep(5); print('Waiting for the dev server...')"
      - curl -f http://localhost:{port} || exit 1

notifications:
  on_success:
    - echo "🎉 React development environment ready"
    - echo "🌐 Access your app at http://localhost:{port}"
  on_failure:
    - echo "💥 React development failed"
  on_always:
    - echo "🔔 React dev pipeline finished"
'''

# Testing pipeline - E2E/unit with full structure
REACT_PIPELINE_TEST_TEMPLATE = '''# pipeline.yml automatically generated for React (Testing)
name: "Local testing {project_name}"
description: "Pipeline for local React testing using Docker containers"

environment:
  PROJECT_NAME: "{project_name}"
  NODE_ENV: "test"
  PORT: "{port}"

pipeline:
  - step: install_dependencies
    description: "Install npm dependencies"
    commands:
      - docker-compose run --rm node npm ci

  - step: code_analysis
    description: "Code analysis (lint and format)"
    commands:
      - docker-compose run --rm node npm run lint
      - docker-compose run --rm node npm run format

  - step: run_tests
    description: "Run tests with coverage"
    commands:
      - docker-compose run --rm test-runner

  - step: collect_results
    description: "Collect test reports (if any)"
    commands:
      - echo "Collecting test results..."

cleanup:
  - step: teardown
    description: "Stop and remove containers"
    commands:
      - docker-compose down

notifications:
  on_success:
    - echo "✅ All tests passed!"
  on_failure:
    - echo "❌ Tests failed"
  on_always:
    - echo "🧹 Test environment cleaned up"
'''

# Production pipeline - build and deploy with full structure
REACT_PIPELINE_PROD_TEMPLATE = '''# pipeline.yml automatically generated for React (Production)
name: "Production deployment {project_name}"
description: "Pipeline for production React deployment using Docker containers"

environment:
  PROJECT_NAME: "{project_name}"
  NODE_ENV: "production"
  PORT: "{port}"

pipeline:
  - step: install_dependencies
    description: "Install npm dependencies"
    commands:
      - docker-compose run --rm node npm ci

  - step: code_analysis
    description: "Code analysis (lint and format)"
    commands:
      - docker-compose run --rm node npm run lint
      - docker-compose run --rm node npm run format

  - step: run_tests
    description: "Run tests with coverage"
    commands:
      - docker-compose run --rm test-runner

  - step: security_audit
    description: "Security audit"
    commands:
      - docker-compose run --rm node npm run security

  - step: build_app
    description: "Build application for production"
    commands:
      - docker-compose run --rm node npm run build
      - docker build -t {project_slug}:latest .

  - step: run_app
    description: "Deploy React application in container"
    commands:
      - docker-compose up -d react-app

  - step: health_check
    description: "Check that the application is running"
    commands:
      - python -c "import time; time.sleep(10); print('Waiting for the service to be available...')"
      - curl -f http://localhost:{port} || exit 1

notifications:
  on_success:
    - echo "🎉 React deployment completed successfully"
    - echo "🌐 Access your application at http://localhost:{port}"
  on_failure:
    - echo "💥 React deployment failed"
  on_always:
    - echo "🔔 React pipeline finished"
'''
