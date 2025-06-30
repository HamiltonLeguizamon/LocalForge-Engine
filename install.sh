#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function check() {
  local name="$1"
  local cmd="$2"
  local critical=${3:-1}
  echo -n "$name: "
  if eval "$cmd" &>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    return 0
  else
    if [ "$critical" -eq 1 ]; then
      echo -e "${RED}✗${NC}"
    else
      echo -e "${YELLOW}✗ (optional)${NC}"
    fi
    return 1
  fi
}


echo "=== LocalForge Engine Installation & Verification ==="

REQUIRED_OK=1

# Check for Python (python3 or python)
check "Python 3" "python3 --version || python --version" || REQUIRED_OK=0
# Check for pip (pip3 or pip)
check "Pip" "pip3 --version || pip --version" || REQUIRED_OK=0
check "Git" "git --version" || REQUIRED_OK=0
check "Docker" "docker --version" || REQUIRED_OK=0
check "Docker without sudo" "docker ps" || REQUIRED_OK=0
check "Node.js" "node --version" || REQUIRED_OK=0
check "npm" "npm --version" || REQUIRED_OK=0

echo "==============================================="

if [ "$REQUIRED_OK" -ne 1 ]; then
  echo -e "${RED}ERROR: One or more critical requirements are missing. Please install all required dependencies before continuing.${NC}"
  exit 1
fi

echo -e "${GREEN}All requirements satisfied. Proceeding with installation...${NC}"

# Create logs directory if it does not exist
mkdir -p logs

# Create virtual environment if it does not exist
echo "Checking for Python virtual environment (.venv)..."
if [ ! -d ".venv" ]; then
  echo "Creating .venv..."
  (python3 -m venv .venv || python -m venv .venv)
fi

# Activar entorno virtual
echo "Activating .venv..."
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
  source .venv/Scripts/activate
else
  echo -e "${RED}ERROR: Could not find the virtual environment activation script.${NC}"
  exit 1
fi

# Instalar dependencias
echo "📦 Installing dependencies..."
(pip install -r requirements.txt || pip3 install -r requirements.txt)

# Instalar el paquete en modo desarrollo
echo "🔧 Installing package in development mode..."
(pip install -e . || pip3 install -e .)

echo -e "${GREEN}✅ Installation completed!${NC}"
echo ""
echo "📋 Available commands:"
echo "  localforge-pipeline --help    # Run pipelines"
echo "  localforge-ui                 # Web interface"
echo "  localforge-generate --help    # Generate projects"
echo ""
echo "🔧 Development mode:"
echo "  python run_pipeline.py --help"
echo "  python run_ui.py"
echo ""
echo "📁 Logs available at: ./logs/"
