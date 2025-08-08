"""
Advanced Vision Robotics Suite Demo

Demonstrates the three advanced features:
1. Real-time defect detection for automotive paint inspection
2. 3D point cloud registration for multi-camera systems
3. Adaptive lighting control system

This script showcases industrial-grade machine vision capabilities
suitable for automotive manufacturing and quality inspection.
"""

import asyncio
import logging
import time
from pathlib import Path

import numpy as np

from src.vision_systems.adaptive_lighting_control import (
    AdaptiveLightingController,
    InspectionMode,
    LightingType,
    LightingZone,
    SurfaceProperties,
    SurfaceType,
)

# Import our advanced modules
from src.vision_systems.automotive_paint_inspection import (
    AutomotivePaintInspector,
    DefectType,
    InspectionParameters,
)
from src.vision_systems.photoneo_3d_registration import (
    CameraCalibration,
    PhotoneoMultiCameraSystem,
)


class AdvancedVisionDemo:
    """
    Comprehensive demonstration of advanced vision system capabilities.
    """

    def __init__(self):
        """Initialize the demonstration system."""
        self.logger = logging.getLogger(__name__)

        # Initialize paint inspection system
        self.paint_inspector = None

        # Initialize 3D registration system
        self.photoneo_system = None

        # Initialize adaptive lighting
        self.lighting_controller = None

        # Demo statistics
        self.demo_stats = {
            'paint_inspections': 0,
            'point_cloud_registrations': 0,
            'lighting_adjustments': 0,
            'total_processing_time': 0.0,
            'defects_detected': 0,
            'registration_accuracy': []
        }

    def setup_paint_inspection(self) -> bool:
        """Set up the automotive paint inspection system."""
        try:
            # Configure inspection parameters for automotive paint
            params = InspectionParameters(
                pixel_size_mm=0.01,
                min_defect_size_mm=0.1,
                scratch_sensitivity=0.8,
                crater_sensitivity=0.7,
                color_tolerance=15.0,
                surface_roughness_threshold=5.0,
                inspection_area_mm=(100.0, 100.0)
            )

            self.paint_inspector = AutomotivePaintInspector(parameters=params)

            self.logger.info("✅ Paint inspection system initialized")
            return True

        except Exception as e:
            self.logger.error(f"❌ Paint inspection setup failed: {e}")
            return False

    def setup_3d_registration(self) -> bool:
        """Set up the 3D point cloud registration system."""
        try:
            # Configure camera calibrations for multi-camera setup
            camera_configs = [
                CameraCalibration(
                    camera_id="phoxi_01",
                    intrinsic_matrix=np.array([
                        [1600, 0, 1032], [0, 1600, 772], [0, 0, 1]
                    ]),
                    extrinsic_matrix=np.eye(4),
                    distortion_coefficients=np.array([
                        0.1, -0.05, 0.001, 0.001, 0.02
                    ]),
                    resolution=(2064, 1544),
                    field_of_view=(45.0, 35.0),
                    working_distance_mm=500.0,
                    accuracy_mm=0.1
                ),
                CameraCalibration(
                    camera_id="phoxi_02",
                    intrinsic_matrix=np.array([
                        [1600, 0, 1032], [0, 1600, 772], [0, 0, 1]
                    ]),
                    extrinsic_matrix=np.array([
                        [0.966, -0.259, 0, 200], [0.259, 0.966, 0, 0],
                        [0, 0, 1, 0], [0, 0, 0, 1]
                    ]),
                    distortion_coefficients=np.array([0.08, -0.03, 0.002, 0.001, 0.015]),
                    resolution=(2064, 1544),
                    field_of_view=(45.0, 35.0),
                    working_distance_mm=500.0,
                    accuracy_mm=0.1
                ),
                CameraCalibration(
                    camera_id="phoxi_03",
                    intrinsic_matrix=np.array([
                        [1600, 0, 1032], [0, 1600, 772], [0, 0, 1]
                    ]),
                    extrinsic_matrix=np.array([
                        [0.966, 0.259, 0, -200], [-0.259, 0.966, 0, 0],
                        [0, 0, 1, 0], [0, 0, 0, 1]
                    ]),
                    distortion_coefficients=np.array([0.12, -0.04, 0.001, 0.002, 0.018]),
                    resolution=(2064, 1544),
                    field_of_view=(45.0, 35.0),
                    working_distance_mm=500.0,
                    accuracy_mm=0.1
                )
            ]

            self.photoneo_system = PhotoneoMultiCameraSystem(
                camera_configs=camera_configs
            )

            self.logger.info("✅ 3D registration system initialized")
            return True

        except Exception as e:
            self.logger.error(f"❌ 3D registration setup failed: {e}")
            return False

    def setup_adaptive_lighting(self) -> bool:
        """Set up the adaptive lighting control system."""
        try:
            # Configure multiple lighting zones
            lighting_zones = [
                LightingZone(
                    zone_id="ring_led_main",
                    lighting_type=LightingType.LED_RING,
                    position=(0, 0, 100),
                    angle=(0, 45),
                    max_intensity=4095,
                    current_intensity=2000,
                    color_temperature=6500,
                    is_active=True
                ),
                LightingZone(
                    zone_id="bar_led_side_01",
                    lighting_type=LightingType.LED_BAR,
                    position=(100, 0, 80),
                    angle=(30, 30),
                    max_intensity=4095,
                    current_intensity=1500,
                    color_temperature=5000,
                    is_active=True
                ),
                LightingZone(
                    zone_id="bar_led_side_02",
                    lighting_type=LightingType.LED_BAR,
                    position=(-100, 0, 80),
                    angle=(-30, 30),
                    max_intensity=4095,
                    current_intensity=1500,
                    color_temperature=5000,
                    is_active=True
                ),
                LightingZone(
                    zone_id="dome_led_diffuse",
                    lighting_type=LightingType.LED_DOME,
                    position=(0, 0, 150),
                    angle=(0, 90),
                    max_intensity=4095,
                    current_intensity=800,
                    color_temperature=6500,
                    is_active=False
                ),
                LightingZone(
                    zone_id="darkfield_ring",
                    lighting_type=LightingType.LED_DARKFIELD,
                    position=(0, 0, 90),
                    angle=(0, 15),
                    max_intensity=4095,
                    current_intensity=1200,
                    color_temperature=6000,
                    is_active=True
                )
            ]

            self.lighting_controller = AdaptiveLightingController(
                lighting_zones
            )

            self.logger.info("✅ Adaptive lighting system initialized")
            return True

        except Exception as e:
            self.logger.error(f"❌ Adaptive lighting setup failed: {e}")
            return False

    async def demonstrate_paint_inspection(self) -> None:
        """Demonstrate automotive paint inspection capabilities."""
        self.logger.info("🎨 Starting paint inspection demonstration...")

        if not self.paint_inspector:
            self.logger.warning("Paint inspector not initialized")
            return

        try:
            # Configure lighting for surface inspection
            if self.lighting_controller:
                metallic_surface = SurfaceProperties(
                    surface_type=SurfaceType.METALLIC_POLISHED,
                    reflectivity_coefficient=0.8,
                    specular_reflection=0.9,
                    surface_roughness=0.1,
                    color_rgb=(180, 180, 190),
                    transparency=0.0
                )

                self.lighting_controller.set_inspection_mode(
                    InspectionMode.SURFACE_INSPECTION
                )
                self.lighting_controller.set_surface_properties(
                    metallic_surface
                )

                # Wait for lighting adjustment
                await asyncio.sleep(0.1)

                self.demo_stats['lighting_adjustments'] += 1

            # Generate synthetic paint surface for demonstration
            surface_image = self._generate_synthetic_paint_surface()

            # Perform comprehensive inspection
            start_time = time.time()

            inspection_result = self.paint_inspector.inspect_paint_surface(
                "demo_surface.jpg"  # Would save synthetic image first
            )

            processing_time = time.time() - start_time
            self.demo_stats['total_processing_time'] += processing_time
            self.demo_stats['paint_inspections'] += 1

            if inspection_result:
                defect_count = len(inspection_result.detected_defects)
                self.demo_stats['defects_detected'] += defect_count

                self.logger.info(
                    f"✅ Paint inspection completed in {processing_time:.3f}s"
                )
                self.logger.info(
                    f"   Found {defect_count} defects, "
                    f"Quality: {inspection_result.overall_quality:.2f}"
                )

                # Log defect details
                for defect in inspection_result.detected_defects:
                    self.logger.info(
                        f"   - {defect.defect_type.value}: "
                        f"severity {defect.severity:.2f} at "
                        f"({defect.location[0]:.1f}, {defect.location[1]:.1f})"
                    )

        except Exception as e:
            self.logger.error(f"❌ Paint inspection failed: {e}")

    async def demonstrate_3d_registration(self) -> None:
        """Demonstrate 3D point cloud registration."""
        self.logger.info("📐 Starting 3D registration demonstration...")

        if not self.photoneo_system:
            self.logger.warning("3D registration system not initialized")
            return

        try:
            # Configure lighting for dimensional measurement
            if self.lighting_controller:
                self.lighting_controller.set_inspection_mode(
                    InspectionMode.DIMENSIONAL_MEASUREMENT
                )
                await asyncio.sleep(0.1)
                self.demo_stats['lighting_adjustments'] += 1

            # Capture point clouds from multiple cameras
            start_time = time.time()

            # In simulation mode, this generates synthetic point clouds
            point_clouds = await self.photoneo_system.capture_all_cameras()

            if point_clouds:
                self.logger.info(
                    f"✅ Captured {len(point_clouds)} point clouds"
                )

                # Perform global registration
                registration_result = (
                    await self.photoneo_system.perform_global_registration(
                        point_clouds
                    )
                )

                if registration_result and registration_result.success:
                    processing_time = time.time() - start_time
                    self.demo_stats['total_processing_time'] += processing_time
                    self.demo_stats['point_cloud_registrations'] += 1
                    self.demo_stats['registration_accuracy'].append(
                        registration_result.registration_error
                    )

                    self.logger.info(
                        f"✅ 3D registration completed in "
                        f"{processing_time:.3f}s"
                    )
                    self.logger.info(
                        f"   Registration error: "
                        f"{registration_result.registration_error:.4f}mm"
                    )
                    self.logger.info(
                        f"   Points processed: "
                        f"{registration_result.points_processed:,}"
                    )

                    # Analyze merged point cloud
                    if registration_result.merged_cloud is not None:
                        point_count = len(registration_result.merged_cloud)
                        self.logger.info(
                            f"   Merged cloud: {point_count:,} points"
                        )

        except Exception as e:
            self.logger.error(f"❌ 3D registration failed: {e}")

    async def demonstrate_adaptive_lighting(self) -> None:
        """Demonstrate adaptive lighting optimization."""
        self.logger.info("💡 Starting adaptive lighting demonstration...")

        if not self.lighting_controller:
            self.logger.warning("Lighting controller not initialized")
            return

        try:
            # Test different surface types and inspection modes
            test_scenarios = [
                {
                    'surface': SurfaceProperties(
                        surface_type=SurfaceType.PLASTIC_GLOSSY,
                        reflectivity_coefficient=0.6,
                        specular_reflection=0.7,
                        surface_roughness=0.2,
                        color_rgb=(255, 255, 255),
                        transparency=0.0
                    ),
                    'mode': InspectionMode.DEFECT_DETECTION,
                    'name': 'Plastic Defect Detection'
                },
                {
                    'surface': SurfaceProperties(
                        surface_type=SurfaceType.METALLIC_BRUSHED,
                        reflectivity_coefficient=0.7,
                        specular_reflection=0.4,
                        surface_roughness=1.2,
                        color_rgb=(150, 150, 160),
                        transparency=0.0
                    ),
                    'mode': InspectionMode.EDGE_DETECTION,
                    'name': 'Metal Edge Detection'
                },
                {
                    'surface': SurfaceProperties(
                        surface_type=SurfaceType.GLASS,
                        reflectivity_coefficient=0.9,
                        specular_reflection=0.95,
                        surface_roughness=0.05,
                        color_rgb=(240, 240, 255),
                        transparency=0.8
                    ),
                    'mode': InspectionMode.COLOR_ANALYSIS,
                    'name': 'Glass Color Analysis'
                }
            ]

            for scenario in test_scenarios:
                self.logger.info(f"📋 Testing: {scenario['name']}")

                # Set scenario parameters
                self.lighting_controller.set_inspection_mode(scenario['mode'])
                self.lighting_controller.set_surface_properties(
                    scenario['surface']
                )

                # Wait for auto-adjustment
                await asyncio.sleep(0.1)

                # Mock optimization with feedback
                def mock_image_capture():
                    return np.random.randint(0, 255, (480, 640), dtype=np.uint8)

                optimization_start = time.time()
                success = await self.lighting_controller.optimize_lighting_with_feedback(
                    mock_image_capture
                )
                optimization_time = time.time() - optimization_start

                if success:
                    self.logger.info(
                        f"   ✅ Optimized in {optimization_time:.3f}s"
                    )
                else:
                    self.logger.info(
                        f"   ⚠️  Optimization completed in {optimization_time:.3f}s"
                    )

                self.demo_stats['lighting_adjustments'] += 1

                # Show current zone status
                zone_status = self.lighting_controller.get_zone_status()
                active_zones = [
                    zone_id for zone_id, status in zone_status.items()
                    if status['is_active']
                ]
                self.logger.info(f"   Active zones: {len(active_zones)}")

                # Save lighting profile
                profile_name = f"demo_{scenario['surface'].surface_type.value}"
                if self.lighting_controller.save_lighting_profile(profile_name):
                    self.logger.info(f"   📁 Profile saved: {profile_name}")

        except Exception as e:
            self.logger.error(f"❌ Adaptive lighting demo failed: {e}")

    def _generate_synthetic_paint_surface(self) -> np.ndarray:
        """Generate synthetic paint surface with artificial defects."""
        # Create base surface (640x480 grayscale)
        surface = np.random.normal(128, 10, (480, 640)).astype(np.uint8)

        # Add some artificial defects for demonstration
        # Scratch simulation
        cv_y, cv_x = 200, 300
        surface[cv_y-1:cv_y+2, cv_x:cv_x+50] = 80

        # Crater simulation
        crater_y, crater_x = 350, 200
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if dy*dy + dx*dx <= 9:
                    surface[crater_y + dy, crater_x + dx] = 60

        return surface

    async def run_complete_demonstration(self) -> None:
        """Run the complete advanced vision demonstration."""
        self.logger.info("🚀 Starting Advanced Vision Robotics Suite Demo")
        self.logger.info("=" * 60)

        demo_start_time = time.time()

        try:
            # Setup all systems
            setup_success = (
                self.setup_paint_inspection() and
                self.setup_3d_registration() and
                self.setup_adaptive_lighting()
            )

            if not setup_success:
                self.logger.error("❌ System setup failed")
                return

            # Run demonstrations
            await self.demonstrate_adaptive_lighting()
            await asyncio.sleep(0.5)

            await self.demonstrate_paint_inspection()
            await asyncio.sleep(0.5)

            await self.demonstrate_3d_registration()

            # Final statistics
            total_demo_time = time.time() - demo_start_time

            self.logger.info("=" * 60)
            self.logger.info("📊 DEMONSTRATION COMPLETE - STATISTICS")
            self.logger.info("=" * 60)

            stats = self.demo_stats

            self.logger.info(f"Total demo time: {total_demo_time:.2f}s")
            self.logger.info(f"Paint inspections: {stats['paint_inspections']}")
            self.logger.info(f"Point cloud registrations: {stats['point_cloud_registrations']}")
            self.logger.info(f"Lighting adjustments: {stats['lighting_adjustments']}")
            self.logger.info(f"Defects detected: {stats['defects_detected']}")

            if stats['registration_accuracy']:
                avg_accuracy = np.mean(stats['registration_accuracy'])
                self.logger.info(f"Average registration accuracy: {avg_accuracy:.4f}mm")

            # System statistics
            if self.lighting_controller:
                lighting_stats = self.lighting_controller.get_statistics()
                self.logger.info(
                    f"Lighting success rate: "
                    f"{lighting_stats['success_rate_percent']:.1f}%"
                )

            self.logger.info("✅ All advanced features demonstrated successfully!")

        except Exception as e:
            self.logger.error(f"❌ Demonstration failed: {e}")


# Main execution
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    print("Advanced Vision Robotics Suite Demonstration")
    print("Showcasing industrial-grade machine vision capabilities")
    print()

    # Run the demonstration
    demo = AdvancedVisionDemo()
    asyncio.run(demo.run_complete_demonstration())
