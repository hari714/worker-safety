"""
Flask API Routes — 9 endpoints for the safety system.

All endpoints return JSON with {"status": "success/error", ...} format.
"""

import json
import logging
from datetime import date, datetime
from flask import Blueprint, request, jsonify, current_app

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')


# ── Serialization Helpers ────────────────────────────────────────

def serialize_worker(w):
    return {
        "worker_id": w.worker_id,
        "name": w.name,
        "email": w.email,
        "phone": w.phone,
        "department": w.department,
        "position": w.position,
        "is_active": w.is_active,
        "date_registered": w.date_registered.isoformat() if w.date_registered else None,
        "last_seen": w.last_seen.isoformat() if w.last_seen else None
    }


def serialize_violation(v):
    return {
        "violation_id": v.violation_id,
        "worker_id": v.worker_id,
        "timestamp": v.timestamp.isoformat() if v.timestamp else None,
        "missing_ppe": json.loads(v.missing_ppe) if v.missing_ppe else [],
        "image_path": v.image_path,
        "email_sent": v.email_sent,
        "severity": v.severity
    }


def _get_db_ops():
    return current_app.config['db_ops']


# ── 1. GET /api/workers ──────────────────────────────────────────

@api_bp.route('/workers', methods=['GET'])
def get_workers():
    """List all active workers."""
    db_ops = _get_db_ops()
    workers = db_ops.get_all_workers()
    return jsonify({
        "status": "success",
        "data": [serialize_worker(w) for w in workers]
    })


# ── 2. POST /api/workers ─────────────────────────────────────────

@api_bp.route('/workers', methods=['POST'])
def create_worker():
    """Add a new worker."""
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "JSON body required"}), 400

    required = ['worker_id', 'name', 'email']
    for field in required:
        if field not in data:
            return jsonify({"status": "error", "message": f"Missing field: {field}"}), 400

    db_ops = _get_db_ops()
    success = db_ops.add_worker(
        worker_id=data['worker_id'],
        name=data['name'],
        email=data['email'],
        phone=data.get('phone'),
        department=data.get('department'),
        position=data.get('position')
    )

    if success:
        return jsonify({"status": "success", "message": "Worker added successfully"}), 201
    return jsonify({"status": "error", "message": "Failed to add worker (may already exist)"}), 409


# ── 3. GET /api/workers/<worker_id> ──────────────────────────────

@api_bp.route('/workers/<worker_id>', methods=['GET'])
def get_worker(worker_id):
    """Get a specific worker by ID."""
    db_ops = _get_db_ops()
    worker = db_ops.get_worker_by_id(worker_id)
    if worker is None:
        return jsonify({"status": "error", "message": "Worker not found"}), 404
    return jsonify({"status": "success", "data": serialize_worker(worker)})


# ── 4. GET /api/violations/today ─────────────────────────────────

@api_bp.route('/violations/today', methods=['GET'])
def get_violations_today():
    """Get today's violations, optionally filtered by worker_id."""
    db_ops = _get_db_ops()
    worker_id = request.args.get('worker_id')
    violations = db_ops.get_violations_today(worker_id=worker_id)
    return jsonify({
        "status": "success",
        "data": [serialize_violation(v) for v in violations]
    })


# ── 5. GET /api/violations/<violation_id> ────────────────────────

@api_bp.route('/violations/<int:violation_id>', methods=['GET'])
def get_violation(violation_id):
    """Get a specific violation by ID."""
    db_ops = _get_db_ops()
    violation = db_ops.get_violation_by_id(violation_id)
    if violation is None:
        return jsonify({"status": "error", "message": "Violation not found"}), 404
    return jsonify({"status": "success", "data": serialize_violation(violation)})


# ── 6. GET /api/statistics/daily ─────────────────────────────────

@api_bp.route('/statistics/daily', methods=['GET'])
def get_daily_statistics():
    """Get daily violation statistics."""
    db_ops = _get_db_ops()
    date_str = request.args.get('date')
    target_date = None
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid date format (use YYYY-MM-DD)"}), 400
    else:
        target_date = date.today()

    stats = db_ops.get_daily_statistics(target_date)
    return jsonify({
        "status": "success",
        "date": target_date.isoformat(),
        "data": stats
    })


# ── 7. GET /api/statistics/worker/<worker_id> ────────────────────

@api_bp.route('/statistics/worker/<worker_id>', methods=['GET'])
def get_worker_statistics(worker_id):
    """Get violation statistics for a specific worker."""
    db_ops = _get_db_ops()
    days = request.args.get('days', 7, type=int)
    stats = db_ops.get_worker_statistics(worker_id, days=days)
    return jsonify({
        "status": "success",
        "worker_id": worker_id,
        "period_days": days,
        "data": stats
    })


# ── 8. POST /api/workers/<worker_id>/register-face ──────────────

@api_bp.route('/workers/<worker_id>/register-face', methods=['POST'])
def register_face(worker_id):
    """Register a worker's face from uploaded images."""
    db_ops = _get_db_ops()

    # Verify worker exists
    worker = db_ops.get_worker_by_id(worker_id)
    if worker is None:
        return jsonify({"status": "error", "message": "Worker not found"}), 404

    # Get uploaded images
    files = request.files.getlist('images')
    if not files:
        return jsonify({"status": "error", "message": "No images uploaded"}), 400

    # Try to use face recognition system
    face_system = current_app.config.get('face_system')
    if face_system is None:
        return jsonify({"status": "error", "message": "Face recognition not available"}), 503

    import cv2
    import numpy as np

    images = []
    for f in files:
        file_bytes = np.frombuffer(f.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if img is not None:
            images.append(img)

    if len(images) < 3:
        return jsonify({
            "status": "error",
            "message": f"Need at least 3 valid images, got {len(images)}"
        }), 400

    success = face_system.register_worker(
        worker_id=worker_id,
        name=worker.name,
        email=worker.email,
        images=images
    )

    if success:
        return jsonify({
            "status": "success",
            "message": f"Face registered successfully for worker {worker_id}"
        })
    return jsonify({"status": "error", "message": "Face registration failed"}), 500


# ── 9. GET /api/health ───────────────────────────────────────────

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Check system component health."""
    components = {
        "ppe_model": "loaded" if current_app.config.get('ppe_detector') else "not loaded",
        "face_recognition": "ready" if current_app.config.get('face_system') else "not available",
        "database": "connected",
        "email": "configured" if current_app.config.get('email_system') else "not configured"
    }

    # Quick DB check
    try:
        db_ops = _get_db_ops()
        db_ops.get_all_workers()
    except Exception:
        components["database"] = "disconnected"

    return jsonify({"status": "healthy", "components": components})
