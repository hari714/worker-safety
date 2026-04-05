"""
Database CRUD Operations.

Provides DatabaseOperations class with all database read/write methods
used by the API and monitoring system.
"""

import json
import logging
from datetime import datetime, date, timedelta
from typing import List, Optional

from config.database import SessionLocal
from .models import (
    Worker, ViolationLog, ComplianceReport, WorkerFaceEmbedding,
    calculate_severity
)

logger = logging.getLogger(__name__)


class DatabaseOperations:
    """CRUD operations for the safety database."""

    def __init__(self, session_factory=None):
        self.session_factory = session_factory or SessionLocal

    def _get_session(self):
        return self.session_factory()

    # ── Worker CRUD ──────────────────────────────────────────────

    def add_worker(self, worker_id: str, name: str, email: str,
                   phone: str = None, department: str = None,
                   position: str = None) -> bool:
        """Insert a new worker into the workers table."""
        session = self._get_session()
        try:
            worker = Worker(
                worker_id=worker_id, name=name, email=email,
                phone=phone, department=department, position=position
            )
            session.add(worker)
            session.commit()
            logger.info(f"Added worker {worker_id} ({name})")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to add worker {worker_id}: {e}")
            return False
        finally:
            session.close()

    def get_worker_by_id(self, worker_id: str) -> Optional[Worker]:
        """Fetch a worker by their ID."""
        session = self._get_session()
        try:
            return session.query(Worker).filter_by(worker_id=worker_id).first()
        finally:
            session.close()

    def get_all_workers(self, active_only: bool = True) -> List[Worker]:
        """Get all workers, optionally filtering by active status."""
        session = self._get_session()
        try:
            query = session.query(Worker)
            if active_only:
                query = query.filter_by(is_active=True)
            return query.all()
        finally:
            session.close()

    def update_worker_last_seen(self, worker_id: str) -> bool:
        """Update a worker's last_seen timestamp to now."""
        session = self._get_session()
        try:
            worker = session.query(Worker).filter_by(worker_id=worker_id).first()
            if worker:
                worker.last_seen = datetime.utcnow()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update last_seen for {worker_id}: {e}")
            return False
        finally:
            session.close()

    # ── Violation CRUD ───────────────────────────────────────────

    def log_violation(self, worker_id: str, missing_ppe: set,
                      image_path: str = None, severity: str = None) -> Optional[int]:
        """Log a PPE violation.

        Args:
            worker_id: Worker ID (or "UNKNOWN")
            missing_ppe: Set of missing PPE item names
            image_path: Path to violation screenshot
            severity: Override severity (auto-calculated if None)

        Returns:
            violation_id on success, None on failure
        """
        if severity is None:
            severity = calculate_severity(len(missing_ppe))

        session = self._get_session()
        try:
            violation = ViolationLog(
                worker_id=worker_id if worker_id != "UNKNOWN" else None,
                timestamp=datetime.utcnow(),
                missing_ppe=json.dumps(sorted(list(missing_ppe))),
                image_path=image_path,
                severity=severity
            )
            session.add(violation)
            session.commit()
            vid = violation.violation_id
            logger.info(f"Logged violation #{vid} for {worker_id} — missing: {missing_ppe}")
            return vid
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to log violation for {worker_id}: {e}")
            return None
        finally:
            session.close()

    def get_violations_today(self, worker_id: str = None) -> List[ViolationLog]:
        """Get today's violations, optionally filtered by worker."""
        session = self._get_session()
        try:
            today_start = datetime.combine(date.today(), datetime.min.time())
            query = session.query(ViolationLog).filter(
                ViolationLog.timestamp >= today_start
            )
            if worker_id:
                query = query.filter_by(worker_id=worker_id)
            return query.order_by(ViolationLog.timestamp.desc()).all()
        finally:
            session.close()

    def get_violation_by_id(self, violation_id: int) -> Optional[ViolationLog]:
        """Fetch a specific violation by ID."""
        session = self._get_session()
        try:
            return session.query(ViolationLog).filter_by(violation_id=violation_id).first()
        finally:
            session.close()

    def update_email_sent(self, violation_id: int) -> bool:
        """Mark a violation's email as sent."""
        session = self._get_session()
        try:
            violation = session.query(ViolationLog).filter_by(violation_id=violation_id).first()
            if violation:
                violation.email_sent = True
                violation.email_sent_time = datetime.utcnow()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update email_sent for violation #{violation_id}: {e}")
            return False
        finally:
            session.close()

    def get_violations_for_period(self, worker_id: str = None,
                                   days: int = 7) -> List[ViolationLog]:
        """Get violations for the past N days."""
        session = self._get_session()
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            query = session.query(ViolationLog).filter(
                ViolationLog.timestamp >= start_date
            )
            if worker_id:
                query = query.filter_by(worker_id=worker_id)
            return query.order_by(ViolationLog.timestamp.desc()).all()
        finally:
            session.close()

    # ── Statistics ───────────────────────────────────────────────

    def get_daily_statistics(self, target_date: date = None) -> dict:
        """Get aggregated statistics for a given day."""
        session = self._get_session()
        try:
            if target_date is None:
                target_date = date.today()
            day_start = datetime.combine(target_date, datetime.min.time())
            day_end = day_start + timedelta(days=1)

            violations = session.query(ViolationLog).filter(
                ViolationLog.timestamp >= day_start,
                ViolationLog.timestamp < day_end
            ).all()

            # Aggregate per-PPE counts
            ppe_counts = {}
            unique_workers = set()
            for v in violations:
                if v.worker_id:
                    unique_workers.add(v.worker_id)
                try:
                    items = json.loads(v.missing_ppe) if v.missing_ppe else []
                except json.JSONDecodeError:
                    items = []
                for item in items:
                    ppe_counts[item] = ppe_counts.get(item, 0) + 1

            return {
                'total_violations': len(violations),
                'unique_workers': len(unique_workers),
                'missing_ppe_count': ppe_counts
            }
        finally:
            session.close()

    def get_worker_statistics(self, worker_id: str, days: int = 7) -> dict:
        """Get violation statistics for a specific worker over N days."""
        violations = self.get_violations_for_period(worker_id=worker_id, days=days)

        violations_by_date = {}
        ppe_summary = {}
        for v in violations:
            day_str = v.timestamp.strftime('%Y-%m-%d') if v.timestamp else 'unknown'
            violations_by_date[day_str] = violations_by_date.get(day_str, 0) + 1
            try:
                items = json.loads(v.missing_ppe) if v.missing_ppe else []
            except json.JSONDecodeError:
                items = []
            for item in items:
                ppe_summary[item] = ppe_summary.get(item, 0) + 1

        return {
            'total_violations': len(violations),
            'violations_by_date': violations_by_date,
            'missing_ppe_summary': ppe_summary
        }

    # ── Face Embedding ───────────────────────────────────────────

    def save_face_embedding(self, worker_id: str, embedding_vector: str,
                             image_path: str = None) -> bool:
        """Save a face embedding record to the database."""
        session = self._get_session()
        try:
            record = WorkerFaceEmbedding(
                worker_id=worker_id,
                embedding_vector=embedding_vector,
                image_path=image_path
            )
            session.add(record)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save face embedding for {worker_id}: {e}")
            return False
        finally:
            session.close()
