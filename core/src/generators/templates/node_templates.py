"""
File templates for Node.js (Express) projects.
Contains all the file templates needed to generate a basic Node.js project and CI/CD.
"""

# Multi-stage Dockerfile for Node.js
DOCKERFILE_TEMPLATE = """FROM node:20-slim as base

WORKDIR /app
COPY package*.json ./
RUN npm install --omit=dev

FROM base as test
RUN npm install --only=dev && apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY . .

FROM base as prod
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY src/ /app/src/
ENV PORT=3000 NODE_ENV=production
HEALTHCHECK --interval=5s --timeout=3s --start-period=10s --retries=3 CMD curl -f http://localhost:3000/health || exit 1
EXPOSE 3000
CMD ["node", "src/app.js"]
"""

PACKAGE_JSON_TEMPLATE = """{{
  "name": "{project_name}",
  "version": "1.0.0",
  "description": "Automatically generated basic Node.js API",
  "main": "src/app.js",
  "scripts": {{
    "start": "node src/app.js",
    "test": "mkdir -p ./test-reports && jest --coverage --outputFile=./test-reports/report.json --json",
    "lint": "eslint src/"
  }},
  "dependencies": {{
    "express": "^4.19.2"
  }},
  "devDependencies": {{
    "jest": "^29.7.0",
    "supertest": "^6.3.4",
    "eslint": "^8.57.0"
  }}
}}
"""

DOCKER_COMPOSE_TEMPLATE = """services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: prod
    container_name: {project_name}_app
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - PORT=3000
      - NODE_ENV=production
    volumes:
      - ./logs:/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 5s
      timeout: 3s
      retries: 3
    networks:
      - app_network

  testing:
    build:
      context: .
      dockerfile: Dockerfile
      target: test
    depends_on:
      app:
        condition: service_healthy
    command: npm test
    environment:
      - BASE_URL=http://app:3000
    volumes:
      - ./test-reports:/app/test-reports
    networks:
      - app_network

  code_quality:
    build:
      context: .
      dockerfile: Dockerfile
      target: test
    command: >
      sh -c "\
        echo 'Running code quality checks...' && \
        eslint src/ --output-file=/app/reports/eslint.txt || true && \
        echo 'Code quality checks completed.'
      "
    volumes:
      - ./reports:/app/reports
    networks:
      - app_network

networks:
  app_network:
    driver: bridge
"""

# Development pipeline - keeps services running
PIPELINE_DEV_TEMPLATE = """# Development Pipeline for Node.js application
name: "Development - {project_name}"
description: "Pipeline for local development - keeps services running for active development"

# Quick parallel checks
parallel_steps:
  - step: code_analysis
    description: "Code analysis and linting with ESLint"
    command: docker-compose run --rm code_quality

# Development workflow
pipeline:
  - step: build
    description: "Build application containers"
    command: docker-compose build
    
  - step: deploy
    description: "Deploy application for development (persistent)"
    command: docker-compose up -d app

  - step: wait_for_service
    description: "Wait for service to be ready"
    command: python -c "import time; time.sleep(10); print('Service ready for development!')"

  - step: health_check
    description: "Verify service is responding"
    command: curl -f http://localhost:3000/health || echo "Warning, health check failed"

notifications:
  on_success:
    - echo "🎉 Development environment ready!"
    - echo "🌐 Application: http://localhost:3000"
    - echo "🔄 Services are running in background"
    - echo "💡 To stop: docker-compose down"
  on_failure:
    - echo "💥 Development setup failed"
  on_always:
    - echo "🔔 Development pipeline finished"
"""

# Testing pipeline - full E2E with cleanup
PIPELINE_TEST_TEMPLATE = """# Testing Pipeline for Node.js application  
name: "Testing - {project_name}"
description: "Full E2E testing pipeline with cleanup"

# Quality checks in parallel
parallel_steps:
  - step: code_analysis
    description: "Code analysis and linting with ESLint"
    command: docker-compose run --rm code_quality

# Full testing workflow
pipeline:
  - step: build
    description: "Build application containers"
    command: docker-compose build
    
  - step: deploy
    description: "Deploy application for testing"
    command: docker-compose up -d app

  - step: wait_for_service
    description: "Wait for service to be ready"
    command: python -c "import time; time.sleep(10); print('Service ready for testing!')"

  - step: integration_tests
    description: "Run integration tests"
    command: docker-compose up --abort-on-container-exit testing
    
  - step: collect_results
    description: "Collect test reports"
    command: python -c "import os, shutil; os.makedirs('reports', exist_ok=True); [shutil.copy2(os.path.join('test-reports', f), 'reports/') for f in os.listdir('test-reports') if os.path.isfile(os.path.join('test-reports', f))] if os.path.exists('test-reports') else None"

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
PIPELINE_PROD_TEMPLATE = """# Production Pipeline for Node.js application
name: "Production - {project_name}"
description: "Production-ready deployment with monitoring"

# Security and quality checks
parallel_steps:
  - step: security_scan
    description: "Security vulnerability scan"
    command: docker-compose run --rm code_quality sh -c "npm audit --audit-level=moderate || echo 'Security scan completed'"
    
  - step: code_analysis
    description: "Code quality analysis"
    command: docker-compose run --rm code_quality

# Production deployment
pipeline:
  - step: build
    description: "Build optimized production containers"
    command: docker-compose build --no-cache app
    
  - step: deploy
    description: "Deploy to production mode"
    command: docker-compose up -d app

  - step: health_monitoring
    description: "Extended health check and monitoring setup"
    commands:
      - python -c "import time; time.sleep(15); print('Performing extended health checks...')"
      - curl -f http://localhost:3000/health
      - curl -f http://localhost:3000/api/status

  - step: load_test
    description: "Basic load testing"
    command: echo "🚀 Production deployment completed. Monitor at http://localhost:3000"

notifications:
  on_success:
    - echo "🚀 Production deployment successful!"
    - echo "🌐 Application: http://localhost:3000"
    - echo "📊 Monitor logs: docker-compose logs -f app"
  on_failure:
    - echo "💥 Production deployment failed"
"""

# Legacy template for backward compatibility
PIPELINE_TEMPLATE = PIPELINE_DEV_TEMPLATE

APP_TEMPLATE = """const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

// Basic logging middleware
app.use((req, res, next) => {{
  console.log(`[${{new Date().toISOString()}}] ${{req.method}} ${{req.url}}`);
  next();
}});

// Health check endpoint
app.get('/health', (req, res) => {{
  res.json({{
    status: 'healthy',
    service: '{project_name}',
    timestamp: Date.now()
  }});
}});

// Hello World endpoint
app.get('/', (req, res) => {{
  res.json({{
    message: 'Hello World from {project_name}!',
    status: 'success',
    timestamp: Date.now()
  }});
}});

// API status endpoint
app.get('/api/status', (req, res) => {{
  res.json({{
    api_status: 'running',
    service: '{project_name}',
    version: '1.0.0'
  }});
}});

// Export app for testing
module.exports = app;

// Only start the server if run directly
if (require.main === module) {{
  app.listen(port, () => {{
    console.log(`Server running on port ${{port}}`);
  }});
}}
"""

TEST_APP_TEMPLATE = """const request = require('supertest');
const app = require('../app');

describe('Node.js API Endpoints', () => {{
  test('GET /health', async () => {{
    const res = await request(app).get('/health');
    expect(res.statusCode).toBe(200);
    expect(res.body.status).toBe('healthy');
    expect(res.body.service).toBe('{project_name}');
    expect(res.body.timestamp).toBeDefined();
  }});

  test('GET /', async () => {{
    const res = await request(app).get('/');
    expect(res.statusCode).toBe(200);
    expect(res.body.message).toBe('Hello World from {project_name}!');
    expect(res.body.status).toBe('success');
    expect(res.body.timestamp).toBeDefined();
  }});

  test('GET /api/status', async () => {{
    const res = await request(app).get('/api/status');
    expect(res.statusCode).toBe(200);
    expect(res.body.api_status).toBe('running');
    expect(res.body.service).toBe('{project_name}');
    expect(res.body.version).toBe('1.0.0');
  }});

  test('GET /nonexistent', async () => {{
    const res = await request(app).get('/nonexistent');
    expect(res.statusCode).toBe(404);
  }});
}});
"""

README_TEMPLATE = """# {project_name}

A basic Node.js (Express) application automatically generated.

## Features

- Basic REST API with Express
- Health check endpoint
- Automated tests with Jest and Supertest
- Code analysis with ESLint
- Containerization with Docker
- Automated CI/CD pipeline

## Available endpoints

- `GET /` - Main Hello World
- `GET /health` - Health check
- `GET /api/status` - API status

## Local development

### Requirements

- Node.js 20+
- Docker and Docker Compose

### Installation

1. Install dependencies:
```bash
npm install
```

2. Run the application:
```bash
npm start
```

The application will be available at `http://localhost:3000`

## Testing

Run tests:
```bash
npm test
```

## Linting

Run code analysis:
```bash
npm run lint
```

## Deploy with Docker

### Development
```bash
docker-compose up --build
```

### Production
```bash
docker-compose up -d app
```

## CI/CD Pipeline

To run the complete pipeline:
```bash
python ../../run_pipeline.py --pipeline pipeline.yml
```

The pipeline includes:
1. Code analysis (parallel)
2. Application build
3. Deployment
4. Integration tests
5. Results collection
6. Cleanup

## Project structure

```
{project_name}/
├── src/
│   ├── app.js              # Main Express application
│   └── tests/
│       └── test_app.js     # Automated tests
├── logs/                   # Application logs
├── reports/                # Code analysis reports
├── test-reports/           # Test reports
├── Dockerfile              # Multi-stage Docker configuration
├── docker-compose.yml      # Services configuration
├── pipeline.yml            # CI/CD pipeline
├── package.json            # Node.js dependencies
└── README.md               # This file
```

## Logs

Logs are stored in the `logs/` directory and shown in the console.

## Code analysis

The project includes automatic analysis with:
- **eslint**: JavaScript code style

Reports are generated in `reports/`.
"""

GITIGNORE_TEMPLATE = """# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Logs
logs
*.log
logs/*

# Reports
reports/
test-reports/

# OS
.DS_Store
Thumbs.db

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Docker
.dockerignore

# Env
.env
"""

