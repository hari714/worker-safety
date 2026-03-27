"""
PPE Detection Web UI — Minimal Black & White Design
Upload an image → See detection results
"""

import os
import io
import base64
import cv2
import numpy as np
from flask import Flask, request, render_template_string
from ultralytics import YOLO

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

MODEL_PATH = 'models/best.pt'
model = YOLO(MODEL_PATH)

CLASS_NAMES = {0: 'Helmet', 1: 'Gloves', 2: 'Vest', 3: 'Boots', 4: 'Goggles'}
REQUIRED_PPE = {'Helmet', 'Gloves', 'Vest', 'Boots', 'Goggles'}

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PPE Detection — Workplace Safety</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
    background: #0a0a0f;
    color: #c8c8d0;
    min-height: 100vh;
  }

  .page {
    max-width: 680px;
    margin: 0 auto;
    padding: 48px 24px 80px;
  }

  /* Header */
  .header {
    text-align: center;
    margin-bottom: 40px;
  }
  .header-icon {
    width: 56px;
    height: 56px;
    border-radius: 16px;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
  }
  .header-icon svg {
    width: 28px;
    height: 28px;
    fill: none;
    stroke: #fff;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
  }
  .header h1 {
    font-size: 1.75rem;
    font-weight: 700;
    color: #fff;
    letter-spacing: -0.02em;
    margin-bottom: 8px;
  }
  .header p {
    font-size: 0.9rem;
    color: #64648a;
    font-weight: 400;
  }

  /* Card wrapper */
  .card {
    background: #12121a;
    border: 1px solid #1e1e2e;
    border-radius: 16px;
    padding: 32px;
    margin-bottom: 24px;
  }

  /* Upload Box */
  .upload-box {
    border: 2px dashed #2a2a3e;
    border-radius: 12px;
    padding: 48px 24px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    background: #0e0e16;
    display: block;
  }
  .upload-box:hover {
    border-color: #3b82f6;
    background: #111120;
  }
  .upload-box.dragover {
    border-color: #3b82f6;
    background: rgba(59, 130, 246, 0.05);
  }
  .upload-box.has-file {
    border-color: #22c55e;
    border-style: solid;
    background: rgba(34, 197, 94, 0.04);
  }
  .upload-icon {
    width: 52px;
    height: 52px;
    border-radius: 12px;
    background: #1a1a2e;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;
    transition: all 0.3s;
  }
  .upload-icon svg {
    width: 24px;
    height: 24px;
    stroke: #64648a;
    fill: none;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
    transition: all 0.3s;
  }
  .upload-box:hover .upload-icon {
    background: rgba(59, 130, 246, 0.15);
  }
  .upload-box:hover .upload-icon svg {
    stroke: #3b82f6;
  }
  .upload-box.has-file .upload-icon {
    background: rgba(34, 197, 94, 0.15);
  }
  .upload-box.has-file .upload-icon svg {
    stroke: #22c55e;
  }
  .upload-text {
    font-size: 0.95rem;
    color: #8888a8;
    margin-bottom: 6px;
  }
  .upload-text strong {
    color: #3b82f6;
    font-weight: 600;
  }
  .upload-hint {
    font-size: 0.78rem;
    color: #44445a;
  }

  input[type="file"] { display: none; }

  .file-name {
    text-align: center;
    font-size: 0.82rem;
    color: #22c55e;
    margin: 16px 0;
    min-height: 20px;
    font-weight: 500;
  }

  /* Button */
  .btn {
    display: block;
    width: 100%;
    padding: 14px 24px;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    color: #fff;
    border: none;
    border-radius: 12px;
    font-family: inherit;
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    cursor: pointer;
    transition: all 0.25s;
    position: relative;
    overflow: hidden;
  }
  .btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3);
  }
  .btn:active { transform: translateY(0); }
  .btn:disabled {
    background: #1a1a2e;
    color: #44445a;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }

  /* Divider */
  .divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #2a2a3e, transparent);
    margin: 32px 0;
  }

  /* Result Image */
  .result-image {
    width: 100%;
    border-radius: 12px;
    border: 1px solid #1e1e2e;
    display: block;
  }

  /* Status */
  .status {
    margin-top: 24px;
    padding: 16px 20px;
    border-radius: 12px;
    font-size: 0.88rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .status-icon {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  .status-pass {
    background: rgba(34, 197, 94, 0.08);
    border: 1px solid rgba(34, 197, 94, 0.25);
    color: #4ade80;
  }
  .status-pass .status-icon {
    background: #22c55e;
    color: #fff;
  }
  .status-fail {
    background: rgba(239, 68, 68, 0.08);
    border: 1px solid rgba(239, 68, 68, 0.25);
    color: #f87171;
  }
  .status-fail .status-icon {
    background: #ef4444;
    color: #fff;
  }

  /* Section Title */
  .section-title {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #64648a;
    margin: 28px 0 14px;
  }

  /* PPE List */
  .ppe-list { list-style: none; }
  .ppe-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    border-radius: 10px;
    margin-bottom: 4px;
    font-size: 0.88rem;
    transition: background 0.2s;
  }
  .ppe-row:hover { background: #16162a; }
  .ppe-row .left { display: flex; align-items: center; gap: 12px; }
  .ppe-row .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }
  .dot-on { background: #22c55e; box-shadow: 0 0 8px rgba(34, 197, 94, 0.4); }
  .dot-off { background: #ef4444; box-shadow: 0 0 8px rgba(239, 68, 68, 0.3); }
  .ppe-row .name { letter-spacing: 0.02em; font-weight: 500; }
  .ppe-row .name.found { color: #e0e0f0; }
  .ppe-row .name.missing { color: #55556a; }
  .right-side { display: flex; align-items: center; gap: 8px; }
  .badge {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    padding: 4px 10px;
    border-radius: 6px;
    text-transform: uppercase;
  }
  .badge-found { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
  .badge-missing { background: rgba(239, 68, 68, 0.1); color: #f87171; }
  .conf { font-size: 0.8rem; color: #64648a; font-weight: 500; }

  /* Stats */
  .stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-top: 24px;
  }
  .stat-card {
    background: #0e0e16;
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    padding: 20px 16px;
    text-align: center;
    transition: border-color 0.3s;
  }
  .stat-card:hover { border-color: #2a2a3e; }
  .stat-num {
    font-size: 2rem;
    font-weight: 700;
    color: #fff;
    line-height: 1;
  }
  .stat-label {
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #55556a;
    margin-top: 8px;
  }
  .stat-card:nth-child(1) .stat-num { color: #3b82f6; }
  .stat-card:nth-child(2) .stat-num { color: #f87171; }
  .stat-card:nth-child(3) .stat-num { color: #a78bfa; }

  .footer {
    text-align: center;
    font-size: 0.7rem;
    color: #2a2a3e;
    margin-top: 48px;
    letter-spacing: 0.05em;
  }

  /* Loading spinner */
  .btn.loading {
    pointer-events: none;
    background: #1e1e2e;
    color: #64648a;
  }
  .btn.loading::after {
    content: '';
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid transparent;
    border-top-color: #64648a;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    margin-left: 10px;
    vertical-align: middle;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* Preview image */
  .preview-container {
    margin: 16px 0;
    text-align: center;
    display: none;
  }
  .preview-container.show { display: block; }
  .preview-image {
    max-width: 100%;
    max-height: 200px;
    border-radius: 10px;
    border: 1px solid #1e1e2e;
    object-fit: contain;
  }
</style>
</head>
<body>
<div class="page">

  <div class="header">
    <div class="header-icon">
      <svg viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
    </div>
    <h1>PPE Detection</h1>
    <p>Workplace Safety System</p>
  </div>

  <div class="card">
    <form method="POST" enctype="multipart/form-data" id="form">
      <label class="upload-box" id="dropArea">
        <div class="upload-icon">
          <svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
        </div>
        <p class="upload-text"><strong>Click to upload</strong> or drag and drop</p>
        <p class="upload-hint">JPG, PNG up to 16 MB</p>
        <input type="file" name="image" id="fileInput" accept="image/jpeg,image/png">
      </label>
      <div class="preview-container" id="previewContainer">
        <img id="previewImage" class="preview-image" alt="Preview">
      </div>
      <div class="file-name" id="fileName"></div>
      <button type="submit" class="btn" id="submitBtn" disabled>Analyze Image</button>
    </form>
  </div>

  {% if error %}
  <div class="status status-fail">
    <span class="status-icon"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></span>
    {{ error }}
  </div>
  {% endif %}

  {% if result %}
  <div class="divider"></div>

  <img src="data:image/jpeg;base64,{{ result.image_b64 }}" class="result-image" alt="Detection Result">

  {% if result.compliant %}
  <div class="status status-pass">
    <span class="status-icon"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></span>
    Compliant &mdash; All PPE Detected
  </div>
  {% else %}
  <div class="status status-fail">
    <span class="status-icon"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></span>
    Non-Compliant &mdash; Missing: {{ result.missing | join(', ') }}
  </div>
  {% endif %}

  <div class="card" style="margin-top:24px">
    <p class="section-title" style="margin-top:0">PPE Checklist</p>
    <ul class="ppe-list">
      {% for ppe in result.all_ppe %}
      <li class="ppe-row">
        <div class="left">
          <span class="dot {% if ppe.found %}dot-on{% else %}dot-off{% endif %}"></span>
          <span class="name {% if ppe.found %}found{% else %}missing{% endif %}">{{ ppe.name }}</span>
        </div>
        <div class="right-side">
          {% if ppe.found %}
          <span class="badge badge-found">Found</span>
          {% else %}
          <span class="badge badge-missing">Missing</span>
          {% endif %}
        </div>
      </li>
      {% endfor %}
    </ul>
  </div>

  <div class="stats">
    <div class="stat-card">
      <div class="stat-num">{{ result.detected_count }}</div>
      <div class="stat-label">Detected</div>
    </div>
    <div class="stat-card">
      <div class="stat-num">{{ result.missing_count }}</div>
      <div class="stat-label">Missing</div>
    </div>
    <div class="stat-card">
      <div class="stat-num">{{ result.total_objects }}</div>
      <div class="stat-label">Objects</div>
    </div>
  </div>
  {% endif %}

  <p class="footer">YOLOv8 &middot; 5-Class PPE Detection</p>
</div>

<script>
  const fileInput = document.getElementById('fileInput');
  const fileName = document.getElementById('fileName');
  const submitBtn = document.getElementById('submitBtn');
  const dropArea = document.getElementById('dropArea');
  const form = document.getElementById('form');
  const previewContainer = document.getElementById('previewContainer');
  const previewImage = document.getElementById('previewImage');

  fileInput.addEventListener('change', function() {
    if (this.files.length > 0) {
      const file = this.files[0];
      fileName.textContent = file.name;
      submitBtn.disabled = false;
      dropArea.classList.add('has-file');

      const reader = new FileReader();
      reader.onload = e => {
        previewImage.src = e.target.result;
        previewContainer.classList.add('show');
      };
      reader.readAsDataURL(file);
    }
  });

  form.addEventListener('submit', function() {
    submitBtn.classList.add('loading');
    submitBtn.textContent = 'Analyzing';
  });

  ['dragover','dragenter'].forEach(e => {
    dropArea.addEventListener(e, ev => {
      ev.preventDefault();
      dropArea.classList.add('dragover');
    });
  });
  ['dragleave','drop'].forEach(e => {
    dropArea.addEventListener(e, ev => {
      ev.preventDefault();
      dropArea.classList.remove('dragover');
    });
  });
  dropArea.addEventListener('drop', ev => {
    ev.preventDefault();
    fileInput.files = ev.dataTransfer.files;
    fileInput.dispatchEvent(new Event('change'));
  });
</script>
</body>
</html>
"""


IMG_SIZE = 640


def detect_ppe(image_bytes):
    """Run PPE detection on uploaded image with upscaling and TTA."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    if frame is None:
        return None
    # Handle PNG with alpha channel — convert to BGR
    if len(frame.shape) == 3 and frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    # Handle grayscale
    elif len(frame.shape) == 2:
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

    # Resize images to optimal size for detection
    h, w = frame.shape[:2]
    max_dim = max(h, w)
    scale = 1.0
    if max_dim > 1280:
        scale = 1280 / max_dim
        proc_frame = cv2.resize(frame, (int(w * scale), int(h * scale)),
                                interpolation=cv2.INTER_AREA)
    elif max_dim < IMG_SIZE:
        scale = IMG_SIZE / max_dim
        proc_frame = cv2.resize(frame, (int(w * scale), int(h * scale)),
                                interpolation=cv2.INTER_CUBIC)
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

        # Map coordinates back to original image space
        x1, y1, x2, y2 = x1 / scale, y1 / scale, x2 / scale, y2 / scale
        x1, y1 = max(0, int(x1)), max(0, int(y1))
        x2, y2 = min(img_w, int(x2)), min(img_h, int(y2))

        # Filter out false positives: skip if bbox covers >60% of image
        box_area = (x2 - x1) * (y2 - y1)
        if box_area > 0.60 * img_area:
            continue

        detections.append({
            'class_id': cls_id,
            'name': CLASS_NAMES.get(cls_id, 'unknown'),
            'confidence': conf,
            'bbox': (x1, y1, x2, y2)
        })

    # Draw white bounding boxes (minimal style)
    for d in detections:
        x1, y1, x2, y2 = d['bbox']
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
        label = d['name']
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (x1, y1 - h - 8), (x1 + w + 4, y1), (255, 255, 255), -1)
        cv2.putText(frame, label, (x1 + 2, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    # Encode result image to base64
    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
    image_b64 = base64.b64encode(buffer).decode('utf-8')

    # Build PPE checklist
    detected_names = {d['name'] for d in detections}
    all_ppe = []
    for name in ['Helmet', 'Gloves', 'Vest', 'Boots', 'Goggles']:
        found = name in detected_names
        all_ppe.append({'name': name, 'found': found, 'conf': ''})

    missing = [name for name in REQUIRED_PPE if name not in detected_names]

    return {
        'image_b64': image_b64,
        'detections': detections,
        'all_ppe': all_ppe,
        'compliant': len(missing) == 0,
        'missing': missing,
        'detected_count': len(detected_names),
        'missing_count': len(missing),
        'total_objects': len(detections)
    }


@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        file = request.files.get('image')
        if file and file.filename:
            image_bytes = file.read()
            result = detect_ppe(image_bytes)
            if result is None:
                return render_template_string(HTML, result=None, error="Could not read image. Try a different file.")
    return render_template_string(HTML, result=result, error=None)


if __name__ == '__main__':
    print("\n" + "=" * 40)
    print("  PPE Detection Web UI")
    print("  http://localhost:5000")
    print("=" * 40 + "\n")
    app.run(debug=False, host='0.0.0.0', port=5000)
