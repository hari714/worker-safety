import re


def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_worker_id(worker_id):
    """Validate worker ID format."""
    return bool(worker_id) and len(worker_id) <= 50


def validate_phone(phone):
    """Validate phone number."""
    if phone is None:
        return True
    pattern = r'^\+?[0-9]{7,15}$'
    return re.match(pattern, phone) is not None
