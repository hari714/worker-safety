"""
Email Notification System.

Sends PPE violation alerts and daily summary reports via SMTP (Gmail).
Implements per-worker cooldown to prevent email flooding.
"""

import os
import logging
import smtplib
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, List
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from config.settings import SENDER_EMAIL, SENDER_PASSWORD, SMTP_SERVER, SMTP_PORT
from .email_templates import violation_alert_template, daily_report_template

logger = logging.getLogger(__name__)


@dataclass
class ViolationRecord:
    """Represents a violation event for email notification."""
    worker_id: str
    worker_name: str
    worker_email: str
    timestamp: datetime
    missing_ppe: set
    violation_count: int
    image_path: Optional[str] = None


class EmailNotificationSystem:
    """Sends safety violation emails with cooldown management."""

    def __init__(self, email_config: dict = None):
        config = email_config or {}
        self.sender_email = config.get('sender_email') or SENDER_EMAIL
        self.sender_password = config.get('sender_password') or SENDER_PASSWORD
        self.smtp_server = config.get('smtp_server') or SMTP_SERVER
        self.smtp_port = config.get('smtp_port') or SMTP_PORT
        self.cooldown_minutes = 15

        # In-memory cooldown tracker: {worker_id: last_email_datetime}
        self._last_email_sent = {}

    def _should_send_email(self, worker_id: str) -> bool:
        """Check if cooldown period has passed for a worker."""
        if worker_id not in self._last_email_sent:
            return True
        elapsed = datetime.utcnow() - self._last_email_sent[worker_id]
        return elapsed >= timedelta(minutes=self.cooldown_minutes)

    def create_violation_email(self, violation: ViolationRecord) -> MIMEMultipart:
        """Build a MIME email with styled HTML and optional inline image."""
        msg = MIMEMultipart('related')
        msg['Subject'] = f"Safety Alert: PPE Violation - {violation.worker_name}"
        msg['From'] = self.sender_email
        msg['To'] = violation.worker_email

        # Generate HTML body
        timestamp_str = violation.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        html = violation_alert_template(
            worker_name=violation.worker_name,
            worker_id=violation.worker_id,
            missing_ppe=sorted(list(violation.missing_ppe)),
            timestamp=timestamp_str,
            violation_count=violation.violation_count
        )
        msg.attach(MIMEText(html, 'html'))

        # Attach violation screenshot inline if available
        if violation.image_path and os.path.exists(violation.image_path):
            try:
                with open(violation.image_path, 'rb') as f:
                    img = MIMEImage(f.read())
                img.add_header('Content-ID', '<violation_image>')
                img.add_header('Content-Disposition', 'inline', filename='violation.jpg')
                msg.attach(img)
            except Exception as e:
                logger.warning(f"Could not attach violation image: {e}")

        return msg

    def send_email(self, violation: ViolationRecord) -> bool:
        """Send a violation alert email with cooldown check.

        Returns:
            True if email was sent, False if skipped (cooldown) or failed
        """
        if not violation.worker_email:
            logger.debug(f"No email for worker {violation.worker_id}, skipping")
            return False

        if not self._should_send_email(violation.worker_id):
            logger.debug(
                f"Cooldown active for {violation.worker_id}, "
                f"skipping email (last sent: {self._last_email_sent[violation.worker_id]})"
            )
            return False

        if not self.sender_email or not self.sender_password:
            logger.warning("Email credentials not configured, skipping send")
            return False

        try:
            msg = self.create_violation_email(violation)
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            self._last_email_sent[violation.worker_id] = datetime.utcnow()
            logger.info(f"Violation email sent to {violation.worker_email} ({violation.worker_id})")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {violation.worker_email}: {e}")
            return False

    def send_daily_report_email(self, recipient_email: str,
                                 violations: List[dict],
                                 report_date: str = None) -> bool:
        """Send a daily summary report email.

        Args:
            recipient_email: Safety manager's email
            violations: List of violation dicts for the report table
            report_date: Date string (defaults to today)

        Returns:
            True if sent successfully
        """
        if not self.sender_email or not self.sender_password:
            logger.warning("Email credentials not configured, skipping daily report")
            return False

        if report_date is None:
            report_date = datetime.utcnow().strftime('%Y-%m-%d')

        try:
            html = daily_report_template(
                report_date=report_date,
                violations=violations,
                total_violations=len(violations)
            )

            msg = MIMEMultipart()
            msg['Subject'] = f"Daily Safety Report - {report_date}"
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg.attach(MIMEText(html, 'html'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            logger.info(f"Daily report sent to {recipient_email} for {report_date}")
            return True

        except Exception as e:
            logger.error(f"Failed to send daily report to {recipient_email}: {e}")
            return False
