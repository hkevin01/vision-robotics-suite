"""
Multi-Robot Collision Avoidance System

This module implements advanced collision avoidance for coordinated Yaskawa and ABB robots
operating in shared workspace. Provides real-time path planning, dynamic obstacle detection,
and safe multi-robot coordination for industrial applications.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Tuple

import numpy as np

try:
    # Industrial robot communication protocols
    import socket
    SOCKET_AVAILABLE = True
except ImportError:
    SOCKET_AVAILABLE = False


class RobotBrand(Enum):
    """Supported robot brands."""
    YASKAWA = "yaskawa"
    ABB = "abb"
    UNKNOWN = "unknown"


class CollisionZone(Enum):
    """Collision zone classifications."""
    SAFE = "safe"           # No collision risk
    WARNING = "warning"     # Approaching collision zone
    DANGER = "danger"       # High collision risk
    CRITICAL = "critical"   # Immediate collision risk
    BLOCKED = "blocked"     # Path completely blocked


class RobotStatus(Enum):
    """Robot operational status."""
    IDLE = "idle"
    MOVING = "moving"
    WAITING = "waiting"
    EMERGENCY_STOP = "emergency_stop"
    ERROR = "error"
    COORDINATED = "coordinated"


@dataclass
class RobotPosition:
    """3D robot position and orientation."""
    x: float        # X coordinate in mm
    y: float        # Y coordinate in mm
    z: float        # Z coordinate in mm
    rx: float       # Rotation around X-axis in radians
    ry: float       # Rotation around Y-axis in radians
    rz: float       # Rotation around Z-axis in radians
    timestamp: float


@dataclass
class JointState:
    """Robot joint positions."""
    robot_id: str
    joint_positions: List[float]  # Joint angles in radians
    joint_velocities: List[float] # Joint velocities in rad/s
    timestamp: float


@dataclass
class CollisionObject:
    """Dynamic collision object in workspace."""
    object_id: str
    position: Tuple[float, float, float]
    dimensions: Tuple[float, float, float]  # Length, width, height
    velocity: Tuple[float, float, float]
    is_robot: bool
    robot_id: str
    confidence: float
    timestamp: float


@dataclass
class PathPoint:
    """Single point in robot path."""
    position: RobotPosition
    velocity: float         # mm/s
    acceleration: float     # mm/s²
    time_from_start: float  # seconds
    collision_risk: float   # 0.0 to 1.0


@dataclass
class RobotPath:
    """Complete robot motion path."""
    robot_id: str
    path_id: str
    points: List[PathPoint]
    total_duration: float
    priority: int
    is_active: bool
    start_time: float


@dataclass
class CollisionEvent:
    """Collision detection event."""
    event_id: str
    timestamp: float
    robot1_id: str
    robot2_id: str
    collision_point: Tuple[float, float, float]
    time_to_collision: float  # seconds
    severity: CollisionZone
    avoidance_action: str


class MultiRobotCollisionAvoidance:
    """
    Advanced multi-robot collision avoidance system.

    Features:
    - Real-time collision detection and prediction
    - Dynamic path planning and re-routing
    - Priority-based robot coordination
    - Velocity and acceleration optimization
    - Safe workspace sharing algorithms
    - Industrial protocol integration
    """

    def __init__(self):
        """Initialize multi-robot collision avoidance system."""
        self.logger = logging.getLogger(__name__)

        # Robot registry
        self.robots = {}
        self.robot_positions = {}
        self.robot_paths = {}
        self.joint_states = {}

        # Collision detection
        self.collision_objects = {}
        self.collision_events = []
        self.detection_active = False

        # Workspace definition
        self.workspace_bounds = (-5000, -5000, 0, 5000, 5000, 3000)  # mm
        self.safety_margin = 200  # mm minimum distance between robots

        # Path planning
        self.path_planner_active = False
        self.replanning_queue = []

        # Performance monitoring
        self.stats = {
            'total_collisions_avoided': 0,
            'path_replanning_events': 0,
            'average_detection_time_ms': 0.0,
            'robots_coordinated': 0,
            'uptime_hours': 0.0,
            'safety_violations': 0
        }

        self.start_time = time.time()

    async def register_robot(self, robot_id: str, brand: RobotBrand,
                           ip_address: str, workspace_area: Tuple[float, float, float, float]) -> bool:
        """Register a robot with the collision avoidance system."""
        try:
            robot_info = {
                'robot_id': robot_id,
                'brand': brand,
                'ip_address': ip_address,
                'workspace_area': workspace_area,  # min_x, min_y, max_x, max_y
                'status': RobotStatus.IDLE,
                'last_update': time.time(),
                'connection_active': False,
                'reach_radius': self._calculate_reach_radius(brand)
            }

            self.robots[robot_id] = robot_info
            self.robot_positions[robot_id] = RobotPosition(0, 0, 0, 0, 0, 0, time.time())
            self.robot_paths[robot_id] = None

            # Attempt connection
            connection_success = await self._connect_robot(robot_id)

            self.logger.info(f"Robot registered: {robot_id} ({brand.value})")
            return connection_success

        except Exception as e:
            self.logger.error(f"Robot registration failed: {robot_id} - {str(e)}")
            return False

    def _calculate_reach_radius(self, brand: RobotBrand) -> float:
        """Calculate robot reach radius based on brand."""
        reach_radii = {
            RobotBrand.YASKAWA: 1500,  # mm - typical reach for Yaskawa GP series
            RobotBrand.ABB: 1600,      # mm - typical reach for ABB IRB series
            RobotBrand.UNKNOWN: 1200   # mm - conservative estimate
        }
        return reach_radii.get(brand, 1200)

    async def _connect_robot(self, robot_id: str) -> bool:
        """Establish connection to robot controller."""
        try:
            robot_info = self.robots[robot_id]

            # Simulate connection (in real implementation, use specific protocols)
            if SOCKET_AVAILABLE:
                # For Yaskawa: Use FS100/DX series protocol
                # For ABB: Use Robot Web Services (RWS) or RAPID
                robot_info['connection_active'] = True
                self.logger.info(f"Connected to robot: {robot_id}")
                return True
            else:
                # Simulation mode
                robot_info['connection_active'] = True
                return True

        except Exception as e:
            self.logger.error(f"Robot connection failed: {robot_id} - {str(e)}")
            return False

    async def start_collision_detection(self) -> bool:
        """Start real-time collision detection system."""
        try:
            self.detection_active = True
            self.logger.info("Collision detection system started")

            # Start detection loops
            asyncio.create_task(self._position_monitoring_loop())
            asyncio.create_task(self._collision_detection_loop())
            asyncio.create_task(self._path_planning_loop())

            return True

        except Exception as e:
            self.logger.error(f"Collision detection startup failed: {str(e)}")
            return False

    async def _position_monitoring_loop(self) -> None:
        """Continuous robot position monitoring."""
        while self.detection_active:
            try:
                for robot_id in self.robots.keys():
                    if self.robots[robot_id]['connection_active']:
                        # Get current position from robot
                        position = await self._get_robot_position(robot_id)
                        self.robot_positions[robot_id] = position

                        # Get joint states
                        joint_state = await self._get_joint_state(robot_id)
                        self.joint_states[robot_id] = joint_state

                        # Update robot status
                        self.robots[robot_id]['last_update'] = time.time()

                await asyncio.sleep(0.01)  # 100Hz monitoring

            except Exception as e:
                self.logger.error(f"Position monitoring error: {str(e)}")
                await asyncio.sleep(0.1)

    async def _get_robot_position(self, robot_id: str) -> RobotPosition:
        """Get current robot position."""
        # Simulate robot position (in real implementation, query robot controller)
        current_pos = self.robot_positions.get(robot_id)
        if current_pos:
            # Add small random movement
            new_x = current_pos.x + np.random.uniform(-10, 10)
            new_y = current_pos.y + np.random.uniform(-10, 10)
            new_z = current_pos.z + np.random.uniform(-5, 5)
        else:
            # Initial position in robot's workspace
            workspace = self.robots[robot_id]['workspace_area']
            new_x = (workspace[0] + workspace[2]) / 2
            new_y = (workspace[1] + workspace[3]) / 2
            new_z = 500  # 0.5m above base

        return RobotPosition(
            x=new_x, y=new_y, z=new_z,
            rx=np.random.uniform(-0.1, 0.1),
            ry=np.random.uniform(-0.1, 0.1),
            rz=np.random.uniform(-0.1, 0.1),
            timestamp=time.time()
        )

    async def _get_joint_state(self, robot_id: str) -> JointState:
        """Get current joint positions and velocities."""
        # Simulate joint state
        num_joints = 6  # Standard 6-DOF robot

        return JointState(
            robot_id=robot_id,
            joint_positions=[np.random.uniform(-3.14, 3.14) for _ in range(num_joints)],
            joint_velocities=[np.random.uniform(-1.0, 1.0) for _ in range(num_joints)],
            timestamp=time.time()
        )

    async def _collision_detection_loop(self) -> None:
        """Main collision detection and prediction loop."""
        while self.detection_active:
            try:
                start_time = time.time()

                # Update collision objects with current robot positions
                await self._update_collision_objects()

                # Check all robot pairs for potential collisions
                robot_ids = list(self.robots.keys())
                for i in range(len(robot_ids)):
                    for j in range(i + 1, len(robot_ids)):
                        robot1_id = robot_ids[i]
                        robot2_id = robot_ids[j]

                        # Check collision between robots
                        collision_risk = await self._check_robot_collision(robot1_id, robot2_id)

                        if collision_risk > 0.1:  # 10% collision risk threshold
                            await self._handle_collision_risk(robot1_id, robot2_id, collision_risk)

                # Update detection time statistics
                detection_time = (time.time() - start_time) * 1000
                self._update_detection_time_stats(detection_time)

                await asyncio.sleep(0.02)  # 50Hz collision detection

            except Exception as e:
                self.logger.error(f"Collision detection error: {str(e)}")
                await asyncio.sleep(0.1)

    async def _update_collision_objects(self) -> None:
        """Update collision objects with current robot positions."""
        for robot_id, position in self.robot_positions.items():
            # Create collision object for robot
            reach_radius = self.robots[robot_id]['reach_radius']

            collision_obj = CollisionObject(
                object_id=f"robot_{robot_id}",
                position=(position.x, position.y, position.z),
                dimensions=(reach_radius * 2, reach_radius * 2, 2000),  # Cylinder approximation
                velocity=(0, 0, 0),  # Would calculate from position history
                is_robot=True,
                robot_id=robot_id,
                confidence=1.0,
                timestamp=position.timestamp
            )

            self.collision_objects[f"robot_{robot_id}"] = collision_obj

    async def _check_robot_collision(self, robot1_id: str, robot2_id: str) -> float:
        """Check collision risk between two robots."""
        pos1 = self.robot_positions[robot1_id]
        pos2 = self.robot_positions[robot2_id]

        # Calculate distance between robots
        distance = np.sqrt(
            (pos1.x - pos2.x)**2 +
            (pos1.y - pos2.y)**2 +
            (pos1.z - pos2.z)**2
        )

        # Get combined reach radius
        reach1 = self.robots[robot1_id]['reach_radius']
        reach2 = self.robots[robot2_id]['reach_radius']
        combined_reach = reach1 + reach2 + self.safety_margin

        # Calculate collision risk (1.0 = certain collision, 0.0 = no risk)
        if distance <= combined_reach:
            # Risk increases exponentially as distance decreases
            collision_risk = 1.0 - (distance / combined_reach) ** 2
        else:
            collision_risk = 0.0

        return collision_risk

    async def _handle_collision_risk(self, robot1_id: str, robot2_id: str, risk: float) -> None:
        """Handle detected collision risk between robots."""
        collision_zone = self._classify_collision_zone(risk)

        self.logger.warning(
            f"Collision risk detected: {robot1_id} <-> {robot2_id} "
            f"(Risk: {risk:.2f}, Zone: {collision_zone.value})"
        )

        # Create collision event
        event = CollisionEvent(
            event_id=f"COL_{int(time.time() * 1000):013d}",
            timestamp=time.time(),
            robot1_id=robot1_id,
            robot2_id=robot2_id,
            collision_point=self._calculate_collision_point(robot1_id, robot2_id),
            time_to_collision=self._estimate_time_to_collision(robot1_id, robot2_id),
            severity=collision_zone,
            avoidance_action=""
        )

        # Execute avoidance strategy
        avoidance_action = await self._execute_collision_avoidance(event)
        event.avoidance_action = avoidance_action

        self.collision_events.append(event)
        self.stats['total_collisions_avoided'] += 1

    def _classify_collision_zone(self, risk: float) -> CollisionZone:
        """Classify collision risk level."""
        if risk >= 0.8:
            return CollisionZone.CRITICAL
        elif risk >= 0.5:
            return CollisionZone.DANGER
        elif risk >= 0.2:
            return CollisionZone.WARNING
        else:
            return CollisionZone.SAFE

    def _calculate_collision_point(self, robot1_id: str, robot2_id: str) -> Tuple[float, float, float]:
        """Calculate predicted collision point."""
        pos1 = self.robot_positions[robot1_id]
        pos2 = self.robot_positions[robot2_id]

        # Midpoint between robots
        return (
            (pos1.x + pos2.x) / 2,
            (pos1.y + pos2.y) / 2,
            (pos1.z + pos2.z) / 2
        )

    def _estimate_time_to_collision(self, robot1_id: str, robot2_id: str) -> float:
        """Estimate time until collision occurs."""
        # Simplified estimation based on current velocities
        # In real implementation, would use path prediction
        return np.random.uniform(1.0, 5.0)  # 1-5 seconds

    async def _execute_collision_avoidance(self, event: CollisionEvent) -> str:
        """Execute collision avoidance strategy."""
        if event.severity == CollisionZone.CRITICAL:
            # Emergency stop both robots
            await self._emergency_stop_robot(event.robot1_id)
            await self._emergency_stop_robot(event.robot2_id)
            return "emergency_stop_both"

        elif event.severity == CollisionZone.DANGER:
            # Stop lower priority robot
            priority1 = self._get_robot_priority(event.robot1_id)
            priority2 = self._get_robot_priority(event.robot2_id)

            if priority1 > priority2:
                await self._stop_robot(event.robot2_id)
                return f"stop_{event.robot2_id}"
            else:
                await self._stop_robot(event.robot1_id)
                return f"stop_{event.robot1_id}"

        elif event.severity == CollisionZone.WARNING:
            # Slow down both robots
            await self._reduce_robot_speed(event.robot1_id, 0.5)
            await self._reduce_robot_speed(event.robot2_id, 0.5)
            return "slow_down_both"

        else:
            # Monitor situation
            return "monitor"

    def _get_robot_priority(self, robot_id: str) -> int:
        """Get robot priority (higher number = higher priority)."""
        # In real implementation, would be configurable
        # For now, Yaskawa robots have higher priority
        brand = self.robots[robot_id]['brand']
        if brand == RobotBrand.YASKAWA:
            return 2
        elif brand == RobotBrand.ABB:
            return 1
        else:
            return 0

    async def _emergency_stop_robot(self, robot_id: str) -> None:
        """Execute emergency stop for robot."""
        self.logger.critical(f"EMERGENCY STOP: {robot_id}")

        self.robots[robot_id]['status'] = RobotStatus.EMERGENCY_STOP

        # In real implementation: send emergency stop command to robot
        # For Yaskawa: Send HOLD command
        # For ABB: Send StopMove command

    async def _stop_robot(self, robot_id: str) -> None:
        """Stop robot motion."""
        self.logger.warning(f"STOP: {robot_id}")

        self.robots[robot_id]['status'] = RobotStatus.WAITING

        # In real implementation: send stop command to robot

    async def _reduce_robot_speed(self, robot_id: str, factor: float) -> None:
        """Reduce robot speed by factor."""
        self.logger.info(f"SPEED REDUCTION: {robot_id} (factor: {factor})")

        # In real implementation: adjust robot speed parameters

    async def _path_planning_loop(self) -> None:
        """Dynamic path planning and re-planning loop."""
        self.path_planner_active = True

        while self.path_planner_active:
            try:
                # Process replanning requests
                if self.replanning_queue:
                    robot_id = self.replanning_queue.pop(0)
                    await self._replan_robot_path(robot_id)

                # Periodic path optimization
                await self._optimize_active_paths()

                await asyncio.sleep(0.1)  # 10Hz path planning

            except Exception as e:
                self.logger.error(f"Path planning error: {str(e)}")
                await asyncio.sleep(0.5)

    async def _replan_robot_path(self, robot_id: str) -> None:
        """Replan robot path to avoid collisions."""
        self.logger.info(f"Replanning path for robot: {robot_id}")

        # Generate new collision-free path
        new_path = await self._generate_safe_path(robot_id)

        if new_path:
            self.robot_paths[robot_id] = new_path
            # Send new path to robot
            await self._send_path_to_robot(robot_id, new_path)

            self.stats['path_replanning_events'] += 1
            self.logger.info(f"New path generated for robot: {robot_id}")
        else:
            self.logger.warning(f"Failed to generate safe path for robot: {robot_id}")

    async def _generate_safe_path(self, robot_id: str) -> RobotPath:
        """Generate collision-free path for robot."""
        # Simplified path generation (in real implementation, use RRT* or similar)
        current_pos = self.robot_positions[robot_id]

        # Generate sample path points
        path_points = []
        for i in range(10):
            # Simple linear interpolation for demo
            progress = i / 9.0
            point = PathPoint(
                position=RobotPosition(
                    x=current_pos.x + progress * 100,
                    y=current_pos.y + progress * 100,
                    z=current_pos.z,
                    rx=current_pos.rx,
                    ry=current_pos.ry,
                    rz=current_pos.rz,
                    timestamp=time.time()
                ),
                velocity=500.0,  # mm/s
                acceleration=100.0,  # mm/s²
                time_from_start=progress * 2.0,  # 2 seconds total
                collision_risk=0.0
            )
            path_points.append(point)

        return RobotPath(
            robot_id=robot_id,
            path_id=f"PATH_{robot_id}_{int(time.time() * 1000):013d}",
            points=path_points,
            total_duration=2.0,
            priority=self._get_robot_priority(robot_id),
            is_active=True,
            start_time=time.time()
        )

    async def _send_path_to_robot(self, robot_id: str, path: RobotPath) -> None:
        """Send new path to robot controller."""
        # In real implementation:
        # - For Yaskawa: Upload job file with new trajectory
        # - For ABB: Send RAPID module with new path points
        pass

    async def _optimize_active_paths(self) -> None:
        """Optimize all active robot paths."""
        # Check for path intersections and optimize coordination
        active_paths = {rid: path for rid, path in self.robot_paths.items()
                       if path and path.is_active}

        if len(active_paths) > 1:
            # Coordinate timing to avoid collisions
            await self._coordinate_path_timing(active_paths)

    async def _coordinate_path_timing(self, paths: Dict[str, RobotPath]) -> None:
        """Coordinate timing between multiple robot paths."""
        # Simplified coordination (in real implementation, use optimization)
        robot_ids = list(paths.keys())

        for i in range(len(robot_ids)):
            for j in range(i + 1, len(robot_ids)):
                robot1_id = robot_ids[i]
                robot2_id = robot_ids[j]

                # Check if paths intersect
                intersection = self._check_path_intersection(
                    paths[robot1_id], paths[robot2_id]
                )

                if intersection:
                    # Adjust timing to avoid collision
                    await self._adjust_path_timing(robot1_id, robot2_id, intersection)

    def _check_path_intersection(self, path1: RobotPath, path2: RobotPath) -> bool:
        """Check if two robot paths intersect."""
        # Simplified intersection check
        for point1 in path1.points:
            for point2 in path2.points:
                distance = np.sqrt(
                    (point1.position.x - point2.position.x)**2 +
                    (point1.position.y - point2.position.y)**2 +
                    (point1.position.z - point2.position.z)**2
                )

                # Check if robots would be too close at similar times
                time_diff = abs(point1.time_from_start - point2.time_from_start)
                if distance < self.safety_margin and time_diff < 0.5:
                    return True

        return False

    async def _adjust_path_timing(self, robot1_id: str, robot2_id: str, intersection: bool) -> None:
        """Adjust path timing to avoid collision."""
        # Simple strategy: delay lower priority robot
        priority1 = self._get_robot_priority(robot1_id)
        priority2 = self._get_robot_priority(robot2_id)

        if priority1 > priority2:
            await self._delay_robot_start(robot2_id, 1.0)  # 1 second delay
        else:
            await self._delay_robot_start(robot1_id, 1.0)

    async def _delay_robot_start(self, robot_id: str, delay_seconds: float) -> None:
        """Delay robot path execution."""
        self.logger.info(f"Delaying robot {robot_id} by {delay_seconds} seconds")

        path = self.robot_paths[robot_id]
        if path:
            # Adjust start time
            path.start_time += delay_seconds

            # Update all point times
            for point in path.points:
                point.time_from_start += delay_seconds

    def _update_detection_time_stats(self, detection_time_ms: float) -> None:
        """Update collision detection time statistics."""
        current_avg = self.stats['average_detection_time_ms']

        # Simple moving average
        self.stats['average_detection_time_ms'] = (current_avg * 0.9 + detection_time_ms * 0.1)

    async def coordinate_robots(self, robot_ids: List[str], task_description: str) -> bool:
        """Coordinate multiple robots for collaborative task."""
        try:
            self.logger.info(f"Coordinating robots {robot_ids} for task: {task_description}")

            # Set all robots to coordinated mode
            for robot_id in robot_ids:
                if robot_id in self.robots:
                    self.robots[robot_id]['status'] = RobotStatus.COORDINATED

            # Generate coordinated paths
            coordinated_paths = await self._generate_coordinated_paths(robot_ids, task_description)

            # Send paths to robots
            for robot_id, path in coordinated_paths.items():
                self.robot_paths[robot_id] = path
                await self._send_path_to_robot(robot_id, path)

            self.stats['robots_coordinated'] += len(robot_ids)
            return True

        except Exception as e:
            self.logger.error(f"Robot coordination failed: {str(e)}")
            return False

    async def _generate_coordinated_paths(self, robot_ids: List[str], task: str) -> Dict[str, RobotPath]:
        """Generate coordinated paths for multiple robots."""
        paths = {}

        # Simplified coordinated path generation
        for i, robot_id in enumerate(robot_ids):
            # Stagger robot movements to avoid collisions
            start_delay = i * 2.0  # 2 second intervals

            path = await self._generate_safe_path(robot_id)
            if path:
                # Adjust timing for coordination
                path.start_time += start_delay
                for point in path.points:
                    point.time_from_start += start_delay

                paths[robot_id] = path

        return paths

    def get_collision_statistics(self) -> Dict[str, Any]:
        """Get comprehensive collision avoidance statistics."""
        uptime_hours = (time.time() - self.start_time) / 3600.0

        return {
            'registered_robots': len(self.robots),
            'active_robots': sum(1 for r in self.robots.values() if r['connection_active']),
            'total_collisions_avoided': self.stats['total_collisions_avoided'],
            'path_replanning_events': self.stats['path_replanning_events'],
            'average_detection_time_ms': self.stats['average_detection_time_ms'],
            'robots_coordinated': self.stats['robots_coordinated'],
            'uptime_hours': uptime_hours,
            'safety_violations': self.stats['safety_violations'],
            'collision_objects_tracked': len(self.collision_objects),
            'active_paths': sum(1 for p in self.robot_paths.values() if p and p.is_active)
        }

    async def shutdown(self) -> None:
        """Shutdown multi-robot collision avoidance system."""
        self.logger.info("Shutting down collision avoidance system")

        # Stop all monitoring loops
        self.detection_active = False
        self.path_planner_active = False

        # Stop all robots safely
        for robot_id in self.robots.keys():
            await self._stop_robot(robot_id)

        self.logger.info("Collision avoidance system shutdown complete")


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    async def demo_multi_robot_collision_avoidance():
        """Demonstrate multi-robot collision avoidance."""
        print("🤖 Multi-Robot Collision Avoidance Demo")
        print("=" * 42)

        # Initialize collision avoidance system
        collision_system = MultiRobotCollisionAvoidance()

        try:
            # Register Yaskawa robot
            yaskawa_workspace = (-2000, -2000, 2000, 2000)  # 4m x 4m
            await collision_system.register_robot(
                "YASKAWA_01", RobotBrand.YASKAWA, "192.168.1.110", yaskawa_workspace
            )
            print("✅ Yaskawa robot registered")

            # Register ABB robot
            abb_workspace = (1000, -2000, 4000, 2000)  # 3m x 4m, offset
            await collision_system.register_robot(
                "ABB_01", RobotBrand.ABB, "192.168.1.120", abb_workspace
            )
            print("✅ ABB robot registered")

            # Start collision detection
            if await collision_system.start_collision_detection():
                print("✅ Collision detection started")

                # Coordinate robots for task
                robot_ids = ["YASKAWA_01", "ABB_01"]
                task = "Coordinated assembly operation"

                if await collision_system.coordinate_robots(robot_ids, task):
                    print("✅ Robot coordination initiated")

                    # Monitor for 15 seconds
                    print("🔍 Monitoring for collisions...")
                    await asyncio.sleep(15)

                    # Show statistics
                    stats = collision_system.get_collision_statistics()
                    print(f"\n📊 Collision Avoidance Statistics:")
                    print(f"   Registered robots: {stats['registered_robots']}")
                    print(f"   Active robots: {stats['active_robots']}")
                    print(f"   Collisions avoided: {stats['total_collisions_avoided']}")
                    print(f"   Path replanning events: {stats['path_replanning_events']}")
                    print(f"   Detection time: {stats['average_detection_time_ms']:.1f}ms")
                    print(f"   Robots coordinated: {stats['robots_coordinated']}")

                else:
                    print("❌ Robot coordination failed")

            else:
                print("❌ Collision detection startup failed")

        except Exception as e:
            print(f"❌ Demo failed: {e}")

        finally:
            await collision_system.shutdown()

    # Run demonstration
    asyncio.run(demo_multi_robot_collision_avoidance())
