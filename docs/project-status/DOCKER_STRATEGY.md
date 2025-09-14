# Universal Docker Development Strategy - Documentation

## Overview

This Universal Docker Development Strategy provides a comprehensive containerized development environment that eliminates dependency conflicts and ensures consistent development across all team members. The strategy supports multiple programming languages, databases, and development tools while maintaining production-ready deployment capabilities.

## Architecture

### Development Containers

1. **Backend Development Container** (`docker/dev-backend.Dockerfile`)
   - Multi-language support (Python, Node.js, Go, Rust)
   - Development tools and package managers
   - Database clients and testing frameworks
   - Hot reload capabilities

2. **Frontend Development Container** (`docker/dev-frontend.Dockerfile`)
   - Node.js with multiple package managers
   - Frontend frameworks and build tools
   - Browser testing tools
   - Live reloading capabilities

3. **Development Tools Container** (`docker/dev-tools.Dockerfile`)
   - Code quality and security tools
   - Linting, formatting, and testing utilities
   - Documentation generation tools

### Infrastructure Services

- **PostgreSQL**: Primary relational database with extensions
- **MySQL**: Alternative relational database
- **Redis**: Caching and session storage
- **MongoDB**: Document database
- **Elasticsearch**: Search capabilities
- **RabbitMQ**: Message queuing
- **MinIO**: S3-compatible object storage
- **NGINX**: Reverse proxy and load balancing
- **Prometheus + Grafana**: Monitoring and visualization

### Management Tools

- **pgAdmin**: PostgreSQL administration
- **phpMyAdmin**: MySQL administration
- **Redis Commander**: Redis management
- **Mongo Express**: MongoDB management

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM and 10GB free disk space

### Setup Commands

```bash
# Clone the repository
git clone <repository-url>
cd vision-robotics-suite

# Run the setup script
bash scripts/dev-setup.sh

# Or use Make commands
make dev-start    # Start development environment
make dev-shell    # Open shell in backend container
```

### Using VS Code Dev Containers

1. Open the project in VS Code
2. Install the "Remote - Containers" extension
3. Press F1 and select "Remote-Containers: Reopen in Container"
4. Wait for the container to build and start

## Available Commands

### Environment Management

```bash
make dev-start      # Start all development containers
make dev-stop       # Stop all development containers
make dev-reset      # Reset environment (removes volumes)
make dev-shell      # Open shell in backend container
make dev-rebuild    # Rebuild and restart containers
```

### Development

```bash
make install        # Install project dependencies
make serve          # Start development server
make jupyter        # Start Jupyter Lab server
make demo          # Run advanced features demonstration
```

### Code Quality

```bash
make test          # Run all tests
make test-cov      # Run tests with coverage
make lint          # Run linting checks
make format        # Format code
make security      # Run security scans
```

### Production

```bash
make build         # Build production containers
make deploy-staging # Deploy to staging
make deploy-prod   # Deploy to production
```

### Utilities

```bash
make logs          # View logs from all services
make status        # Show service status
make clean         # Clean up Docker resources
make backup-db     # Backup development database
make restore-db    # Restore database from backup
```

## Service Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Backend API | <http://localhost:8000> | Main application API |
| Frontend | <http://localhost:3000> | Development frontend |
| Jupyter Lab | <http://localhost:8888> | Interactive notebooks |
| Database Admin | <http://localhost:5050> | pgAdmin interface |
| Redis Commander | <http://localhost:8081> | Redis management |
| Mongo Express | <http://localhost:8082> | MongoDB management |
| RabbitMQ Management | <http://localhost:15672> | Message queue admin |
| MinIO Console | <http://localhost:9001> | Object storage admin |
| Prometheus | <http://localhost:9090> | Metrics collection |
| Grafana | <http://localhost:3000> | Metrics visualization |

## Configuration

### Environment Variables

Environment variables are managed through `.env` files:

- `.env` - Main environment configuration
- `.env.example` - Template for team sharing
- `.env.local` - Local overrides (gitignored)

### Database Configuration

Default credentials for development:

- PostgreSQL: `developer` / `devpass123`
- MySQL: `developer` / `devpass123`
- MongoDB: `admin` / `adminpass123`
- Redis: No password (development only)

### Volume Persistence

The following volumes are created for data persistence:

- Database data volumes
- Cache volumes for package managers
- Log and backup volumes

## Development Workflow

### 1. Starting Development

```bash
# Start the environment
make dev-start

# Install dependencies
make install

# Open shell for development
make dev-shell
```

### 2. Code Development

- Use VS Code with the dev container for the best experience
- All extensions and settings are preconfigured
- Debugger configurations are available for multiple languages

### 3. Testing and Quality

```bash
# Run tests frequently
make test

# Check code quality
make lint

# Format code before committing
make format
```

### 4. Database Management

```bash
# Run migrations
make db-migrate

# Access database shell
make db-shell

# Backup data
make backup-db
```

## Production Deployment

### Building Production Images

```bash
# Build optimized production containers
make build

# Or build specific services
docker build -t vision-robotics-suite:latest .
```

### Production Configuration

- Multi-stage builds for minimal image size
- Non-root user configuration
- Security scanning integration
- Health checks and monitoring

### Deployment Options

- Docker Swarm
- Kubernetes with Helm charts
- Cloud container services
- Traditional VPS deployment

## Security Considerations

### Development Security

- Isolated container environments
- Separate networks for different services
- Default credentials only for development
- Volume permissions properly configured

### Production Security

- Distroless or minimal base images
- Non-root container execution
- Security scanning in CI/CD
- Encrypted secrets management
- Network policies and firewalls

## Troubleshooting

### Common Issues

1. **Port conflicts**: Check if ports are already in use
2. **Permission errors**: Ensure Docker daemon is running
3. **Out of disk space**: Clean up with `make clean`
4. **Container build failures**: Check Docker resource limits

### Debug Commands

```bash
# Check container status
make status

# View logs
make logs

# Check resource usage
docker stats

# Inspect networks
docker network ls
```

### Reset Environment

```bash
# Complete reset (removes all data)
make dev-reset

# Or manual cleanup
docker-compose -f docker-compose.dev.yml down -v
docker system prune -f
```

## Team Collaboration

### Onboarding New Developers

1. Share the repository with `.env.example`
2. Run `bash scripts/dev-setup.sh`
3. Start coding immediately with `make dev-start`

### Consistent Development Environment

- All dependencies containerized
- Version-controlled configuration
- Automated setup scripts
- Shared database schemas and test data

### Code Quality Standards

- Pre-commit hooks for code formatting
- Automated testing in containers
- Security scanning integration
- Documentation generation

## Benefits

### For Developers

- **No local dependencies**: Everything runs in containers
- **Consistent environment**: Same setup across all machines
- **Easy onboarding**: One command setup
- **Isolated development**: No conflicts between projects
- **Production parity**: Development matches production

### For Teams

- **Standardized workflows**: Consistent development practices
- **Reduced debugging**: "Works on my machine" eliminated
- **Easy collaboration**: Shared environment configuration
- **Faster onboarding**: New team members productive immediately
- **Simplified CI/CD**: Same containers in all environments

### For Operations

- **Production-ready**: Same containers from dev to prod
- **Scalable architecture**: Easy to scale individual services
- **Monitoring ready**: Built-in metrics and logging
- **Security first**: Best practices baked in
- **Infrastructure as code**: Everything version controlled

## Advanced Features

### Multi-Language Projects

The development environment supports:

- Python with Poetry, pip, or pipenv
- Node.js with npm, yarn, or pnpm
- Go with modules
- Rust with Cargo
- Java with Maven or Gradle

### Database Migration

- Automated schema initialization
- Sample data seeding
- Migration scripts for all databases
- Cross-database compatibility

### Testing Infrastructure

- Unit testing frameworks
- Integration testing with real databases
- End-to-end testing with Selenium/Playwright
- Performance testing with Artillery/k6
- Code coverage reporting

### Monitoring and Observability

- Application metrics with Prometheus
- Log aggregation and analysis
- Performance monitoring
- Health check endpoints
- Alerting and notification setup

This Universal Docker Development Strategy provides a complete, production-ready development environment that scales from individual developers to large teams while maintaining consistency, security, and performance.
