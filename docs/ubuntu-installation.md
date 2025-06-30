# Ubuntu Installation Guide for LocalForge Engine

This guide provides detailed installation instructions specifically for Ubuntu systems, with special attention to Virtual Machine setups.

## Prerequisites Check

Before starting, verify your Ubuntu version:

```bash
lsb_release -a
```

This guide is tested on Ubuntu 20.04 LTS and 22.04 LTS.

## Step 1: System Package Installation

Update your package list and install required system packages:

```bash
# Update package list
sudo apt update

# Install core dependencies
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    software-properties-common

# Install Docker
sudo apt install -y docker.io

# Install Node.js and npm (latest stable)
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installations
python3 --version
pip3 --version
git --version
docker --version
node --version
npm --version
```

## Step 2: Docker Configuration (Critical for VMs)

Docker configuration is often the most problematic part in Ubuntu VMs. Follow these steps carefully:

```bash
# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Create docker group (may already exist)
sudo groupadd docker

# Add your user to docker group
sudo usermod -aG docker $USER

# Fix Docker socket permissions (important for VMs)
sudo chown root:docker /var/run/docker.sock
sudo chmod 666 /var/run/docker.sock

# Restart Docker service
sudo systemctl restart docker
```

**Important:** After adding yourself to the docker group, you MUST log out and log back in (or restart your terminal session) for the changes to take effect.

### Docker Verification

Test Docker access without sudo:

```bash
# This should work without sudo after logging out/in
docker run hello-world

# If it fails, try:
sudo docker run hello-world

# If sudo works but regular user doesn't, you need to log out/in
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

# You should see (.venv) in your prompt now

# Install Python dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Verify installation
localforge-generate --help
localforge-ui --help
```

## Step 4: Testing Installation

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

1. **Start with the Web UI:** `localforge-ui` and visit `http://localhost:5001`
2. **Try Project Generation:** Create a simple Node.js or React project
3. **Explore Templates:** Check out the Flask and Django generators

## Getting Help

If you encounter issues not covered here:

1. Check the `logs/` directory for detailed error messages
2. Run commands with `--log-level DEBUG` for verbose output
3. Create a GitHub issue with:
   - Your Ubuntu version (`lsb_release -a`)
   - Error logs from the `logs/` directory

## Additional Resources

- [Docker Ubuntu Installation Guide](https://docs.docker.com/engine/install/ubuntu/)
- [Node.js Ubuntu Installation](https://nodejs.org/en/download/package-manager/#debian-and-ubuntu-based-linux-distributions)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
