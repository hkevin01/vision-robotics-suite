"""
Vision Robotics Suite - Core Package

A comprehensive industrial automation platform demonstrating integration
between machine vision systems, industrial robots, PLCs, and quality control systems.
"""

__version__ = "0.1.0"
__author__ = "Vision Robotics Team"
__email__ = "team@vision-robotics-suite.com"
__license__ = "MIT"

# Core modules
from . import (
    plc_integration,
    quality_systems,
    robot_programming,
    scada_hmi,
    simulation,
    vision_systems,
)

__all__ = [
    "vision_systems",
    "robot_programming",
    "plc_integration",
    "scada_hmi",
    "simulation",
    "quality_systems",
]
