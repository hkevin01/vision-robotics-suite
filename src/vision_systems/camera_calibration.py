"""
Camera Calibration Module

Provides calibration utilities for industrial cameras and
hand-eye calibration for robot guidance systems.
"""

from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

from .base import CalibrationError, VisionSystemBase


class CameraCalibrator:
    """Camera calibration utility for industrial vision systems."""

    def __init__(self, camera_matrix: Optional[np.ndarray] = None,
                 distortion_coeffs: Optional[np.ndarray] = None):
        """Initialize camera calibrator.

        Args:
            camera_matrix: Intrinsic camera matrix (3x3)
            distortion_coeffs: Distortion coefficients
        """
        self.camera_matrix = camera_matrix
        self.distortion_coeffs = distortion_coeffs
        self.is_calibrated = camera_matrix is not None

    def calibrate_camera(
        self,
        object_points: List[np.ndarray],
        image_points: List[np.ndarray],
        image_size: Tuple[int, int]
    ) -> Dict[str, Any]:
        """Calibrate camera using checkerboard pattern.

        Args:
            object_points: 3D points in real world space
            image_points: 2D points in image plane
            image_size: Size of calibration images (width, height)

        Returns:
            Dictionary containing calibration results

        Raises:
            CalibrationError: If calibration fails
        """
        try:
            ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
                object_points, image_points, image_size, None, None
            )

            if not ret:
                raise CalibrationError("Camera calibration failed")

            self.camera_matrix = mtx
            self.distortion_coeffs = dist
            self.is_calibrated = True

            return {
                "camera_matrix": mtx,
                "distortion_coefficients": dist,
                "rotation_vectors": rvecs,
                "translation_vectors": tvecs,
                "reprojection_error": ret
            }

        except Exception as e:
            raise CalibrationError(f"Calibration failed: {str(e)}")

    def undistort_image(self, image: np.ndarray) -> np.ndarray:
        """Undistort image using calibration parameters.

        Args:
            image: Input distorted image

        Returns:
            Undistorted image

        Raises:
            CalibrationError: If camera not calibrated
        """
        if not self.is_calibrated:
            raise CalibrationError("Camera not calibrated")

        return cv2.undistort(
            image,
            self.camera_matrix,
            self.distortion_coeffs
        )

    def save_calibration(self, filepath: str) -> None:
        """Save calibration data to file.

        Args:
            filepath: Path to save calibration file
        """
        if not self.is_calibrated:
            raise CalibrationError("No calibration data to save")

        np.savez(
            filepath,
            camera_matrix=self.camera_matrix,
            distortion_coefficients=self.distortion_coeffs
        )

    def load_calibration(self, filepath: str) -> None:
        """Load calibration data from file.

        Args:
            filepath: Path to calibration file
        """
        try:
            data = np.load(filepath)
            self.camera_matrix = data['camera_matrix']
            self.distortion_coeffs = data['distortion_coefficients']
            self.is_calibrated = True
        except Exception as e:
            raise CalibrationError(f"Failed to load calibration: {str(e)}")


class HandEyeCalibrator:
    """Hand-eye calibration for robot-camera coordination."""

    def __init__(self):
        """Initialize hand-eye calibrator."""
        self.robot_poses: List[np.ndarray] = []
        self.camera_poses: List[np.ndarray] = []
        self.transformation_matrix: Optional[np.ndarray] = None

    def add_pose_pair(
        self,
        robot_pose: np.ndarray,
        camera_pose: np.ndarray
    ) -> None:
        """Add robot-camera pose pair for calibration.

        Args:
            robot_pose: 4x4 transformation matrix for robot pose
            camera_pose: 4x4 transformation matrix for camera pose
        """
        self.robot_poses.append(robot_pose)
        self.camera_poses.append(camera_pose)

    def calibrate(self) -> np.ndarray:
        """Perform hand-eye calibration.

        Returns:
            4x4 transformation matrix from robot to camera

        Raises:
            CalibrationError: If insufficient data or calibration fails
        """
        if len(self.robot_poses) < 3:
            raise CalibrationError("At least 3 pose pairs required")

        # Convert to format expected by OpenCV
        R_gripper2base = []
        t_gripper2base = []
        R_target2cam = []
        t_target2cam = []

        for robot_pose, camera_pose in zip(self.robot_poses, self.camera_poses):
            R_gripper2base.append(robot_pose[:3, :3])
            t_gripper2base.append(robot_pose[:3, 3])
            R_target2cam.append(camera_pose[:3, :3])
            t_target2cam.append(camera_pose[:3, 3])

        try:
            R_cam2gripper, t_cam2gripper = cv2.calibrateHandEye(
                R_gripper2base, t_gripper2base,
                R_target2cam, t_target2cam,
                method=cv2.CALIB_HAND_EYE_TSAI
            )

            # Construct transformation matrix
            self.transformation_matrix = np.eye(4)
            self.transformation_matrix[:3, :3] = R_cam2gripper
            self.transformation_matrix[:3, 3] = t_cam2gripper.flatten()

            return self.transformation_matrix

        except Exception as e:
            raise CalibrationError(f"Hand-eye calibration failed: {str(e)}")

    def transform_point(self, point: np.ndarray) -> np.ndarray:
        """Transform point from camera to robot coordinates.

        Args:
            point: 3D point in camera coordinates

        Returns:
            3D point in robot coordinates
        """
        if self.transformation_matrix is None:
            raise CalibrationError("Hand-eye calibration not performed")

        # Convert to homogeneous coordinates
        point_homo = np.append(point, 1)

        # Apply transformation
        transformed = self.transformation_matrix @ point_homo

        return transformed[:3]
