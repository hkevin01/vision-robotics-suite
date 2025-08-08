"""
Base Vision System Classes

This module provides abstract base classes and interfaces for all vision systems
in the Vision Robotics Suite.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class VisionSystemBase(ABC):
    """Abstract base class for all vision systems."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """Initialize vision system.

        Args:
            name: Name identifier for the vision system
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.is_connected = False
        self.is_calibrated = False

    @abstractmethod
    def connect(self) -> bool:
        """Connect to the vision system.

        Returns:
            True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the vision system."""
        pass

    @abstractmethod
    def capture_image(self) -> Optional[np.ndarray]:
        """Capture a single image.

        Returns:
            Captured image as numpy array, None if capture failed
        """
        pass

    @abstractmethod
    def process_image(self, image: np.ndarray) -> Dict[str, Any]:
        """Process an image and return results.

        Args:
            image: Input image as numpy array

        Returns:
            Dictionary containing processing results
        """
        pass

    def get_status(self) -> Dict[str, Any]:
        """Get current status of the vision system.

        Returns:
            Status dictionary with system information
        """
        return {
            "name": self.name,
            "connected": self.is_connected,
            "calibrated": self.is_calibrated,
            "config": self.config
        }


class MeasurementResult:
    """Container for vision measurement results."""

    def __init__(
        self,
        x: float,
        y: float,
        z: Optional[float] = None,
        rotation: Optional[Tuple[float, float, float]] = None,
        confidence: float = 1.0,
        timestamp: Optional[float] = None
    ):
        """Initialize measurement result.

        Args:
            x: X coordinate in mm
            y: Y coordinate in mm
            z: Z coordinate in mm (optional for 2D measurements)
            rotation: Rotation angles (rx, ry, rz) in radians
            confidence: Confidence score (0-1)
            timestamp: Measurement timestamp
        """
        self.x = x
        self.y = y
        self.z = z
        self.rotation = rotation
        self.confidence = confidence
        self.timestamp = timestamp

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "rotation": self.rotation,
            "confidence": self.confidence,
            "timestamp": self.timestamp
        }


class VisionError(Exception):
    """Base exception for vision system errors."""
    pass


class CameraError(VisionError):
    """Exception for camera-related errors."""
    pass


class CalibrationError(VisionError):
    """Exception for calibration-related errors."""
    pass


class ProcessingError(VisionError):
    """Exception for image processing errors."""
    pass
