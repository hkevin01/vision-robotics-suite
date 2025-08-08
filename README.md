# Vision Robotics Suite

[![CI/CD Pipeline](https://github.com/vision-robotics-suite/vision-robotics-suite/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/vision-robotics-suite/vision-robotics-suite/actions)
[![Tests](https://github.com/vision-robotics-suite/vision-robotics-suite/workflows/Tests/badge.svg)](https://github.com/vision-robotics-suite/vision-robotics-suite/actions)
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

```
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

```
vision-robotics-suite/
├── src/                          # Source code (src layout)
│   ├── vision_systems/           # Machine vision components
│   │   ├── halcon_algorithms/    # MVTec HALCON implementations
│   │   ├── cognex_integration/   # Cognex VisionPro systems
│   │   ├── three_d_vision/       # 3D vision and point clouds
│   │   └── camera_calibration/   # Calibration utilities
│   ├── robot_programming/        # Robot controller interfaces
│   │   ├── fanuc/               # FANUC R-30iB integration
│   │   ├── yaskawa/             # Yaskawa DX200/YRC1000
│   │   ├── abb/                 # ABB IRC5 systems
│   │   └── universal_robots/    # UR collaborative robots
│   ├── plc_integration/         # PLC communication systems
│   │   ├── siemens_tia/         # Siemens TIA Portal
│   │   ├── rockwell_rslogix/    # Allen-Bradley systems
│   │   └── communication_protocols/ # OPC UA, EtherNet/IP
│   ├── scada_hmi/              # SCADA and HMI systems
│   │   ├── ignition_projects/   # Inductive Automation
│   │   ├── web_dashboard/       # Modern web interfaces
│   │   └── data_logging/        # Historical data systems
│   ├── simulation/             # Digital twin and simulation
│   │   ├── robodk_models/       # RoboDK integration
│   │   ├── emulate3d/           # Virtual commissioning
│   │   └── digital_twin/        # Digital twin models
│   └── quality_systems/        # Quality and compliance
│       ├── iatf_16949/          # Automotive quality
│       ├── vda_6_3/             # VDA process audits
│       └── spc_analysis/        # Statistical control
├── tests/                      # Comprehensive test suites
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── performance/            # Performance benchmarks
├── docs/                       # Documentation
├── scripts/                    # Build and deployment
├── data/                       # Sample data and configs
├── assets/                     # Images and resources
└── .github/                    # GitHub workflows and templates
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** for core development
- **Java 11+** for PLC integration components
- **C++17** compatible compiler for performance modules
- **Docker** for containerized development
- **Industrial automation knowledge** (helpful but not required)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vision-robotics-suite/vision-robotics-suite.git
   cd vision-robotics-suite
   ```

2. **Set up Python environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install poetry
   poetry install --with dev,test
   ```

3. **Install development dependencies:**
   ```bash
   # Pre-commit hooks for code quality
   pre-commit install

   # Additional system dependencies (Ubuntu/Debian)
   sudo apt-get install build-essential cmake
   ```

4. **Verify installation:**
   ```bash
   poetry run pytest tests/ -v
   ```

## 🔧 Core Technologies

### Machine Vision Systems
- **MVTec HALCON**: Advanced image processing for inspection and measurement
- **Cognex VisionPro**: Industrial vision for part identification and quality control
- **3D Vision**: Point cloud processing with Photoneo PhoXi and Zivid cameras
- **OpenCV Integration**: Computer vision algorithms and camera calibration

### Industrial Robotics
- **FANUC Integration**: R-30iB controllers for material handling and assembly
- **Yaskawa Programming**: DX200/YRC1000 systems for pick-and-place operations
- **ABB Systems**: IRC5 controllers for complex assembly tasks
- **Universal Robots**: Collaborative applications with safety integration

### Automation Controls
- **Siemens TIA Portal**: S7-1500 PLC programming with safety functions
- **Rockwell Automation**: CompactLogix/ControlLogix system integration
- **Communication Protocols**: OPC UA, EtherNet/IP, Profinet implementation

### Quality & Compliance Systems
- **IATF 16949**: Automotive quality management system implementation
- **VDA 6.3**: Process assessment and audit procedures
- **SPC Analysis**: Statistical process control and capability studies
- **Traceability**: Complete part tracking and genealogy systems

## 💡 Featured Applications

### 1. Vision-Guided Assembly Cell

```python
# Example: HALCON-based part recognition and robot guidance
from src.vision_systems.halcon_algorithms import PartDetector
from src.robot_programming.fanuc import FanucController

def vision_guided_assembly():
    """Demonstrates HALCON vision integration with FANUC robot"""
    # Initialize systems
    vision = PartDetector(camera_id=0)
    robot = FanucController(ip="192.168.1.10")

    # Process workflow
    image = vision.capture_image()
    parts = vision.detect_parts(image)

    for part in parts:
        robot_pose = vision.calculate_robot_pose(part)
        robot.move_to_position(robot_pose)
        robot.execute_pick_sequence()
```

### 2. Quality Inspection System

```python
# Example: 3D vision inspection with statistical analysis
from src.vision_systems.three_d_vision import PhotoneoScanner
from src.quality_systems.spc_analysis import QualityController

def dimensional_inspection():
    """3D inspection with SPC analysis for automotive parts"""
    scanner = PhotoneoScanner()
    quality = QualityController()

    point_cloud = scanner.capture_3d()
    measurements = scanner.measure_dimensions(point_cloud)

    # Evaluate against specifications
    results = quality.evaluate_measurements(measurements)
    if results.cpk < 1.33:
        quality.trigger_process_adjustment()
```

### 3. Multi-Robot Coordination

```python
# Example: Coordinated material handling system
from src.robot_programming import FanucController, YaskawaController
from src.plc_integration.siemens_tia import S7PLCController

def coordinated_assembly():
    """Multi-robot coordination through PLC"""
    fanuc = FanucController("192.168.1.10")
    yaskawa = YaskawaController("192.168.1.11")
    plc = S7PLCController("192.168.1.5")

    # Synchronized operation
    while plc.read_bool("DB1.Production_Active"):
        if plc.read_bool("DB1.Part_Ready"):
            fanuc.pick_part()
            yaskawa.position_fixture()
            coordinate_assembly_sequence()
```

## 📊 SCADA & Data Analytics

### Real-time Monitoring
- Production metrics and KPIs
- Equipment status and alarms
- Quality data trending
- Energy consumption monitoring
- Predictive maintenance indicators

### Data Integration
- OPC UA server implementation
- Time-series database (InfluxDB/TimescaleDB)
- REST API for external systems
- Industrial IoT connectivity (MQTT)

## 🛠️ Development

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run specific test categories
poetry run pytest tests/unit/
poetry run pytest tests/integration/
poetry run pytest tests/performance/

# Run with coverage
poetry run pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
poetry run black src tests
poetry run isort src tests

# Lint code
poetry run flake8 src tests
poetry run mypy src

# Security scan
poetry run bandit -r src
```

### Documentation

```bash
# Build documentation
cd docs
make html

# Serve locally
python -m http.server 8000 -d _build/html
```

## 🏭 Industrial Applications

### Automotive Manufacturing
- Engine assembly line automation
- Body-in-white inspection systems
- Paint booth quality control
- Final assembly coordination

### Electronics Production
- PCB inspection and testing
- Component placement systems
- Semiconductor handling
- Quality traceability systems

### General Manufacturing
- Material handling automation
- Quality inspection cells
- Packaging and palletizing
- Process optimization

## 🔒 Safety & Security

### Industrial Safety (ISO 13849)
- Emergency stop integration
- Safety zone monitoring
- Risk assessment procedures
- Safety validation testing

### Cybersecurity (IEC 62443)
- Network segmentation guidelines
- Authentication and authorization
- Encrypted communications
- Vulnerability management

## 📚 Documentation

- [📖 **User Manual**](docs/user_manual.md) - Complete user guide
- [🏗️ **Architecture Guide**](docs/architecture.md) - System design details
- [🤖 **Robot Programming**](docs/robot_programming.md) - Robot integration guide
- [👁️ **Vision Systems**](docs/vision_systems.md) - Vision setup and calibration
- [🔧 **PLC Integration**](docs/plc_integration.md) - PLC communication guide
- [📊 **Quality Systems**](docs/quality_systems.md) - Quality compliance procedures
- [🛠️ **API Reference**](docs/api/) - Complete API documentation

## 🤝 Contributing

We welcome contributions from the automation community! Please see our [Contributing Guide](.github/CONTRIBUTING.md) for details.

### Development Areas
- **Vision Algorithms**: New inspection and measurement techniques
- **Robot Integration**: Additional robot manufacturer support
- **Quality Systems**: Enhanced compliance and traceability features
- **Safety Systems**: Advanced safety function implementation
- **Documentation**: User guides and technical documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Certifications & Standards

- **IATF 16949:2016** Automotive Quality Management
- **VDA 6.3** Process Assessment Standards
- **ISO 13849** Functional Safety Implementation
- **IEC 62443** Industrial Cybersecurity Framework

## 📞 Support & Community

- **📧 Email**: support@vision-robotics-suite.com
- **💬 Discussions**: [GitHub Discussions](https://github.com/vision-robotics-suite/vision-robotics-suite/discussions)
- **🐛 Issues**: [Bug Reports](https://github.com/vision-robotics-suite/vision-robotics-suite/issues)
- **📋 Project Board**: [Development Progress](https://github.com/vision-robotics-suite/vision-robotics-suite/projects)

## 🙏 Acknowledgments

- Industrial automation community for best practices and standards
- Open source contributors for foundational libraries and tools
- Manufacturing partners for real-world validation and feedback
- Academic institutions for research collaboration and innovation

---

**Built with ❤️ for the Industrial Automation Community**

*Demonstrating the future of intelligent manufacturing through vision-guided robotics and integrated automation systems.*
