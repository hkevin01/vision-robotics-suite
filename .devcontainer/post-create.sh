#!/bin/bash
# Post-create script for development container setup

set -e

echo "🚀 Setting up Vision Robotics Suite development environment..."

# Create necessary directories
mkdir -p /home/developer/.local/bin
mkdir -p /home/developer/workspace/.vscode
mkdir -p /home/developer/workspace/logs
mkdir -p /home/developer/workspace/data

# Set up Python environment
echo "🐍 Setting up Python environment..."
if [ -f "pyproject.toml" ]; then
    echo "Installing Poetry dependencies..."
    poetry install --with dev,test
elif [ -f "requirements.txt" ]; then
    echo "Installing pip requirements..."
    pip install -r requirements.txt
    if [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
    fi
fi

# Set up Node.js environment
echo "📦 Setting up Node.js environment..."
if [ -f "package.json" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

# Set up pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
if [ -f ".pre-commit-config.yaml" ]; then
    pre-commit install
    pre-commit install --hook-type commit-msg
fi

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    echo "📝 Initializing git repository..."
    git init
    git config --global user.name "Developer"
    git config --global user.email "developer@vision-robotics.local"
fi

# Set up shell aliases and functions
echo "⚡ Setting up shell configuration..."
cat >> /home/developer/.bashrc << 'EOF'

# Vision Robotics Suite aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias ..='cd ..'
alias ...='cd ../..'

# Development shortcuts
alias dps='docker ps'
alias dlog='docker logs'
alias dexec='docker exec -it'
alias dc='docker-compose'
alias dcup='docker-compose up'
alias dcdown='docker-compose down'
alias dcbuild='docker-compose build'

# Python shortcuts
alias py='python3'
alias pip='pip3'
alias pytest='python -m pytest'
alias black='python -m black'
alias isort='python -m isort'
alias flake8='python -m flake8'

# Testing shortcuts
alias test='make test'
alias lint='make lint'
alias format='make format'

# Project shortcuts
alias logs='tail -f logs/*.log'
alias serve='python -m http.server 8000'

# Function to quickly start Jupyter
jupyter-start() {
    jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token=''
}

# Function to run tests with coverage
test-cov() {
    pytest --cov=src --cov-report=html --cov-report=term-missing
}

# Function to check code quality
check() {
    echo "Running code quality checks..."
    black --check .
    isort --check-only .
    flake8 .
    mypy src/
    bandit -r src/
}

# Function to format code
format() {
    echo "Formatting code..."
    black .
    isort .
}

EOF

# Make sure the user owns the workspace
sudo chown -R developer:developer /home/developer/workspace || true

# Set up VS Code workspace settings
echo "📝 Setting up VS Code workspace..."
cat > /home/developer/workspace/.vscode/settings.json << 'EOF'
{
    "python.defaultInterpreterPath": "/usr/bin/python3",
    "python.terminal.activateEnvironment": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "editor.rulers": [79, 88, 120],
    "files.trimTrailingWhitespace": true,
    "files.insertFinalNewline": true,
    "terminal.integrated.defaultProfile.linux": "bash"
}
EOF

# Create launch.json for debugging
cat > /home/developer/workspace/.vscode/launch.json << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "src.api.main:app",
                "--reload",
                "--host",
                "0.0.0.0",
                "--port",
                "8000"
            ],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Python: Django",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/manage.py",
            "args": [
                "runserver",
                "0.0.0.0:8000"
            ],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Python: Pytest Current File",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": [
                "${file}",
                "-v"
            ],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
EOF

# Create tasks.json for common tasks
cat > /home/developer/workspace/.vscode/tasks.json << 'EOF'
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run Tests",
            "type": "shell",
            "command": "make test",
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "Lint Code",
            "type": "shell",
            "command": "make lint",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "Format Code",
            "type": "shell",
            "command": "make format",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "Start Backend",
            "type": "shell",
            "command": "python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "Start Jupyter",
            "type": "shell",
            "command": "jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        }
    ]
}
EOF

echo "✅ Development environment setup complete!"
echo "📚 Available commands:"
echo "  - make dev-start: Start development environment"
echo "  - make test: Run tests"
echo "  - make lint: Run linting"
echo "  - make format: Format code"
echo "  - jupyter-start: Start Jupyter Lab"
echo "  - test-cov: Run tests with coverage"
echo ""
echo "🌐 Access points:"
echo "  - Backend API: http://localhost:8000"
echo "  - Frontend: http://localhost:3000"
echo "  - Jupyter Lab: http://localhost:8888"
echo "  - Database Admin: http://localhost:5050 (pgAdmin)"
echo "  - Redis Commander: http://localhost:8081"
echo ""
echo "Happy coding! 🚀"
