"""
Worker Registry — High-level worker management.

Provides a clean API for registering workers and managing face embeddings,
bridging the face recognition module with the database.
"""

import json
import logging
import numpy as np
from typing import Optional
from .db_operations import DatabaseOperations
from utils.validators import validate_email, validate_worker_id

logger = logging.getLogger(__name__)


class WorkerRegistry:
    """High-level worker registration and management."""

    def __init__(self, db_ops: DatabaseOperations = None):
        self.db_ops = db_ops or DatabaseOperations()

    def register_worker(self, worker_id: str, name: str, email: str,
                         phone: str = None, department: str = None,
                         position: str = None) -> bool:
        """Register a new worker with validation."""
        if not validate_worker_id(worker_id):
            logger.error(f"Invalid worker ID: {worker_id}")
            return False
        if not validate_email(email):
            logger.error(f"Invalid email: {email}")
            return False

        return self.db_ops.add_worker(
            worker_id=worker_id, name=name, email=email,
            phone=phone, department=department, position=position
        )

    def register_face(self, worker_id: str, embedding_vector: np.ndarray,
                       image_path: str = None) -> bool:
        """Store a face embedding in the database."""
        embedding_json = json.dumps(embedding_vector.tolist())
        return self.db_ops.save_face_embedding(
            worker_id=worker_id,
            embedding_vector=embedding_json,
            image_path=image_path
        )

    def get_worker_info(self, worker_id: str) -> Optional[dict]:
        """Get worker info as a dictionary."""
        worker = self.db_ops.get_worker_by_id(worker_id)
        if worker is None:
            return None
        return {
            'worker_id': worker.worker_id,
            'name': worker.name,
            'email': worker.email,
            'phone': worker.phone,
            'department': worker.department,
            'position': worker.position,
            'is_active': worker.is_active
        }

    def deactivate_worker(self, worker_id: str) -> bool:
        """Mark a worker as inactive."""
        from config.database import SessionLocal
        session = SessionLocal()
        try:
            from .models import Worker
            worker = session.query(Worker).filter_by(worker_id=worker_id).first()
            if worker:
                worker.is_active = False
                session.commit()
                logger.info(f"Deactivated worker {worker_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to deactivate worker {worker_id}: {e}")
            return False
        finally:
            session.close()
