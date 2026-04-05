"""
Face Embedding Module using FaceNet (InceptionResnetV1).

Extracts 512-dimensional face embeddings for worker identification.
"""

import logging
import numpy as np
import cv2
import torch
from dataclasses import dataclass
from typing import Optional
from facenet_pytorch import InceptionResnetV1
from .face_detection import FaceDetection

logger = logging.getLogger(__name__)


@dataclass
class WorkerIdentification:
    """Represents an identified worker."""
    worker_id: str          # "W001"
    worker_name: str        # "Ravi"
    confidence: float       # cosine similarity score
    email: str              # "ravi@company.com"


class FaceEmbedder:
    """Extracts 512-dim face embeddings using FaceNet (InceptionResnetV1)."""

    def __init__(self, device=None):
        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        logger.info(f"FaceEmbedder initialized on {self.device}")

    def extract_embedding(self, frame: np.ndarray, face: FaceDetection) -> Optional[np.ndarray]:
        """Extract 512-dim embedding from a detected face.

        Args:
            frame: BGR numpy image (full frame)
            face: FaceDetection with bbox coordinates

        Returns:
            512-dimensional numpy array, or None if extraction fails
        """
        x1, y1, x2, y2 = face.bbox

        # Validate crop dimensions
        if x2 <= x1 or y2 <= y1:
            logger.warning("Invalid face bbox dimensions")
            return None

        # Crop face from frame
        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            logger.warning("Empty face crop")
            return None

        try:
            # BGR to RGB
            rgb_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)

            # Resize to 160x160 (FaceNet input size)
            resized = cv2.resize(rgb_crop, (160, 160))

            # Convert to float32 tensor in [0, 255] range, then standardize
            # facenet_pytorch standardization: (pixel - 127.5) / 128.0
            tensor = torch.tensor(resized.transpose(2, 0, 1), dtype=torch.float32)
            tensor = (tensor - 127.5) / 128.0
            tensor = tensor.unsqueeze(0).to(self.device)

            # Extract embedding
            with torch.no_grad():
                embedding = self.model(tensor)

            return embedding.cpu().numpy().flatten()

        except Exception as e:
            logger.error(f"Embedding extraction failed: {e}")
            return None
