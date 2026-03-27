import os
from datetime import datetime


def ensure_dir(directory):
    """Create directory if it doesn't exist."""
    os.makedirs(directory, exist_ok=True)


def generate_violation_filename(worker_id):
    """Generate unique filename for violation screenshot."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"violations/{worker_id}_{timestamp}.jpg"


def get_timestamp_str():
    """Get current timestamp as formatted string."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
