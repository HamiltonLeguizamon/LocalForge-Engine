"""
Specific generator for React projects based on react_scaffold.py.
Implements the specific logic to create React projects with Vite, tests, and CI/CD.
"""
import os
import subprocess
import sys
from core.src.generators.base_generator import BaseProjectGenerator
from pathlib import Path
from core.src.utils.generator_utils import DependencyManager, GitManager
from core.src.generators.templates.react_pipeline_templates import (
    REACT_PIPELINE_DEV_TEMPLATE,
    REACT_PIPELINE_TEST_TEMPLATE,
    REACT_PIPELINE_PROD_TEMPLATE
)
import logging


class ReactProjectGenerator(BaseProjectGenerator):
    """Specific generator for React projects using Vite."""
      # React-specific reserved words (common ones are in ProjectValidator.COMMON_RESERVED_NAMES)
    REACT_RESERVED_NAMES = {
        'vite', 'webpack', 'babel', 'jest', 'enzyme', 'cypress',
        'components', 'hooks', 'context', 'store', 'reducers', 'actions'
    }

    def __init__(self, project_name: str, output_dir: str, use_typescript: bool = False, port: int = 3000):
        """
        Initialize the React generator.
        
        Args:
            project_name: Name of the project to generate
            output_dir: Directory where the project will be created
            use_typescript: Whether to use TypeScript
            port: Port for the development server
        """        # Use centralized validation with React-specific reserved words
        super().__init__(project_name, output_dir, self.REACT_RESERVED_NAMES)
        self.use_typescript = use_typescript
        self.port = port
        self._ensure_dependencies()
        
    def get_project_type(self) -> str:
        """Returns the project type."""
        return "react"

    def get_directory_structure(self) -> list:
        """Defines the directory structure for a React project."""
        return [
            "src/components",
            "src/pages", 
            "src/hooks",
            "src/utils",
            "src/styles",
            "src/__tests__",
            "public",
            "docs",
            ".github/workflows"
        ]
        
    def get_project_files(self) -> dict:
        """Defines all the files that will be generated for the React project."""
        ext = 'tsx' if self.use_typescript else 'jsx'
        setup_ext = 'ts' if self.use_typescript else 'js'
        project_slug = self.project_name.lower().replace(' ', '-')
        port = self.port

        files = {
            # Project configuration
            "package.json": self._get_package_json(),
            f"vite.config.{setup_ext}": self._get_vite_config(),
            
            # Main React files
            f"src/App.{ext}": self._get_app_component(),
            f"src/main.{ext}": self._get_main_component(),
            
            # Components
            f"src/components/Navbar.{ext}": self._get_navbar_component(),
            
            # Pages
            f"src/pages/Home.{ext}": self._get_home_page(),
            f"src/pages/About.{ext}": self._get_about_page(),
            
            # Tests
            f"src/setupTests.{setup_ext}": self._get_setup_tests(),
            f"src/__tests__/App.test.{ext}": self._get_app_test(),
            f"src/__tests__/Navbar.test.{ext}": self._get_navbar_test(),
            
            # CSS styles
            "src/styles/index.css": self._get_index_css(),
            "src/styles/App.css": self._get_app_css(),
            "src/styles/Navbar.css": self._get_navbar_css(),
            "src/styles/Home.css": self._get_home_css(),
            
            # Tooling configuration
            ".eslintrc.json": self._get_eslint_config(),
            ".prettierrc.json": self._get_prettier_config(),
            ".prettierignore": self._get_prettier_ignore(),
            
            # Docker
            "Dockerfile": self._get_dockerfile(port),
            "Dockerfile.dev": self._get_dockerfile_dev(port),
            "docker-compose.yml": self._get_docker_compose(port),
            "nginx.conf": self._get_nginx_config(),
            
            # HTML template
            "index.html": self._get_html_template(),
            
            # Security configuration
            ".audit-ci.json": self._get_audit_config(),
            
            # Git
            ".gitignore": self._get_gitignore(),
            
            # CI/CD Pipeline
            "pipeline-dev.yml": REACT_PIPELINE_DEV_TEMPLATE.format(project_name=self.project_name, project_slug=project_slug, port=port),
            "pipeline-test.yml": REACT_PIPELINE_TEST_TEMPLATE.format(project_name=self.project_name, project_slug=project_slug, port=port),
            "pipeline-prod.yml": REACT_PIPELINE_PROD_TEMPLATE.format(project_name=self.project_name, project_slug=project_slug, port=port),
            "pipeline.yml": REACT_PIPELINE_DEV_TEMPLATE.format(project_name=self.project_name, project_slug=project_slug, port=port),
            
            # Documentation
            "README.md": self._get_readme(),
        }
        
        # Add TypeScript files if needed
        if self.use_typescript:
            files["tsconfig.json"] = self._get_tsconfig()
            files["tsconfig.node.json"] = self._get_tsconfig_node()
        
        return files
    def create_project(self) -> bool:
        """
        Creates the React project using centralized validation and cleanup.
        
        Returns:
            bool: True if the project was created successfully, False otherwise
        """
        try:
            logging.info(f"🚀 Creating React project: {self.project_name}")
            
            # Use base class create_project which handles validation and cleanup
            success = super().create_project()
            
            if success:
                # Apply React-specific setup after base creation
                self._install_dependencies()
                self._initialize_git()
                
                logging.info(f"✅ React project '{self.project_name}' created successfully")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"❌ Error creating React project: {e}")
            # Base class will handle cleanup
            return False
    def _ensure_dependencies(self):
        """Check that Node.js, npm, and Docker are installed using centralized dependency manager."""
        try:
            node_available, npm_available = DependencyManager.ensure_node_npm()
            docker_available = DependencyManager.ensure_docker()
            
            # Store availability for later use
            self.node_available = node_available
            self.npm_available = npm_available
            self.docker_available = docker_available
            
            if not node_available:
                logging.warning("⚠️ Node.js is not available. Project files will be created but Node.js features will be disabled.")
            
            if not npm_available:
                logging.warning("⚠️ npm is not available. Project files will be created but dependency installation will be skipped.")
            
            # Docker is optional but recommended
            if not docker_available:
                logging.warning("⚠️ Docker is not available. Containerization features will be disabled.")
                
        except Exception as e:
            logging.warning(f"⚠️ Error checking dependencies: {e}")
            # Set defaults if dependency check fails
            self.node_available = False
            self.npm_available = False
            self.docker_available = False

    def _install_dependencies(self):
        """Install npm dependencies using centralized package manager."""
        if not hasattr(self, 'npm_available') or not self.npm_available:
            logging.warning("⚠️ npm is not available. Skipping dependency installation.")
            logging.info("💡 To install dependencies manually, run: npm install")
            return
            
        logging.info("📦 Installing npm dependencies...")
        success = DependencyManager.install_npm_dependencies(str(self.project_path))
        
        if not success:
            logging.warning("⚠️ Error installing dependencies")
            logging.info("💡 You can install dependencies manually by running: npm install")

    def _initialize_git(self):
        """Initialize Git repository using centralized Git manager."""
        if not GitManager.check_git_available():
            logging.warning("⚠️ Git is not available. Skipping Git repository initialization.")
            logging.info("� You can initialize Git manually by running: git init")
            return
            
        logging.info("�📋 Initializing Git repository...")
        success = GitManager.initialize_repository(str(self.project_path), "Initial commit")
        
        if not success:
            logging.warning("⚠️ Error initializing Git repository")
            logging.info("💡 You can initialize Git manually by running: git init")

    def _get_package_json(self) -> str:
        """Generate package.json"""
        import json
        
        deps = {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "react-router-dom": "^6.8.0"
        }
        
        dev_deps = {
            "@vitejs/plugin-react": "^4.0.0",
            "vite": "^4.4.0",
            "vitest": "^0.34.0",
            "@vitest/ui": "^0.34.0",
            "@vitest/coverage-v8": "^0.34.0",
            "@testing-library/react": "^14.0.0",
            "@testing-library/jest-dom": "^6.6.3",
            "@testing-library/user-event": "^14.4.3",
            "jsdom": "^22.0.0",
            "eslint": "^8.45.0",
            "eslint-plugin-react": "^7.33.0",
            "eslint-plugin-react-hooks": "^4.6.0",
            "eslint-plugin-react-refresh": "^0.4.3",
            "prettier": "^3.0.0",
            "audit-ci": "^6.6.1"
        }
        
        if self.use_typescript:
            dev_deps.update({
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0",
                "@typescript-eslint/eslint-plugin": "^6.0.0",
                "@typescript-eslint/parser": "^6.0.0",
                "typescript": "^5.0.0"
            })
        
        package_data = {
            "name": self.project_name.lower().replace(' ', '-'),
            "version": "1.0.0",
            "private": True,
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview",
                "test": "vitest run",
                "test:watch": "vitest",
                "test:ui": "vitest --ui",
                "test:coverage": "vitest run --coverage",
                "lint": "eslint src --ext js,jsx,ts,tsx --report-unused-disable-directives --max-warnings 0",
                "lint:fix": "eslint src --ext js,jsx,ts,tsx --fix",
                "format": "prettier --write \"src/**/*.{js,jsx,ts,tsx,css}\"",
                "security": "audit-ci --config .audit-ci.json",
                "docker:build": "docker build -t react-app .",
                "docker:run": f"docker run -p {self.port}:80 react-app",
                "docker:dev": "docker-compose up -d",
                "docker:down": "docker-compose down"
            },
            "dependencies": deps,
            "devDependencies": dev_deps
        }
        
        return json.dumps(package_data, indent=2)

    def _get_vite_config(self) -> str:
        """Generate Vite configuration"""
        ext = 'ts' if self.use_typescript else 'js'
        return f'''import {{ defineConfig }} from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({{
  plugins: [react()],
  server: {{
    host: true,
    port: {self.port},
  }},
  preview: {{
    host: true,
    port: {self.port},
  }},
  test: {{
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/setupTests.{ext}',
  }},
}})
'''

    def _get_app_component(self) -> str:
        """Generate main App component"""
        ext = 'tsx' if self.use_typescript else 'jsx'
        
        return f'''import {{ Routes, Route }} from 'react-router-dom'
import Home from './pages/Home'
import About from './pages/About'
import Navbar from './components/Navbar'
import './styles/App.css'

function App() {{
  return (
    <div className="App">
      <Navbar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={{<Home />}} />
          <Route path="/about" element={{<About />}} />
        </Routes>
      </main>
    </div>
  )
}}

export default App
'''

    def _get_main_component(self) -> str:
        """Generate main entry component"""
        ext = 'tsx' if self.use_typescript else 'jsx'
        exclamation = '!' if self.use_typescript else ''
        
        return f'''import React from 'react'
import ReactDOM from 'react-dom/client'
import {{ BrowserRouter }} from 'react-router-dom'
import App from './App.{ext}'
import './styles/index.css'

ReactDOM.createRoot(document.getElementById('root'){exclamation}).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
'''

    def _get_navbar_component(self) -> str:
        """Generate Navbar component"""
        component_def = 'const Navbar = () => {' if self.use_typescript else 'function Navbar() {'
        closing = '}' if self.use_typescript else '}'
        
        return f'''import {{ Link }} from 'react-router-dom'
import '../styles/Navbar.css'

{component_def}
  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          {self.project_name}
        </Link>
        <ul className="nav-menu">
          <li className="nav-item">
            <Link to="/" className="nav-link">
              Home
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/about" className="nav-link">
              About
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  )
{closing}

export default Navbar
'''

    def _get_home_page(self) -> str:
        """Generate Home page"""
        component_def = 'const Home = () => {' if self.use_typescript else 'function Home() {'
        closing = '}' if self.use_typescript else '}'
        ts_item = '<li>📘 TypeScript for type safety</li>' if self.use_typescript else ''
        
        return f'''import '../styles/Home.css'

{component_def}
  return (
    <div className="home">
      <h1>Welcome to {self.project_name}!</h1>
      <p>This is an automatically generated React project with:</p>
      <ul>
        <li>⚡ Vite for fast development</li>
        <li>🧪 Vitest for testing</li>
        <li>🐳 Docker for containers</li>
        <li>⚙️ Automatic CI/CD Pipeline</li>
        <li>🔍 ESLint + Prettier for code quality</li>
        {ts_item}
      </ul>
    </div>
  )
{closing}

export default Home
'''

    def _get_about_page(self) -> str:
        """Generate About page"""
        component_def = 'const About = () => {' if self.use_typescript else 'function About() {'
        closing = '}' if self.use_typescript else '}'
        
        return f'''
{component_def}
  return (
    <div className="about">
      <h1>About the Project</h1>
      <p>
        This project was generated using the LocalForge Engine React generator,
        a tool that creates complete React projects with all best practices.
      </p>
    </div>
  )
{closing}

export default About
'''

    def _get_setup_tests(self) -> str:
        """Generate test setup configuration"""
        return '''import { afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'
import '@testing-library/jest-dom'

afterEach(() => {
  cleanup()
})
'''

    def _get_app_test(self) -> str:
        """Generate App test"""
        ext = 'tsx' if self.use_typescript else 'jsx'
        
        return f'''import {{ describe, it, expect }} from 'vitest'
import {{ render, screen }} from '@testing-library/react'
import {{ MemoryRouter }} from 'react-router-dom'
import App from '../App.{ext}'

describe('App', () => {{
  it('renders without crashing', () => {{
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    )
    expect(screen.getByText(/Welcome/i)).toBeInTheDocument()
  }})
  
  it('has navigation links', () => {{
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    )
    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('About')).toBeInTheDocument()
  }})
}})
'''

    def _get_navbar_test(self) -> str:
        """Generate Navbar test"""
        ext = 'tsx' if self.use_typescript else 'jsx'
        
        return f'''import {{ describe, it, expect }} from 'vitest'
import {{ render, screen }} from '@testing-library/react'
import {{ MemoryRouter }} from 'react-router-dom'
import Navbar from '../components/Navbar.{ext}'

describe('Navbar', () => {{
  it('renders navigation links', () => {{
    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>
    )
    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('About')).toBeInTheDocument()
  }})
}})
'''

    def _get_index_css(self) -> str:
        """Generate main CSS"""
        return '''* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f5f5;
  color: #333;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}

#root {
  min-height: 100vh;
}
'''

    def _get_app_css(self) -> str:
        """Generate App CSS"""
        return '''.App {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

@media (max-width: 768px) {
  .main-content {
    padding: 1rem;
  }
}
'''

    def _get_navbar_css(self) -> str:
        """Generate Navbar CSS"""
        return '''.navbar {
  background-color: #282c34;
  padding: 1rem 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: #61dafb;
  text-decoration: none;
}

.nav-menu {
  display: flex;
  list-style: none;
  gap: 2rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  transition: color 0.3s ease;
}

.nav-link:hover {
  color: #61dafb;
}

@media (max-width: 768px) {
  .nav-container {
    padding: 0 1rem;
  }
  
  .nav-menu {
    gap: 1rem;
  }
}
'''

    def _get_home_css(self) -> str:
        """Generate Home CSS"""
        return '''.home {
  text-align: center;
  padding: 2rem;
}

.home h1 {
  color: #282c34;
  margin-bottom: 1rem;
  font-size: 2.5rem;
}

.home p {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  color: #666;
}

.home ul {
  list-style: none;
  max-width: 500px;
  margin: 0 auto;
  text-align: left;
}

.home li {
  padding: 0.5rem 0;
  font-size: 1.1rem;
  border-bottom: 1px solid #eee;
}

.home li:last-child {
  border-bottom: none;
}

@media (max-width: 768px) {
  .home h1 {
    font-size: 2rem;
  }
  
  .home {
    padding: 1rem;
  }
}
'''

    def _get_eslint_config(self) -> str:
        """Generate ESLint configuration"""
        extends_list = [
            "eslint:recommended",
            "plugin:react/recommended",
            "plugin:react/jsx-runtime",
            "plugin:react-hooks/recommended"
        ]
        
        plugins_list = ["react-refresh"]
        
        if self.use_typescript:
            extends_list.insert(1, "plugin:@typescript-eslint/recommended")
            plugins_list.append("@typescript-eslint")
        
        config = {
            "root": True,
            "env": {"browser": True, "es2020": True},
            "extends": extends_list,
            "ignorePatterns": ["dist", ".eslintrc.cjs"],
            "parserOptions": {"ecmaVersion": "latest", "sourceType": "module"},
            "settings": {"react": {"version": "18.2"}},
            "plugins": plugins_list,
            "rules": {
                "react-refresh/only-export-components": [
                    "warn",
                    {"allowConstantExport": True}
                ]
            }
        }
        
        if self.use_typescript:
            config["parser"] = "@typescript-eslint/parser"
        
        import json
        return json.dumps(config, indent=2)

    def _get_prettier_config(self) -> str:
        """Generate Prettier configuration"""
        import json
        return json.dumps({
            "semi": False,
            "singleQuote": True,
            "tabWidth": 2,
            "trailingComma": "es5",
            "printWidth": 80,
            "bracketSpacing": True,
            "arrowParens": "avoid"
        }, indent=2)

    def _get_prettier_ignore(self) -> str:
        """Generate .prettierignore"""
        return '''node_modules
dist
build
coverage
.env
.env.local
.env.production
*.log
'''

    def _get_dockerfile(self, port=None) -> str:
        """Generate production Dockerfile with dynamic port"""
        port = port or 3000
        return f'''# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev for build)
RUN npm ci

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built app to nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port {port}
EXPOSE {port}

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
'''

    def _get_dockerfile_dev(self, port=None) -> str:
        """Generate development Dockerfile with dynamic port"""
        port = port or 3000
        return f'''FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Expose port
EXPOSE {port}

# Start development server
CMD ["npm", "run", "dev"]
'''

    def _get_docker_compose(self, port=None) -> str:
        """Generate docker-compose.yml with dynamic port"""
        project_slug = self.project_name.lower().replace(' ', '-')
        port = port or 3000
        return f'''services:
  # Service to build and run the app in production
  react-app:
    image: {project_slug}:latest
    ports:
      - "{port}:80"
    environment:
      - NODE_ENV=production
      - PORT={port}
    restart: unless-stopped

  # Development service
  react-dev:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "{port}:{port}"
    volumes:
      - .:/app
      - /app/node_modules
      - $HOME/.npm:/root/.npm
    environment:
      - NODE_ENV=development
      - PORT={port}
    command: npm run dev

  # Node.js service for CI/CD (install, lint, test, build)
  node:
    build:
      context: .
      dockerfile: Dockerfile.dev
    working_dir: /app
    volumes:
      - .:/app
      - /app/node_modules
      - $HOME/.npm:/root/.npm
    environment:
      - NODE_ENV=development
      - PORT={port}

  # Service for testing
  test-runner:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=test
      - PORT={port}
    command: npm run test:coverage

  # Service for security analysis
  security-scanner:
    image: aquasec/trivy:latest
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - $HOME/.cache:/root/.cache
    command: image {project_slug}:latest
'''
    def _get_nginx_config(self) -> str:
        """Generate nginx configuration"""
        return '''events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        location / {
            try_files $uri $uri/ /index.html;
        }

        location /static/ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
'''

    def _get_html_template(self) -> str:
        """Generate HTML template"""
        main_file_ext = "tsx" if self.use_typescript else "jsx"
        
        return f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="React application generated with LocalForge Engine" />
    <title>{self.project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.{main_file_ext}"></script>
  </body>
</html>
'''

    def _get_audit_config(self) -> str:
        """Generate security audit configuration"""
        import json
        return json.dumps({
            "low": False,
            "moderate": False,
            "high": True,
            "critical": True,
            "allowlist": [],
            "report-type": "important",
            "skip-dev": True
        }, indent=2)

    def _get_gitignore(self) -> str:
        """Generate .gitignore"""
        return '''# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Production build
dist/
build/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Coverage reports
coverage/

# Logs
logs
*.log

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Microbundle cache
.rpt2_cache/
.rts2_cache_cjs/
.rts2_cache_es/
.rts2_cache_umd/

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# Stores VSCode versions used for testing VSCode extensions
.vscode-test

# Temporary folders
tmp/
temp/
'''

    def _get_pipeline_config(self) -> str:
        """Generate pipeline.yml for CI/CD using template file"""
        project_slug = self.project_name.lower().replace(' ', '-')
        return REACT_PIPELINE_DEV_TEMPLATE.format(project_name=self.project_name, project_slug=project_slug)

    def _get_tsconfig(self) -> str:
        """Generate tsconfig.json for TypeScript"""
        import json
        return json.dumps({
            "compilerOptions": {
                "target": "ES2020",
                "useDefineForClassFields": True,
                "lib": ["ES2020", "DOM", "DOM.Iterable"],
                "module": "ESNext",
                "skipLibCheck": True,
                "moduleResolution": "bundler",
                "allowImportingTsExtensions": True,
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "jsx": "react-jsx",
                "strict": True,
                "noUnusedLocals": True,
                "noUnusedParameters": True,
                "noFallthroughCasesInSwitch": True
            },
            "include": ["src"],
            "references": [{"path": "./tsconfig.node.json"}]
        }, indent=2)

    def _get_tsconfig_node(self) -> str:
        """Generate tsconfig.node.json for TypeScript"""
        import json
        return json.dumps({
            "compilerOptions": {
                "composite": True,
                "skipLibCheck": True,
                "module": "ESNext",
                "moduleResolution": "bundler",
                "allowSyntheticDefaultImports": True
            },
            "include": ["vite.config.ts"]
        }, indent=2)

    def _get_readme(self) -> str:
        """Generate README.md"""
        ext = 'tsx' if self.use_typescript else 'jsx'
        setup_ext = 'ts' if self.use_typescript else 'js'
        
        ts_section = '''
## TypeScript

This project uses TypeScript for type safety. The configuration files include:
- `tsconfig.json` - Main TypeScript configuration
- `tsconfig.node.json` - Configuration for build tools
''' if self.use_typescript else ''
        
        return f'''# {self.project_name}

React application automatically generated with LocalForge Engine.

## 🚀 Features

- ⚡ **Vite** - Modern and fast build tool
- ⚛️ **React 18** - UI library
- 🧪 **Vitest** - Fast testing framework
- 🎨 **CSS Modules** - Modular styles
- 🐳 **Docker** - Containers for development and production
- ⚙️ **CI/CD Pipeline** - Complete automation
- 🔍 **ESLint + Prettier** - Code quality and formatting
- 🔒 **Security audit** - Automated npm audit{"" if not self.use_typescript else ""}
- 📘 **TypeScript** - Type safety and better DX

## 📋 Requirements

- Node.js 18+
- npm or yarn
- Docker and Docker Compose

## 🛠️ Development

### Installation

```bash
# Install dependencies
npm install

# Run in development mode
npm run dev
```

The application will be available at `http://localhost:{self.port}`

### Available scripts

```bash
# Development
npm run dev              # Development server
npm run build            # Production build
npm run preview          # Preview build

# Testing
npm run test             # Run tests
npm run test:watch       # Watch mode tests
npm run test:ui          # Vitest UI tests
npm run test:coverage    # Tests with coverage

# Code quality
npm run lint             # Linting with ESLint
npm run lint:fix         # Auto-fix linting
npm run format           # Format code with Prettier

# Security
npm run security         # Dependency audit

# Docker
npm run docker:build     # Build Docker image
npm run docker:run       # Run container
npm run docker:dev       # Development environment
npm run docker:down      # Stop containers
```

## 🐳 Docker

### Development

```bash
# Run in development mode
docker-compose up react-dev

# With rebuild
docker-compose up --build react-dev
```

### Production

```bash
# Build and run
npm run docker:build
npm run docker:run

# Or with docker-compose
docker-compose up react-app
```

## 🧪 Testing

Tests use **Vitest** and **Testing Library**:

```bash
# Run all tests
npm run test

# Watch mode tests
npm run test:watch

# Tests with UI
npm run test:ui

# Coverage report
npm run test:coverage
```

## 🚀 CI/CD Pipeline

To run the complete pipeline:

```bash
python ../../run_pipeline.py --pipeline pipeline.yml
```

The pipeline includes:

1. **Dependency installation**
2. **Code analysis** (ESLint + Prettier)
3. **Tests with coverage**
4. **Security audit**
5. **Application build**
6. **Container deployment**
7. **Health check**
8. **Cleanup**
{ts_section}
## 📁 Project structure

```
{self.project_name}/
├── public/                 # Static files
├── src/
│   ├── components/         # Reusable components
│   ├── pages/             # Application pages
│   ├── hooks/             # Custom hooks
│   ├── utils/             # Utilities
│   ├── styles/            # CSS styles
│   ├── __tests__/         # Tests
│   ├── App.{ext}          # Main component
│   └── main.{ext}         # Entry point
├── docs/                  # Documentation
├── .github/workflows/     # GitHub Actions
├── Dockerfile             # Production image
├── Dockerfile.dev         # Development image
├── docker-compose.yml     # Container orchestration
├── vite.config.{setup_ext}           # Vite configuration
├── pipeline.yml           # CI/CD pipeline
└── README.md              # This file
```

## 🔧 Configuration

### Environment variables

Create a `.env.local` file for development variables:

```env
VITE_API_URL=http://localhost:{self.port}
VITE_APP_TITLE={self.project_name}
```

### Vite configuration

The `vite.config.{setup_ext}` file contains the build tool configuration.

### ESLint configuration

`.eslintrc.json` contains linting rules.

### Prettier configuration

`.prettierrc.json` contains formatting rules.

## 📦 Deployment

### Production build

```bash
npm run build
```

The files are generated in the `dist/` folder.

### Docker

```bash
# Build production image
docker build -t {self.project_name.lower().replace(" ", "-")} .

# Run container
docker run -p {self.port}:80 {self.project_name.lower().replace(" ", "-")}
```

## 🤝 Contribution

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is under the MIT License.

---

Generated with ❤️ by [LocalForge Engine](https://github.com/your-repo/localforge-engine)
'''
