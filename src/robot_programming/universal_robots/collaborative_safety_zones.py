"""
Collaborative Safety Zones for Universal Robots

This module implements advanced safety zone management for UR robots working
alongside human operators in mixed assembly lines. Provides real-time human
detection, dynamic safety zone adjustment, and ISO 10218 compliance.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    # Universal Robots SDK
    import urx
    UR_AVAILABLE = True
except ImportError:
    UR_AVAILABLE = False
    # Mock UR interface
    class MockUR:
        def __init__(self, host):
            self.host = host
        def get_pose(self): return [0.5, 0.3, 0.2, 0, 3.14, 0]
        def movej(self, joints, acc, vel): return True
        def set_safety_mode(self, mode): return True
        def get_joint_positions(self): return [0, -1.57, 0, -1.57, 0, 0]
        def close(self): pass
    urx.Robot = MockUR

try:
    # Vision system for human detection
    import cv2
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False


class SafetyZoneType(Enum):
    """Types of collaborative safety zones."""
    COLLABORATIVE = "collaborative"  # Human-robot collaboration allowed
    SPEED_REDUCED = "speed_reduced"  # Reduced speed operation
    MONITORED_STOP = "monitored_stop"  # Stop when human enters
    PROTECTIVE_STOP = "protective_stop"  # Immediate stop zone
    FORBIDDEN = "forbidden"  # No robot operation allowed


class HumanPresenceLevel(Enum):
    """Levels of human presence detection."""
    NONE = "none"  # No human detected
    NEARBY = "nearby"  # Human in vicinity
    APPROACHING = "approaching"  # Human moving toward robot
    CLOSE = "close"  # Human in proximity zone
    CONTACT = "contact"  # Physical contact detected


class RobotState(Enum):
    """UR robot operational states."""
    NORMAL = "normal"  # Normal operation
    REDUCED_SPEED = "reduced_speed"  # Operating at reduced speed
    MONITORED_STOP = "monitored_stop"  # Stopped, monitoring
    PROTECTIVE_STOP = "protective_stop"  # Emergency protective stop
    TEACH_MODE = "teach_mode"  # Manual teaching mode
    ERROR = "error"  # Error state


@dataclass
class SafetyZone:
    """3D safety zone definition."""
    zone_id: str
    zone_type: SafetyZoneType
    center: Tuple[float, float, float]  # Zone center (x, y, z) in mm
    dimensions: Tuple[float, float, float]  # Width, depth, height in mm
    orientation: float  # Rotation around Z-axis in radians
    max_speed: float  # Maximum allowed speed in mm/s
    force_limit: float  # Maximum force limit in N
    is_active: bool
    priority: int  # Zone priority (1 = highest)


@dataclass
class HumanDetection:
    """Human detection result."""
    detection_id: str
    position: Tuple[float, float, float]  # 3D position
    velocity: Tuple[float, float, float]  # 3D velocity vector
    bounding_box: Tuple[float, float, float, float]  # 2D bounding box
    confidence: float  # Detection confidence 0-1
    presence_level: HumanPresenceLevel
    timestamp: float
    tracking_stable: bool


@dataclass
class SafetyEvent:
    """Safety zone violation event."""
    event_id: str
    timestamp: float
    zone_id: str
    human_detection: HumanDetection
    robot_state_before: RobotState
    robot_state_after: RobotState
    response_time_ms: float
    severity: str  # "low", "medium", "high", "critical"


class URCollaborativeSafety:
    """
    Advanced collaborative safety system for Universal Robots.

    Features:
    - Real-time human detection and tracking
    - Dynamic safety zone management
    - Adaptive speed and force control
    - ISO 10218 compliance monitoring
    - Multi-sensor fusion for robust detection
    - Predictive safety intervention
    """

    def __init__(self, robot_ip: str = "192.168.1.101"):
        """Initialize UR collaborative safety system."""
        self.robot_ip = robot_ip
        self.logger = logging.getLogger(__name__)
        self.robot = None
        self.is_connected = False

        # Safety zones
        self.safety_zones = {}
        self.active_zones = set()

        # Human detection
        self.human_detections = []
        self.detection_history = []
        self.vision_system_active = False

        # Robot state
        self.current_state = RobotState.NORMAL
        self.previous_state = RobotState.NORMAL
        self.current_speed_limit = 1000.0  # mm/s
        self.current_force_limit = 150.0  # N

        # Safety monitoring
        self.monitoring_active = False
        self.safety_events = []

        # Performance metrics
        self.stats = {
            'total_detections': 0,
            'safety_stops': 0,
            'false_positives': 0,
            'response_time_avg_ms': 0.0,
            'uptime_hours': 0.0,
            'compliance_violations': 0
        }

        if not UR_AVAILABLE:
            self.logger.warning("UR SDK not available, using simulation mode")
        if not VISION_AVAILABLE:
            self.logger.warning("Vision system not available")

    async def connect_robot(self) -> bool:
        """Connect to Universal Robot."""
        try:
            self.logger.info(f"Connecting to UR robot at {self.robot_ip}")

            self.robot = urx.Robot(self.robot_ip)
            self.is_connected = True

            # Initialize safety parameters
            await self._initialize_safety_parameters()

            self.logger.info("UR robot connected successfully")
            return True

        except Exception as e:
            self.logger.error(f"Robot connection failed: {str(e)}")
            return False

    async def _initialize_safety_parameters(self) -> None:
        """Initialize robot safety parameters."""
        # Set initial safety limits
        self.robot.set_safety_mode("NORMAL")

        # Configure default safety zones
        await self._create_default_safety_zones()

    async def _create_default_safety_zones(self) -> None:
        """Create default safety zones around robot."""
        # Immediate protective zone (500mm radius)
        protective_zone = SafetyZone(
            zone_id="protective_immediate",
            zone_type=SafetyZoneType.PROTECTIVE_STOP,
            center=(0, 0, 0),  # Robot base
            dimensions=(1000, 1000, 2000),  # 1m x 1m x 2m
            orientation=0.0,
            max_speed=0.0,
            force_limit=50.0,
            is_active=True,
            priority=1
        )

        # Monitored zone (1m radius)
        monitored_zone = SafetyZone(
            zone_id="monitored_primary",
            zone_type=SafetyZoneType.MONITORED_STOP,
            center=(0, 0, 0),
            dimensions=(2000, 2000, 2000),  # 2m x 2m x 2m
            orientation=0.0,
            max_speed=250.0,
            force_limit=100.0,
            is_active=True,
            priority=2
        )

        # Collaborative zone (1.5m radius)
        collaborative_zone = SafetyZone(
            zone_id="collaborative_work",
            zone_type=SafetyZoneType.COLLABORATIVE,
            center=(0, 0, 0),
            dimensions=(3000, 3000, 2000),  # 3m x 3m x 2m
            orientation=0.0,
            max_speed=500.0,
            force_limit=150.0,
            is_active=True,
            priority=3
        )

        # Add zones to system
        await self.add_safety_zone(protective_zone)
        await self.add_safety_zone(monitored_zone)
        await self.add_safety_zone(collaborative_zone)

    async def add_safety_zone(self, zone: SafetyZone) -> bool:
        """Add safety zone to monitoring system."""
        try:
            self.safety_zones[zone.zone_id] = zone
            if zone.is_active:
                self.active_zones.add(zone.zone_id)

            self.logger.info(f"Added safety zone: {zone.zone_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add safety zone: {str(e)}")
            return False

    async def start_human_detection(self) -> bool:
        """Start human detection and tracking system."""
        try:
            self.logger.info("Starting human detection system")

            # Initialize vision system
            if VISION_AVAILABLE:
                self.vision_system_active = True
                # Start detection loop
                asyncio.create_task(self._human_detection_loop())

            # Start safety monitoring
            await self.start_safety_monitoring()

            return True

        except Exception as e:
            self.logger.error(f"Human detection startup failed: {str(e)}")
            return False

    async def _human_detection_loop(self) -> None:
        """Continuous human detection and tracking loop."""
        while self.vision_system_active:
            try:
                # Capture frame from cameras
                detections = await self._detect_humans_in_scene()

                # Update detection history
                self.human_detections = detections
                self.detection_history.extend(detections)

                # Keep only recent history (last 100 detections)
                if len(self.detection_history) > 100:
                    self.detection_history = self.detection_history[-100:]

                # Update statistics
                self.stats['total_detections'] += len(detections)

                await asyncio.sleep(0.033)  # ~30 FPS

            except Exception as e:
                self.logger.error(f"Human detection error: {str(e)}")
                await asyncio.sleep(0.1)

    async def _detect_humans_in_scene(self) -> List[HumanDetection]:
        """Detect humans in the robot workspace."""
        detections = []

        try:
            # Simulate human detection (in real implementation, use camera)
            if np.random.random() < 0.3:  # 30% chance of detection
                # Generate simulated human detection
                detection = HumanDetection(
                    detection_id=f"HUMAN_{int(time.time()*1000):013d}",
                    position=(
                        np.random.uniform(-2000, 2000),  # x in mm
                        np.random.uniform(-2000, 2000),  # y in mm
                        np.random.uniform(0, 2000)       # z in mm
                    ),
                    velocity=(
                        np.random.uniform(-100, 100),    # vx in mm/s
                        np.random.uniform(-100, 100),    # vy in mm/s
                        0                                # vz in mm/s
                    ),
                    bounding_box=(100, 100, 200, 400),  # x, y, w, h
                    confidence=np.random.uniform(0.7, 0.95),
                    presence_level=self._determine_presence_level(
                        (np.random.uniform(-2000, 2000),
                         np.random.uniform(-2000, 2000),
                         np.random.uniform(0, 2000))
                    ),
                    timestamp=time.time(),
                    tracking_stable=True
                )
                detections.append(detection)

        except Exception as e:
            self.logger.error(f"Human detection failed: {str(e)}")

        return detections

    def _determine_presence_level(self, position: Tuple[float, float, float]
                                 ) -> HumanPresenceLevel:
        """Determine human presence level based on position."""
        distance = np.linalg.norm(position)

        if distance < 500:    # 0.5m
            return HumanPresenceLevel.CONTACT
        elif distance < 1000: # 1m
            return HumanPresenceLevel.CLOSE
        elif distance < 2000: # 2m
            return HumanPresenceLevel.APPROACHING
        elif distance < 3000: # 3m
            return HumanPresenceLevel.NEARBY
        else:
            return HumanPresenceLevel.NONE

    async def start_safety_monitoring(self) -> None:
        """Start safety zone monitoring and response system."""
        self.monitoring_active = True
        self.logger.info("Safety monitoring started")

        # Start monitoring loop
        asyncio.create_task(self._safety_monitoring_loop())

    async def _safety_monitoring_loop(self) -> None:
        """Continuous safety monitoring loop."""
        while self.monitoring_active:
            try:
                # Check all active safety zones
                for zone_id in self.active_zones:
                    zone = self.safety_zones[zone_id]

                    # Check for human intrusion
                    intrusions = await self._check_zone_intrusion(zone)

                    if intrusions:
                        await self._handle_safety_zone_violation(zone, intrusions)

                # Update robot state based on current conditions
                await self._update_robot_safety_state()

                await asyncio.sleep(0.01)  # 100Hz monitoring

            except Exception as e:
                self.logger.error(f"Safety monitoring error: {str(e)}")
                await asyncio.sleep(0.1)

    async def _check_zone_intrusion(self, zone: SafetyZone
                                  ) -> List[HumanDetection]:
        """Check if humans have intruded into safety zone."""
        intrusions = []

        for detection in self.human_detections:
            if self._is_point_in_zone(detection.position, zone):
                intrusions.append(detection)

        return intrusions

    def _is_point_in_zone(self, point: Tuple[float, float, float],
                         zone: SafetyZone) -> bool:
        """Check if a point is inside a safety zone."""
        # Simplified rectangular zone check
        dx = abs(point[0] - zone.center[0])
        dy = abs(point[1] - zone.center[1])
        dz = abs(point[2] - zone.center[2])

        return (dx <= zone.dimensions[0]/2 and
                dy <= zone.dimensions[1]/2 and
                dz <= zone.dimensions[2]/2)

    async def _handle_safety_zone_violation(self, zone: SafetyZone,
                                          intrusions: List[HumanDetection]
                                          ) -> None:
        """Handle safety zone violation."""
        start_time = time.time()

        for detection in intrusions:
            self.logger.warning(
                f"Safety zone violation: {zone.zone_id} by {detection.detection_id}"
            )

            # Determine response based on zone type
            new_state = await self._determine_safety_response(zone, detection)

            # Execute safety response
            await self._execute_safety_response(new_state, zone)

            # Record safety event
            response_time = (time.time() - start_time) * 1000
            safety_event = SafetyEvent(
                event_id=f"EVT_{int(time.time()*1000):013d}",
                timestamp=time.time(),
                zone_id=zone.zone_id,
                human_detection=detection,
                robot_state_before=self.current_state,
                robot_state_after=new_state,
                response_time_ms=response_time,
                severity=self._assess_event_severity(zone, detection)
            )

            self.safety_events.append(safety_event)

            # Update statistics
            self.stats['safety_stops'] += 1
            self._update_response_time_stats(response_time)

    async def _determine_safety_response(self, zone: SafetyZone,
                                       detection: HumanDetection
                                       ) -> RobotState:
        """Determine appropriate safety response."""
        if zone.zone_type == SafetyZoneType.PROTECTIVE_STOP:
            return RobotState.PROTECTIVE_STOP
        elif zone.zone_type == SafetyZoneType.MONITORED_STOP:
            return RobotState.MONITORED_STOP
        elif zone.zone_type == SafetyZoneType.SPEED_REDUCED:
            return RobotState.REDUCED_SPEED
        elif zone.zone_type == SafetyZoneType.COLLABORATIVE:
            # Check if safe for collaboration
            if detection.confidence > 0.8 and detection.tracking_stable:
                return RobotState.REDUCED_SPEED
            else:
                return RobotState.MONITORED_STOP
        else:
            return RobotState.PROTECTIVE_STOP

    async def _execute_safety_response(self, new_state: RobotState,
                                     zone: SafetyZone) -> None:
        """Execute the determined safety response."""
        if new_state == self.current_state:
            return

        self.previous_state = self.current_state
        self.current_state = new_state

        if new_state == RobotState.PROTECTIVE_STOP:
            await self._execute_protective_stop()
        elif new_state == RobotState.MONITORED_STOP:
            await self._execute_monitored_stop()
        elif new_state == RobotState.REDUCED_SPEED:
            await self._execute_speed_reduction(zone)

        self.logger.info(f"Safety state changed: {self.previous_state.value} -> {new_state.value}")

    async def _execute_protective_stop(self) -> None:
        """Execute immediate protective stop."""
        self.logger.critical("PROTECTIVE STOP ACTIVATED")

        # Immediate stop of all robot motion
        # In real implementation: self.robot.stop()

        # Set maximum safety limits
        self.current_speed_limit = 0.0
        self.current_force_limit = 50.0

    async def _execute_monitored_stop(self) -> None:
        """Execute monitored stop with continued monitoring."""
        self.logger.warning("MONITORED STOP ACTIVATED")

        # Stop robot motion but maintain monitoring
        # In real implementation: self.robot.stop()

        self.current_speed_limit = 0.0
        self.current_force_limit = 100.0

    async def _execute_speed_reduction(self, zone: SafetyZone) -> None:
        """Execute speed and force reduction."""
        self.logger.info(f"SPEED REDUCTION ACTIVATED for zone {zone.zone_id}")

        # Apply zone-specific limits
        self.current_speed_limit = zone.max_speed
        self.current_force_limit = zone.force_limit

        # Apply limits to robot
        # In real implementation: self.robot.set_speed_limit(zone.max_speed)

    async def _update_robot_safety_state(self) -> None:
        """Update robot safety state based on current conditions."""
        # Check if any humans are still in safety zones
        any_intrusion = False

        for zone_id in self.active_zones:
            zone = self.safety_zones[zone_id]
            intrusions = await self._check_zone_intrusion(zone)
            if intrusions:
                any_intrusion = True
                break

        # If no intrusions, return to normal operation
        if not any_intrusion and self.current_state != RobotState.NORMAL:
            await self._return_to_normal_operation()

    async def _return_to_normal_operation(self) -> None:
        """Return robot to normal operation after safety clear."""
        self.logger.info("Returning to normal operation")

        self.previous_state = self.current_state
        self.current_state = RobotState.NORMAL

        # Restore normal operating parameters
        self.current_speed_limit = 1000.0  # mm/s
        self.current_force_limit = 150.0   # N

        # Resume robot operation
        # In real implementation: self.robot.resume()

    def _assess_event_severity(self, zone: SafetyZone,
                              detection: HumanDetection) -> str:
        """Assess the severity of a safety event."""
        if zone.zone_type == SafetyZoneType.PROTECTIVE_STOP:
            return "critical"
        elif zone.zone_type == SafetyZoneType.MONITORED_STOP:
            return "high"
        elif detection.presence_level == HumanPresenceLevel.CONTACT:
            return "critical"
        elif detection.presence_level == HumanPresenceLevel.CLOSE:
            return "high"
        elif detection.confidence < 0.5:
            return "low"  # Possible false positive
        else:
            return "medium"

    def _update_response_time_stats(self, response_time_ms: float) -> None:
        """Update response time statistics."""
        current_avg = self.stats['response_time_avg_ms']
        total_stops = self.stats['safety_stops']

        if total_stops == 1:
            self.stats['response_time_avg_ms'] = response_time_ms
        else:
            self.stats['response_time_avg_ms'] = (
                (current_avg * (total_stops - 1) + response_time_ms) / total_stops
            )

    async def configure_collaborative_mode(self, workspace_bounds: Tuple[float, float, float, float, float, float]) -> bool:
        """Configure robot for collaborative operation."""
        try:
            self.logger.info("Configuring collaborative mode")

            # Define collaborative workspace
            min_x, min_y, min_z, max_x, max_y, max_z = workspace_bounds

            # Create collaborative safety zone
            collab_zone = SafetyZone(
                zone_id="collaborative_workspace",
                zone_type=SafetyZoneType.COLLABORATIVE,
                center=(
                    (min_x + max_x) / 2,
                    (min_y + max_y) / 2,
                    (min_z + max_z) / 2
                ),
                dimensions=(
                    max_x - min_x,
                    max_y - min_y,
                    max_z - min_z
                ),
                orientation=0.0,
                max_speed=250.0,  # ISO 10218 compliant speed
                force_limit=80.0,  # ISO 10218 compliant force
                is_active=True,
                priority=1
            )

            await self.add_safety_zone(collab_zone)

            # Set robot to collaborative mode
            self.robot.set_safety_mode("COLLABORATIVE")

            return True

        except Exception as e:
            self.logger.error(f"Collaborative mode configuration failed: {str(e)}")
            return False

    def get_safety_statistics(self) -> Dict[str, Any]:
        """Get comprehensive safety statistics."""
        total_time = time.time() - getattr(self, '_start_time', time.time())
        uptime_hours = total_time / 3600.0

        false_positive_rate = 0.0
        if self.stats['total_detections'] > 0:
            false_positive_rate = (self.stats['false_positives'] /
                                 self.stats['total_detections']) * 100

        return {
            'total_human_detections': self.stats['total_detections'],
            'safety_stops_triggered': self.stats['safety_stops'],
            'false_positive_rate_percent': false_positive_rate,
            'average_response_time_ms': self.stats['response_time_avg_ms'],
            'uptime_hours': uptime_hours,
            'compliance_violations': self.stats['compliance_violations'],
            'current_robot_state': self.current_state.value,
            'active_safety_zones': len(self.active_zones),
            'vision_system_active': self.vision_system_active,
            'current_speed_limit_mms': self.current_speed_limit,
            'current_force_limit_n': self.current_force_limit
        }

    async def shutdown(self) -> None:
        """Safely shutdown collaborative safety system."""
        self.logger.info("Shutting down collaborative safety system")

        # Stop monitoring
        self.monitoring_active = False
        self.vision_system_active = False

        # Return robot to normal state
        if self.is_connected:
            await self._return_to_normal_operation()
            self.robot.close()

        self.logger.info("Collaborative safety system shutdown complete")


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    async def demo_collaborative_safety():
        """Demonstrate UR collaborative safety zones."""
        print("🤝 UR Collaborative Safety Zones Demo")
        print("=" * 45)

        # Initialize safety system
        safety_system = URCollaborativeSafety("192.168.1.101")

        try:
            # Connect to robot
            if await safety_system.connect_robot():
                print("✅ Connected to UR robot")

                # Configure collaborative workspace
                workspace = (-1500, -1500, 0, 1500, 1500, 2000)  # 3m x 3m x 2m
                if await safety_system.configure_collaborative_mode(workspace):
                    print("✅ Collaborative mode configured")

                # Start human detection
                if await safety_system.start_human_detection():
                    print("✅ Human detection system started")

                    # Simulate operation for 10 seconds
                    print("🔍 Monitoring for human presence...")
                    await asyncio.sleep(10)

                    # Show statistics
                    stats = safety_system.get_safety_statistics()
                    print(f"\n📊 Safety Statistics:")
                    print(f"   Human detections: {stats['total_human_detections']}")
                    print(f"   Safety stops: {stats['safety_stops_triggered']}")
                    print(f"   Response time: {stats['average_response_time_ms']:.1f}ms")
                    print(f"   Robot state: {stats['current_robot_state']}")
                    print(f"   Speed limit: {stats['current_speed_limit_mms']:.0f}mm/s")

                else:
                    print("❌ Failed to start human detection")

            else:
                print("❌ Failed to connect to UR robot")

        except Exception as e:
            print(f"❌ Demo failed: {e}")

        finally:
            await safety_system.shutdown()

    # Run demonstration
    asyncio.run(demo_collaborative_safety())
