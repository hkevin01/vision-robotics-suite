# 🤖 Vision Robotics Suite

*A Comprehensive Industrial Automation Platform*

[![Tests](https://github.com/hkevin01/vision-robotics-suite/workflows/Tests/badge.svg)](https://github.com/hkevin01/vision-robotics-suite/actions)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://docker.com)

> **A production-ready industrial automation platform demonstrating seamless integration between machine vision systems, collaborative robots, PLCs, and quality control systems for Industry 4.0 manufacturing environments.**

## 🎯 Project Purpose & Vision

The Vision Robotics Suite addresses the critical need for **integrated, intelligent manufacturing systems** that combine:

- **Machine Vision** for real-time quality inspection and guidance
- **Collaborative Robotics** for flexible, human-safe automation
- **Industrial Communication** via OPC-UA, Modbus, and proprietary protocols
- **Quality Systems** compliant with IATF 16949 and aerospace standards
- **SCADA/HMI** for centralized monitoring and control
- **Digital Twin Simulation** for predictive maintenance and optimization

### Why This Platform Exists

Modern manufacturing demands **smart, connected systems** that can:

- ✅ Adapt to changing production requirements in real-time
- ✅ Ensure consistent quality through automated inspection
- ✅ Enable human-robot collaboration with safety guarantees
- ✅ Provide full traceability for regulatory compliance
- ✅ Integrate legacy equipment with modern IoT infrastructure
- ✅ Support predictive maintenance and continuous improvement

## �️ System Architecture

### High-Level Architecture Overview

```mermaid
graph TD
    %% User Interface Layer (Top)
    subgraph "🖥️ User Interface Layer"
        GUI[Web GUI Dashboard]
        WEB[Web Dashboard]
        IGNITION[Ignition HMI]
        LOGGING[Data Logging & Reports]
    end

    %% Application Programming Interface (Core)
    subgraph "🚀 API Integration Layer"
        API[FastAPI Backend<br/>WebSocket Support]
        AUTH[Authentication & Security]
        QUEUE[Message Queue & Events]
    end

    %% Parallel Processing Layers
    subgraph "👁️ Vision Systems"
        direction TB
        VS[Vision Controller]
        CAM[Camera Calibration]
        HALCON[HALCON Algorithms]
        COGNEX[Cognex Integration]
        PHOTONEO[Photoneo 3D Scanner]
    end

    subgraph "🤖 Robot Programming"
        direction TB
        RP[Robot Controller]
        UR[Universal Robots]
        FANUC[FANUC Integration]
        ABB[ABB Robotics]
        COLLISION[Collision Avoidance]
    end

    subgraph "🔌 Industrial Communication"
        direction TB
        PLC[PLC Gateway]
        OPCUA[OPC-UA Server]
        MODBUS[Modbus TCP/RTU]
        ROCKWELL[Rockwell RSLogix]
        SIEMENS[Siemens TIA Portal]
    end

    subgraph "✅ Quality Control"
        direction TB
        QC[Quality Manager]
        IATF[IATF 16949 Compliance]
        SPC[SPC Analysis Engine]
        VDA[VDA 6.3 Auditing]
    end

    subgraph "🎮 Simulation & Digital Twin"
        direction TB
        SIM[Simulation Engine]
        TWIN[Digital Twin Model]
        EMULATE[Emulate3D Integration]
        ROBODK[RoboDK Virtual Cell]
    end

    %% Data Storage Layer
    subgraph "💾 Data Storage Layer"
        direction LR
        DB[(PostgreSQL<br/>Relational Data)]
        TSDB[(InfluxDB<br/>Time Series)]
        CACHE[(Redis<br/>Cache & Sessions)]
    end

    %% Connections - Top Down Flow
    GUI --> API
    WEB --> API
    IGNITION --> API
    LOGGING --> API

    API --> AUTH
    API --> QUEUE

    %% Core systems to API
    VS --> API
    RP --> API
    PLC --> API
    QC --> API
    SIM --> API

    %% API to Data Layer
    API --> DB
    API --> TSDB
    API --> CACHE

    %% Internal system connections
    VS --> CAM
    VS --> HALCON
    VS --> COGNEX
    VS --> PHOTONEO

    RP --> UR
    RP --> FANUC
    RP --> ABB
    RP --> COLLISION

    PLC --> OPCUA
    PLC --> MODBUS
    PLC --> ROCKWELL
    PLC --> SIEMENS

    QC --> IATF
    QC --> SPC
    QC --> VDA

    SIM --> TWIN
    SIM --> EMULATE
    SIM --> ROBODK

    %% Cross-system integration
    VS -.-> QC
    RP -.-> VS
    PLC -.-> RP
    SIM -.-> VS
    SIM -.-> RP

    classDef userLayer fill:#e1f5fe
    classDef apiLayer fill:#f3e5f5
    classDef systemLayer fill:#e8f5e8
    classDef dataLayer fill:#fff3e0

    class GUI,WEB,IGNITION,LOGGING userLayer
    class API,AUTH,QUEUE apiLayer
    class VS,RP,PLC,QC,SIM,CAM,HALCON,COGNEX,PHOTONEO,UR,FANUC,ABB,COLLISION,OPCUA,MODBUS,ROCKWELL,SIEMENS,IATF,SPC,VDA,TWIN,EMULATE,ROBODK systemLayer
    class DB,TSDB,CACHE dataLayer
```

### Technology Stack & Component Selection

| Layer | Technology | Purpose | Why Chosen |
|-------|------------|---------|------------|
| **Vision Processing** | HALCON, OpenCV, Cognex | Image analysis, quality inspection | Industry-standard machine vision libraries with proven reliability |
| **Robot Control** | Universal Robots SDK, FANUC APIs | Robot programming and coordination | Native manufacturer APIs for real-time control |
| **Industrial Communication** | OPC-UA, Modbus, pycomm3 | PLC and device connectivity | Open standards ensuring interoperability |
| **Web Framework** | FastAPI, WebSockets | Real-time API and WebSocket support | High-performance async framework with automatic documentation |
| **Database** | PostgreSQL, InfluxDB | Relational and time-series data | Enterprise-grade reliability with time-series optimization |
| **Frontend** | HTML5, CSS3, JavaScript | Responsive web interface | Universal browser compatibility with real-time updates |
| **Containerization** | Docker, Docker Compose | Deployment and scaling | Consistent deployment across environments |
| **Quality Assurance** | pytest, mypy, black | Code quality and testing | Industry best practices for Python development |

## 📊 What's Actually Here

This repository contains a comprehensive industrial automation platform with:

### Core Systems Implementation

- **🤖 Vision Systems Architecture**: Production-ready base classes and interfaces for machine vision
- **🦾 Multi-Vendor Robot Integration**: Universal Robots, FANUC, ABB, and Yaskawa robot control
- **🔌 Industrial Communication**: OPC-UA, Modbus, Rockwell, and Siemens PLC integration
- **✅ Quality Management Systems**: IATF 16949, SPC analysis, and VDA 6.3 compliance
- **📊 SCADA/HMI Interface**: Web-based monitoring with real-time data visualization
- **🎮 Digital Twin Simulation**: Emulate3D and RoboDK integration for virtual commissioning

### Application-Specific Modules

- **🎨 Automotive Paint Inspection**: Surface defect detection and color matching algorithms
- **🏗️ Body-in-White Inspection**: Dimensional accuracy and gap/flush measurements
- **🔋 Battery Pack Quality Control**: Cell alignment and connection integrity verification
- **⚙️ Engine Timing Chain Verification**: Precision timing analysis and wear detection
- **🚗 Adaptive Lighting Control**: Dynamic lighting adjustment for optimal vision conditions

## 📁 Project Structure

```text
vision-robotics-suite/
├── src/vision_systems/           # Vision system modules
│   ├── automotive_paint_inspection.py
│   ├── body_in_white_inspection.py
│   ├── battery_pack_quality_control.py
│   ├── engine_timing_chain_verification.py
│   └── base.py                   # Base classes
├── docker/                       # Development containers
├── tests/                        # Test modules
├── scripts/                      # Setup and utility scripts
└── README.md
```

## 🚀 Quick Start Guide

### Prerequisites

- **Python 3.8+** with Poetry package manager
- **Docker & Docker Compose** for containerized deployment
- **Git** for version control

### Installation

1. **Clone the repository:**

```bash
git clone https://github.com/hkevin01/vision-robotics-suite.git
cd vision-robotics-suite
```

2. **Install dependencies:**

```bash
# Using Poetry (recommended)
poetry install --all-extras

# Or using pip
pip install -e .
```

3. **Start the development environment:**

```bash
# Quick start with Docker
./run.sh

# Or manually with Docker Compose
docker-compose up -d
```

4. **Access the web interface:**

- **Main Dashboard**: <http://localhost:8080>
- **API Documentation**: <http://localhost:8000/docs>
- **Grafana Monitoring**: <http://localhost:3000>

### Running Tests

```bash
# Run all tests
poetry run pytest -v

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test categories
poetry run pytest -m unit        # Unit tests only
poetry run pytest -m integration # Integration tests only
```

### Configuration

Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/vision_robotics
INFLUXDB_URL=http://localhost:8086

# Robot Configuration
UR_ROBOT_IP=192.168.1.100
FANUC_ROBOT_IP=192.168.1.101

# Vision System Configuration
HALCON_LICENSE_FILE=/opt/halcon/license.dat
COGNEX_VISIONPRO_PATH=/opt/cognex/visionpro

# Security
SECRET_KEY=your-secret-key-here
API_KEY=your-api-key-here
```

## 🔧 Implementation Details

The codebase includes:

### Simulation Modules

- **Paint Inspection**: Defect detection algorithms with OpenCV (HALCON integration uses mock for development)
- **Body-in-White**: 360° inspection simulation with pass/fail logic
- **Timing Chain Verification**: Engine assembly verification with traceability
- **Battery Pack QC**: Thermal analysis and dimensional verification simulation

### Development Infrastructure

- **Multi-language Docker containers**: Python 3.10, Node.js LTS, Go 1.21.5, Rust
- **Code quality pipeline**: Black formatting, flake8 linting, mypy type checking
- **Testing framework**: pytest with coverage reporting

## 💡 Usage Example

```python
from src.vision_systems.automotive_paint_inspection import (
    AutomotivePaintInspector,
    InspectionParameters
)

# Initialize paint inspector with simulation
params = InspectionParameters()
inspector = AutomotivePaintInspector(params)

# Run inspection (uses mock HALCON for demo)
result = inspector.inspect_paint_surface("sample.jpg")
print(f"Defects found: {len(result.get('defects', []))}")
```

## 🛠️ Development Commands

```bash
# Code quality
poetry run black src tests       # Format code
poetry run flake8 src tests      # Lint
poetry run mypy src              # Type check
poetry run pytest               # Run tests

# Docker development
make dev-start                   # Start containers
make dev-stop                    # Stop containers
make dev-shell                   # Enter development shell
```

## 📄 License

MIT License

## ⚠️ Important Notes

- **Simulation Only**: This is a demonstration codebase with simulated data
- **Mock Integrations**: HALCON, Cognex, and robot SDK integrations use mock implementations
- **Educational Purpose**: Designed to show software architecture patterns, not production industrial systems
- **No Real Hardware**: Does not connect to actual cameras, PLCs, or robots

---

*A Python codebase exploring industrial automation software patterns.*
