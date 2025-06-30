# Windows Installation Guide for LocalForge Engine

This guide provides detailed installation instructions specifically for Windows systems.

## Step 1: Install Required Software

### Python Installation

Download and install Python 3.8+ from the official website:

```powershell
# Option 1: Download from python.org
# Visit https://www.python.org/downloads/windows/
# Download Python 3.8+ and run the installer
# ⚠️ IMPORTANT: Check "Add Python to PATH" during installation

# Option 2: Using winget (Windows Package Manager)
winget install Python.Python.3.11

# Option 3: Using Chocolatey (if installed)
choco install python3

# Verify installation
python --version
pip --version
```

### Git Installation

```powershell
# Option 1: Download from git-scm.com
# Visit https://git-scm.com/download/win
# Download Git for Windows and run the installer

# Option 2: Using winget
winget install Git.Git

# Option 3: Using Chocolatey
choco install git

# Verify installation
git --version
```

### Docker Installation (Required)

Docker is required for container operations. You can install Docker using Docker Desktop (recommended for most users) or other methods (e.g., Docker Toolbox, WSL2 integration):

```powershell
# Option 1: Docker Desktop (recommended for most users)
# Visit https://hub.docker.com/editions/community/docker-ce-desktop-windows
# Download Docker Desktop for Windows and run the installer

# Option 2: Using winget
winget install Docker.DockerDesktop

# Option 3: Using Chocolatey
choco install docker-desktop

# Option 4: Advanced users can install Docker Engine via WSL2 or Docker Toolbox
# See: https://docs.docker.com/engine/install/
```

> **Note:** Docker Desktop is the easiest way to get Docker running on Windows, but advanced users may use WSL2 or other alternatives. Only Docker itself is required.

**Troubleshooting Docker Issues:**

If Docker fails to start:

- Ensure Virtualization is enabled in BIOS
- Enable Windows features: Hyper-V and Containers
- For WSL 2: Install WSL 2 kernel update

```powershell
# Enable Windows features (run as Administrator)
Enable-WindowsOptionalFeature -Online -FeatureName containers -All
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```

### Node.js and npm Installation

```powershell
# Option 1: Download from nodejs.org
# Visit https://nodejs.org/en/download/
# Download the Windows Installer (.msi) and run it

# Option 2: Using winget
winget install OpenJS.NodeJS

# Option 3: Using Chocolatey
choco install nodejs

# Verify installation
node --version
npm --version
```

## Step 3: LocalForge Engine Installation

> **Recommended:** Use the automated installation and verification script for a complete and safe setup.
>
> **On Windows, you must run this script from Bash (Git Bash or WSL). It will not work in CMD or PowerShell.**
>
> This script will check all requirements, create and activate a `.venv`, and install everything for you.

```bash
bash install.sh
```

If you prefer a manual installation, follow these steps:

```powershell
# Clone the repository
git clone https://github.com/HamiltonLeguizamon/LocalForge-Engine
cd LocalForge-Engine

# (Recommended) Create and activate a virtual environment for LocalForge
python -m venv .venv
.venv\Scripts\Activate.ps1  # For PowerShell
# If using CMD: .venv\Scripts\activate.bat
# If using Git Bash: source .venv/Scripts/activate

# Install Python dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Step 4: Testing Installation

Test the key components:

```powershell
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
   - Your Windows version (`Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion`)
   - Error logs from the `logs/` directory
   - PowerShell version (`$PSVersionTable.PSVersion`)

## Additional Resources

- [Docker Desktop for Windows Documentation](https://docs.docker.com/desktop/windows/)
- [Node.js Windows Installation Guide](https://nodejs.org/en/download/package-manager/#windows)
- [Python Windows Installation Guide](https://docs.python.org/3/using/windows.html)
- [Git for Windows Documentation](https://gitforwindows.org/)
- [PowerShell Documentation](https://docs.microsoft.com/en-us/powershell/)
