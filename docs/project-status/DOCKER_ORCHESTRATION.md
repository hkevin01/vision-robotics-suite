# Vision Robotics Suite - Docker Orchestration

## Overview

The Vision Robotics Suite now features complete Docker orchestration with automatic GUI generation and comprehensive container management. This deployment system provides a production-ready, containerized solution for the entire platform.

## Quick Start

### 1. Prerequisites
- Docker Engine 20.10+ with BuildKit support
- Docker Compose v2.0+ (or docker-compose 1.27+)
- 4GB+ available RAM
- 10GB+ available disk space

### 2. Launch the Complete System
```bash
# Make the orchestration script executable and start everything
chmod +x run.sh
./run.sh up
```

This single command will:
- Detect if GUI exists (creates one if missing)
- Build all container images
- Start the complete infrastructure
- Display access URLs

### 3. Access the Platform
- **GUI Dashboard**: http://localhost:3000
- **API Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Architecture

### Services
1. **API Backend** (`api`)
   - FastAPI-based Python application
   - Port 8000 (configurable)
   - Handles all vision/robotics operations
   - RESTful API with automatic documentation

2. **GUI Frontend** (`gui`)
   - Responsive web dashboard
   - Port 3000 (configurable)
   - Real-time system monitoring
   - Interactive demo controls

### Container Images
- `vision-robotics-api:local` - Backend API server
- `vision-robotics-gui:local` - Frontend web interface

## Command Reference

### Core Commands
```bash
./run.sh help          # Show all available commands
./run.sh up             # Start all services
./run.sh down           # Stop and remove containers
./run.sh restart        # Restart all services
./run.sh status         # Show detailed system status
```

### Development Commands
```bash
./run.sh build          # Build container images
./run.sh logs [service] # Show logs (default: api)
./run.sh shell          # Open shell in API container
./run.sh exec "command" # Execute command in API container
```

### GUI Management
```bash
./run.sh gui:create     # Create GUI scaffold
./run.sh gui:create --force  # Force recreate GUI
./run.sh gui:open       # Open GUI in browser
```

### Maintenance Commands
```bash
./run.sh ps             # Show container status
./run.sh clean          # Remove containers and images
./run.sh prune          # Clean up Docker system
```

## Configuration

### Environment Variables
Create or modify `.env` file for custom configuration:

```bash
# Backend Configuration
API_HOST=0.0.0.0
API_PORT=8000
PORTS=8000:8000

# GUI Configuration
GUI_PORT=3000
API_URL=http://localhost:8000

# Container Configuration
IMAGE_NAME=vision-robotics-api:local
GUI_IMAGE_NAME=vision-robotics-gui:local
SERVICE_NAME=api
GUI_SERVICE_NAME=gui

# Development Options
DEV_MODE=false
LOG_LEVEL=INFO
```

### Advanced Configuration
```bash
# Custom volume mounts
MOUNTS="./data:/app/data,./config:/app/config"

# Docker build arguments
BUILD_ARGS="--build-arg PYTHON_VERSION=3.10"

# Target platform
DOCKER_PLATFORM=linux/amd64
```

## GUI Features

### Automatically Generated Dashboard
When no GUI exists, the system creates a professional, responsive web interface with:

- **Real-time System Status** - API, vision systems, and robot status indicators
- **Interactive Controls** - Run demos, health checks, and system operations
- **Live Logging** - Real-time system logs with filtering and clearing
- **Responsive Design** - Works on desktop, tablet, and mobile devices
- **System Integration** - Direct API communication and automatic discovery

### Demo Capabilities
- Complete system demonstrations
- Individual vision system demos (paint inspection, 3D registration, safety zones)
- Robot system testing
- Health monitoring and diagnostics

## Development Workflow

### 1. Start Development Environment
```bash
./run.sh up
```

### 2. View Logs During Development
```bash
# Follow API logs
./run.sh logs api

# Follow GUI logs
./run.sh logs gui
```

### 3. Execute Commands in Container
```bash
# Run tests
./run.sh exec "pytest tests/"

# Install new packages
./run.sh exec "pip install package-name"

# Open interactive shell
./run.sh shell
```

### 4. Rebuild After Changes
```bash
# Rebuild and restart
./run.sh build
./run.sh restart
```

## Production Deployment

### 1. Environment Setup
```bash
# Set production environment
export DEV_MODE=false
export API_URL=https://your-domain.com

# Configure secure origins in docker-compose.yml
# Update CORS settings in src/api/main.py
```

### 2. Security Considerations
- Change default ports if needed
- Configure proper CORS origins
- Set up reverse proxy (nginx/traefik)
- Enable HTTPS/TLS termination
- Configure container resource limits

### 3. Monitoring
```bash
# Check system health
./run.sh status

# Monitor resource usage
docker stats

# Check logs
./run.sh logs
```

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using the port
sudo lsof -i :8000
sudo lsof -i :3000

# Change ports in .env
echo "PORTS=8001:8000" >> .env
echo "GUI_PORT=3001" >> .env
```

#### Container Build Failures
```bash
# Clean Docker cache
./run.sh prune

# Force rebuild
./run.sh clean
./run.sh build
```

#### GUI Not Loading
```bash
# Check GUI service status
./run.sh ps

# Recreate GUI
./run.sh gui:create --force
./run.sh restart
```

### Logs and Debugging
```bash
# View detailed container logs
./run.sh logs api
./run.sh logs gui

# Check Docker system
docker system df
docker system events

# Container inspection
docker inspect vision-robotics-api-container
docker inspect vision-robotics-gui-container
```

## API Integration

### Health Endpoints
- `GET /health` - System health check
- `GET /api/info` - Detailed system information

### Vision System Endpoints
- `GET /api/vision/status` - Vision systems status
- `POST /api/vision/{system}/run` - Run specific vision system

### Robot System Endpoints
- `GET /api/robots/status` - Robot systems status
- `POST /api/robots/{system}/run` - Run specific robot system

### Demo Endpoints
- `POST /api/demo/run` - Run complete system demo
- `POST /api/demo/vision/{type}` - Run specific vision demo

## File Structure

```
vision-robotics-suite/
├── run.sh                 # Main orchestration script
├── docker-compose.yml     # Container orchestration
├── Dockerfile            # Backend container definition
├── .env                  # Environment configuration
├── gui/                  # Auto-generated GUI
│   ├── Dockerfile        # GUI container definition
│   ├── index.html        # Main web interface
│   ├── app.js           # Frontend application logic
│   ├── styles.css       # Responsive styling
│   └── config.json      # GUI configuration
├── src/                  # Application source code
│   └── api/
│       └── main.py      # FastAPI backend
└── logs/                 # Application logs
```

## License

This Docker orchestration system is part of the Vision Robotics Suite and follows the same MIT license terms.
