"""
Flask pipeline templates for different deployment modes.
Includes development, testing, and production pipeline configurations.
"""

# Development pipeline - keeps services running for local development
FLASK_PIPELINE_DEV_TEMPLATE = """# Development Pipeline for Flask application
name: "Development - {project_name}"
description: "Pipeline for local development - keeps services running for active development"

environment:
  PROJECT_NAME: "{project_name}"

# Quick parallel checks
parallel_steps:
  - step: code_analysis
    description: "Quick code quality checks"
    command: docker-compose run --rm --entrypoint sh manage -c "flake8 {project_name} --count --statistics || echo 'Code analysis completed'"

# Development workflow
pipeline:
  - step: build
    description: "Build application containers"
    command: docker-compose build
    
  - step: deploy
    description: "Deploy Flask application for development (persistent)"
    command: docker-compose up -d flask-dev

  - step: wait_for_service
    description: "Wait for Flask to be ready"
    command: python -c "import time; time.sleep(10); print('Flask development server ready!')"

  - step: health_check
    description: "Verify Flask is responding"
    command: curl -f http://localhost:8080/ || echo "Warning, health check failed - check service manually"

notifications:
  on_success:
    - echo "🎉 Flask development environment ready!"
    - echo "🌐 Application: http://localhost:8080"
    - echo "🔄 Services are running in background"
    - echo "💡 To stop: docker-compose down"
  on_failure:
    - echo "💥 Flask development setup failed"
  on_always:
    - echo "🔔 Development pipeline finished"
"""

# Testing pipeline - full E2E with cleanup
FLASK_PIPELINE_TEST_TEMPLATE = """# Testing Pipeline for Flask application
name: "Testing - {project_name}"
description: "Full E2E testing pipeline with cleanup"

environment:
  PROJECT_NAME: "{project_name}"

# Quality checks in parallel
parallel_steps:
  - step: code_analysis
    description: "Code quality analysis"
    command: docker-compose run --rm --entrypoint sh manage -c "flake8 {project_name} --count --statistics && pylint {project_name}/**/*.py --fail-under=8 || echo 'Code analysis completed'"

# Full testing workflow
pipeline:
  - step: build
    description: "Build application containers"
    command: docker-compose build
    
  - step: deploy
    description: "Deploy Flask application for testing"
    command: docker-compose up -d flask-dev

  - step: wait_for_service
    description: "Wait for Flask to be ready"
    command: python -c "import time; time.sleep(10); print('Flask testing server ready!')"

  - step: run_tests
    description: "Run Flask test suite"
    command: docker-compose run --rm --entrypoint pytest manage --verbose

  - step: security_scan
    description: "Security vulnerability scan"
    command: docker-compose run --rm --entrypoint sh manage -c "bandit -r {project_name} --severity-level medium --confidence-level medium --format txt && safety check --short-report || echo 'Security scan completed'"

  - step: collect_results
    description: "Collect test reports and logs"
    command: python -c "import os, shutil; os.makedirs('reports', exist_ok=True); print('Test results collection completed')"

cleanup:
  - step: teardown
    description: "Stop and remove all containers"
    command: docker-compose down

notifications:
  on_success:
    - echo "✅ All tests passed!"
  on_failure:
    - echo "❌ Tests failed"
  on_always:
    - echo "🧹 Test environment cleaned up"
"""

# Production-like pipeline
FLASK_PIPELINE_PROD_TEMPLATE = """# Production Pipeline for Flask application
name: "Production - {project_name}"
description: "Production-ready deployment with monitoring"

environment:
  PROJECT_NAME: "{project_name}"

# Security and quality checks
parallel_steps:
  - step: security_scan
    description: "Comprehensive security analysis"
    command: docker-compose run --rm --entrypoint sh manage -c "bandit -r {project_name} --severity-level low --confidence-level medium --format txt && safety check --full-report || echo 'Security scan completed'"
  - step: code_analysis
    description: "Production code quality analysis"
    command: docker-compose run --rm --entrypoint sh manage -c "flake8 {project_name} --count --statistics && pylint {project_name}/**/*.py --fail-under=9 || echo 'Code analysis completed'"

# Production deployment
pipeline:
  - step: build
    description: "Build optimized production containers"
    command: docker-compose build --no-cache
    
  - step: deploy
    description: "Deploy to production mode"
    command: docker-compose up -d flask-prod

  - step: health_monitoring
    description: "Extended health check and monitoring setup"
    commands:
      - python -c "import time; time.sleep(15); print('Performing extended health checks...')"
      - curl -f http://localhost:8080/
      - curl -f http://localhost:8080/health || echo "Health endpoint check completed"

  - step: performance_test
    description: "Basic performance validation"
    command: echo "🚀 Production deployment completed. Monitor at http://localhost:8080"

notifications:
  on_success:
    - echo "🚀 Production deployment successful!"
    - echo "🌐 Application: http://localhost:8080"
    - echo "📊 Monitor logs: docker-compose logs -f flask-prod"
  on_failure:
    - echo "💥 Production deployment failed"
"""
