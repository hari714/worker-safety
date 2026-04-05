"""
Face Detection Module using MTCNN from facenet_pytorch.

Detects face locations and 5 facial landmarks in images/frames.
"""

import logging
import numpy as np
import cv2
import torch
from dataclasses import dataclass
from typing import List, Tuple, Optional
from facenet_pytorch import MTCNN as FacenetMTCNN
from config.settings import FACE_CONFIDENCE_THRESHOLD

logger = logging.getLogger(__name__)

LANDMARK_NAMES = ['left_eye', 'right_eye', 'nose', 'mouth_left', 'mouth_right']


@dataclass
class FaceDetection:
    """Represents a single detected face."""
    bbox: Tuple[int, int, int, int]       # (x1, y1, x2, y2)
    confidence: float                      # 0.0 - 1.0
    landmarks: Optional[dict] = None       # 5 facial landmarks


class FaceDetector:
    """Face detection using MTCNN from facenet_pytorch."""

    def __init__(self, min_face_size=20, confidence_threshold=None, device=None):
        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.confidence_threshold = confidence_threshold or FACE_CONFIDENCE_THRESHOLD

        self.mtcnn = FacenetMTCNN(
            keep_all=True,
            min_face_size=min_face_size,
            thresholds=[self.confidence_threshold, 0.7, 0.7],
            device=self.device,
            post_process=False,
            select_largest=False
        )
        logger.info(f"FaceDetector initialized on {self.device}, threshold={self.confidence_threshold}")

    def detect(self, frame: np.ndarray) -> List[FaceDetection]:
        """Detect all faces in a BGR frame.

        Args:
            frame: BGR numpy image (OpenCV format)

        Returns:
            List of FaceDetection objects
        """
        if frame is None or frame.size == 0:
            return []

        h, w = frame.shape[:2]

        # Downscale large frames for faster MTCNN processing on CPU
        max_dim = max(h, w)
        scale = 1.0
        if max_dim > 640:
            scale = 640 / max_dim
            small = cv2.resize(frame, (int(w * scale), int(h * scale)),
                               interpolation=cv2.INTER_AREA)
        else:
            small = frame

        # Convert BGR (OpenCV) to RGB (MTCNN expects RGB)
        rgb_frame = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        try:
            boxes, probs, points = self.mtcnn.detect(rgb_frame, landmarks=True)
        except Exception as e:
            logger.error(f"MTCNN detection failed: {e}")
            return []

        if boxes is None:
            return []

        detections = []
        for i in range(len(boxes)):
            conf = float(probs[i])
            if conf < self.confidence_threshold:
                continue

            # Map coordinates back to original frame size
            x1 = max(0, int(boxes[i][0] / scale))
            y1 = max(0, int(boxes[i][1] / scale))
            x2 = min(w, int(boxes[i][2] / scale))
            y2 = min(h, int(boxes[i][3] / scale))

            if x2 <= x1 or y2 <= y1:
                continue

            # Convert landmarks array to named dict (scaled back)
            landmarks_dict = None
            if points is not None and points[i] is not None:
                landmarks_dict = {
                    name: (int(points[i][j][0] / scale), int(points[i][j][1] / scale))
                    for j, name in enumerate(LANDMARK_NAMES)
                }

            detections.append(FaceDetection(
                bbox=(x1, y1, x2, y2),
                confidence=conf,
                landmarks=landmarks_dict
            ))

        logger.debug(f"Detected {len(detections)} face(s)")
        return detections
