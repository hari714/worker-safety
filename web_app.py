"""
PPE Detection & Face Recognition Web UI
Upload an image or video → See detection results with face identification
"""

import os
import base64
import tempfile
import time
import threading
from datetime import datetime, timezone
import cv2
import numpy as np
from flask import Flask, request, render_template, jsonify, Response
from ultralytics import YOLO

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max for videos

MODEL_PATH = 'models/best.pt'
model = YOLO(MODEL_PATH)

CLASS_NAMES = {0: 'Helmet', 1: 'Gloves', 2: 'Vest', 3: 'Boots', 4: 'Goggles'}
REQUIRED_PPE = {'Helmet', 'Gloves', 'Vest', 'Boots', 'Goggles'}

# PPE Detector for live feed
from ppe_detection.inference import PPEDetector
live_ppe_detector = PPEDetector(MODEL_PATH, confidence_threshold=0.08)

# Face Recognition (optional)
face_system = None
try:
    from face_recognition import FaceRecognitionSystem
    face_system = FaceRecognitionSystem()
    print(f"Face recognition loaded: {len(face_system.database.workers)} worker(s)")
except Exception as e:
    print(f"Face recognition not available: {e}")

# Email Notification System (SMTP)
email_system = None
try:
    from notification_system.email_sender import EmailNotificationSystem, ViolationRecord
    email_system = EmailNotificationSystem()
    print(f"Email system loaded: {email_system.sender_email or 'No credentials configured'}")
except Exception as e:
    print(f"Email system not available: {e}")

# ── Live Camera State ──────────────────────────────────────────────
live_camera = {
    'cap': None,
    'running': False,
    'lock': threading.Lock(),
    'frame_count': 0,
    'face_interval': 5,
    'cached_faces': [],
    # Auto-email tracking for live violations:
    #   auto_email_attempts: {worker_id: datetime} — last time we *tried* to send
    #     (cheap throttle so we don't spawn a thread every frame)
    #   auto_email_results:  {worker_id: {sent, time, message, missing}} — UI state
    'auto_email_attempts': {},
    'auto_email_results': {},
    'auto_email_lock': threading.Lock(),
    'last_status': {
        'faces': [],
        'ppe_found': [],
        'missing_ppe': [],
        'compliant': True,
        'fps': 0.0,
        'auto_emails': {}
    }
}

# Don't re-spawn an auto-email thread for the same worker within this many seconds.
# EmailNotificationSystem enforces a longer per-worker cooldown (15 min) — this just
# keeps the live loop from spawning threads on every face detection cycle.
AUTO_EMAIL_THROTTLE_SECONDS = 30


def _send_violation_email_background(worker_id, worker_name, worker_email,
                                      missing_ppe, frame_snapshot):
    """Worker thread: persist a violation screenshot and email the worker.

    Runs off the live capture thread so frame streaming is never blocked.
    The 15-minute per-worker cooldown inside EmailNotificationSystem handles
    flood protection — this function just records the outcome for the UI.
    """
    image_path = None
    try:
        os.makedirs('violations', exist_ok=True)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_path = os.path.join('violations', f'{worker_id}_{ts}.jpg')
        cv2.imwrite(image_path, frame_snapshot)
    except Exception as e:
        print(f"[auto-email] could not save violation image: {e}")
        image_path = None

    violation = ViolationRecord(
        worker_id=worker_id,
        worker_name=worker_name,
        worker_email=worker_email,
        timestamp=datetime.now(timezone.utc),
        missing_ppe=set(missing_ppe),
        violation_count=1,
        image_path=image_path
    )

    sent = False
    message = ''
    try:
        sent = email_system.send_email(violation)
        message = 'Email sent' if sent else 'Skipped (cooldown or send failed)'
    except Exception as e:
        message = f'Error: {e}'
        print(f"[auto-email] send failed for {worker_id}: {e}")

    with live_camera['auto_email_lock']:
        live_camera['auto_email_results'][worker_id] = {
            'sent': bool(sent),
            'time': datetime.now().strftime('%H:%M:%S'),
            'message': message,
            'missing': sorted(list(missing_ppe))
        }


def _maybe_auto_send_violation_emails(faces_info, missing_ppe, frame):
    """Spawn background email sends for identified, non-compliant workers.

    Called from the live frame generator. Throttled per worker so we don't
    spawn a thread on every face-detection cycle.
    """
    if email_system is None or not email_system.sender_email:
        return
    if not missing_ppe or not faces_info:
        return

    now = datetime.now()
    for f in faces_info:
        if f.get('status') != 'Identified':
            continue
        worker_id = f.get('worker_id')
        worker_email = f.get('email')
        if not worker_id or not worker_email:
            continue

        with live_camera['auto_email_lock']:
            last_attempt = live_camera['auto_email_attempts'].get(worker_id)
            if last_attempt and (now - last_attempt).total_seconds() < AUTO_EMAIL_THROTTLE_SECONDS:
                continue
            live_camera['auto_email_attempts'][worker_id] = now

        threading.Thread(
            target=_send_violation_email_background,
            args=(worker_id, f.get('name', ''), worker_email,
                  list(missing_ppe), frame.copy()),
            daemon=True
        ).start()


# ── Helper Functions ───────────────────────────────────────────────

IMG_SIZE = 640


# MTCNN can fire on hi-vis vests, helmets, and construction signs.
# Stricter thresholds for displaying *unidentified* faces filter those out.
# Identified workers are always kept (their match is the proof of validity).
FACE_DISPLAY_CONF = 0.95
FACE_DISPLAY_MIN_SIZE = 40


def _filter_face_results(face_results):
    """Drop likely false-positive face detections.

    Identified workers always pass; unknowns must clear a higher confidence
    bar and a minimum bbox size.
    """
    filtered = []
    for face_det, worker in face_results:
        if worker:
            filtered.append((face_det, worker))
            continue
        x1, y1, x2, y2 = face_det.bbox
        if (x2 - x1) < FACE_DISPLAY_MIN_SIZE or (y2 - y1) < FACE_DISPLAY_MIN_SIZE:
            continue
        if face_det.confidence < FACE_DISPLAY_CONF:
            continue
        filtered.append((face_det, worker))
    return filtered


def _face_results_to_dicts(face_results):
    """Convert (FaceDetection, Worker) tuples to UI-friendly dicts."""
    faces = []
    for face_det, worker in face_results:
        if worker:
            faces.append({
                'name': worker.worker_name,
                'confidence': f"{worker.confidence:.2f}",
                'status': 'Identified',
                'worker_id': worker.worker_id
            })
        else:
            faces.append({
                'name': 'Unknown',
                'confidence': f"{face_det.confidence:.2f}",
                'status': 'Unknown',
                'worker_id': None
            })
    return faces


def run_face_detection(frame):
    """Run face detection on a frame. Returns list of face info dicts."""
    if face_system is None:
        return []

    try:
        face_results = face_system.identify_faces_in_frame(frame)
        face_results = _filter_face_results(face_results)
        return _face_results_to_dicts(face_results)
    except Exception as e:
        print(f"Face detection error: {e}")
        return []


def draw_faces_on_frame(frame, face_results):
    """Draw face bounding boxes on frame."""
    if face_system is None:
        return frame
    try:
        results = face_system.identify_faces_in_frame(frame)
        frame = face_system.draw_face_detections(frame, results)
    except Exception:
        pass
    return frame


def detect_ppe(image_bytes):
    """Run PPE + face detection on uploaded image."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    if frame is None:
        return None

    if len(frame.shape) == 3 and frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    elif len(frame.shape) == 2:
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

    # PPE Detection
    h, w = frame.shape[:2]
    max_dim = max(h, w)
    scale = 1.0
    if max_dim > 1280:
        scale = 1280 / max_dim
        proc_frame = cv2.resize(frame, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    elif max_dim < IMG_SIZE:
        scale = IMG_SIZE / max_dim
        proc_frame = cv2.resize(frame, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)
    else:
        proc_frame = frame

    results = model(proc_frame, verbose=False, conf=0.08, device='cpu', augment=True)[0]

    img_h, img_w = frame.shape[:2]
    img_area = img_h * img_w
    detections = []
    for box in results.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        x1, y1, x2, y2 = x1 / scale, y1 / scale, x2 / scale, y2 / scale
        x1, y1 = max(0, int(x1)), max(0, int(y1))
        x2, y2 = min(img_w, int(x2)), min(img_h, int(y2))
        box_area = (x2 - x1) * (y2 - y1)
        if box_area > 0.60 * img_area:
            continue
        detections.append({'class_id': cls_id, 'name': CLASS_NAMES.get(cls_id, 'unknown'), 'confidence': conf, 'bbox': (x1, y1, x2, y2)})

    # Draw PPE detections
    for d in detections:
        x1, y1, x2, y2 = d['bbox']
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
        label = d['name']
        (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (x1, y1 - lh - 8), (x1 + lw + 4, y1), (255, 255, 255), -1)
        cv2.putText(frame, label, (x1 + 2, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    # Face Detection — single pass, filter false positives, then draw + report.
    faces = []
    if face_system:
        try:
            face_results = face_system.identify_faces_in_frame(frame)
            face_results = _filter_face_results(face_results)
            frame = face_system.draw_face_detections(frame, face_results)
            faces = _face_results_to_dicts(face_results)
        except Exception as e:
            print(f"Face detection error: {e}")

    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
    image_b64 = base64.b64encode(buffer).decode('utf-8')

    detected_names = {d['name'] for d in detections}
    all_ppe = [{'name': name, 'found': name in detected_names} for name in ['Helmet', 'Gloves', 'Vest', 'Boots', 'Goggles']]
    missing = [name for name in REQUIRED_PPE if name not in detected_names]

    return {
        'mode': 'image',
        'image_b64': image_b64,
        'detections': detections,
        'all_ppe': all_ppe,
        'compliant': len(missing) == 0,
        'missing': missing,
        'detected_count': len(detected_names),
        'missing_count': len(missing),
        'total_objects': len(detections),
        'faces': faces,
        'face_count': len(faces)
    }


def process_video(video_path):
    """Process video: sample frames, run PPE + face detection."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None

    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    sample_interval = max(1, int(fps))
    sample_positions = list(range(0, total_frames, sample_interval))[:20]

    frames_data = []
    all_faces = {}
    compliant_count = 0
    total_faces_count = 0

    from ppe_detection.inference import PPEDetector
    ppe_detector = PPEDetector('models/best.pt', confidence_threshold=0.08)

    for pos in sample_positions:
        cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
        ret, frame = cap.read()
        if not ret:
            continue

        time_sec = round(pos / fps, 1)

        detections = ppe_detector.detect_ppe(frame)
        annotated = ppe_detector.draw_detections(frame.copy(), detections)

        # PPEDetector returns lowercase class names ('helmet', 'gloves', ...)
        # while REQUIRED_PPE is Title-case — normalize before comparing.
        detected_names = {d.class_name.title() for d in detections}
        missing = list(REQUIRED_PPE - detected_names)
        is_compliant = len(missing) == 0
        if is_compliant:
            compliant_count += 1

        faces = []
        if face_system:
            try:
                face_results = face_system.identify_faces_in_frame(frame)
                annotated = face_system.draw_face_detections(annotated, face_results)
                for face_det, worker in face_results:
                    total_faces_count += 1
                    if worker:
                        name = worker.worker_name
                        conf = worker.confidence
                        status = 'Identified'
                    else:
                        name = 'Unknown'
                        conf = face_det.confidence
                        status = 'Unknown'
                    faces.append(name)
                    if name not in all_faces:
                        all_faces[name] = {'count': 0, 'total_conf': 0.0, 'status': status}
                    all_faces[name]['count'] += 1
                    all_faces[name]['total_conf'] += conf
            except Exception as e:
                print(f"Face detection error at {time_sec}s: {e}")

        _, buffer = cv2.imencode('.jpg', annotated, [cv2.IMWRITE_JPEG_QUALITY, 85])
        image_b64 = base64.b64encode(buffer).decode('utf-8')

        frames_data.append({
            'image_b64': image_b64,
            'time': time_sec,
            'compliant': is_compliant,
            'missing': missing,
            'ppe_found': list(detected_names),
            'faces': len(faces)
        })

    cap.release()

    faces_summary = []
    for name, info in sorted(all_faces.items(), key=lambda x: x[1]['count'], reverse=True):
        faces_summary.append({
            'name': name,
            'frame_count': info['count'],
            'avg_conf': f"{info['total_conf'] / info['count']:.2f}",
            'status': info['status']
        })

    analyzed = len(frames_data)
    compliance_pct = round(compliant_count / analyzed * 100) if analyzed > 0 else 0

    return {
        'mode': 'video',
        'video_info': {
            'duration': round(duration, 1),
            'fps': round(fps, 1),
            'resolution': f"{width}x{height}",
            'total_frames': total_frames
        },
        'frames_analyzed': analyzed,
        'violation_frames': analyzed - compliant_count,
        'compliance_pct': compliance_pct,
        'total_faces': total_faces_count,
        'faces_summary': faces_summary,
        'frames': frames_data
    }


# ── Page Routes ────────────────────────────────────────────────────

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    if request.method == 'POST':
        file = request.files.get('image')
        if file and file.filename:
            image_bytes = file.read()
            result = detect_ppe(image_bytes)
            if result is None:
                error = "Could not read image. Try a different file."
    return render_template('index.html', result=result, error=error, active_tab='image')


@app.route('/video', methods=['POST'])
def video_upload():
    result = None
    error = None
    file = request.files.get('video')
    if not file or not file.filename:
        return render_template('index.html', result=None, error="No video file uploaded", active_tab='video')

    suffix = os.path.splitext(file.filename)[1] or '.mp4'
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        file.save(tmp.name)
        tmp.close()
        result = process_video(tmp.name)
        if result is None:
            error = "Could not process video. Try a different file."
    except Exception as e:
        error = f"Video processing failed: {str(e)}"
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass

    return render_template('index.html', result=result, error=error, active_tab='video')


# ── Live Camera Routes ─────────────────────────────────────────────

def generate_live_frames():
    """Generator that yields MJPEG frames with PPE + face detection."""
    frame_count = 0
    cached_face_results = []
    fps_start = time.time()
    fps_count = 0
    current_fps = 0.0

    while live_camera['running']:
        with live_camera['lock']:
            cap = live_camera['cap']
            if cap is None or not cap.isOpened():
                break
            ret, frame = cap.read()

        if not ret:
            continue

        fps_count += 1
        elapsed = time.time() - fps_start
        if elapsed >= 1.0:
            current_fps = fps_count / elapsed
            fps_count = 0
            fps_start = time.time()

        annotated = frame.copy()

        try:
            detections = live_ppe_detector.detect_ppe(frame)
            annotated = live_ppe_detector.draw_detections(annotated, detections)
            # PPEDetector returns lowercase class names — normalize to Title case
            # so they match REQUIRED_PPE.
            detected_names = [d.class_name.title() for d in detections]
            missing = list(REQUIRED_PPE - set(detected_names))
            is_compliant = len(missing) == 0
        except Exception:
            detected_names = []
            missing = list(REQUIRED_PPE)
            is_compliant = False

        frame_count += 1
        faces_info = []
        if face_system and frame_count % live_camera['face_interval'] == 0:
            try:
                face_results = face_system.identify_faces_in_frame(frame)
                cached_face_results = face_results
                for face_det, worker in face_results:
                    if worker:
                        faces_info.append({
                            'name': worker.worker_name,
                            'confidence': f"{worker.confidence:.2f}",
                            'status': 'Identified',
                            'worker_id': worker.worker_id,
                            'email': worker.email
                        })
                    else:
                        faces_info.append({
                            'name': 'Unknown',
                            'confidence': f"{face_det.confidence:.2f}",
                            'status': 'Unknown',
                            'worker_id': None,
                            'email': None
                        })
            except Exception:
                cached_face_results = []

        if face_system and cached_face_results:
            try:
                annotated = face_system.draw_face_detections(annotated, cached_face_results)
            except Exception:
                pass

        if not faces_info and cached_face_results:
            for face_det, worker in cached_face_results:
                if worker:
                    faces_info.append({
                        'name': worker.worker_name,
                        'confidence': f"{worker.confidence:.2f}",
                        'status': 'Identified',
                        'worker_id': worker.worker_id,
                        'email': worker.email
                    })
                else:
                    faces_info.append({
                        'name': 'Unknown',
                        'confidence': f"{face_det.confidence:.2f}",
                        'status': 'Unknown',
                        'worker_id': None,
                        'email': None
                    })

        h, w = annotated.shape[:2]
        cv2.putText(annotated, f"FPS: {current_fps:.1f}", (w - 140, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2, cv2.LINE_AA)
        face_label = "Face: ON" if face_system else "Face: OFF"
        face_color = (0, 255, 0) if face_system else (0, 0, 255)
        cv2.putText(annotated, face_label, (w - 140, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, face_color, 2, cv2.LINE_AA)

        status_color = (0, 255, 0) if is_compliant else (0, 0, 255)
        status_text = "COMPLIANT" if is_compliant else f"MISSING: {', '.join(missing)}"
        cv2.putText(annotated, status_text, (10, h - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2, cv2.LINE_AA)

        # Auto-send violation emails for identified workers who are non-compliant.
        # Only attempt on face-detection cycles (not every frame) — the throttle
        # inside _maybe_auto_send_violation_emails further protects against bursts.
        if not is_compliant and frame_count % live_camera['face_interval'] == 0:
            _maybe_auto_send_violation_emails(faces_info, missing, frame)

        with live_camera['auto_email_lock']:
            auto_emails_snapshot = dict(live_camera['auto_email_results'])

        live_camera['last_status'] = {
            'faces': faces_info,
            'ppe_found': detected_names,
            'missing_ppe': missing,
            'compliant': is_compliant,
            'fps': round(current_fps, 1),
            'auto_emails': auto_emails_snapshot
        }

        _, buffer = cv2.imencode('.jpg', annotated, [cv2.IMWRITE_JPEG_QUALITY, 75])
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/live/start', methods=['POST'])
def live_start():
    """Start the live camera feed."""
    if live_camera['running']:
        return jsonify({'status': 'already_running'})

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return jsonify({'status': 'error', 'message': 'Cannot open camera'}), 500

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    # Warm-up: discard initial black frames (common on Windows webcams)
    for _ in range(10):
        cap.read()

    with live_camera['lock']:
        live_camera['cap'] = cap
        live_camera['running'] = True
        live_camera['frame_count'] = 0
        live_camera['cached_faces'] = []

    # Clear auto-email UI state on session start so stale "Email Sent" badges
    # from a previous run don't show. (The 15-min SMTP cooldown still applies.)
    with live_camera['auto_email_lock']:
        live_camera['auto_email_results'].clear()

    return jsonify({'status': 'ok'})


@app.route('/live/stop', methods=['POST'])
def live_stop():
    """Stop the live camera feed."""
    with live_camera['lock']:
        live_camera['running'] = False
        if live_camera['cap'] is not None:
            live_camera['cap'].release()
            live_camera['cap'] = None

    return jsonify({'status': 'ok'})


@app.route('/live_feed')
def live_feed():
    """MJPEG stream endpoint for live camera."""
    if not live_camera['running']:
        return "Camera not started", 503
    return Response(generate_live_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/live/status')
def live_status():
    """Return current detection status as JSON."""
    return jsonify(live_camera['last_status'])


# ── Worker Registration Routes ────────────────────────────────────────

@app.route('/register', methods=['POST'])
def register_worker():
    """Register a new worker with face images from browser webcam."""
    if not face_system:
        return jsonify({'status': 'error', 'message': 'Face recognition system not available'}), 500

    data = request.get_json()
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    images_b64 = data.get('images', [])

    if not name or not email:
        return jsonify({'status': 'error', 'message': 'Name and email are required'}), 400

    if len(images_b64) < 3:
        return jsonify({'status': 'error', 'message': 'At least 3 face photos required'}), 400

    existing_count = len(face_system.database.workers)
    worker_id = f"W{existing_count + 1:03d}"
    while worker_id in face_system.database.workers:
        existing_count += 1
        worker_id = f"W{existing_count + 1:03d}"

    images = []
    for img_b64 in images_b64:
        try:
            if ',' in img_b64:
                img_b64 = img_b64.split(',')[1]
            img_bytes = base64.b64decode(img_b64)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is not None:
                images.append(img)
        except Exception:
            continue

    if len(images) < 3:
        return jsonify({'status': 'error', 'message': 'Could not decode enough valid images'}), 400

    success = face_system.register_worker(worker_id, name, email, images)
    if success:
        return jsonify({
            'status': 'ok',
            'message': f'Worker "{name}" registered successfully as {worker_id}',
            'worker_id': worker_id
        })
    else:
        return jsonify({'status': 'error', 'message': 'Registration failed. Ensure clear, well-lit face photos with one face visible.'}), 400


@app.route('/registered-workers')
def registered_workers():
    """Get list of all registered workers."""
    if not face_system:
        return jsonify({'workers': []})
    workers = face_system.database.get_all_workers()
    return jsonify({'workers': workers})


@app.route('/delete-worker', methods=['POST'])
def delete_worker():
    """Delete a registered worker and their face embedding."""
    if not face_system:
        return jsonify({'status': 'error', 'message': 'Face recognition system not available'}), 500

    data = request.get_json()
    worker_id = data.get('worker_id', '')

    if not worker_id:
        return jsonify({'status': 'error', 'message': 'Worker ID is required'}), 400

    success = face_system.database.remove_worker(worker_id)
    if success:
        return jsonify({'status': 'ok', 'message': f'Worker {worker_id} deleted'})
    else:
        return jsonify({'status': 'error', 'message': f'Failed to delete worker {worker_id}'}), 400


@app.route('/send-violation-email', methods=['POST'])
def send_violation_email():
    """Send PPE violation email to a worker via SMTP."""
    if not email_system:
        return jsonify({'status': 'error', 'message': 'Email system not configured. Set SENDER_EMAIL and SENDER_PASSWORD in .env'}), 500

    data = request.get_json()
    worker_id = data.get('worker_id', '')
    worker_name = data.get('worker_name', '')
    worker_email = data.get('worker_email', '')
    missing_ppe = data.get('missing_ppe', [])

    if not worker_email:
        return jsonify({'status': 'error', 'message': 'No email address for this worker'}), 400

    # Capture current live frame as violation screenshot
    image_path = None
    if live_camera['running'] and live_camera['cap'] is not None:
        try:
            os.makedirs('violations', exist_ok=True)
            with live_camera['lock']:
                ret, frame = live_camera['cap'].read()
            if ret and frame is not None:
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                image_path = os.path.join('violations', f'{worker_id}_{ts}.jpg')
                cv2.imwrite(image_path, frame)
        except Exception:
            image_path = None

    violation = ViolationRecord(
        worker_id=worker_id,
        worker_name=worker_name,
        worker_email=worker_email,
        timestamp=datetime.now(timezone.utc),
        missing_ppe=set(missing_ppe),
        violation_count=1,
        image_path=image_path
    )

    success = email_system.send_email(violation)
    if success:
        return jsonify({'status': 'ok', 'message': f'Violation email sent to {worker_email}'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send email. Check SMTP credentials and cooldown period (15 min).'}), 500


if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  PPE Detection & Face Recognition Web UI")
    print("  http://localhost:5000")
    print(f"  Face Recognition: {'ACTIVE' if face_system else 'DISABLED'}")
    print(f"  Email System:     {'ACTIVE' if email_system and email_system.sender_email else 'DISABLED'}")
    print("=" * 50 + "\n")
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
