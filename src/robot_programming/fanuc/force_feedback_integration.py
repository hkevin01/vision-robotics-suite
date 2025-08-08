"""
FANUC Force-Feedback Integration for Delicate Assembly Operations

This module implements advanced force and torque monitoring capabilities for
FANUC R-30iB controllers performing precision assembly tasks requiring
haptic feedback. Designed for automotive engine assembly and electronic
component placement.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

try:
    # FANUC ROBOGUIDE integration (proprietary)
    import fanuc_robot_interface as fanuc
    FANUC_AVAILABLE = True
except ImportError:
    FANUC_AVAILABLE = False
    # Mock FANUC interface for development

    class MockFanuc:
        def connect(self): return True
        def get_position(self): return [100, 200, 300, 0, 90, 0]
        def get_force_torque(self): return [0.1, 0.2, 0.3, 0.01, 0.02, 0.03]
        def move_linear(self, position, speed):
            # Mock implementation
            return True
        def set_force_mode(self, enabled):
            # Mock implementation
            return True
        def emergency_stop(self): return True
    fanuc = MockFanuc()


class AssemblyOperation(Enum):
    """Types of delicate assembly operations."""
    COMPONENT_INSERTION = "component_insertion"
    BEARING_INSTALLATION = "bearing_installation"
    GASKET_PLACEMENT = "gasket_placement"
    SCREW_FASTENING = "screw_fastening"
    CONNECTOR_MATING = "connector_mating"
    PRECISION_ALIGNMENT = "precision_alignment"
    SURFACE_POLISHING = "surface_polishing"
    THREAD_CUTTING = "thread_cutting"


class ForceControlMode(Enum):
    """Force control operation modes."""
    POSITION_BASED = "position_based"
    FORCE_BASED = "force_based"
    HYBRID_CONTROL = "hybrid_control"
    COMPLIANCE_MODE = "compliance_mode"
    IMPEDANCE_CONTROL = "impedance_control"


class SafetyState(Enum):
    """Robot safety states during force operations."""
    NORMAL = "normal"
    FORCE_LIMIT_EXCEEDED = "force_limit_exceeded"
    TORQUE_LIMIT_EXCEEDED = "torque_limit_exceeded"
    CONTACT_DETECTED = "contact_detected"
    EMERGENCY_STOP = "emergency_stop"
    CALIBRATION_REQUIRED = "calibration_required"


@dataclass
class ForceVector:
    """3D force and torque measurements."""
    fx: float  # Force X (N)
    fy: float  # Force Y (N)
    fz: float  # Force Z (N)
    tx: float  # Torque X (Nm)
    ty: float  # Torque Y (Nm)
    tz: float  # Torque Z (Nm)
    timestamp: float

    @property
    def magnitude(self) -> float:
        """Calculate force magnitude."""
        return np.sqrt(self.fx**2 + self.fy**2 + self.fz**2)

    @property
    def torque_magnitude(self) -> float:
        """Calculate torque magnitude."""
        return np.sqrt(self.tx**2 + self.ty**2 + self.tz**2)


@dataclass
class AssemblyParameters:
    """Parameters for delicate assembly operations."""
    operation_type: AssemblyOperation
    max_force_x: float = 10.0  # Maximum force in X direction (N)
    max_force_y: float = 10.0  # Maximum force in Y direction (N)
    max_force_z: float = 15.0  # Maximum force in Z direction (N)
    max_torque_x: float = 1.0  # Maximum torque around X axis (Nm)
    max_torque_y: float = 1.0  # Maximum torque around Y axis (Nm)
    max_torque_z: float = 1.0  # Maximum torque around Z axis (Nm)
    approach_speed: float = 10.0  # mm/s
    insertion_speed: float = 2.0  # mm/s
    force_threshold: float = 5.0  # Contact detection threshold (N)
    compliance_stiffness: float = 100.0  # N/mm
    damping_ratio: float = 0.7
    position_tolerance: float = 0.1  # mm
    force_timeout: float = 30.0  # seconds


@dataclass
class AssemblyResult:
    """Result of assembly operation."""
    operation_id: str
    success: bool
    completion_time: float
    max_force_recorded: ForceVector
    position_accuracy: float
    force_profile: List[ForceVector]
    error_message: Optional[str] = None
    quality_score: float = 0.0


class FanucForceController:
    """
    Advanced force-feedback controller for FANUC robots.

    Features:
    - Real-time force/torque monitoring (1kHz sampling)
    - Adaptive force control with compliance
    - Contact detection and response
    - Multi-axis force limiting
    - Assembly operation optimization
    - Safety monitoring and emergency stops
    """

    def __init__(self, robot_ip: str = "192.168.1.100"):
        """Initialize FANUC force controller."""
        self.robot_ip = robot_ip
        self.logger = logging.getLogger(__name__)
        self.is_connected = False
        self.force_sensor_calibrated = False
        self.current_operation = None
        self.safety_state = SafetyState.NORMAL

        # Force monitoring
        self.force_history = []
        self.monitoring_active = False
        self.sample_rate = 1000  # Hz

        # Control parameters
        self.control_mode = ForceControlMode.POSITION_BASED
        self.force_feedback_gains = {
            'kp': 0.1,  # Proportional gain
            'ki': 0.01,  # Integral gain
            'kd': 0.05  # Derivative gain
        }

        # Statistics
        self.stats = {
            'operations_completed': 0,
            'successful_operations': 0,
            'force_violations': 0,
            'emergency_stops': 0,
            'avg_cycle_time': 0.0,
            'uptime_hours': 0.0
        }

        if not FANUC_AVAILABLE:
            self.logger.warning(
                "FANUC interface not available, using simulation mode"
            )

    async def connect_robot(self) -> bool:
        """Connect to FANUC robot controller."""
        try:
            self.logger.info(f"Connecting to FANUC robot at {self.robot_ip}")

            # Initialize robot connection
            if fanuc.connect():
                self.is_connected = True
                self.logger.info("FANUC robot connected successfully")

                # Initialize force sensor
                await self.calibrate_force_sensor()
                return True
            else:
                self.logger.error("Failed to connect to FANUC robot")
                return False

        except Exception as e:
            self.logger.error(f"Robot connection failed: {str(e)}")
            return False

    async def calibrate_force_sensor(self) -> bool:
        """Calibrate force/torque sensor for accurate measurements."""
        try:
            self.logger.info("Calibrating force sensor...")

            # Record baseline measurements (robot stationary)
            baseline_samples = []
            for _ in range(100):
                force_data = fanuc.get_force_torque()
                baseline_samples.append(force_data)
                await asyncio.sleep(0.001)  # 1ms sampling

            # Calculate offset compensation
            baseline_avg = np.mean(baseline_samples, axis=0)
            self.force_offset = baseline_avg

            self.force_sensor_calibrated = True
            self.logger.info("Force sensor calibration completed")
            return True

        except Exception as e:
            self.logger.error(f"Force sensor calibration failed: {str(e)}")
            return False

    async def start_force_monitoring(self) -> None:
        """Start real-time force monitoring."""
        if not self.is_connected or not self.force_sensor_calibrated:
            raise RuntimeError("Robot not connected or force sensor not calibrated")

        self.monitoring_active = True
        self.logger.info("Force monitoring started")

        # Start monitoring task
        asyncio.create_task(self._force_monitoring_loop())

    async def _force_monitoring_loop(self) -> None:
        """Continuous force monitoring loop."""
        while self.monitoring_active:
            try:
                # Read force/torque data
                raw_data = fanuc.get_force_torque()
                compensated_data = np.array(raw_data) - self.force_offset

                # Create force vector
                force_vector = ForceVector(
                    fx=compensated_data[0],
                    fy=compensated_data[1],
                    fz=compensated_data[2],
                    tx=compensated_data[3],
                    ty=compensated_data[4],
                    tz=compensated_data[5],
                    timestamp=time.time()
                )

                # Store in history (keep last 1000 samples)
                self.force_history.append(force_vector)
                if len(self.force_history) > 1000:
                    self.force_history.pop(0)

                # Check safety limits
                await self._check_safety_limits(force_vector)

                # Sleep for next sample
                await asyncio.sleep(1.0 / self.sample_rate)

            except Exception as e:
                self.logger.error(f"Force monitoring error: {str(e)}")
                await asyncio.sleep(0.01)

    async def _check_safety_limits(self, force_vector: ForceVector) -> None:
        """Check force/torque safety limits."""
        if self.current_operation is None:
            return

        params = self.current_operation

        # Check force limits
        if (abs(force_vector.fx) > params.max_force_x or
            abs(force_vector.fy) > params.max_force_y or
            abs(force_vector.fz) > params.max_force_z):

            self.safety_state = SafetyState.FORCE_LIMIT_EXCEEDED
            self.stats['force_violations'] += 1
            await self._handle_safety_violation("Force limit exceeded")

        # Check torque limits
        if (abs(force_vector.tx) > params.max_torque_x or
            abs(force_vector.ty) > params.max_torque_y or
            abs(force_vector.tz) > params.max_torque_z):

            self.safety_state = SafetyState.TORQUE_LIMIT_EXCEEDED
            self.stats['force_violations'] += 1
            await self._handle_safety_violation("Torque limit exceeded")

    async def _handle_safety_violation(self, reason: str) -> None:
        """Handle safety limit violations."""
        self.logger.warning(f"Safety violation: {reason}")

        # Stop robot motion
        await self.emergency_stop()

        # Trigger safety callback if registered
        # await self.safety_callback(reason) if self.safety_callback else None

    async def emergency_stop(self) -> bool:
        """Execute emergency stop procedure."""
        try:
            self.logger.critical("EMERGENCY STOP INITIATED")
            self.safety_state = SafetyState.EMERGENCY_STOP
            self.stats['emergency_stops'] += 1

            # Stop robot immediately
            fanuc.emergency_stop()

            # Disable force mode
            fanuc.set_force_mode(False)

            return True

        except Exception as e:
            self.logger.error(f"Emergency stop failed: {str(e)}")
            return False

    async def perform_delicate_assembly(self, params: AssemblyParameters,
                                      target_position: List[float],
                                      approach_position: List[float]) -> AssemblyResult:
        """
        Perform delicate assembly operation with force feedback.

        Args:
            params: Assembly operation parameters
            target_position: Final assembly position [x, y, z, rx, ry, rz]
            approach_position: Safe approach position

        Returns:
            AssemblyResult with operation outcome
        """
        operation_id = f"ASM_{int(time.time()*1000):013d}"
        start_time = time.time()

        try:
            self.logger.info(f"Starting {params.operation_type.value} operation {operation_id}")

            # Set current operation for safety monitoring
            self.current_operation = params
            self.safety_state = SafetyState.NORMAL

            # Clear force history
            self.force_history.clear()

            # Move to approach position
            await self._move_to_approach_position(approach_position, params.approach_speed)

            # Switch to force control mode
            await self._enable_force_control(params)

            # Perform assembly operation based on type
            success = await self._execute_assembly_operation(params, target_position)

            # Calculate completion time
            completion_time = time.time() - start_time

            # Analyze force profile
            max_force = self._get_max_force_recorded()
            position_accuracy = await self._measure_position_accuracy(target_position)
            quality_score = self._calculate_quality_score(params)

            # Update statistics
            self.stats['operations_completed'] += 1
            if success:
                self.stats['successful_operations'] += 1

            # Update average cycle time
            total_time = (self.stats['avg_cycle_time'] *
                         (self.stats['operations_completed'] - 1) + completion_time)
            self.stats['avg_cycle_time'] = total_time / self.stats['operations_completed']

            # Return result
            return AssemblyResult(
                operation_id=operation_id,
                success=success,
                completion_time=completion_time,
                max_force_recorded=max_force,
                position_accuracy=position_accuracy,
                force_profile=self.force_history.copy(),
                quality_score=quality_score
            )

        except Exception as e:
            error_message = f"Assembly operation failed: {str(e)}"
            self.logger.error(error_message)

            return AssemblyResult(
                operation_id=operation_id,
                success=False,
                completion_time=time.time() - start_time,
                max_force_recorded=ForceVector(0, 0, 0, 0, 0, 0, time.time()),
                position_accuracy=float('inf'),
                force_profile=[],
                error_message=error_message,
                quality_score=0.0
            )

        finally:
            # Always disable force control and return to position mode
            await self._disable_force_control()
            self.current_operation = None

    async def _move_to_approach_position(self, position: List[float], speed: float) -> None:
        """Move robot to approach position safely."""
        self.logger.debug(f"Moving to approach position: {position}")
        fanuc.move_linear(position, speed)

        # Wait for motion completion
        await asyncio.sleep(0.1)

    async def _enable_force_control(self, params: AssemblyParameters) -> None:
        """Enable force control mode with specified parameters."""
        self.logger.debug("Enabling force control mode")

        # Configure force control parameters
        fanuc.set_force_mode(True)

        # Set compliance parameters
        self.control_mode = ForceControlMode.HYBRID_CONTROL

    async def _disable_force_control(self) -> None:
        """Disable force control and return to position mode."""
        self.logger.debug("Disabling force control mode")
        fanuc.set_force_mode(False)
        self.control_mode = ForceControlMode.POSITION_BASED

    async def _execute_assembly_operation(self, params: AssemblyParameters,
                                        target_position: List[float]) -> bool:
        """Execute specific assembly operation with force guidance."""

        if params.operation_type == AssemblyOperation.COMPONENT_INSERTION:
            return await self._perform_component_insertion(params, target_position)
        elif params.operation_type == AssemblyOperation.BEARING_INSTALLATION:
            return await self._perform_bearing_installation(params, target_position)
        elif params.operation_type == AssemblyOperation.SCREW_FASTENING:
            return await self._perform_screw_fastening(params, target_position)
        elif params.operation_type == AssemblyOperation.CONNECTOR_MATING:
            return await self._perform_connector_mating(params, target_position)
        else:
            # Generic force-guided insertion
            return await self._perform_generic_insertion(params, target_position)

    async def _perform_component_insertion(self, params: AssemblyParameters,
                                         target_position: List[float]) -> bool:
        """Perform precision component insertion with force feedback."""
        self.logger.debug("Executing component insertion")

        try:
            # Get current position
            current_pos = fanuc.get_position()

            # Calculate insertion vector
            insertion_vector = np.array(target_position[:3]) - np.array(current_pos[:3])
            insertion_distance = np.linalg.norm(insertion_vector)
            insertion_direction = insertion_vector / insertion_distance

            # Perform incremental insertion
            step_size = 0.5  # 0.5mm steps
            steps = int(insertion_distance / step_size)

            for step in range(steps):
                # Calculate intermediate position
                progress = (step + 1) / steps
                intermediate_pos = current_pos.copy()
                intermediate_pos[:3] = (np.array(current_pos[:3]) +
                                      insertion_vector * progress).tolist()

                # Move with force monitoring
                fanuc.move_linear(intermediate_pos, params.insertion_speed)
                await asyncio.sleep(0.1)

                # Check for contact and force limits
                if self.force_history:
                    current_force = self.force_history[-1]

                    # Detect contact
                    if current_force.magnitude > params.force_threshold:
                        self.logger.debug(f"Contact detected at step {step}")

                        # Implement compliant insertion
                        await self._compliant_insertion_control(params, target_position)
                        break

                    # Check safety limits
                    if self.safety_state != SafetyState.NORMAL:
                        return False

            return True

        except Exception as e:
            self.logger.error(f"Component insertion failed: {str(e)}")
            return False

    async def _compliant_insertion_control(self, params: AssemblyParameters,
                                         target_position: List[float]) -> None:
        """Implement compliant control during insertion."""
        self.logger.debug("Switching to compliant insertion control")

        # Reduce speed and implement force-based control
        compliant_speed = params.insertion_speed * 0.5

        # Continue insertion with force feedback
        timeout = time.time() + params.force_timeout

        while time.time() < timeout:
            current_pos = fanuc.get_position()
            target_vector = np.array(target_position[:3]) - np.array(current_pos[:3])

            if np.linalg.norm(target_vector) < params.position_tolerance:
                self.logger.debug("Target position reached")
                break

            # Get current force
            if self.force_history:
                current_force = self.force_history[-1]

                # Calculate force-based position adjustment
                force_adjustment = self._calculate_force_adjustment(current_force, params)
                adjusted_target = np.array(current_pos[:3]) + force_adjustment

                # Move with adjustment
                adjusted_position = current_pos.copy()
                adjusted_position[:3] = adjusted_target.tolist()
                fanuc.move_linear(adjusted_position, compliant_speed)

            await asyncio.sleep(0.01)

    def _calculate_force_adjustment(self, force: ForceVector,
                                  params: AssemblyParameters) -> np.ndarray:
        """Calculate position adjustment based on force feedback."""
        # Simple proportional control
        force_vector = np.array([force.fx, force.fy, force.fz])

        # Apply compliance matrix (simplified)
        compliance = 1.0 / params.compliance_stiffness
        adjustment = -force_vector * compliance

        # Limit adjustment magnitude
        max_adjustment = 0.1  # mm
        adjustment_magnitude = np.linalg.norm(adjustment)
        if adjustment_magnitude > max_adjustment:
            adjustment = adjustment * (max_adjustment / adjustment_magnitude)

        return adjustment

    async def _perform_bearing_installation(self, params: AssemblyParameters,
                                          target_position: List[float]) -> bool:
        """Specialized bearing installation with press-fit control."""
        self.logger.debug("Executing bearing installation")

        # Bearing installation requires controlled press-fit force
        max_press_force = 50.0  # N
        press_speed = 1.0  # mm/s

        # Implement specialized bearing press logic
        # This would include chamfer detection, progressive loading, etc.

        return await self._perform_generic_insertion(params, target_position)

    async def _perform_screw_fastening(self, params: AssemblyParameters,
                                     target_position: List[float]) -> bool:
        """Screw fastening with torque control."""
        self.logger.debug("Executing screw fastening")

        # Implement rotational motion with torque feedback
        # This would include thread engagement detection, torque ramping, etc.

        return await self._perform_generic_insertion(params, target_position)

    async def _perform_connector_mating(self, params: AssemblyParameters,
                                      target_position: List[float]) -> bool:
        """Electrical connector mating with multi-axis force control."""
        self.logger.debug("Executing connector mating")

        # Connector mating requires precise alignment and gentle insertion
        # This would include wiggle motions, force balancing, etc.

        return await self._perform_generic_insertion(params, target_position)

    async def _perform_generic_insertion(self, params: AssemblyParameters,
                                       target_position: List[float]) -> bool:
        """Generic force-guided insertion operation."""
        self.logger.debug("Executing generic insertion")

        try:
            # Move towards target with force monitoring
            fanuc.move_linear(target_position, params.insertion_speed)

            # Monitor completion
            timeout = time.time() + params.force_timeout
            while time.time() < timeout:
                current_pos = fanuc.get_position()
                distance_to_target = np.linalg.norm(
                    np.array(target_position[:3]) - np.array(current_pos[:3])
                )

                if distance_to_target < params.position_tolerance:
                    return True

                if self.safety_state != SafetyState.NORMAL:
                    return False

                await asyncio.sleep(0.01)

            return False

        except Exception as e:
            self.logger.error(f"Generic insertion failed: {str(e)}")
            return False

    def _get_max_force_recorded(self) -> ForceVector:
        """Get maximum force recorded during operation."""
        if not self.force_history:
            return ForceVector(0, 0, 0, 0, 0, 0, time.time())

        # Find maximum force magnitude
        max_force = max(self.force_history, key=lambda f: f.magnitude)
        return max_force

    async def _measure_position_accuracy(self, target_position: List[float]) -> float:
        """Measure final position accuracy."""
        current_pos = fanuc.get_position()
        position_error = np.linalg.norm(
            np.array(target_position[:3]) - np.array(current_pos[:3])
        )
        return position_error

    def _calculate_quality_score(self, params: AssemblyParameters) -> float:
        """Calculate operation quality score (0-1)."""
        if not self.force_history:
            return 0.0

        # Factors: force consistency, no violations, completion time
        force_consistency = self._calculate_force_consistency()
        safety_score = 1.0 if self.safety_state == SafetyState.NORMAL else 0.5

        quality_score = (force_consistency * 0.6 + safety_score * 0.4)
        return min(max(quality_score, 0.0), 1.0)

    def _calculate_force_consistency(self) -> float:
        """Calculate force profile consistency."""
        if len(self.force_history) < 10:
            return 0.5

        # Calculate force variation coefficient
        forces = [f.magnitude for f in self.force_history]
        mean_force = np.mean(forces)
        std_force = np.std(forces)

        if mean_force == 0:
            return 1.0

        variation_coefficient = std_force / mean_force
        consistency_score = max(0.0, 1.0 - variation_coefficient)

        return consistency_score

    def get_operation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive operation statistics."""
        success_rate = (self.stats['successful_operations'] /
                       max(1, self.stats['operations_completed'])) * 100

        return {
            'total_operations': self.stats['operations_completed'],
            'successful_operations': self.stats['successful_operations'],
            'success_rate_percent': success_rate,
            'force_violations': self.stats['force_violations'],
            'emergency_stops': self.stats['emergency_stops'],
            'average_cycle_time_seconds': self.stats['avg_cycle_time'],
            'current_safety_state': self.safety_state.value,
            'force_sensor_calibrated': self.force_sensor_calibrated,
            'monitoring_active': self.monitoring_active,
            'connection_status': self.is_connected
        }

    async def shutdown(self) -> None:
        """Safely shutdown force controller."""
        self.logger.info("Shutting down FANUC force controller")

        # Stop monitoring
        self.monitoring_active = False

        # Disable force control
        await self._disable_force_control()

        # Reset safety state
        self.safety_state = SafetyState.NORMAL

        self.logger.info("Force controller shutdown complete")


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    async def demo_force_feedback():
        """Demonstrate FANUC force-feedback integration."""
        print("🤖 FANUC Force-Feedback Integration Demo")
        print("=" * 50)

        # Initialize force controller
        controller = FanucForceController("192.168.1.100")

        try:
            # Connect to robot
            if await controller.connect_robot():
                print("✅ Connected to FANUC robot")

                # Start force monitoring
                await controller.start_force_monitoring()
                print("✅ Force monitoring started")

                # Define assembly parameters
                assembly_params = AssemblyParameters(
                    operation_type=AssemblyOperation.COMPONENT_INSERTION,
                    max_force_x=8.0,
                    max_force_y=8.0,
                    max_force_z=12.0,
                    max_torque_x=0.5,
                    max_torque_y=0.5,
                    max_torque_z=0.5,
                    approach_speed=15.0,
                    insertion_speed=3.0,
                    force_threshold=3.0,
                    compliance_stiffness=150.0,
                    position_tolerance=0.05
                )

                # Define positions
                approach_pos = [100, 200, 350, 0, 90, 0]  # Safe approach
                target_pos = [100, 200, 300, 0, 90, 0]    # Assembly target

                # Perform delicate assembly
                print("🔧 Performing component insertion...")
                result = await controller.perform_delicate_assembly(
                    assembly_params, target_pos, approach_pos
                )

                # Display results
                print(f"✅ Assembly completed: {result.success}")
                print(f"   Operation ID: {result.operation_id}")
                print(f"   Completion time: {result.completion_time:.2f}s")
                print(f"   Max force: {result.max_force_recorded.magnitude:.2f}N")
                print(f"   Position accuracy: {result.position_accuracy:.3f}mm")
                print(f"   Quality score: {result.quality_score:.2f}")

                # Show statistics
                stats = controller.get_operation_statistics()
                print(f"\n📊 Operation Statistics:")
                print(f"   Success rate: {stats['success_rate_percent']:.1f}%")
                print(f"   Average cycle time: {stats['average_cycle_time_seconds']:.2f}s")

            else:
                print("❌ Failed to connect to FANUC robot")

        except Exception as e:
            print(f"❌ Demo failed: {e}")

        finally:
            await controller.shutdown()

    # Run demonstration
    asyncio.run(demo_force_feedback())
