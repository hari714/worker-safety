"""
Workplace Safety Monitor — Main Integration Hub.

Combines PPE detection, face recognition, compliance checking,
violation logging, and email notifications into a unified processing loop.
"""

import logging
import time
import cv2
from datetime import datetime

from ppe_detection import PPEDetector
from config.settings import (
    PPE_MODEL_PATH, PPE_CONFIDENCE_THRESHOLD,
    CAMERA_ID, FRAME_WIDTH, FRAME_HEIGHT, VIDEO_FPS
)
from config.database import init_db, SessionLocal
from config.email_config import EMAIL_CONFIG
from worker_management.db_operations import DatabaseOperations
from notification_system.email_sender import EmailNotificationSystem
from .compliance_checker import ComplianceChecker
from .violation_logger import ViolationLogger

logger = logging.getLogger(__name__)


class WorkplaceSafetyMonitor:
    """Central monitor integrating all safety system modules."""

    def __init__(self, db_url=None, email_config=None):
        logger.info("Initializing Workplace Safety Monitor...")

        # Initialize database
        init_db()

        # Module 1: PPE Detection
        self.ppe_detector = PPEDetector(
            model_path=PPE_MODEL_PATH,
            confidence_threshold=PPE_CONFIDENCE_THRESHOLD
        )

        # Module 2: Face Recognition (optional — graceful fallback)
        self.face_system = None
        try:
            from face_recognition import FaceRecognitionSystem
            self.face_system = FaceRecognitionSystem()
            logger.info("Face recognition module loaded successfully")
        except ImportError as e:
            logger.error(
                f"Face recognition DISABLED — missing dependency: {e}. "
                f"Install with: pip install facenet-pytorch"
            )
        except Exception as e:
            logger.error(f"Face recognition DISABLED — initialization failed: {e}", exc_info=True)

        # Module 3: Email Notifications
        self.email_system = EmailNotificationSystem(email_config or EMAIL_CONFIG)

        # Module 4: Database Operations
        self.db_ops = DatabaseOperations(session_factory=SessionLocal)

        # Compliance & violation handling
        self.compliance_checker = ComplianceChecker()
        self.violation_logger = ViolationLogger(self.db_ops, self.email_system)

        # Cooldown: only log a violation once per worker every 30 seconds
        self._violation_cooldown = 30  # seconds
        self._last_violation_time = {}  # {worker_id: timestamp}

        # Face detection frame skipping for real-time performance
        # MTCNN + FaceNet is too slow to run on every frame
        self._frame_count = 0
        self._face_detect_interval = 5  # run face detection every N frames
        self._cached_face_results = []  # reuse between detection frames

        # FPS tracking
        self._fps_start_time = time.time()
        self._fps_frame_count = 0
        self._current_fps = 0.0

        logger.info("Workplace Safety Monitor initialized successfully")
        if self.face_system is None:
            logger.warning(">>> FACE DETECTION IS NOT ACTIVE — check errors above <<<")

    def process_frame(self, frame):
        """Run the full safety pipeline on a single frame.

        Args:
            frame: BGR numpy image

        Returns:
            (annotated_frame, result_dict)
        """
        annotated = frame.copy()

        # Update FPS counter
        self._fps_frame_count += 1
        elapsed = time.time() - self._fps_start_time
        if elapsed >= 1.0:
            self._current_fps = self._fps_frame_count / elapsed
            self._fps_frame_count = 0
            self._fps_start_time = time.time()

        # Step 1: PPE Detection
        detections = self.ppe_detector.detect_ppe(frame)
        annotated = self.ppe_detector.draw_detections(annotated, detections)

        # Step 2: Face Recognition (with frame skipping for performance)
        worker_info = None
        face_results = self._cached_face_results
        if self.face_system:
            self._frame_count += 1
            if self._frame_count % self._face_detect_interval == 0:
                try:
                    face_results = self.face_system.identify_faces_in_frame(frame)
                    self._cached_face_results = face_results
                except Exception as e:
                    logger.error(f"Face detection error on frame: {e}")
                    face_results = self._cached_face_results

            # Draw face results (cached or fresh)
            if face_results:
                annotated = self.face_system.draw_face_detections(annotated, face_results)
                # Use the first identified worker (if any)
                for _, worker in face_results:
                    if worker is not None:
                        worker_info = worker
                        break

        # Step 3: Compliance Check
        is_compliant, missing_ppe = self.compliance_checker.check_compliance(detections)

        # Step 4: Handle violation (with cooldown to avoid spam)
        if not is_compliant:
            worker_key = worker_info.worker_id if worker_info else "UNKNOWN"
            now = time.time()
            last_time = self._last_violation_time.get(worker_key, 0)
            if now - last_time >= self._violation_cooldown:
                self._last_violation_time[worker_key] = now
                self._handle_violation(worker_info, missing_ppe, frame)

        # Step 5: Update last_seen
        if worker_info:
            self.db_ops.update_worker_last_seen(worker_info.worker_id)

        # Step 6: Draw status overlay (now includes FPS)
        self._draw_status_overlay(annotated, worker_info, is_compliant, missing_ppe)

        result = {
            'is_compliant': is_compliant,
            'missing_ppe': missing_ppe,
            'worker': worker_info,
            'detections': detections,
            'faces': face_results
        }
        return annotated, result

    def _handle_violation(self, worker_info, missing_ppe, frame):
        """Handle a detected PPE violation."""
        if worker_info:
            worker_id = worker_info.worker_id
            worker_name = worker_info.worker_name
            worker_email = worker_info.email
        else:
            worker_id = "UNKNOWN"
            worker_name = "Unknown Worker"
            worker_email = None

        # Get today's violation count
        today_violations = self.db_ops.get_violations_today(worker_id)
        count = len(today_violations) + 1

        self.violation_logger.log_violation(
            worker_id=worker_id,
            worker_name=worker_name,
            worker_email=worker_email,
            missing_ppe=missing_ppe,
            frame=frame,
            violation_count=count
        )

    def _draw_status_overlay(self, frame, worker_info, is_compliant, missing_ppe):
        """Draw timestamp, FPS, worker name, and compliance status on frame."""
        h, w = frame.shape[:2]
        font = cv2.FONT_HERSHEY_SIMPLEX

        # Timestamp at top-left
        timestamp = datetime.now().strftime('Time: %Y-%m-%d %H:%M:%S')
        cv2.putText(frame, timestamp, (10, 30), font, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

        # FPS at top-right
        fps_text = f"FPS: {self._current_fps:.1f}"
        cv2.putText(frame, fps_text, (w - 150, 30), font, 0.7, (0, 255, 255), 2, cv2.LINE_AA)

        # Face detection status indicator
        face_status = "Face: ON" if self.face_system else "Face: OFF"
        face_color = (0, 255, 0) if self.face_system else (0, 0, 255)
        cv2.putText(frame, face_status, (w - 150, 60), font, 0.6, face_color, 2, cv2.LINE_AA)

        # Worker name and compliance status at bottom
        name = worker_info.worker_name if worker_info else "Unknown"
        status = "Compliant: True" if is_compliant else "Compliant: False"
        color = (0, 255, 0) if is_compliant else (0, 0, 255)

        label = f"{name} - {status}"
        if not is_compliant:
            label += f" | Missing: {', '.join(sorted(missing_ppe))}"

        cv2.putText(frame, label, (10, h - 20), font, 0.6, color, 2, cv2.LINE_AA)

    def run_from_webcam(self):
        """Start live monitoring from webcam."""
        # Print startup diagnostics
        print("\n" + "=" * 60)
        print("  WORKPLACE SAFETY MONITOR — LIVE MODE")
        print("=" * 60)
        print(f"  PPE Detection:  ACTIVE")
        if self.face_system:
            worker_count = len(self.face_system.database.workers)
            print(f"  Face Detection: ACTIVE ({worker_count} worker(s) registered)")
        else:
            print(f"  Face Detection: DISABLED (check logs for errors)")
        print(f"  Camera ID:      {CAMERA_ID}")
        print(f"  Press 'q' to quit")
        print("=" * 60 + "\n")

        # Try DirectShow backend first (more reliable on Windows)
        cap = cv2.VideoCapture(CAMERA_ID, cv2.CAP_DSHOW)
        if not cap.isOpened():
            logger.warning("DirectShow failed, trying default backend...")
            cap = cv2.VideoCapture(CAMERA_ID)

        if not cap.isOpened():
            logger.error(f"Cannot open camera {CAMERA_ID}. Check if camera is connected and not in use by another app.")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, VIDEO_FPS)

        actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        logger.info(f"Starting webcam monitoring (Camera {CAMERA_ID}, {actual_w}x{actual_h})")

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    logger.error("Failed to read from webcam")
                    break

                annotated, result = self.process_frame(frame)
                cv2.imshow('Workplace Safety Monitor', annotated)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logger.info("Monitoring stopped by user (q pressed)")
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()

    def run_from_video(self, video_path: str):
        """Process a recorded video file."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Cannot open video: {video_path}")
            return

        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        delay = int(1000 / fps)
        logger.info(f"Processing video: {video_path} ({fps} fps)")

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    logger.info("Video processing complete")
                    break

                annotated, result = self.process_frame(frame)
                cv2.imshow('Workplace Safety Monitor', annotated)

                if cv2.waitKey(delay) & 0xFF == ord('q'):
                    logger.info("Video processing stopped by user (q pressed)")
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()
