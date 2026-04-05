"""
Face Database Module.

Manages worker face embeddings stored as .pkl files.
Handles loading, saving, and matching worker embeddings.
"""

import os
import logging
import pickle
import numpy as np
from typing import Dict, Optional, List, Tuple
from config.settings import FACE_EMBEDDING_DIR, SIMILARITY_THRESHOLD

logger = logging.getLogger(__name__)


class FaceDatabase:
    """Manages worker face embeddings stored as pickle files."""

    def __init__(self, embedding_dir=None, similarity_threshold=None):
        self.embedding_dir = embedding_dir or FACE_EMBEDDING_DIR
        self.similarity_threshold = similarity_threshold or SIMILARITY_THRESHOLD
        self.workers: Dict[str, dict] = {}  # {worker_id: {'embedding': np.ndarray, 'info': dict}}

        os.makedirs(self.embedding_dir, exist_ok=True)
        self.load_all_embeddings()

    def load_all_embeddings(self):
        """Load all worker embeddings from .pkl files."""
        self.workers.clear()
        count = 0

        for filename in os.listdir(self.embedding_dir):
            if not filename.endswith('.pkl'):
                continue
            filepath = os.path.join(self.embedding_dir, filename)
            try:
                with open(filepath, 'rb') as f:
                    data = pickle.load(f)
                worker_id = data['info']['id']
                self.workers[worker_id] = data
                count += 1
            except Exception as e:
                logger.error(f"Failed to load {filename}: {e}")

        logger.info(f"Loaded {count} worker embedding(s) from {self.embedding_dir}")

    def save_worker_embedding(self, worker_id: str, name: str, email: str,
                               embedding: np.ndarray) -> bool:
        """Save a worker's averaged embedding to a .pkl file.

        Args:
            worker_id: Unique worker ID (e.g., "W001")
            name: Worker full name
            email: Worker email address
            embedding: 512-dim L2-normalized numpy array

        Returns:
            True on success, False on failure
        """
        data = {
            'embedding': embedding,
            'info': {
                'id': worker_id,
                'name': name,
                'email': email
            }
        }

        filepath = os.path.join(self.embedding_dir, f"{worker_id}.pkl")
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
            self.workers[worker_id] = data
            logger.info(f"Saved embedding for worker {worker_id} ({name})")
            return True
        except Exception as e:
            logger.error(f"Failed to save embedding for {worker_id}: {e}")
            return False

    def find_best_match(self, embedding: np.ndarray) -> Optional[Tuple[str, dict, float]]:
        """Find the best matching worker for a given face embedding.

        Uses dot product (equivalent to cosine similarity for L2-normalized vectors).

        Args:
            embedding: 512-dim numpy array

        Returns:
            (worker_id, worker_info, similarity) or None if no match above threshold
        """
        if not self.workers:
            return None

        worker_ids = list(self.workers.keys())
        stored_embeddings = np.array([self.workers[wid]['embedding'] for wid in worker_ids])

        # Dot product = cosine similarity for L2-normalized vectors
        similarities = stored_embeddings @ embedding

        best_idx = np.argmax(similarities)
        best_score = float(similarities[best_idx])

        if best_score >= self.similarity_threshold:
            best_id = worker_ids[best_idx]
            return (best_id, self.workers[best_id]['info'], best_score)

        return None

    def get_worker(self, worker_id: str) -> Optional[dict]:
        """Get worker info by ID."""
        if worker_id in self.workers:
            return self.workers[worker_id]['info']
        return None

    def remove_worker(self, worker_id: str) -> bool:
        """Remove a worker's embedding."""
        filepath = os.path.join(self.embedding_dir, f"{worker_id}.pkl")
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
            self.workers.pop(worker_id, None)
            logger.info(f"Removed worker {worker_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove worker {worker_id}: {e}")
            return False

    def get_all_workers(self) -> List[dict]:
        """Get info for all registered workers."""
        return [data['info'] for data in self.workers.values()]
