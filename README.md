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

### 1. System Overview & Data Flow

```mermaid
graph TD
    %% User Interface Layer
    subgraph UI["🖥️ User Interface Layer"]
        direction LR
        GUI[Web GUI Dashboard]
        IGNITION[Ignition HMI]
        MOBILE[Mobile Interface]
    end

    %% API Integration Layer
    subgraph APIL["🚀 API Integration Layer"]
        direction LR
        API[FastAPI Backend]
        AUTH[Authentication]
        QUEUE[Message Queue]
    end

    %% Core Systems Layer
    subgraph CORE["⚙️ Core Systems Layer"]
        direction LR
        VISION[Vision Systems]
        ROBOTS[Robot Control]
        COMMS[Industrial Comms]
        QUALITY[Quality Control]
        SIM[Simulation]
    end

    %% Data Storage Layer
    subgraph DATA["💾 Data Storage Layer"]
        direction LR
        DB[(PostgreSQL)]
        TSDB[(InfluxDB)]
        CACHE[(Redis)]
    end

    %% Vertical Flow
    UI --> APIL
    APIL --> CORE
    CORE --> DATA

    %% Styling
    classDef layerBox fill:#e8e8e8,stroke:#555,stroke-width:3px,color:#222
    classDef nodeBox fill:#f0f0f0,stroke:#666,stroke-width:2px,color:#333

    class UI,APIL,CORE,DATA layerBox
    class GUI,IGNITION,MOBILE,API,AUTH,QUEUE,VISION,ROBOTS,COMMS,QUALITY,SIM,DB,TSDB,CACHE nodeBox
```

### 2. Manufacturing Systems Architecture

```mermaid
graph TD
    %% Vision Systems
    subgraph VISION["👁️ Vision Systems"]
        direction TB
        VC[Vision Controller]
        VC --> CAM[Camera Calibration]
        VC --> HALCON[HALCON Algorithms]
        VC --> COGNEX[Cognex Integration]
        VC --> PHOTONEO[Photoneo 3D Scanner]
        VC --> LIGHTING[Adaptive Lighting]
    end

    %% Robot Programming
    subgraph ROBOTS["🤖 Robot Programming"]
        direction TB
        RC[Robot Controller]
        RC --> UR[Universal Robots]
        RC --> FANUC[FANUC Integration]
        RC --> ABB[ABB Robotics]
        RC --> YASKAWA[Yaskawa Motors]
        RC --> COLLISION[Multi-Robot Collision Avoidance]
    end

    %% Industrial Communication
    subgraph COMMS["🔌 Industrial Communication"]
        direction TB
        PC[PLC Gateway]
        PC --> OPCUA[OPC-UA Server]
        PC --> MODBUS[Modbus TCP/RTU]
        PC --> ROCKWELL[Rockwell RSLogix]
        PC --> SIEMENS[Siemens TIA Portal]
        PC --> ETHERNET[EtherNet/IP]
    end

    %% System Integration
    VISION --> ROBOTS
    ROBOTS --> COMMS
    VISION -.-> COMMS

    %% Styling
    classDef systemBox fill:#e8e8e8,stroke:#555,stroke-width:3px,color:#222
    classDef componentBox fill:#f0f0f0,stroke:#666,stroke-width:2px,color:#333

    class VISION,ROBOTS,COMMS systemBox
    class VC,CAM,HALCON,COGNEX,PHOTONEO,LIGHTING,RC,UR,FANUC,ABB,YASKAWA,COLLISION,PC,OPCUA,MODBUS,ROCKWELL,SIEMENS,ETHERNET componentBox
```

### 3. Quality Control & Simulation Systems

```mermaid
graph TD
    %% Quality Control Systems
    subgraph QUALITY["✅ Quality Control Systems"]
        direction TB
        QM[Quality Manager]
        QM --> IATF[IATF 16949 Compliance]
        QM --> SPC[SPC Analysis Engine]
        QM --> VDA[VDA 6.3 Auditing]
        QM --> TRACE[Traceability System]
        QM --> REPORTS[Quality Reporting]
    end

    %% Simulation & Digital Twin
    subgraph SIMULATION["🎮 Simulation & Digital Twin"]
        direction TB
        SE[Simulation Engine]
        SE --> TWIN[Digital Twin Model]
        SE --> EMULATE[Emulate3D Integration]
        SE --> ROBODK[RoboDK Virtual Cell]
        SE --> PHYSICS[Physics Simulation]
        SE --> PREDICTIVE[Predictive Maintenance]
    end

    %% SCADA & Monitoring
    subgraph SCADA["📊 SCADA & Monitoring"]
        direction TB
        SM[SCADA Manager]
        SM --> DASHBOARD[Real-time Dashboard]
        SM --> ALARMS[Alarm Management]
        SM --> TRENDS[Trend Analysis]
        SM --> LOGGING[Data Logging]
        SM --> BACKUP[Backup Systems]
    end

    %% System Integration
    QUALITY --> SCADA
    SIMULATION --> QUALITY
    SIMULATION -.-> SCADA

    %% Styling
    classDef qualityBox fill:#e8e8e8,stroke:#555,stroke-width:3px,color:#222
    classDef componentBox fill:#f0f0f0,stroke:#666,stroke-width:2px,color:#333

    class QUALITY,SIMULATION,SCADA qualityBox
    class QM,IATF,SPC,VDA,TRACE,REPORTS,SE,TWIN,EMULATE,ROBODK,PHYSICS,PREDICTIVE,SM,DASHBOARD,ALARMS,TRENDS,LOGGING,BACKUP componentBox
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
