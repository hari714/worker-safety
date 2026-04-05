"""
PPE Compliance Checker.

Centralizes compliance logic: checks detected PPE against requirements
and calculates violation severity.
"""

from typing import List, Tuple, Set
from ppe_detection.ppe_classes import PPEDetection, REQUIRED_PPE
from worker_management.models import calculate_severity


class ComplianceChecker:
    """Checks PPE compliance and calculates severity."""

    def __init__(self, required_ppe: Set[str] = None):
        self.required_ppe = required_ppe or REQUIRED_PPE

    def check_compliance(self, detections: List[PPEDetection]) -> Tuple[bool, set]:
        """Check if all required PPE is detected.

        Args:
            detections: List of PPE detections for a person

        Returns:
            (is_compliant, missing_ppe_set)
        """
        detected = {d.class_name for d in detections}
        missing = self.required_ppe - detected
        return len(missing) == 0, missing

    def get_severity(self, missing_ppe: set) -> str:
        """Calculate violation severity from missing PPE count."""
        return calculate_severity(len(missing_ppe))
