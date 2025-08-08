# Vision Robotics Suite

[![CI/CD Pipeline](https://github.com/vision-robotics-suite/vision-robotics-suite/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/vision-robotics-suite/vision-robotics-suite/actions/workflows/ci-cd.yml)
[![Tests](https://github.com/vision-robotics-suite/vision-robotics-suite/actions/workflows/test.yml/badge.svg)](https://github.com/vision-robotics-suite/vision-robotics-suite/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Industrial Automation](https://img.shields.io/badge/Industrial-Automation-green.svg)](https://github.com/vision-robotics-suite)

A comprehensive industrial automation platform demonstrating integration between machine vision systems, industrial robots, PLCs, and quality control systems for modern manufacturing applications.

## 🎯 Project Overview

The Vision Robotics Suite showcases expertise in vision-guided robotics systems, industrial automation, and manufacturing integration - covering core competencies required for modern automation engineering roles including:

- **Machine Vision Integration**: HALCON, Cognex VisionPro, 3D vision systems
- **Industrial Robotics**: FANUC, Yaskawa, ABB, Universal Robots programming
- **PLC Systems**: Siemens TIA Portal, Rockwell RSLogix integration
- **Quality Compliance**: IATF 16949, VDA 6.3 frameworks implementation
- **SCADA/HMI**: Modern web-based interfaces and industrial monitoring
- **Digital Twin**: Simulation and virtual commissioning capabilities

## 🏗️ System Architecture

```text
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Vision System   │────│ Control Layer    │────│ Robot System    │
│ (HALCON/Cognex) │    │ (PLC/SCADA)      │    │ (Multi-vendor)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                  ┌──────────────────┐
                  │ HMI/Dashboard    │
                  │ (Web-based)      │
                  └──────────────────┘
```

## 📁 Project Structure

```text
vision-robotics-suite/
├── src/
├── tests/
├── docs/
├── scripts/
├── config/
├── docker*/
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Docker (for containerized workflow)
- Git

### Local Install (Minimal)

```bash
git clone https://github.com/vision-robotics-suite/vision-robotics-suite.git
cd vision-robotics-suite
python -m venv venv
source venv/bin/activate
pip install poetry
poetry install --with dev,test
poetry run pytest -q
```

### Docker Dev Environment

```bash
bash scripts/dev-setup.sh          # One-time setup
make dev-start                     # Start full stack
make dev-shell                     # Enter backend dev container
```

## 🔧 Core Technologies

### Machine Vision Systems

- HALCON (conceptual integration stubs)
- Cognex VisionPro (integration scaffolding)
- OpenCV, 3D point cloud handling

### Robotics

- FANUC (force feedback integration examples)
- Yaskawa & ABB (multi-robot coordination scaffolds)
- Universal Robots (collaborative safety zone logic)

### Controls & Data

- PLC communication placeholders
- Quality & SPC analysis modules
- Monitoring / logging integration points

## 💡 Example (Abbreviated)

```python
from src.vision_systems.automotive_paint_inspection import AutomotivePaintInspector, InspectionParameters

params = InspectionParameters()
inspector = AutomotivePaintInspector(params)
result = inspector.inspect_paint_surface("sample.jpg")
print(result.get("defects_detected"))
```

## 🛠️ Development Commands

```bash
poetry run pytest                # Run tests
poetry run black src tests       # Format
poetry run flake8 src tests      # Lint
poetry run mypy src              # Type check
```

## 📚 Documentation

Currently only high-level planning exists:

- `docs/project_plan.md` – roadmap / planning notes

(Additional architecture and API docs can be added incrementally as modules mature.)

## 🤝 Contributing

Contributions are welcome. Open an issue or submit a pull request with:

- Clear problem statement
- Minimal reproducible example (if bug)
- Focused, scoped changes

## 📄 License

MIT License – see `LICENSE`.

## 📊 Status & Scope

This repository contains illustrative, prototype-level modules. Some integrations (HALCON, Cognex, proprietary robot SDKs) are represented with stubs or mock implementations for demonstration and cannot run production workflows without vendor SDKs.

## 🧩 Removed Placeholder Content

Removed previous placeholder email, generic support inbox, and links to non‑existent docs to keep the README factual and lean.

## 🙏 Acknowledgments

Open source ecosystem and industrial automation community for tooling and patterns.

---

Focused, realistic, and incrementally extensible.
