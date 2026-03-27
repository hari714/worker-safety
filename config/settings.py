import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'sqlite:///safety_db.sqlite'
)

# Email Configuration
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))

# Model Paths
PPE_MODEL_PATH = os.getenv('PPE_MODEL_PATH', 'models/best.pt')
FACE_EMBEDDING_DIR = os.getenv('FACE_EMBEDDING_DIR', 'worker_embeddings')

# Camera/Video Settings
CAMERA_ID = int(os.getenv('CAMERA_ID', 0))
VIDEO_FPS = int(os.getenv('VIDEO_FPS', 30))
FRAME_WIDTH = int(os.getenv('FRAME_WIDTH', 1280))
FRAME_HEIGHT = int(os.getenv('FRAME_HEIGHT', 720))

# Detection Settings
PPE_CONFIDENCE_THRESHOLD = float(os.getenv('PPE_CONFIDENCE_THRESHOLD', 0.08))
FACE_CONFIDENCE_THRESHOLD = float(os.getenv('FACE_CONFIDENCE_THRESHOLD', 0.6))
SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', 0.6))

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/safety_system.log')
