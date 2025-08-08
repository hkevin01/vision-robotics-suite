# Universal Development Makefile
# Provides consistent commands across different project types and environments

.PHONY: help dev-start dev-stop dev-reset test lint format build deploy logs clean install

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m # No Color

# Project configuration
PROJECT_NAME := vision-robotics-suite
DOCKER_COMPOSE_FILE := docker-compose.dev.yml
BACKEND_SERVICE := backend-dev
FRONTEND_SERVICE := frontend-dev

# Help target - shows available commands
help: ## Show this help message
	@echo "$(BLUE)Vision Robotics Suite - Development Commands$(NC)"
	@echo "=================================================="
	@echo ""
	@echo "$(GREEN)Environment Management:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && /Environment Management/ {found=1; next} found && /^[a-zA-Z_-]+:.*?## / && !/Environment Management/ {found=0} found {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && /Development/ {found=1; next} found && /^[a-zA-Z_-]+:.*?## / && !/Development/ {found=0} found {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(GREEN)Code Quality:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && /Code Quality/ {found=1; next} found && /^[a-zA-Z_-]+:.*?## / && !/Code Quality/ {found=0} found {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(GREEN)Production:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && /Production/ {found=1; next} found && /^[a-zA-Z_-]+:.*?## / && !/Production/ {found=0} found {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Environment Management Commands

dev-start: ## Environment Management - Start all development containers
	@echo "$(BLUE)Starting development environment...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) up -d
	@echo "$(GREEN)Development environment started!$(NC)"
	@echo "$(YELLOW)Services available at:$(NC)"
	@echo "  Backend API: http://localhost:8000"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Database Admin: http://localhost:5050"
	@echo "  Redis Commander: http://localhost:8081"
	@echo "  Grafana: http://localhost:3000"

dev-stop: ## Environment Management - Stop all development containers
	@echo "$(BLUE)Stopping development environment...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) down
	@echo "$(GREEN)Development environment stopped!$(NC)"

dev-reset: ## Environment Management - Reset development environment (removes volumes)
	@echo "$(RED)Resetting development environment (this will remove all data)...$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo ""; \
		docker-compose -f $(DOCKER_COMPOSE_FILE) down -v --remove-orphans; \
		docker system prune -f; \
		echo "$(GREEN)Development environment reset complete!$(NC)"; \
	else \
		echo ""; \
		echo "$(YELLOW)Reset cancelled.$(NC)"; \
	fi

dev-shell: ## Environment Management - Open shell in backend development container
	@echo "$(BLUE)Opening shell in backend container...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) exec $(BACKEND_SERVICE) /bin/bash

dev-rebuild: ## Environment Management - Rebuild and restart development containers
	@echo "$(BLUE)Rebuilding development containers...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) down
	@docker-compose -f $(DOCKER_COMPOSE_FILE) build --no-cache
	@docker-compose -f $(DOCKER_COMPOSE_FILE) up -d
	@echo "$(GREEN)Development containers rebuilt and started!$(NC)"

# Development Commands

install: ## Development - Install project dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@if [ -f "pyproject.toml" ]; then \
		echo "Installing Python dependencies with Poetry..."; \
		poetry install --with dev,test; \
	elif [ -f "requirements.txt" ]; then \
		echo "Installing Python dependencies with pip..."; \
		pip install -r requirements.txt; \
		if [ -f "requirements-dev.txt" ]; then pip install -r requirements-dev.txt; fi; \
	fi
	@if [ -f "package.json" ]; then \
		echo "Installing Node.js dependencies..."; \
		npm install; \
	fi
	@echo "$(GREEN)Dependencies installed!$(NC)"

serve: ## Development - Start development server
	@echo "$(BLUE)Starting development server...$(NC)"
	@if [ -f "manage.py" ]; then \
		python manage.py runserver 0.0.0.0:8000; \
	elif [ -f "src/api/main.py" ]; then \
		uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000; \
	elif [ -f "app.py" ]; then \
		python app.py; \
	else \
		echo "$(RED)No recognized server file found$(NC)"; \
	fi

jupyter: ## Development - Start Jupyter Lab server
	@echo "$(BLUE)Starting Jupyter Lab...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) exec $(BACKEND_SERVICE) \
		jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token=''

demo: ## Development - Run the advanced features demonstration
	@echo "$(BLUE)Running advanced features demo...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) exec $(BACKEND_SERVICE) \
		python simple_demo.py

# Code Quality Commands

test: ## Code Quality - Run all tests
	@echo "$(BLUE)Running tests...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) exec $(BACKEND_SERVICE) \
		python -m pytest tests/ -v --tb=short

test-cov: ## Code Quality - Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) exec $(BACKEND_SERVICE) \
		python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

test-watch: ## Code Quality - Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) exec $(BACKEND_SERVICE) \
		python -m pytest-watch tests/

lint: ## Code Quality - Run all linting checks
	@echo "$(BLUE)Running linting checks...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) exec $(BACKEND_SERVICE) /bin/bash -c " \
		echo 'Running Black...'; \
		black --check --diff . || true; \
		echo 'Running isort...'; \
		isort --check-only --diff . || true; \
		echo 'Running flake8...'; \
		flake8 . || true; \
		echo 'Running mypy...'; \
		mypy src/ || true; \
		echo 'Running bandit...'; \
		bandit -r src/ || true; \
	"

format: ## Code Quality - Format all code
	@echo "$(BLUE)Formatting code...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) exec $(BACKEND_SERVICE) /bin/bash -c " \
		echo 'Running Black...'; \
		black .; \
		echo 'Running isort...'; \
		isort .; \
	"
	@echo "$(GREEN)Code formatting complete!$(NC)"

security: ## Code Quality - Run security scans
	@echo "$(BLUE)Running security scans...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) exec $(BACKEND_SERVICE) /bin/bash -c " \
		echo 'Running bandit...'; \
		bandit -r src/ || true; \
		echo 'Running safety...'; \
		safety check || true; \
	"

# Production Commands

build: ## Production - Build production containers
	@echo "$(BLUE)Building production containers...$(NC)"
	@docker build -t $(PROJECT_NAME):latest .
	@echo "$(GREEN)Production containers built!$(NC)"

deploy-staging: ## Production - Deploy to staging environment
	@echo "$(BLUE)Deploying to staging...$(NC)"
	@echo "$(YELLOW)Staging deployment not implemented yet$(NC)"

deploy-prod: ## Production - Deploy to production environment
	@echo "$(RED)Production deployment...$(NC)"
	@read -p "Are you sure you want to deploy to production? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo ""; \
		echo "$(YELLOW)Production deployment not implemented yet$(NC)"; \
	else \
		echo ""; \
		echo "$(YELLOW)Deployment cancelled.$(NC)"; \
	fi

# Utility Commands

logs: ## View logs from all services
	@echo "$(BLUE)Showing logs from all services...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) logs -f

logs-backend: ## View logs from backend service
	@docker-compose -f $(DOCKER_COMPOSE_FILE) logs -f $(BACKEND_SERVICE)

logs-frontend: ## View logs from frontend service
	@docker-compose -f $(DOCKER_COMPOSE_FILE) logs -f $(FRONTEND_SERVICE)

status: ## Show status of all services
	@echo "$(BLUE)Service Status:$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) ps

clean: ## Clean up Docker resources
	@echo "$(BLUE)Cleaning up Docker resources...$(NC)"
	@docker system prune -f
	@docker volume prune -f
	@echo "$(GREEN)Cleanup complete!$(NC)"

backup-db: ## Backup development database
	@echo "$(BLUE)Backing up development database...$(NC)"
	@mkdir -p backups
	@docker-compose -f $(DOCKER_COMPOSE_FILE) exec postgres \
		pg_dump -U developer vision_robotics > backups/vision_robotics_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Database backup complete!$(NC)"

restore-db: ## Restore development database from backup
	@echo "$(BLUE)Available backups:$(NC)"
	@ls -la backups/*.sql 2>/dev/null || echo "No backups found"
	@read -p "Enter backup filename: " backup_file; \
	if [ -f "backups/$$backup_file" ]; then \
		docker-compose -f $(DOCKER_COMPOSE_FILE) exec -T postgres \
			psql -U developer -d vision_robotics < "backups/$$backup_file"; \
		echo "$(GREEN)Database restored!$(NC)"; \
	else \
		echo "$(RED)Backup file not found!$(NC)"; \
	fi

# Environment-specific configurations
.env.local:
	@echo "$(BLUE)Creating local environment file...$(NC)"
	@cp .env.example .env.local || echo "No .env.example found"

# Database management
db-migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) exec $(BACKEND_SERVICE) \
		python manage.py migrate || echo "No Django migrations found"

db-shell: ## Open database shell
	@echo "$(BLUE)Opening database shell...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) exec postgres \
		psql -U developer vision_robotics

# Development workflow shortcuts
quick-test: ## Run quick test suite (unit tests only)
	@echo "$(BLUE)Running quick tests...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) exec $(BACKEND_SERVICE) \
		python -m pytest tests/unit/ -v --tb=short

full-test: ## Run complete test suite
	@echo "$(BLUE)Running full test suite...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) exec $(BACKEND_SERVICE) \
		python -m pytest tests/ -v --tb=short --cov=src

docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) exec $(BACKEND_SERVICE) \
		sphinx-build -b html docs/ docs/_build/html || echo "No Sphinx documentation found"
