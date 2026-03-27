from dataclasses import dataclass
from typing import Tuple


@dataclass
class PPEDetection:
    """PPE Detection result."""
    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    x_center: float
    y_center: float


# PPE Class definitions
CLASS_NAMES = {
    0: 'helmet',
    1: 'gloves',
    2: 'vest',
    3: 'boots',
    4: 'goggles'
}

REQUIRED_PPE = {'helmet', 'gloves', 'vest', 'boots', 'goggles'}

# Bounding box colors (BGR format for OpenCV)
CLASS_COLORS = {
    'helmet': (0, 255, 0),      # Green
    'gloves': (255, 0, 0),      # Blue
    'boots': (0, 0, 255),       # Red
    'goggles': (255, 255, 0),   # Cyan
    'vest': (255, 0, 255)       # Magenta
}
