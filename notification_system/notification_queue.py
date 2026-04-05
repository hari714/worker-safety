"""
Notification Queue for batching daily report data.

Accumulates violation records throughout the day for the daily summary report.
"""

from typing import List
from .email_sender import ViolationRecord


class NotificationQueue:
    """Simple in-memory queue for accumulating violations for daily reports."""

    def __init__(self):
        self._queue: List[ViolationRecord] = []

    def add(self, violation: ViolationRecord):
        """Add a violation record to the queue."""
        self._queue.append(violation)

    def get_all(self) -> List[ViolationRecord]:
        """Get all queued violation records."""
        return list(self._queue)

    def clear(self):
        """Clear the queue."""
        self._queue.clear()

    def count(self) -> int:
        """Get the number of queued records."""
        return len(self._queue)
