"""
Adaptive Lighting Control System

This module implements an intelligent lighting control system that
automatically adjusts illumination based on part reflectivity, surface
conditions, and inspection requirements for machine vision applications.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False


class LightingType(Enum):
    """Types of industrial lighting."""
    LED_RING = "led_ring"
    LED_BAR = "led_bar"
    LED_DOME = "led_dome"
    LED_COAXIAL = "led_coaxial"
    LED_BACKLIGHT = "led_backlight"
    LED_DARKFIELD = "led_darkfield"
    STROBE = "strobe"
    LASER_LINE = "laser_line"


class SurfaceType(Enum):
    """Surface material types affecting reflectivity."""
    METALLIC_POLISHED = "metallic_polished"
    METALLIC_BRUSHED = "metallic_brushed"
    METALLIC_ANODIZED = "metallic_anodized"
    PLASTIC_GLOSSY = "plastic_glossy"
    PLASTIC_MATTE = "plastic_matte"
    CERAMIC = "ceramic"
    GLASS = "glass"
    RUBBER = "rubber"
    PAINTED = "painted"
    TEXTURED = "textured"


class InspectionMode(Enum):
    """Vision inspection modes requiring different lighting."""
    DEFECT_DETECTION = "defect_detection"
    DIMENSIONAL_MEASUREMENT = "dimensional_measurement"
    SURFACE_INSPECTION = "surface_inspection"
    COLOR_ANALYSIS = "color_analysis"
    BARCODE_READING = "barcode_reading"
    OCR_TEXT_READING = "ocr_text_reading"
    EDGE_DETECTION = "edge_detection"
    TEXTURE_ANALYSIS = "texture_analysis"


@dataclass
class LightingZone:
    """Individual lighting zone configuration."""
    zone_id: str
    lighting_type: LightingType
    position: Tuple[float, float, float]  # X, Y, Z coordinates
    angle: Tuple[float, float]  # Azimuth, elevation angles
    max_intensity: int  # 0-255 or 0-4095 depending on hardware
    current_intensity: int
    color_temperature: int  # Kelvin
    is_active: bool
    wavelength_nm: Optional[int] = None  # For specific wavelength LEDs


@dataclass
class SurfaceProperties:
    """Surface material properties for lighting calculation."""
    surface_type: SurfaceType
    reflectivity_coefficient: float  # 0.0 - 1.0
    specular_reflection: float  # 0.0 - 1.0 (0=diffuse, 1=specular)
    surface_roughness: float  # Ra value in micrometers
    color_rgb: Tuple[int, int, int]
    transparency: float  # 0.0 = opaque, 1.0 = transparent
    preferred_angle: Optional[float] = None  # Optimal lighting angle


@dataclass
class ImageQualityMetrics:
    """Image quality assessment metrics."""
    mean_brightness: float
    contrast_ratio: float
    signal_to_noise_ratio: float
    sharpness_score: float
    histogram_distribution: List[int]
    over_exposed_pixels: int
    under_exposed_pixels: int
    uniformity_score: float


class AdaptiveLightingController:
    """
    Intelligent lighting control system for machine vision applications.

    Features:
    - Automatic intensity adjustment based on material properties
    - Real-time image quality feedback
    - Multi-zone lighting coordination
    - Inspection mode optimization
    - Reflectivity compensation
    - Surface condition adaptation
    """

    def __init__(self, lighting_zones: List[LightingZone]):
        """Initialize the adaptive lighting controller."""
        self.zones = {zone.zone_id: zone for zone in lighting_zones}
        self.logger = logging.getLogger(__name__)
        self.current_surface = None
        self.current_inspection_mode = None
        self.auto_adjustment_enabled = True
        self.learning_mode = False

        # Learning database for surface-lighting combinations
        self.lighting_database = {}

        # Quality thresholds
        self.quality_targets = {
            'min_brightness': 50,
            'max_brightness': 200,
            'min_contrast': 30,
            'min_snr': 20,
            'max_overexposed_percent': 5,
            'max_underexposed_percent': 5,
            'min_uniformity': 0.8
        }

        # Statistics
        self.stats = {
            'adjustments_made': 0,
            'quality_improvements': 0,
            'average_adjustment_time_ms': 0.0,
            'success_rate': 0.0
        }

        if not OPENCV_AVAILABLE:
            self.logger.warning("OpenCV not available, using simulation mode")

    def set_inspection_mode(self, mode: InspectionMode) -> None:
        """Set the current inspection mode."""
        self.current_inspection_mode = mode
        self.logger.info(f"Inspection mode set to: {mode.value}")

        # Apply mode-specific lighting presets
        self._apply_inspection_mode_preset(mode)

    def set_surface_properties(self, surface: SurfaceProperties) -> None:
        """Set current surface properties for adaptive adjustment."""
        self.current_surface = surface
        self.logger.info(
            f"Surface properties set: {surface.surface_type.value}"
        )

        # Trigger automatic adjustment if enabled
        if self.auto_adjustment_enabled:
            asyncio.create_task(self._auto_adjust_for_surface())

    def _apply_inspection_mode_preset(self, mode: InspectionMode) -> None:
        """Apply lighting presets based on inspection mode."""
        presets = {
            InspectionMode.DEFECT_DETECTION: {
                'intensity_factor': 0.8,
                # Multiple angles for shadows
                'preferred_angles': [15, 45, 75],
                'use_darkfield': True
            },
            InspectionMode.DIMENSIONAL_MEASUREMENT: {
                'intensity_factor': 1.0,
                'preferred_angles': [90],  # Direct illumination
                'use_darkfield': False
            },
            InspectionMode.SURFACE_INSPECTION: {
                'intensity_factor': 0.6,
                'preferred_angles': [30, 60],  # Grazing angles
                'use_darkfield': True
            },
            InspectionMode.COLOR_ANALYSIS: {
                'intensity_factor': 0.9,
                'preferred_angles': [45],  # Even illumination
                'use_darkfield': False
            },
            InspectionMode.BARCODE_READING: {
                'intensity_factor': 1.0,
                'preferred_angles': [90],  # High contrast needed
                'use_darkfield': False
            },
            InspectionMode.EDGE_DETECTION: {
                'intensity_factor': 0.7,
                'preferred_angles': [20, 70],  # Side lighting for edges
                'use_darkfield': True
            }
        }

        if mode in presets:
            preset = presets[mode]
            for zone in self.zones.values():
                # Adjust intensity based on mode
                intensity_factor = preset['intensity_factor']
                base_intensity = int(zone.max_intensity * intensity_factor)
                self._set_zone_intensity(zone.zone_id, base_intensity)

    async def _auto_adjust_for_surface(self) -> None:
        """Automatically adjust lighting based on surface properties."""
        if self.current_surface is None:
            return

        start_time = time.time()

        try:
            # Calculate optimal lighting parameters
            optimal_config = self._calculate_optimal_lighting(
                self.current_surface
            )

            # Apply calculated configuration
            for zone_id, config in optimal_config.items():
                if zone_id in self.zones:
                    await self._apply_zone_config(zone_id, config)

            # Record adjustment time
            adjustment_time = (time.time() - start_time) * 1000
            self.stats['adjustments_made'] += 1
            self.stats['average_adjustment_time_ms'] = (
                (self.stats['average_adjustment_time_ms'] *
                 (self.stats['adjustments_made'] - 1) + adjustment_time) /
                self.stats['adjustments_made']
            )

            self.logger.info(
                f"Auto-adjustment completed in {adjustment_time:.1f}ms "
                f"for {self.current_surface.surface_type.value}"
            )

        except Exception as e:
            self.logger.error(f"Auto-adjustment failed: {str(e)}")

    def _calculate_optimal_lighting(
            self, surface: SurfaceProperties) -> Dict[str, Dict]:
        """Calculate optimal lighting configuration for surface."""
        optimal_config = {}

        # Base intensity calculation based on reflectivity
        base_intensity_factor = 1.0 - surface.reflectivity_coefficient * 0.7

        # Angle optimization based on surface type
        if surface.specular_reflection > 0.7:
            # Highly specular - avoid direct angles
            preferred_angles = [30, 150]  # Avoid specular reflection
        elif surface.specular_reflection < 0.3:
            # Diffuse surface - direct lighting OK
            preferred_angles = [45, 90, 135]
        else:
            # Mixed reflection - moderate angles
            preferred_angles = [25, 45, 65]

        for zone in self.zones.values():
            config = {}

            # Calculate intensity for this zone
            zone_angle = self._calculate_zone_angle(zone)

            # Distance factor from preferred angles
            angle_factor = min(
                abs(zone_angle - angle) for angle in preferred_angles
            )
            angle_factor = max(0.3, 1.0 - angle_factor / 90.0)

            # Final intensity calculation
            optimal_intensity = int(
                zone.max_intensity * base_intensity_factor * angle_factor
            )
            optimal_intensity = max(
                0, min(optimal_intensity, zone.max_intensity)
            )

            config['intensity'] = optimal_intensity
            config['active'] = optimal_intensity > zone.max_intensity * 0.1

            optimal_config[zone.zone_id] = config

        return optimal_config

    def _calculate_zone_angle(self, zone: LightingZone) -> float:
        """Calculate effective lighting angle for a zone."""
        # Simplified angle calculation based on position
        # In real implementation, would use actual geometry
        azimuth, elevation = zone.angle
        return elevation  # Use elevation as primary angle

    async def _apply_zone_config(self, zone_id: str, config: Dict) -> None:
        """Apply configuration to a specific lighting zone."""
        if zone_id not in self.zones:
            return

        zone = self.zones[zone_id]

        # Set intensity
        if 'intensity' in config:
            await self._set_zone_intensity_async(zone_id, config['intensity'])

        # Set active state
        if 'active' in config:
            zone.is_active = config['active']

        self.logger.debug(
            f"Zone {zone_id}: intensity={zone.current_intensity}, "
            f"active={zone.is_active}"
        )

    async def _set_zone_intensity_async(
            self, zone_id: str, intensity: int) -> None:
        """Asynchronously set zone intensity with hardware communication."""
        # Simulate hardware communication delay
        await asyncio.sleep(0.01)
        self._set_zone_intensity(zone_id, intensity)

    def _set_zone_intensity(self, zone_id: str, intensity: int) -> None:
        """Set lighting intensity for a specific zone."""
        if zone_id not in self.zones:
            return

        zone = self.zones[zone_id]
        zone.current_intensity = max(0, min(intensity, zone.max_intensity))

        # In real implementation, send command to lighting hardware
        # hardware_interface.set_intensity(zone_id, intensity)

    def analyze_image_quality(self, image: np.ndarray) -> ImageQualityMetrics:
        """Analyze image quality for lighting optimization."""
        if not OPENCV_AVAILABLE:
            # Return mock metrics
            return ImageQualityMetrics(
                mean_brightness=128.0,
                contrast_ratio=50.0,
                signal_to_noise_ratio=25.0,
                sharpness_score=0.8,
                histogram_distribution=[100] * 256,
                over_exposed_pixels=100,
                under_exposed_pixels=200,
                uniformity_score=0.85
            )

        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            # Calculate metrics
            mean_brightness = float(np.mean(gray))

            # Contrast calculation (RMS contrast)
            contrast_ratio = float(np.std(gray))

            # Histogram analysis
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            histogram_distribution = hist.flatten().tolist()

            # Over/under exposure analysis
            over_exposed = np.sum(gray > 240)
            under_exposed = np.sum(gray < 15)

            # Sharpness using Laplacian variance
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(1.0, laplacian_var / 1000.0)

            # Uniformity - coefficient of variation
            uniformity_score = 1.0 - (np.std(gray) / (np.mean(gray) + 1e-6))
            uniformity_score = max(0.0, uniformity_score)

            # Signal-to-noise ratio approximation
            signal = mean_brightness
            # Noise in signal areas
            noise = np.std(gray[gray > mean_brightness * 0.1])
            snr = signal / (noise + 1e-6)

            return ImageQualityMetrics(
                mean_brightness=mean_brightness,
                contrast_ratio=contrast_ratio,
                signal_to_noise_ratio=float(snr),
                sharpness_score=sharpness_score,
                histogram_distribution=histogram_distribution,
                over_exposed_pixels=int(over_exposed),
                under_exposed_pixels=int(under_exposed),
                uniformity_score=float(uniformity_score)
            )

        except Exception as e:
            self.logger.error(f"Image quality analysis failed: {str(e)}")
            return ImageQualityMetrics(
                mean_brightness=0.0,
                contrast_ratio=0.0,
                signal_to_noise_ratio=0.0,
                sharpness_score=0.0,
                histogram_distribution=[],
                over_exposed_pixels=0,
                under_exposed_pixels=0,
                uniformity_score=0.0
            )

    async def optimize_lighting_with_feedback(
            self, capture_function: Callable) -> bool:
        """Optimize lighting using real-time image feedback."""
        max_iterations = 10
        improvement_threshold = 0.05

        try:
            # Initial image capture and analysis
            initial_image = capture_function()
            initial_quality = self.analyze_image_quality(initial_image)

            best_quality_score = self._calculate_quality_score(initial_quality)
            best_config = self._get_current_config()

            self.logger.info(f"Initial quality score: {best_quality_score:.3f}")

            for iteration in range(max_iterations):
                # Generate adjustment strategy
                adjustments = self._generate_adjustments(initial_quality)

                # Apply adjustments
                for zone_id, adjustment in adjustments.items():
                    current_intensity = self.zones[zone_id].current_intensity
                    new_intensity = current_intensity + adjustment
                    await self._set_zone_intensity_async(zone_id, new_intensity)

                # Wait for lighting to stabilize
                await asyncio.sleep(0.1)

                # Capture and analyze new image
                test_image = capture_function()
                test_quality = self.analyze_image_quality(test_image)
                quality_score = self._calculate_quality_score(test_quality)

                # Check for improvement
                if quality_score > best_quality_score + improvement_threshold:
                    best_quality_score = quality_score
                    best_config = self._get_current_config()
                    self.stats['quality_improvements'] += 1

                    self.logger.info(
                        f"Iteration {iteration + 1}: Quality improved to "
                        f"{quality_score:.3f}"
                    )
                else:
                    # Revert to best configuration
                    await self._apply_config(best_config)
                    break

            # Apply final best configuration
            await self._apply_config(best_config)

            final_improvement = best_quality_score - self._calculate_quality_score(initial_quality)

            self.logger.info(
                f"Optimization completed: {final_improvement:.3f} improvement"
            )

            return final_improvement > improvement_threshold

        except Exception as e:
            self.logger.error(f"Lighting optimization failed: {str(e)}")
            return False

    def _calculate_quality_score(self, metrics: ImageQualityMetrics) -> float:
        """Calculate overall quality score from metrics."""
        # Normalize and weight different metrics
        brightness_score = 1.0 - abs(metrics.mean_brightness - 128) / 128.0
        contrast_score = min(1.0, metrics.contrast_ratio / 60.0)
        snr_score = min(1.0, metrics.signal_to_noise_ratio / 30.0)
        sharpness_score = metrics.sharpness_score
        uniformity_score = metrics.uniformity_score

        # Penalty for over/under exposure
        total_pixels = 640 * 480  # Assumed image size
        exposure_penalty = (metrics.over_exposed_pixels +
                          metrics.under_exposed_pixels) / total_pixels

        # Weighted combination
        quality_score = (
            brightness_score * 0.25 +
            contrast_score * 0.25 +
            snr_score * 0.20 +
            sharpness_score * 0.15 +
            uniformity_score * 0.15
        ) - exposure_penalty * 0.5

        return max(0.0, min(1.0, quality_score))

    def _generate_adjustments(self,
                            current_quality: ImageQualityMetrics) -> Dict[str, int]:
        """Generate intensity adjustments based on quality metrics."""
        adjustments = {}

        for zone_id, zone in self.zones.items():
            adjustment = 0

            # Brightness adjustment
            if current_quality.mean_brightness < 80:
                adjustment += 20  # Increase intensity
            elif current_quality.mean_brightness > 180:
                adjustment -= 20  # Decrease intensity

            # Contrast adjustment
            if current_quality.contrast_ratio < 30:
                adjustment += 15  # More directional lighting

            # Over-exposure correction
            if current_quality.over_exposed_pixels > 1000:
                adjustment -= 25

            # Under-exposure correction
            if current_quality.under_exposed_pixels > 2000:
                adjustment += 15

            adjustments[zone_id] = adjustment

        return adjustments

    def _get_current_config(self) -> Dict[str, int]:
        """Get current lighting configuration."""
        return {zone_id: zone.current_intensity
                for zone_id, zone in self.zones.items()}

    async def _apply_config(self, config: Dict[str, int]) -> None:
        """Apply lighting configuration."""
        for zone_id, intensity in config.items():
            await self._set_zone_intensity_async(zone_id, intensity)

    def save_lighting_profile(self, profile_name: str) -> bool:
        """Save current lighting configuration as a profile."""
        try:
            profile = {
                'name': profile_name,
                'timestamp': time.time(),
                'surface_type': (self.current_surface.surface_type.value
                               if self.current_surface else None),
                'inspection_mode': (self.current_inspection_mode.value
                                  if self.current_inspection_mode else None),
                'zones': {
                    zone_id: {
                        'intensity': zone.current_intensity,
                        'active': zone.is_active,
                        'lighting_type': zone.lighting_type.value
                    }
                    for zone_id, zone in self.zones.items()
                }
            }

            # Save to database (simplified - would use proper database)
            profile_key = f"{profile['surface_type']}_{profile['inspection_mode']}"
            self.lighting_database[profile_key] = profile

            self.logger.info(f"Lighting profile '{profile_name}' saved")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save lighting profile: {str(e)}")
            return False

    def load_lighting_profile(self, profile_name: str) -> bool:
        """Load a saved lighting profile."""
        try:
            # Find profile in database
            profile = None
            for stored_profile in self.lighting_database.values():
                if stored_profile['name'] == profile_name:
                    profile = stored_profile
                    break

            if profile is None:
                self.logger.warning(f"Profile '{profile_name}' not found")
                return False

            # Apply profile configuration
            for zone_id, zone_config in profile['zones'].items():
                if zone_id in self.zones:
                    self._set_zone_intensity(zone_id, zone_config['intensity'])
                    self.zones[zone_id].is_active = zone_config['active']

            self.logger.info(f"Lighting profile '{profile_name}' loaded")
            return True

        except Exception as e:
            self.logger.error(f"Failed to load lighting profile: {str(e)}")
            return False

    def get_zone_status(self) -> Dict[str, Dict]:
        """Get current status of all lighting zones."""
        return {
            zone_id: {
                'lighting_type': zone.lighting_type.value,
                'current_intensity': zone.current_intensity,
                'max_intensity': zone.max_intensity,
                'intensity_percent': (zone.current_intensity / zone.max_intensity) * 100,
                'is_active': zone.is_active,
                'position': zone.position,
                'angle': zone.angle
            }
            for zone_id, zone in self.zones.items()
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get lighting control statistics."""
        success_rate = (self.stats['quality_improvements'] /
                       max(1, self.stats['adjustments_made'])) * 100

        return {
            'total_adjustments': self.stats['adjustments_made'],
            'quality_improvements': self.stats['quality_improvements'],
            'success_rate_percent': success_rate,
            'average_adjustment_time_ms': self.stats['average_adjustment_time_ms'],
            'profiles_saved': len(self.lighting_database),
            'zones_configured': len(self.zones),
            'auto_adjustment_enabled': self.auto_adjustment_enabled
        }


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Create sample lighting zones
    zones = [
        LightingZone(
            zone_id="ring_led_01",
            lighting_type=LightingType.LED_RING,
            position=(0, 0, 100),
            angle=(0, 45),
            max_intensity=4095,
            current_intensity=2000,
            color_temperature=6500,
            is_active=True
        ),
        LightingZone(
            zone_id="bar_led_01",
            lighting_type=LightingType.LED_BAR,
            position=(50, 0, 80),
            angle=(30, 30),
            max_intensity=4095,
            current_intensity=1500,
            color_temperature=5000,
            is_active=True
        ),
        LightingZone(
            zone_id="dome_led_01",
            lighting_type=LightingType.LED_DOME,
            position=(0, 0, 120),
            angle=(0, 90),
            max_intensity=4095,
            current_intensity=1000,
            color_temperature=6500,
            is_active=False
        )
    ]

    # Initialize controller
    controller = AdaptiveLightingController(zones)

    # Define surface properties
    metallic_surface = SurfaceProperties(
        surface_type=SurfaceType.METALLIC_POLISHED,
        reflectivity_coefficient=0.8,
        specular_reflection=0.9,
        surface_roughness=0.1,
        color_rgb=(200, 200, 200),
        transparency=0.0
    )

    print("Running adaptive lighting control demonstration...")

    async def demo():
        try:
            # Set inspection mode and surface
            controller.set_inspection_mode(InspectionMode.DEFECT_DETECTION)
            controller.set_surface_properties(metallic_surface)

            # Wait for auto-adjustment
            await asyncio.sleep(0.1)

            print("✅ Lighting automatically adjusted for metallic surface")

            # Show zone status
            status = controller.get_zone_status()
            for zone_id, zone_status in status.items():
                print(f"  {zone_id}: {zone_status['intensity_percent']:.1f}% "
                      f"({zone_status['lighting_type']})")

            # Save profile
            if controller.save_lighting_profile("metallic_defect_detection"):
                print("✅ Lighting profile saved")

            # Mock image quality optimization
            def mock_capture():
                return np.random.randint(0, 255, (480, 640), dtype=np.uint8)

            if await controller.optimize_lighting_with_feedback(mock_capture):
                print("✅ Lighting optimized with feedback")

            # Show final statistics
            stats = controller.get_statistics()
            print(f"✅ Statistics: {stats['success_rate_percent']:.1f}% success rate")

        except Exception as e:
            print(f"❌ Demo failed: {e}")

    # Run demonstration
    asyncio.run(demo())
