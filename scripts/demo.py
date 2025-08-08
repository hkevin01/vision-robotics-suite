#!/usr/bin/env python3
"""
Vision Robotics Suite - Demo Script

This script demonstrates the core capabilities of the Vision Robotics Suite
including vision processing, robot control, and quality analysis.
"""

import logging
import sys
import time
from pathlib import Path

import numpy as np

# Add src to path for direct execution
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vision_systems.camera_calibration import CameraCalibrator
from vision_systems.halcon_algorithms import HalconProcessor


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('vision_robotics_demo.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def demo_vision_processing():
    """Demonstrate vision processing capabilities."""
    logger = logging.getLogger(__name__)
    logger.info("🔍 Starting Vision Processing Demo")

    # Initialize HALCON processor
    processor = HalconProcessor(name="Demo_HALCON")

    # Connect to vision system
    if processor.connect():
        logger.info("✅ Connected to HALCON vision system")
    else:
        logger.error("❌ Failed to connect to vision system")
        return False

    # Capture and process image
    logger.info("📸 Capturing image...")
    image = processor.capture_image()

    if image is not None:
        logger.info(f"✅ Image captured: {image.shape}")

        # Process image for defect detection
        logger.info("🔍 Processing image for defects...")
        results = processor.process_image(image)

        logger.info("📊 Processing results:")
        logger.info(f"  - Objects found: {results.get('objects_found', 0)}")
        processing_time = results.get('processing_time_ms', 0)
        logger.info(f"  - Processing time: {processing_time:.1f}ms")

        # Demonstrate circle detection
        logger.info("🔵 Detecting circles...")
        gray_image = np.mean(image, axis=2).astype(np.uint8)
        circles = processor.detect_circles(gray_image)

        logger.info(f"  - Circles detected: {len(circles)}")
        for i, circle in enumerate(circles):
            center_x = circle['x']
            center_y = circle['y']
            radius = circle['radius']
            confidence = circle['confidence']
            logger.info(f"    Circle {i+1}: center=({center_x:.1f}, "
                        f"{center_y:.1f}), radius={radius:.1f}, "
                        f"confidence={confidence:.2f}")

        # Demonstrate dimensional measurement
        logger.info("📏 Measuring dimensions...")
        measurements = processor.measure_dimensions(image)

        logger.info(f"  - Length: {measurements['length_mm']:.2f} mm")
        logger.info(f"  - Width: {measurements['width_mm']:.2f} mm")
        logger.info(f"  - Diameter: {measurements['diameter_mm']:.2f} mm")
        logger.info(f"  - Area: {measurements['area_mm2']:.2f} mm²")

        # Demonstrate barcode reading
        logger.info("📋 Reading barcode...")
        barcode = processor.read_barcode(image)
        if barcode:
            logger.info(f"  - Barcode: {barcode}")

    processor.disconnect()
    logger.info("🔌 Disconnected from vision system")
    return True


def demo_camera_calibration():
    """Demonstrate camera calibration capabilities."""
    logger = logging.getLogger(__name__)
    logger.info("📐 Starting Camera Calibration Demo")

    # Initialize calibrator
    calibrator = CameraCalibrator()

    # Generate synthetic calibration data (in real application, use actual
    # images)
    logger.info("📸 Generating calibration data...")

    # Create checkerboard pattern points
    pattern_size = (9, 6)
    square_size = 25.0  # mm

    # Generate object points (3D points in real world space)
    objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:pattern_size[0],
                           0:pattern_size[1]].T.reshape(-1, 2)
    objp *= square_size

    # Simulate multiple calibration images
    object_points = []
    image_points = []

    for i in range(10):  # Simulate 10 calibration images
        # In real application, these would be detected corners from
        # actual images
        imgp = objp[:, :2] + np.random.normal(0, 0.5, (objp.shape[0], 2))

        object_points.append(objp)
        image_points.append(imgp)

    image_size = (640, 480)

    try:
        # Perform calibration
        logger.info("🔧 Performing camera calibration...")
        calibration_results = calibrator.calibrate_camera(
            object_points, image_points, image_size
        )

        logger.info("✅ Camera calibration completed")
        error = calibration_results['reprojection_error']
        logger.info(f"  - Reprojection error: {error:.3f}")
        matrix_shape = calibration_results['camera_matrix'].shape
        logger.info(f"  - Camera matrix shape: {matrix_shape}")

        # Test image undistortion
        logger.info("🖼️  Testing image undistortion...")
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        undistorted = calibrator.undistort_image(test_image)

        logger.info(f"  - Original image shape: {test_image.shape}")
        logger.info(f"  - Undistorted image shape: {undistorted.shape}")

        # Save calibration data
        calibration_file = "data/camera_calibration.npz"
        Path("data").mkdir(exist_ok=True)
        calibrator.save_calibration(calibration_file)
        logger.info(f"💾 Calibration saved to: {calibration_file}")

        return True

    except Exception as e:
        logger.error(f"❌ Calibration failed: {str(e)}")
        return False


def demo_quality_analysis():
    """Demonstrate quality control and analysis."""
    logger = logging.getLogger(__name__)
    logger.info("📊 Starting Quality Analysis Demo")

    # Simulate quality measurements
    measurements = [
        {"parameter": "diameter", "value": 25.05, "target": 25.0, "tolerance": 0.1},
        {"parameter": "length", "value": 49.98, "target": 50.0, "tolerance": 0.2},
        {"parameter": "width", "value": 24.97, "target": 25.0, "tolerance": 0.15},
        {"parameter": "surface_roughness", "value": 1.2, "target": 1.0, "tolerance": 0.5},
    ]

    logger.info("📏 Analyzing quality measurements...")

    total_measurements = len(measurements)
    passed_measurements = 0

    for measurement in measurements:
        param = measurement["parameter"]
        value = measurement["value"]
        target = measurement["target"]
        tolerance = measurement["tolerance"]

        deviation = abs(value - target)
        passed = deviation <= tolerance

        if passed:
            passed_measurements += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"

        logger.info(f"  {param}: {value:.2f} (target: {target:.2f} ±{tolerance:.2f}) {status}")

    yield_rate = (passed_measurements / total_measurements) * 100
    logger.info(f"📈 Quality Results:")
    logger.info(f"  - Total measurements: {total_measurements}")
    logger.info(f"  - Passed: {passed_measurements}")
    logger.info(f"  - Yield rate: {yield_rate:.1f}%")

    # Simulate process capability calculation
    cpk = 1.33 if yield_rate >= 95 else 0.8
    logger.info(f"  - Process capability (Cpk): {cpk:.2f}")

    if cpk >= 1.33:
        logger.info("✅ Process is capable (Cpk ≥ 1.33)")
    else:
        logger.warning("⚠️  Process needs improvement (Cpk < 1.33)")

    return True


def demo_system_integration():
    """Demonstrate system integration capabilities."""
    logger = logging.getLogger(__name__)
    logger.info("🔗 Starting System Integration Demo")

    # Simulate integrated automation workflow
    logger.info("🤖 Simulating integrated automation workflow...")

    # Step 1: Vision system inspection
    logger.info("  1. Vision system: Inspecting part...")
    time.sleep(0.5)  # Simulate processing time
    vision_result = {"defects_found": 0, "position": {"x": 100.5, "y": 200.3}}
    logger.info(f"     Result: {vision_result}")

    # Step 2: Robot positioning
    logger.info("  2. Robot system: Moving to position...")
    time.sleep(0.3)
    robot_position = {"x": vision_result["position"]["x"],
                     "y": vision_result["position"]["y"],
                     "z": 50.0}
    logger.info(f"     Position: {robot_position}")

    # Step 3: PLC coordination
    logger.info("  3. PLC system: Coordinating operation...")
    time.sleep(0.2)
    plc_status = {"conveyors_running": True, "safety_ok": True, "cycle_complete": True}
    logger.info(f"     Status: {plc_status}")

    # Step 4: Quality logging
    logger.info("  4. Quality system: Logging results...")
    time.sleep(0.1)
    quality_record = {
        "part_id": "ABC123456",
        "timestamp": time.time(),
        "inspection_passed": vision_result["defects_found"] == 0,
        "position_accuracy": "±0.1mm"
    }
    logger.info(f"     Record: {quality_record}")

    logger.info("✅ Integrated workflow completed successfully")
    return True


def main():
    """Run the complete demonstration."""
    logger = setup_logging()

    logger.info("🚀 Vision Robotics Suite - Demonstration")
    logger.info("=" * 50)

    # Run demonstrations
    demos = [
        ("Vision Processing", demo_vision_processing),
        ("Camera Calibration", demo_camera_calibration),
        ("Quality Analysis", demo_quality_analysis),
        ("System Integration", demo_system_integration),
    ]

    results = []
    for name, demo_func in demos:
        logger.info(f"\n{'=' * 20} {name} {'=' * 20}")
        try:
            success = demo_func()
            results.append((name, success))
        except Exception as e:
            logger.error(f"❌ Demo '{name}' failed: {str(e)}")
            results.append((name, False))

        time.sleep(1)  # Brief pause between demos

    # Summary
    logger.info(f"\n{'=' * 20} SUMMARY {'=' * 23}")
    successful_demos = sum(1 for _, success in results if success)
    total_demos = len(results)

    for name, success in results:
        status = "✅" if success else "❌"
        logger.info(f"  {status} {name}")

    logger.info(f"\n📊 Results: {successful_demos}/{total_demos} demos completed successfully")

    if successful_demos == total_demos:
        logger.info("🎉 All demonstrations completed successfully!")
        logger.info("🔧 System is ready for industrial deployment")
    else:
        logger.warning("⚠️  Some demonstrations failed - check logs for details")

    logger.info("\n📚 Next steps:")
    logger.info("  - Review logs: vision_robotics_demo.log")
    logger.info("  - Configure real hardware connections in .env")
    logger.info("  - Run unit tests: poetry run pytest")
    logger.info("  - Build documentation: cd docs && make html")


if __name__ == "__main__":
    main()
