# Copilot Instructions for Vision Robotics Suite

This project focuses on industrial automation, machine vision, and robotics integration. When providing assistance:

## Code Style Guidelines:
- Follow PEP 8 for Python code
- Use Google style for Java and C++
- Prefer descriptive variable names relevant to industrial automation
- Include comprehensive docstrings and comments
- Use type hints in Python code

## Domain Knowledge:
- Industrial robots: FANUC, Yaskawa, ABB, Universal Robots
- Vision systems: HALCON, Cognex, OpenCV
- PLCs: Siemens TIA Portal, Rockwell RSLogix
- Communication protocols: OPC UA, EtherNet/IP, Profinet
- Quality standards: IATF 16949, VDA 6.3
- Safety standards: ISO 13849, IEC 62443

## Common Patterns:
- Error handling for industrial communication
- Safety interlocks and emergency stops
- Data logging and traceability
- Real-time monitoring and alarms
- Calibration and measurement validation

## Naming Conventions:
- Classes: PascalCase (e.g., `RobotController`, `VisionSystem`)
- Functions/Methods: snake_case (e.g., `move_to_position`, `capture_image`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_SPEED`, `DEFAULT_TIMEOUT`)
- Files: snake_case (e.g., `fanuc_controller.py`, `quality_check.py`)

## Security Considerations:
- Never hardcode IP addresses, passwords, or API keys
- Use environment variables for sensitive configuration
- Implement proper authentication for industrial systems
- Follow cybersecurity best practices for industrial networks
