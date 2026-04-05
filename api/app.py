"""
Flask Application Factory.

Creates and configures the Flask app with all services.
"""

import logging
from flask import Flask
from flask_cors import CORS

from api.routes import api_bp
from api.middleware import register_error_handlers
from config.database import init_db, SessionLocal
from config.email_config import EMAIL_CONFIG
from config.settings import PPE_MODEL_PATH, PPE_CONFIDENCE_THRESHOLD
from worker_management.db_operations import DatabaseOperations
from notification_system.email_sender import EmailNotificationSystem
from ppe_detection import PPEDetector

logger = logging.getLogger(__name__)


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)

    # Initialize database tables
    init_db()

    # Create shared services
    db_ops = DatabaseOperations(session_factory=SessionLocal)
    email_system = EmailNotificationSystem(EMAIL_CONFIG)
    ppe_detector = PPEDetector(
        model_path=PPE_MODEL_PATH,
        confidence_threshold=PPE_CONFIDENCE_THRESHOLD
    )

    # Face recognition (optional)
    face_system = None
    try:
        from face_recognition import FaceRecognitionSystem
        face_system = FaceRecognitionSystem()
    except Exception as e:
        logger.warning(f"Face recognition not available for API: {e}")

    # Store services on app config for route access
    app.config['db_ops'] = db_ops
    app.config['email_system'] = email_system
    app.config['ppe_detector'] = ppe_detector
    app.config['face_system'] = face_system

    # Register blueprint and error handlers
    app.register_blueprint(api_bp)
    register_error_handlers(app)

    logger.info("Flask API application created")
    return app
