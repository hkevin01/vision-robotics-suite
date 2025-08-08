#!/bin/bash
# Universal Docker Development Environment Validation Script
# This script validates that the complete containerized development environment works correctly

set -e

echo "🚀 Universal Docker Development Environment Validation"
echo "======================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a service is responding
check_service() {
    local service_name="$1"
    local url="$2"
    local expected_status="${3:-200}"

    print_status "Checking $service_name at $url..."

    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_status"; then
        print_success "$service_name is responding correctly"
        return 0
    else
        print_error "$service_name is not responding correctly"
        return 1
    fi
}

# Function to check Docker service health
check_docker_service() {
    local service_name="$1"
    print_status "Checking Docker service: $service_name"

    if docker-compose -f docker-compose.dev.yml ps "$service_name" | grep -q "Up"; then
        print_success "$service_name container is running"
        return 0
    else
        print_error "$service_name container is not running"
        return 1
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local service_name="$1"
    local url="$2"
    local max_attempts="${3:-30}"
    local attempt=1

    print_status "Waiting for $service_name to be ready (max ${max_attempts}s)..."

    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            print_success "$service_name is ready"
            return 0
        fi

        echo -n "."
        sleep 1
        attempt=$((attempt + 1))
    done

    print_error "$service_name failed to become ready within ${max_attempts} seconds"
    return 1
}

# Start validation
echo
print_status "Starting Universal Docker Development Environment validation..."

# Step 1: Check prerequisites
echo
print_status "Step 1: Checking prerequisites..."

if ! command_exists docker; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi
print_success "Docker is installed"

if ! command_exists docker-compose; then
    print_error "Docker Compose is not installed or not in PATH"
    exit 1
fi
print_success "Docker Compose is installed"

if ! command_exists make; then
    print_warning "Make is not installed - some convenience commands may not work"
else
    print_success "Make is installed"
fi

# Step 2: Check if Docker daemon is running
echo
print_status "Step 2: Checking Docker daemon..."

if ! docker info > /dev/null 2>&1; then
    print_error "Docker daemon is not running"
    exit 1
fi
print_success "Docker daemon is running"

# Step 3: Check if required files exist
echo
print_status "Step 3: Checking required configuration files..."

required_files=(
    "docker-compose.dev.yml"
    "docker/dev-backend.Dockerfile"
    "docker/dev-frontend.Dockerfile"
    "docker/dev-tools.Dockerfile"
    "Makefile"
    ".devcontainer/devcontainer.json"
    "scripts/dev-setup.sh"
    "scripts/db-init/01-init-postgres.sql"
    "config/redis.conf"
    "config/nginx.conf"
    "config/prometheus.yml"
    "config/grafana-datasources.yml"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "Found $file"
    else
        print_error "Missing required file: $file"
        exit 1
    fi
done

# Step 4: Check environment file
echo
print_status "Step 4: Checking environment configuration..."

if [ ! -f ".env" ]; then
    print_warning ".env file not found, creating from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Created .env from template"
    else
        print_error "No .env.example template found"
        exit 1
    fi
else
    print_success ".env file exists"
fi

# Step 5: Start the development environment
echo
print_status "Step 5: Starting development environment..."

print_status "Building and starting containers..."
if command_exists make; then
    make dev-start
else
    docker-compose -f docker-compose.dev.yml up -d --build
fi

# Step 6: Wait for services to be ready
echo
print_status "Step 6: Waiting for services to be ready..."

sleep 10  # Give containers time to start

# Check Docker services
services=(
    "postgres"
    "redis"
    "backend-dev"
    "nginx"
)

for service in "${services[@]}"; do
    check_docker_service "$service"
done

# Step 7: Test service endpoints
echo
print_status "Step 7: Testing service endpoints..."

# Wait for and test key services
service_tests=(
    "PostgreSQL:http://localhost:5432:Connection refused"
    "Redis:http://localhost:6379:Connection refused"
    "NGINX:http://localhost:80:200"
)

# Test direct service connections where applicable
print_status "Testing database connections..."

# Test PostgreSQL connection
if docker-compose -f docker-compose.dev.yml exec -T postgres pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    print_success "PostgreSQL is accepting connections"
else
    print_error "PostgreSQL is not accepting connections"
fi

# Test Redis connection
if docker-compose -f docker-compose.dev.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    print_success "Redis is responding to ping"
else
    print_error "Redis is not responding to ping"
fi

# Step 8: Test development container functionality
echo
print_status "Step 8: Testing development container functionality..."

# Test backend container
print_status "Testing backend development container..."
if docker-compose -f docker-compose.dev.yml exec -T backend-dev python3 --version > /dev/null 2>&1; then
    print_success "Python is available in backend container"
else
    print_error "Python is not available in backend container"
fi

if docker-compose -f docker-compose.dev.yml exec -T backend-dev node --version > /dev/null 2>&1; then
    print_success "Node.js is available in backend container"
else
    print_error "Node.js is not available in backend container"
fi

# Step 9: Test Make commands
echo
print_status "Step 9: Testing Make commands..."

if command_exists make; then
    print_status "Testing make status command..."
    if make status > /dev/null 2>&1; then
        print_success "Make status command works"
    else
        print_warning "Make status command failed"
    fi
else
    print_warning "Make not available, skipping command tests"
fi

# Step 10: Resource usage check
echo
print_status "Step 10: Checking resource usage..."

print_status "Docker container resource usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null || print_warning "Could not get container stats"

# Step 11: Network connectivity test
echo
print_status "Step 11: Testing network connectivity..."

# Test internal network connectivity
if docker-compose -f docker-compose.dev.yml exec -T backend-dev ping -c 1 postgres > /dev/null 2>&1; then
    print_success "Backend can reach PostgreSQL"
else
    print_error "Backend cannot reach PostgreSQL"
fi

if docker-compose -f docker-compose.dev.yml exec -T backend-dev ping -c 1 redis > /dev/null 2>&1; then
    print_success "Backend can reach Redis"
else
    print_error "Backend cannot reach Redis"
fi

# Step 12: Volume persistence test
echo
print_status "Step 12: Testing volume persistence..."

volumes=$(docker volume ls --format "{{.Name}}" | grep "vision-robotics-suite" | wc -l)
if [ "$volumes" -gt 0 ]; then
    print_success "Docker volumes are created ($volumes volumes found)"
else
    print_warning "No project-specific Docker volumes found"
fi

# Step 13: Configuration validation
echo
print_status "Step 13: Validating configurations..."

# Check if configuration files are being used
if docker-compose -f docker-compose.dev.yml exec -T redis redis-cli CONFIG GET save > /dev/null 2>&1; then
    print_success "Redis configuration is loaded"
else
    print_warning "Could not verify Redis configuration"
fi

# Final summary
echo
echo "======================================================"
print_status "Validation Summary"
echo "======================================================"

# Get container status
running_containers=$(docker-compose -f docker-compose.dev.yml ps --services --filter "status=running" | wc -l)
total_containers=$(docker-compose -f docker-compose.dev.yml ps --services | wc -l)

print_success "Environment Status: $running_containers/$total_containers containers running"

if [ "$running_containers" -eq "$total_containers" ]; then
    echo
    print_success "🎉 Universal Docker Development Environment validation completed successfully!"
    echo
    print_status "Your development environment is ready for use. You can now:"
    echo "  • Access services through the provided URLs"
    echo "  • Use 'make dev-shell' to open a development shell"
    echo "  • Use VS Code with the dev container configuration"
    echo "  • Run 'make' to see all available commands"
    echo
    print_status "Service URLs:"
    echo "  • Backend API: http://localhost:8000"
    echo "  • Frontend: http://localhost:3000"
    echo "  • Database Admin: http://localhost:5050"
    echo "  • Redis Commander: http://localhost:8081"
    echo "  • Monitoring: http://localhost:9090 (Prometheus), http://localhost:3001 (Grafana)"
    echo
else
    print_warning "Some containers are not running. Check logs with 'make logs' or 'docker-compose logs'"
fi

echo
print_status "Validation completed at $(date)"
echo "======================================================"
