"""
Real-time PPE Detection using YOLOv8.
Detects 5 PPE items and checks compliance.
"""

from ultralytics import YOLO
import cv2
import numpy as np
from typing import List, Tuple
from .ppe_classes import PPEDetection, CLASS_NAMES, REQUIRED_PPE, CLASS_COLORS


class PPEDetector:
    """Real-time PPE Detection using YOLOv8."""

    def __init__(self, model_path, confidence_threshold=0.5, use_tta=True):
        """
        Initialize PPE Detector.

        Args:
            model_path: Path to trained YOLOv8 model (.pt file)
            confidence_threshold: Minimum confidence for detection
            use_tta: Enable Test Time Augmentation for better accuracy on small objects
        """
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        self.use_tta = use_tta
        self.img_size = 640

    def _preprocess(self, frame):
        """
        Resize images to optimal size for detection.
        - Small images: upscale to at least 640px
        - Very large images: downscale to ~1280px to keep objects visible
        Returns (processed_frame, scale) where scale maps
        detected coordinates back to original image space.
        """
        h, w = frame.shape[:2]
        max_dim = max(h, w)

        # Very large images — downscale to 1280 so objects stay visible
        if max_dim > 1280:
            scale = 1280 / max_dim
            new_w, new_h = int(w * scale), int(h * scale)
            resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
            return resized, scale

        # Small images — upscale to at least 640
        if max_dim < self.img_size:
            scale = self.img_size / max_dim
            new_w, new_h = int(w * scale), int(h * scale)
            resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
            return resized, scale

        return frame, 1.0

    def detect_ppe(self, frame) -> List[PPEDetection]:
        """
        Detect PPE in frame. Automatically preprocesses small images
        for better detection accuracy.

        Args:
            frame: Input image/frame (numpy array)

        Returns:
            List of PPEDetection objects
        """
        orig_h, orig_w = frame.shape[:2]
        processed, scale = self._preprocess(frame)

        results = self.model(processed, verbose=False, augment=self.use_tta,
                              conf=self.confidence_threshold)[0]
        raw_detections = []

        for detection in results.boxes:
            x1, y1, x2, y2 = detection.xyxy[0].cpu().numpy()

            # Map coordinates back to original image space
            x1 = x1 / scale
            y1 = y1 / scale
            x2 = x2 / scale
            y2 = y2 / scale

            x1 = max(0, int(x1))
            y1 = max(0, int(y1))
            x2 = min(orig_w, int(x2))
            y2 = min(orig_h, int(y2))

            class_id = int(detection.cls[0].cpu().numpy())
            confidence = float(detection.conf[0].cpu().numpy())

            if confidence < self.confidence_threshold:
                continue

            x_center = (x1 + x2) / 2
            y_center = (y1 + y2) / 2

            ppe_detection = PPEDetection(
                class_id=class_id,
                class_name=CLASS_NAMES.get(class_id, 'unknown'),
                confidence=confidence,
                bbox=(x1, y1, x2, y2),
                x_center=x_center,
                y_center=y_center
            )
            raw_detections.append(ppe_detection)

        # Keep only the highest confidence detection per class
        best_per_class = {}
        for d in raw_detections:
            if d.class_name not in best_per_class or d.confidence > best_per_class[d.class_name].confidence:
                best_per_class[d.class_name] = d

        return list(best_per_class.values())

    def draw_detections(self, frame, detections: List[PPEDetection]):
        """
        Draw detected PPE on frame with colored bounding boxes.

        Args:
            frame: Input image
            detections: List of PPEDetection objects

        Returns:
            Frame with drawings
        """
        for detection in detections:
            x1, y1, x2, y2 = detection.bbox
            class_name = detection.class_name
            confidence = detection.confidence

            color = CLASS_COLORS.get(class_name, (255, 255, 255))

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            label = f"{class_name}: {confidence:.2f}"
            (label_w, label_h), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2
            )
            cv2.rectangle(frame, (x1, y1 - label_h - 10), (x1 + label_w, y1), color, -1)
            cv2.putText(
                frame, label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (255, 255, 255), 2
            )

        return frame

    def check_ppe_compliance(self, detections: List[PPEDetection]) -> Tuple[bool, set]:
        """
        Check if all required PPE is present.

        Args:
            detections: List of PPEDetection objects

        Returns:
            (is_compliant, missing_ppe)
        """
        detected_ppe = {d.class_name for d in detections}
        missing_ppe = REQUIRED_PPE - detected_ppe
        is_compliant = len(missing_ppe) == 0

        return is_compliant, missing_ppe
