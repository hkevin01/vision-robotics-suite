# Vision Robotics Suite

[![CI/CD Pipeline](https://github.com/vision-robotics-suite/vision-robotics-suite/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/vision-robotics-suite/vision-robotics-suite/actions/workflows/ci-cd.yml)
[![Tests](https://github.com/vision-robotics-suite/vision-robotics-suite/actions/workflows/test.yml/badge.svg)](https://github.com/vision-robotics-suite/vision-robotics-suite/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A Python codebase demonstrating industrial automation concepts through simulated vision systems and quality control modules.

## 🎯 What's Actually Here

This repository contains Python modules that simulate industrial automation workflows:

- **Vision System Architecture**: Base classes and interfaces for vision systems
- **Simulated Inspection Modules**: Paint inspection, body-in-white, timing chain verification, battery pack QC
- **Development Environment**: Docker containers with Python, Node.js, Go, Rust toolchains
- **Code Quality Tools**: Black, flake8, mypy, pytest with CI/CD workflows

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

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Docker (optional, for containerized development)
- Git

### Local Setup

```bash
git clone <repository-url>
cd vision-robotics-suite
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install poetry
poetry install
```

### Docker Development Environment

```bash
# Start development containers with full toolchain
make dev-start

# Enter development shell
make dev-shell
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
