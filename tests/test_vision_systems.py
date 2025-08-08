"""
Test suite for vision systems module.
"""

import numpy as np
import pytest

from src.vision_systems.base import MeasurementResult, VisionSystemBase
from src.vision_systems.camera_calibration import CameraCalibrator
from src.vision_systems.halcon_algorithms import HalconProcessor


class TestVisionSystemBase:
    """Test cases for VisionSystemBase abstract class."""

    def test_measurement_result_creation(self):
        """Test MeasurementResult object creation."""
        result = MeasurementResult(x=10.5, y=20.3, confidence=0.95)
        assert result.x == 10.5
        assert result.y == 20.3
        assert result.confidence == 0.95

    def test_measurement_result_to_dict(self):
        """Test MeasurementResult conversion to dictionary."""
        result = MeasurementResult(x=10.5, y=20.3, z=5.1)
        result_dict = result.to_dict()

        assert result_dict['x'] == 10.5
        assert result_dict['y'] == 20.3
        assert result_dict['z'] == 5.1


class TestCameraCalibrator:
    """Test cases for CameraCalibrator."""

    def test_calibrator_initialization(self):
        """Test calibrator initialization."""
        calibrator = CameraCalibrator()
        assert not calibrator.is_calibrated
        assert calibrator.camera_matrix is None

    def test_calibrator_with_existing_calibration(self):
        """Test calibrator with existing calibration data."""
        camera_matrix = np.eye(3)
        dist_coeffs = np.zeros(5)

        calibrator = CameraCalibrator(camera_matrix, dist_coeffs)
        assert calibrator.is_calibrated
        assert np.array_equal(calibrator.camera_matrix, camera_matrix)


class TestHalconProcessor:
    """Test cases for HalconProcessor."""

    def test_halcon_initialization(self):
        """Test HALCON processor initialization."""
        processor = HalconProcessor()
        assert processor.name == "HALCON_System"
        assert not processor.is_connected

    def test_halcon_connection(self):
        """Test HALCON connection."""
        processor = HalconProcessor()
        assert processor.connect()
        assert processor.is_connected

    def test_halcon_image_capture(self):
        """Test HALCON image capture."""
        processor = HalconProcessor()
        processor.connect()

        image = processor.capture_image()
        assert image is not None
        assert image.shape == (480, 640, 3)

    def test_halcon_circle_detection(self):
        """Test HALCON circle detection."""
        processor = HalconProcessor()
        processor.connect()

        # Create dummy grayscale image
        image = np.zeros((480, 640), dtype=np.uint8)
        circles = processor.detect_circles(image)

        assert len(circles) > 0
        assert 'x' in circles[0]
        assert 'y' in circles[0]
        assert 'radius' in circles[0]

    def test_halcon_dimensional_measurement(self):
        """Test HALCON dimensional measurements."""
        processor = HalconProcessor()
        processor.connect()

        # Create dummy image
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        measurements = processor.measure_dimensions(image)

        assert 'length_mm' in measurements
        assert 'width_mm' in measurements
        assert measurements['length_mm'] > 0

    def test_halcon_system_info(self):
        """Test HALCON system information."""
        processor = HalconProcessor()
        info = processor.get_system_info()

        assert 'halcon_version' in info
        assert 'license_type' in info
        assert info['halcon_version'] == "21.11"


if __name__ == "__main__":
    pytest.main([__file__])
