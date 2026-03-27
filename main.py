"""
Workplace Safety and Access Control System
Using YOLO PPE and Face Detection

Entry point for the application.
"""

import argparse
import logging
from config.settings import (
    DATABASE_URL, SENDER_EMAIL, SENDER_PASSWORD,
    CAMERA_ID, PPE_MODEL_PATH, LOG_LEVEL
)

logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Workplace Safety Monitoring System'
    )
    parser.add_argument(
        '--mode', type=str, default='webcam',
        choices=['webcam', 'video', 'api'],
        help='Run mode: webcam (live camera), video (file), api (Flask server)'
    )
    parser.add_argument(
        '--video', type=str, default=None,
        help='Path to video file (required if mode=video)'
    )
    parser.add_argument(
        '--host', type=str, default='0.0.0.0',
        help='API host (default: 0.0.0.0)'
    )
    parser.add_argument(
        '--port', type=int, default=5000,
        help='API port (default: 5000)'
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Workplace Safety Monitoring System")
    logger.info("=" * 60)
    logger.info(f"Mode: {args.mode}")
    logger.info(f"PPE Model: {PPE_MODEL_PATH}")
    logger.info(f"Database: {DATABASE_URL}")
    logger.info(f"Email: {SENDER_EMAIL}")

    if args.mode == 'webcam':
        logger.info(f"Camera ID: {CAMERA_ID}")
        # Phase 5: Will import and run WorkplaceSafetyMonitor.run_from_webcam()
        logger.info("Webcam mode will be available after Phase 5 implementation.")

    elif args.mode == 'video':
        if not args.video:
            logger.error("Please provide --video path for video mode")
            return
        logger.info(f"Video: {args.video}")
        # Phase 5: Will import and run WorkplaceSafetyMonitor.run_from_video()
        logger.info("Video mode will be available after Phase 5 implementation.")

    elif args.mode == 'api':
        logger.info(f"Starting API server at {args.host}:{args.port}")
        # Phase 5: Will import and run Flask app
        logger.info("API mode will be available after Phase 5 implementation.")


if __name__ == '__main__':
    main()
