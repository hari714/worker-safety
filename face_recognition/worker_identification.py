"""
Face Recognition System — Main Orchestrator.

Composes FaceDetector, FaceEmbedder, and FaceDatabase to provide
a high-level API for face detection, worker registration, and identification.
"""

import logging
import numpy as np
import cv2
from typing import List, Optional, Tuple
from .face_detection import FaceDetection, FaceDetector
from .face_embedding import WorkerIdentification, FaceEmbedder
from .face_database import FaceDatabase
from config.settings import (
    FACE_CONFIDENCE_THRESHOLD,
    SIMILARITY_THRESHOLD,
    FACE_EMBEDDING_DIR
)

logger = logging.getLogger(__name__)


class FaceRecognitionSystem:
    """Complete face recognition pipeline: detect, embed, identify."""

    def __init__(self, embedding_dir=None, face_confidence=None,
                 similarity_threshold=None, device=None):
        self.detector = FaceDetector(
            confidence_threshold=face_confidence or FACE_CONFIDENCE_THRESHOLD,
            device=device
        )
        self.embedder = FaceEmbedder(device=device)
        self.database = FaceDatabase(
            embedding_dir=embedding_dir or FACE_EMBEDDING_DIR,
            similarity_threshold=similarity_threshold or SIMILARITY_THRESHOLD
        )
        logger.info(
            f"FaceRecognitionSystem initialized — "
            f"{len(self.database.workers)} registered worker(s)"
        )

    def detect_faces(self, frame: np.ndarray) -> List[FaceDetection]:
        """Detect all faces in a frame."""
        return self.detector.detect(frame)

    def extract_face_embedding(self, frame: np.ndarray,
                                face: FaceDetection) -> Optional[np.ndarray]:
        """Extract 512-dim embedding for a detected face."""
        return self.embedder.extract_embedding(frame, face)

    def identify_worker(self, embedding: np.ndarray) -> Optional[WorkerIdentification]:
        """Match an embedding against registered workers.

        Returns:
            WorkerIdentification if match found (similarity >= threshold), else None
        """
        match = self.database.find_best_match(embedding)
        if match is None:
            return None

        worker_id, info, similarity = match
        return WorkerIdentification(
            worker_id=worker_id,
            worker_name=info['name'],
            confidence=similarity,
            email=info['email']
        )

    def register_worker(self, worker_id: str, name: str, email: str,
                         images: List[np.ndarray]) -> bool:
        """Register a new worker from multiple face images.

        Detects face in each image, extracts embeddings, averages them,
        and saves as a single .pkl file.

        Args:
            worker_id: Unique worker ID
            name: Worker full name
            email: Worker email
            images: List of BGR numpy images (10-20 recommended)

        Returns:
            True if registration succeeded, False otherwise
        """
        embeddings = []

        for i, img in enumerate(images):
            faces = self.detector.detect(img)
            if len(faces) == 0:
                logger.warning(f"No face found in image {i+1}/{len(images)}, skipping")
                continue
            if len(faces) > 1:
                logger.warning(f"Multiple faces in image {i+1}/{len(images)}, using largest")
                # Use the face with largest area
                faces.sort(key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]),
                           reverse=True)

            embedding = self.embedder.extract_embedding(img, faces[0])
            if embedding is not None:
                embeddings.append(embedding)

        if len(embeddings) < 3:
            logger.error(
                f"Only {len(embeddings)} valid embeddings extracted "
                f"(minimum 3 required). Registration failed for {worker_id}."
            )
            return False

        # Average embeddings and L2-normalize
        mean_embedding = np.mean(np.array(embeddings), axis=0)
        mean_embedding = mean_embedding / np.linalg.norm(mean_embedding)

        logger.info(
            f"Registering worker {worker_id} ({name}) with "
            f"{len(embeddings)}/{len(images)} valid embeddings"
        )
        return self.database.save_worker_embedding(worker_id, name, email, mean_embedding)

    def identify_faces_in_frame(self, frame: np.ndarray) -> List[Tuple[FaceDetection, Optional[WorkerIdentification]]]:
        """Detect and identify all faces in a single frame.

        Returns:
            List of (FaceDetection, WorkerIdentification or None) tuples
        """
        faces = self.detector.detect(frame)
        results = []

        for face in faces:
            embedding = self.embedder.extract_embedding(frame, face)
            worker = None
            if embedding is not None:
                worker = self.identify_worker(embedding)
            results.append((face, worker))

        return results

    def draw_face_detections(self, frame: np.ndarray,
                              detections: List[Tuple[FaceDetection, Optional[WorkerIdentification]]]) -> np.ndarray:
        """Draw face bounding boxes and worker names on frame.

        Args:
            frame: BGR numpy image
            detections: Output from identify_faces_in_frame()

        Returns:
            Annotated frame
        """
        for face, worker in detections:
            x1, y1, x2, y2 = face.bbox

            if worker:
                color = (0, 255, 0)  # Green for identified
                label = f"{worker.worker_name} ({worker.confidence:.2f})"
            else:
                color = (0, 0, 255)  # Red for unknown
                label = f"Unknown ({face.confidence:.2f})"

            # Draw face rectangle
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Draw label background
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            thickness = 1
            (text_w, text_h), baseline = cv2.getTextSize(label, font, font_scale, thickness)
            cv2.rectangle(frame, (x1, y1 - text_h - 10), (x1 + text_w, y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 5), font, font_scale,
                        (255, 255, 255), thickness, cv2.LINE_AA)

        return frame
