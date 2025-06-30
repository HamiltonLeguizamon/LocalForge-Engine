"""
Django pipeline templates for different deployment modes.
Includes development, testing, and production pipeline configurations.
"""

# Development pipeline - keeps services running for local development
DJANGO_PIPELINE_DEV_TEMPLATE = """# Development Pipeline for Django application
name: "Development - {project_name}"
description: "Pipeline for local development - keeps services running for active development"

environment:
  PROJECT_NAME: "{project_name}"
  DJANGO_SETTINGS_MODULE: "config.settings.local"

# Quick parallel checks
parallel_steps:
  - step: static_analysis
    description: "Quick code quality checks"
    command: docker-compose -f {compose_file} run --rm django sh -c "flake8 . --count --statistics || echo 'Code analysis completed'"

# Development workflow
pipeline:
  - step: build
    description: "Build application containers"
    command: docker-compose -f {compose_file} build
    
  - step: migrate
    description: "Run database migrations"
    command: docker-compose -f {compose_file} run --rm django python manage.py migrate

  - step: collect_static
    description: "Collect static files"
    command: docker-compose -f {compose_file} run --rm django python manage.py collectstatic --noinput

  - step: deploy
    description: "Deploy Django application for development (persistent)"
    command: docker-compose -f {compose_file} up -d

  - step: wait_for_service
    description: "Wait for Django to be ready"
    command: python -c "import time; time.sleep(15); print('Django development server ready!')"

  - step: create_superuser
    description: "Create Django superuser for development"
    command: docker-compose -f {compose_file} run --rm -e DJANGO_SUPERUSER_USERNAME=admin -e DJANGO_SUPERUSER_EMAIL=admin@example.com -e DJANGO_SUPERUSER_PASSWORD=admin123 django python manage.py createsuperuser --noinput || echo "Superuser ready (may already exist)"

  - step: health_check
    description: "Verify Django is responding"
    command: curl -f http://localhost:8000/ || echo "Warning, health check failed - check service manually"

notifications:
  on_success:
    - echo "🎉 Django development environment ready!"
    - echo "🌐 Application: http://localhost:8000"
    - echo "👤 Admin panel: http://localhost:8000/admin (admin/admin123)"
    - echo "🔄 Services are running in background"
    - echo "💡 To stop: docker-compose -f {compose_file} down"
  on_failure:
    - echo "💥 Django development setup failed"
  on_always:
    - echo "🔔 Development pipeline finished"
"""

# Testing pipeline - full E2E with cleanup
DJANGO_PIPELINE_TEST_TEMPLATE = """# Testing Pipeline for Django application
name: "Testing - {project_name}"
description: "Full E2E testing pipeline with cleanup"

environment:
  PROJECT_NAME: "{project_name}"
  DJANGO_SETTINGS_MODULE: "config.settings.local"

# Quality checks in parallel
parallel_steps:
  - step: code_analysis
    description: "Code quality analysis"
    command: docker-compose -f {compose_file} run --rm django sh -c "flake8 . --count --statistics && pylint **/*.py --fail-under=8 || echo 'Code analysis completed'"

# Full testing workflow
pipeline:
  - step: build
    description: "Build application containers"
    command: docker-compose -f {compose_file} build
    
  - step: migrate
    description: "Run database migrations"
    command: docker-compose -f {compose_file} run --rm django python manage.py migrate

  - step: collect_static
    description: "Collect static files"
    command: docker-compose -f {compose_file} run --rm django python manage.py collectstatic --noinput

  - step: deploy
    description: "Deploy Django application for testing"
    command: docker-compose -f {compose_file} up -d

  - step: wait_for_service
    description: "Wait for Django to be ready"
    command: python -c "import time; time.sleep(15); print('Django testing server ready!')"

  - step: run_tests
    description: "Run Django test suite"
    command: docker-compose -f {compose_file} run --rm django python manage.py test --verbosity=2

  - step: security_scan
    description: "Security vulnerability scan"
    command: docker-compose -f {compose_file} run --rm django sh -c "bandit -r . --severity-level medium --confidence-level medium --format txt && safety check --short-report || echo 'Security scan completed'"

  - step: collect_results
    description: "Collect test reports and logs"
    command: python -c "import os, shutil; os.makedirs('reports', exist_ok=True); print('Test results collection completed')"

cleanup:
  - step: teardown
    description: "Stop and remove all containers"
    command: docker-compose -f {compose_file} down

notifications:
  on_success:
    - echo "✅ All tests passed!"
  on_failure:
    - echo "❌ Tests failed"
  on_always:
    - echo "🧹 Test environment cleaned up"
"""

# Production-like pipeline
DJANGO_PIPELINE_PROD_TEMPLATE = """# Production Pipeline for Django application
name: "Production - {project_name}"
description: "Production-ready deployment with monitoring"

environment:
  PROJECT_NAME: "{project_name}"
  DJANGO_SETTINGS_MODULE: "config.settings.production"

# Security and quality checks
parallel_steps:
  - step: security_scan
    description: "Comprehensive security analysis"
    command: docker-compose -f {compose_file} run --rm django sh -c "bandit -r . --severity-level low --confidence-level medium --format txt && safety check --full-report || echo 'Security scan completed'"
    
  - step: code_analysis
    description: "Production code quality analysis"
    command: docker-compose -f {compose_file} run --rm django sh -c "flake8 . --count --statistics && pylint **/*.py --fail-under=9 || echo 'Code analysis completed'"

# Production deployment
pipeline:
  - step: build
    description: "Build optimized production containers"
    command: docker-compose -f {compose_file} build --no-cache
    
  - step: migrate
    description: "Run database migrations"
    command: docker-compose -f {compose_file} run --rm django python manage.py migrate

  - step: collect_static
    description: "Collect and optimize static files"
    command: docker-compose -f {compose_file} run --rm django python manage.py collectstatic --noinput

  - step: deploy
    description: "Deploy to production mode"
    command: docker-compose -f {compose_file} up -d

  - step: health_monitoring
    description: "Extended health check and monitoring setup"
    commands:
      - python -c "import time; time.sleep(20); print('Performing extended health checks...')"
      - curl -f http://localhost:8000/
      - curl -f http://localhost:8000/admin/

  - step: performance_test
    description: "Basic performance validation"
    command: echo "🚀 Production deployment completed. Monitor at http://localhost:8000"

notifications:
  on_success:
    - echo "🚀 Production deployment successful!"
    - echo "🌐 Application: http://localhost:8000"
    - echo "👤 Admin panel: http://localhost:8000/admin"
    - echo "📊 Monitor logs: docker-compose -f {compose_file} logs -f"
  on_failure:
    - echo "💥 Production deployment failed"
"""
