"""
Violation Logger.

Handles the full violation workflow: save screenshot, log to database,
and trigger email notification.
"""

import logging
import cv2
from datetime import datetime
from typing import Optional

from worker_management.db_operations import DatabaseOperations
from worker_management.models import calculate_severity
from notification_system.email_sender import EmailNotificationSystem, ViolationRecord
from utils.helpers import ensure_dir, generate_violation_filename

logger = logging.getLogger(__name__)


class ViolationLogger:
    """Logs violations: screenshot + database + email."""

    def __init__(self, db_ops: DatabaseOperations,
                 email_system: EmailNotificationSystem):
        self.db_ops = db_ops
        self.email_system = email_system

    def log_violation(self, worker_id: str, worker_name: str,
                      worker_email: Optional[str], missing_ppe: set,
                      frame=None, violation_count: int = 1) -> bool:
        """Process a full violation: save image, log to DB, send email.

        Args:
            worker_id: Worker ID or "UNKNOWN"
            worker_name: Worker name or "Unknown Worker"
            worker_email: Worker email (None for unknown workers)
            missing_ppe: Set of missing PPE item names
            frame: BGR numpy frame for screenshot (optional)
            violation_count: Today's violation count for this worker

        Returns:
            True if violation was logged successfully
        """
        # 1. Save violation screenshot
        image_path = None
        if frame is not None:
            image_path = self._save_screenshot(frame, worker_id)

        # 2. Calculate severity
        severity = calculate_severity(len(missing_ppe))

        # 3. Log to database
        violation_id = self.db_ops.log_violation(
            worker_id=worker_id,
            missing_ppe=missing_ppe,
            image_path=image_path,
            severity=severity
        )

        if violation_id is None:
            logger.error(f"Failed to log violation for {worker_id}")
            return False

        # 4. Send email notification (if worker has email)
        if worker_email:
            record = ViolationRecord(
                worker_id=worker_id,
                worker_name=worker_name,
                worker_email=worker_email,
                timestamp=datetime.utcnow(),
                missing_ppe=missing_ppe,
                violation_count=violation_count,
                image_path=image_path
            )
            email_sent = self.email_system.send_email(record)
            if email_sent:
                self.db_ops.update_email_sent(violation_id)

        return True

    def _save_screenshot(self, frame, worker_id: str) -> Optional[str]:
        """Save violation screenshot to violations/ directory."""
        try:
            ensure_dir('violations')
            filepath = generate_violation_filename(worker_id)
            cv2.imwrite(filepath, frame)
            logger.debug(f"Saved violation screenshot: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save violation screenshot: {e}")
            return None
