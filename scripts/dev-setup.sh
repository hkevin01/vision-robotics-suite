#!/bin/bash
# Universal development environment setup script
# Works across Windows, Mac, and Linux platforms

set -e

# Colors for output
BLUE='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_NAME="vision-robotics-suite"
DOCKER_COMPOSE_FILE="docker-compose.dev.yml"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect operating system
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Function to install Docker on different platforms
install_docker() {
    local os=$(detect_os)

    print_status "Installing Docker for $os..."

    case $os in
        "linux")
            # Install Docker on Linux
            curl -fsSL https://get.docker.com -o get-docker.sh
            sh get-docker.sh
            sudo usermod -aG docker $USER
            rm get-docker.sh

            # Install Docker Compose
            sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
            ;;
        "macos")
            print_warning "Please install Docker Desktop for Mac from https://docker.com/products/docker-desktop"
            print_warning "After installation, restart this script."
            exit 1
            ;;
        "windows")
            print_warning "Please install Docker Desktop for Windows from https://docker.com/products/docker-desktop"
            print_warning "After installation, restart this script."
            exit 1
            ;;
        *)
            print_error "Unsupported operating system: $os"
            exit 1
            ;;
    esac
}

# Function to check system requirements
check_requirements() {
    print_status "Checking system requirements..."

    local requirements_met=true

    # Check Docker
    if ! command_exists docker; then
        print_warning "Docker is not installed"
        read -p "Would you like to install Docker? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_docker
        else
            print_error "Docker is required to run this development environment"
            requirements_met=false
        fi
    else
        print_success "Docker is installed: $(docker --version)"
    fi

    # Check Docker Compose
    if ! command_exists docker-compose; then
        print_warning "Docker Compose is not installed"
        # Try to install Docker Compose
        if command_exists docker; then
            local os=$(detect_os)
            if [[ "$os" == "linux" ]]; then
                sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                sudo chmod +x /usr/local/bin/docker-compose
            fi
        fi
    else
        print_success "Docker Compose is installed: $(docker-compose --version)"
    fi

    # Check available disk space (minimum 10GB)
    local available_space=$(df . | tail -1 | awk '{print $4}')
    local min_space=10485760  # 10GB in KB

    if [[ $available_space -lt $min_space ]]; then
        print_warning "Low disk space detected. At least 10GB is recommended."
    else
        print_success "Sufficient disk space available"
    fi

    # Check available memory (minimum 4GB)
    if command_exists free; then
        local available_memory=$(free -m | awk 'NR==2{printf "%.0f", $2}')
        if [[ $available_memory -lt 4096 ]]; then
            print_warning "Low memory detected. At least 4GB RAM is recommended."
        else
            print_success "Sufficient memory available: ${available_memory}MB"
        fi
    fi

    return $([ "$requirements_met" = true ])
}

# Function to create environment files
create_env_files() {
    print_status "Creating environment configuration files..."

    # Create .env file if it doesn't exist
    if [[ ! -f ".env" ]]; then
        cat > .env << 'EOF'
# Vision Robotics Suite Development Environment Configuration

# Database Configuration
POSTGRES_USER=developer
POSTGRES_PASSWORD=devpass123
POSTGRES_DB=vision_robotics
DATABASE_URL=postgresql://developer:devpass123@postgres:5432/vision_robotics

# Redis Configuration
REDIS_URL=redis://redis:6379

# MongoDB Configuration
MONGODB_URL=mongodb://admin:adminpass123@mongodb:27017/vision_robotics

# Application Configuration
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend Configuration
FRONTEND_URL=http://localhost:3000

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=detailed

# Development Configuration
NODE_ENV=development
PYTHONPATH=/home/developer/workspace

# External Services (for production)
# HALCON_LICENSE_PATH=/path/to/halcon/license
# PHOTONEO_SDK_PATH=/path/to/photoneo/sdk

EOF
        print_success "Created .env file with default development settings"
    else
        print_success ".env file already exists"
    fi

    # Create .env.example for team sharing
    if [[ ! -f ".env.example" ]]; then
        cp .env .env.example
        # Remove sensitive values from example
        sed -i.bak 's/=dev-secret-key-change-in-production/=your-secret-key-here/g' .env.example
        sed -i.bak 's/=devpass123/=your-password-here/g' .env.example
        rm .env.example.bak 2>/dev/null || true
        print_success "Created .env.example template"
    fi
}

# Function to create necessary directories
create_directories() {
    print_status "Creating project directories..."

    local directories=(
        "logs"
        "data"
        "backups"
        "docs"
        "scripts"
        "config"
        "tests/unit"
        "tests/integration"
        "tests/fixtures"
        ".vscode"
    )

    for dir in "${directories[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        fi
    done
}

# Function to create configuration files
create_config_files() {
    print_status "Creating configuration files..."

    # Create .gitignore if it doesn't exist
    if [[ ! -f ".gitignore" ]]; then
        cat > .gitignore << 'EOF'
# Environment files
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/settings.json
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Database
*.db
*.sqlite3

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Coverage
htmlcov/
.coverage
.coverage.*
coverage.xml

# Docker
.dockerignore

# Temporary files
tmp/
temp/
*.tmp

# Backup files
backups/
*.bak

# Data files
data/
*.csv
*.json
*.xml

EOF
        print_success "Created .gitignore file"
    fi

    # Create .dockerignore
    if [[ ! -f ".dockerignore" ]]; then
        cat > .dockerignore << 'EOF'
# Git
.git
.gitignore

# Documentation
README.md
docs/

# Environment files
.env
.env.*

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
htmlcov
.pytest_cache

# Node.js
node_modules
npm-debug.log
yarn-error.log

# IDE
.vscode
.idea
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
logs
*.log

# Temporary files
tmp
temp
*.tmp

# Backups
backups
*.bak

# Data
data

EOF
        print_success "Created .dockerignore file"
    fi
}

# Function to initialize development environment
init_dev_environment() {
    print_status "Initializing development environment..."

    # Pull base images to speed up first build
    print_status "Pulling base Docker images..."
    docker pull ubuntu:22.04
    docker pull node:20-alpine
    docker pull postgres:15-alpine
    docker pull redis:7-alpine

    # Build development containers
    print_status "Building development containers..."
    docker-compose -f $DOCKER_COMPOSE_FILE build

    # Start the environment
    print_status "Starting development environment..."
    docker-compose -f $DOCKER_COMPOSE_FILE up -d

    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30

    # Check service health
    print_status "Checking service health..."
    docker-compose -f $DOCKER_COMPOSE_FILE ps
}

# Function to display access information
display_access_info() {
    print_success "Development environment setup complete!"
    echo
    echo "🌐 Service Access Points:"
    echo "┌─────────────────────────────────────────────────────────┐"
    echo "│ Service               │ URL                             │"
    echo "├─────────────────────────────────────────────────────────┤"
    echo "│ Backend API           │ http://localhost:8000           │"
    echo "│ Frontend              │ http://localhost:3000           │"
    echo "│ Jupyter Lab           │ http://localhost:8888           │"
    echo "│ Database Admin        │ http://localhost:5050           │"
    echo "│ Redis Commander       │ http://localhost:8081           │"
    echo "│ Mongo Express         │ http://localhost:8082           │"
    echo "│ RabbitMQ Management   │ http://localhost:15672          │"
    echo "│ MinIO Console         │ http://localhost:9001           │"
    echo "│ Prometheus            │ http://localhost:9090           │"
    echo "│ Grafana               │ http://localhost:3000           │"
    echo "└─────────────────────────────────────────────────────────┘"
    echo
    echo "🚀 Quick Start Commands:"
    echo "  make dev-start    - Start development environment"
    echo "  make dev-stop     - Stop development environment"
    echo "  make dev-shell    - Open shell in backend container"
    echo "  make test         - Run tests"
    echo "  make lint         - Run code quality checks"
    echo "  make format       - Format code"
    echo "  make demo         - Run the advanced features demo"
    echo
    echo "📚 Documentation:"
    echo "  See README.md for detailed setup and usage instructions"
    echo "  Configuration files are in the config/ directory"
    echo "  Log files are stored in the logs/ directory"
    echo
    echo "🔧 VS Code Integration:"
    echo "  Open this folder in VS Code and select 'Reopen in Container'"
    echo "  All extensions and settings will be automatically configured"
    echo
    print_success "Happy coding! 🎉"
}

# Function to run setup wizard
run_setup_wizard() {
    echo "🚀 Vision Robotics Suite Development Environment Setup"
    echo "======================================================"
    echo

    # Check if already initialized
    if [[ -f ".dev-initialized" ]]; then
        print_warning "Development environment appears to be already initialized."
        read -p "Would you like to reinitialize? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_status "Skipping initialization. Use 'make dev-start' to start services."
            exit 0
        fi
    fi

    print_status "Starting setup wizard..."
    echo

    # Step 1: Check requirements
    if ! check_requirements; then
        print_error "System requirements not met. Please install missing dependencies."
        exit 1
    fi
    echo

    # Step 2: Create directories and files
    create_directories
    create_env_files
    create_config_files
    echo

    # Step 3: Initialize development environment
    init_dev_environment
    echo

    # Step 4: Mark as initialized
    touch .dev-initialized
    echo "$(date)" > .dev-initialized

    # Step 5: Display access information
    display_access_info
}

# Main execution
main() {
    # Change to script directory
    cd "$(dirname "${BASH_SOURCE[0]}")"

    # Parse command line arguments
    case "${1:-setup}" in
        "setup"|"init")
            run_setup_wizard
            ;;
        "requirements"|"check")
            check_requirements
            ;;
        "clean")
            print_status "Cleaning up development environment..."
            docker-compose -f $DOCKER_COMPOSE_FILE down -v --remove-orphans
            docker system prune -f
            rm -f .dev-initialized
            print_success "Development environment cleaned!"
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [command]"
            echo
            echo "Commands:"
            echo "  setup      - Run full development environment setup (default)"
            echo "  init       - Alias for setup"
            echo "  check      - Check system requirements only"
            echo "  clean      - Clean up development environment"
            echo "  help       - Show this help message"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use '$0 help' for available commands."
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
