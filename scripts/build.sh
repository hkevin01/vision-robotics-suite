#!/bin/bash

# Build script for Vision Robotics Suite
# Builds all components and prepares for deployment

set -e

echo "🏗️  Building Vision Robotics Suite"
echo "=================================="

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/

# Install dependencies
echo "📦 Installing dependencies..."
poetry install --with dev,test,docs

# Format and lint code
echo "✨ Formatting code..."
poetry run black src tests scripts
poetry run isort src tests

echo "🔍 Linting code..."
poetry run flake8 src tests
poetry run mypy src

# Run security checks
echo "🔒 Running security checks..."
poetry run bandit -r src

# Run tests
echo "🧪 Running tests..."
poetry run pytest tests/ --cov=src --cov-report=xml --cov-report=html

# Build documentation
echo "📚 Building documentation..."
cd docs
make clean
make html
cd ..

# Build Python package
echo "📦 Building Python package..."
poetry build

# Build Docker images
if command -v docker &> /dev/null; then
    echo "🐳 Building Docker images..."

    # Build production image
    docker build -t vision-robotics-suite:latest .

    # Build development image
    docker build -f Dockerfile.dev -t vision-robotics-suite:dev .

    echo "✅ Docker images built successfully"
else
    echo "⚠️  Docker not available - skipping container builds"
fi

# Generate deployment artifacts
echo "📋 Generating deployment artifacts..."
mkdir -p build/deploy

# Copy built packages
cp dist/*.whl build/deploy/
cp dist/*.tar.gz build/deploy/

# Copy configuration templates
cp -r configs/ build/deploy/configs/
cp docker-compose.yml build/deploy/
cp scripts/deploy.sh build/deploy/

# Create deployment documentation
cat > build/deploy/README.md << EOF
# Vision Robotics Suite Deployment

This directory contains all artifacts needed to deploy the Vision Robotics Suite.

## Contents

- \`*.whl\`: Python wheel package
- \`*.tar.gz\`: Source distribution
- \`configs/\`: Configuration templates
- \`docker-compose.yml\`: Container orchestration
- \`deploy.sh\`: Deployment script

## Quick Deployment

1. Configure your environment:
   \`\`\`bash
   cp configs/env.template .env
   # Edit .env with your settings
   \`\`\`

2. Deploy with Docker:
   \`\`\`bash
   docker-compose up -d
   \`\`\`

3. Or deploy with Python:
   \`\`\`bash
   pip install *.whl
   ./deploy.sh
   \`\`\`

## Documentation

See docs/deployment.md for detailed deployment instructions.
EOF

echo ""
echo "✅ Build completed successfully!"
echo ""
echo "📁 Build artifacts:"
echo "  - Python packages: dist/"
echo "  - Documentation: docs/_build/html/"
echo "  - Test coverage: htmlcov/"
echo "  - Deployment package: build/deploy/"
echo ""
echo "🚀 Ready for deployment!"
