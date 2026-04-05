"""
API Middleware — Error handlers and request logging.
"""

import logging
from flask import jsonify, request

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Register error handlers and request hooks on a Flask app."""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"status": "error", "message": str(error.description)}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"status": "error", "message": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500

    @app.before_request
    def log_request():
        logger.info(f"{request.method} {request.path}")
