# macOS Installation Guide for LocalForge Engine

This guide provides detailed installation instructions specifically for macOS systems.

## Step 1: Install Homebrew (Recommended)

Homebrew is the easiest way to install required packages on macOS:

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add Homebrew to your PATH (Apple Silicon Macs)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc

# Add Homebrew to your PATH (Intel Macs)
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc

# Verify Homebrew installation
brew --version
```

## Step 2: Install Required Software

### Python Installation

macOS comes with Python:

```bash
# Verify installation
python3 --version
pip3 --version
```

### Git Installation

```bash
# Install Git using Homebrew
brew install git

# Alternative: Xcode Command Line Tools (if not using Homebrew)
# xcode-select --install

# Verify installation
git --version
```

### Docker Installation (Required)

Docker is required for container operations. You can install Docker using Docker Desktop (recommended for most users) or other methods (e.g., Homebrew, direct engine install):

```bash
# Option 1: Docker Desktop (recommended for most users)
brew install --cask docker

# Option 2: Download manually
# Visit https://docs.docker.com/desktop/mac/install/
# Download Docker Desktop for Mac and drag to Applications

# Option 3: Advanced users can install Docker Engine directly
# See: https://docs.docker.com/engine/install/
```

> **Note:** Docker Desktop is the easiest way to get Docker running on macOS.

### Node.js and npm Installation

```bash
# Install Node.js using Homebrew
brew install node

# Alternative: Using Node Version Manager (nvm) - recommended for developers
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.zshrc
nvm install --lts
nvm use --lts

# Verify installation
node --version
npm --version
```

## Step 3: LocalForge Engine Installation

> **Recommended:** Use the automated installation and verification script for a complete and safe setup.
>
> This script will check all requirements, create and activate a `.venv`, and install everything for you.

```bash
bash install.sh
```

If you prefer a manual installation, follow these steps:

```bash
# Clone the repository
git clone https://github.com/HamiltonLeguizamon/LocalForge-Engine
cd LocalForge-Engine

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install Python dependencies
pip3 install -r requirements.txt

# Install the package in development mode
pip3 install -e .
```

## Step 5: Testing Installation

Test the key components:

```bash
# Test dependency checking
localforge-generate --list-types

# Test Docker integration
docker ps

# Test Node.js project generation
localforge-generate --type node --name test-node-app

# Test React project generation
localforge-generate --type react --name test-react-app

# Start web interface
localforge-ui
```

## Next Steps

After successful installation:

1. **Start with the Web UI:** Run `localforge-ui` and visit `http://localhost:5001`
2. **Try Project Generation:** Create a simple Node.js or React project
3. **Explore Templates:** Check out the Flask and Django generators

## Getting Help

If you encounter issues not covered here:

1. Check the `logs/` directory for detailed error messages
2. Run commands with `--log-level DEBUG` for verbose output
3. Create a GitHub issue with:
   - Your macOS version (`sw_vers`)
   - Your processor architecture (`uname -m`)
   - Error logs from the `logs/` directory
