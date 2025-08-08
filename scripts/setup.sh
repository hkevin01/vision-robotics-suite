#!/bin/bash

# Setup script for Vision Robotics Suite development environment
# This script sets up the complete development environment

set -e  # Exit on any error

echo "🔧 Setting up Vision Robotics Suite Development Environment"
echo "==========================================================="

# Check if Python 3.8+ is available
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Found Python $PYTHON_VERSION"

# Check if Poetry is installed
echo "📋 Checking Poetry installation..."
if ! command -v poetry &> /dev/null; then
    echo "📦 Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi
echo "✅ Poetry is available"

# Create virtual environment and install dependencies
echo "📦 Installing Python dependencies..."
poetry install --with dev,test,docs

# Install pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
poetry run pre-commit install

# Check if Docker is available (optional)
echo "📋 Checking Docker installation..."
if command -v docker &> /dev/null; then
    echo "✅ Docker is available"

    # Build development container
    echo "🐳 Building development container..."
    docker build -t vision-robotics-suite:dev .
else
    echo "⚠️  Docker not found - containerized development won't be available"
fi

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/models
mkdir -p data/calibration

mkdir -p assets/images
mkdir -p assets/models
mkdir -p assets/documentation

mkdir -p logs

# Set up configuration files
echo "⚙️  Setting up configuration..."
if [ ! -f .env ]; then
    cat > .env << EOF
# Vision Robotics Suite Environment Configuration

# Development settings
DEBUG=true
LOG_LEVEL=INFO

# Database settings (for development)
DATABASE_URL=postgresql://postgres:password@localhost:5432/vision_robotics_dev

# Industrial system connections (configure as needed)
# FANUC_ROBOT_IP=192.168.1.10
# SIEMENS_PLC_IP=192.168.1.5
# COGNEX_VISION_IP=192.168.1.20

# OPC UA settings
OPC_UA_ENDPOINT=opc.tcp://localhost:4840

# Security settings
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Monitoring and logging
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your-influxdb-token
INFLUXDB_ORG=vision-robotics-suite
INFLUXDB_BUCKET=automation-data
EOF
    echo "✅ Created .env configuration file"
fi

# Run tests to verify installation
echo "🧪 Running tests to verify installation..."
poetry run pytest tests/ -v --tb=short

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📚 Next steps:"
echo "  1. Activate the virtual environment: poetry shell"
echo "  2. Configure your industrial systems in .env file"
echo "  3. Review documentation: docs/README.md"
echo "  4. Start development: poetry run python -m src.main"
echo ""
echo "🔗 Useful commands:"
echo "  poetry run pytest              # Run tests"
echo "  poetry run black src tests     # Format code"
echo "  poetry run flake8 src tests    # Lint code"
echo "  poetry run mypy src            # Type checking"
echo "  poetry run pre-commit run --all-files  # Run all quality checks"
echo ""
echo "📖 Documentation will be available at: http://localhost:8000 (after building)"
echo "🌐 Web interface will be available at: http://localhost:8080 (when running)"
