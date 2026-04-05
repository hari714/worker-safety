"""
PPE Detection & Face Recognition Web UI
Upload an image or video → See detection results with face identification
"""

import os
import io
import base64
import tempfile
import time
import threading
import cv2
import numpy as np
from flask import Flask, request, render_template_string, jsonify, Response
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

# ── Live Camera State ──────────────────────────────────────────────
live_camera = {
    'cap': None,
    'running': False,
    'lock': threading.Lock(),
    'frame_count': 0,
    'face_interval': 5,        # run face detection every N frames
    'cached_faces': [],         # cached face detection results
    'last_status': {
        'faces': [],
        'ppe_found': [],
        'missing_ppe': [],
        'compliant': True,
        'fps': 0.0
    }
}


HTML = """
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SafetyVision - PPE Detection</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  /* ── Theme Variables ─────────────────────────────────── */
  :root {
    --transition-speed: 0.25s;
  }

  [data-theme="dark"] {
    --bg-body: #0c0c0c;
    --bg-sidebar: #0f0f0f;
    --bg-main: #141414;
    --bg-card: #1a1a1a;
    --bg-card-hover: #1f1f1f;
    --bg-input: #111111;
    --bg-upload: #111111;
    --border-color: #222222;
    --border-light: #2a2a2a;
    --text-primary: #e8e8e8;
    --text-secondary: #888888;
    --text-muted: #555555;
    --text-heading: #ffffff;
    --accent: #e0e0e0;
    --accent-hover: #cccccc;
    --accent-glow: rgba(255, 255, 255, 0.1);
    --accent-subtle: rgba(255, 255, 255, 0.04);
    --danger: #ef4444;
    --danger-bg: rgba(239, 68, 68, 0.08);
    --danger-border: rgba(239, 68, 68, 0.25);
    --info: #888888;
    --info-bg: rgba(255, 255, 255, 0.05);
    --info-border: rgba(255, 255, 255, 0.15);
    --success-bg: rgba(255, 255, 255, 0.05);
    --success-border: rgba(255, 255, 255, 0.15);
    --purple: #cccccc;
    --purple-bg: rgba(255, 255, 255, 0.06);
    --sidebar-active-bg: rgba(255, 255, 255, 0.08);
    --sidebar-hover-bg: rgba(255, 255, 255, 0.04);
    --scrollbar-track: #1a1a1a;
    --scrollbar-thumb: #333333;
    --shadow: 0 1px 3px rgba(0,0,0,0.4);
    --btn-text: #000000;
  }

  [data-theme="light"] {
    --bg-body: #f2f2f2;
    --bg-sidebar: #ffffff;
    --bg-main: #f7f7f7;
    --bg-card: #ffffff;
    --bg-card-hover: #f0f0f0;
    --bg-input: #f0f0f0;
    --bg-upload: #f5f5f5;
    --border-color: #d4d4d4;
    --border-light: #bbbbbb;
    --text-primary: #111111;
    --text-secondary: #444444;
    --text-muted: #777777;
    --text-heading: #000000;
    --accent: #111111;
    --accent-hover: #000000;
    --accent-glow: rgba(0, 0, 0, 0.1);
    --accent-subtle: rgba(0, 0, 0, 0.04);
    --danger: #cc0000;
    --danger-bg: rgba(204, 0, 0, 0.08);
    --danger-border: rgba(204, 0, 0, 0.25);
    --info: #333333;
    --info-bg: rgba(0, 0, 0, 0.05);
    --info-border: rgba(0, 0, 0, 0.15);
    --success-bg: rgba(0, 0, 0, 0.05);
    --success-border: rgba(0, 0, 0, 0.15);
    --purple: #222222;
    --purple-bg: rgba(0, 0, 0, 0.06);
    --sidebar-active-bg: rgba(0, 0, 0, 0.08);
    --sidebar-hover-bg: rgba(0, 0, 0, 0.05);
    --scrollbar-track: #eeeeee;
    --scrollbar-thumb: #bbbbbb;
    --shadow: 0 1px 4px rgba(0,0,0,0.1);
    --btn-text: #ffffff;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  [data-theme="light"] { color-scheme: light; }
  [data-theme="dark"] { color-scheme: dark; }

  html, body {
    font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
    background: var(--bg-body);
    color: var(--text-primary);
    min-height: 100vh;
  }
  body {
    display: flex;
  }

  /* ── Scrollbar ─────────────────────────────────────── */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: var(--scrollbar-track); }
  ::-webkit-scrollbar-thumb { background: var(--scrollbar-thumb); border-radius: 3px; }

  /* ── Sidebar ───────────────────────────────────────── */
  .sidebar {
    width: 260px;
    min-width: 260px;
    height: 100vh;
    position: fixed;
    left: 0; top: 0;
    background: var(--bg-sidebar);
    border-right: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    z-index: 100;
    transition: background var(--transition-speed), border-color var(--transition-speed);
  }

  .sidebar-brand {
    padding: 20px 20px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    border-bottom: 1px solid var(--border-color);
  }
  .brand-icon {
    width: 36px; height: 36px;
    border-radius: 10px;
    background: var(--text-heading);
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }
  .brand-icon svg { width: 18px; height: 18px; fill: none; stroke: var(--bg-body); stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
  .brand-name { font-size: 1rem; font-weight: 700; color: var(--text-heading); letter-spacing: -0.02em; }
  .brand-sub { font-size: 0.65rem; color: var(--text-muted); letter-spacing: 0.04em; text-transform: uppercase; font-weight: 500; }

  .sidebar-section {
    padding: 16px 12px 8px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
  }

  .sidebar-nav { flex: 1; overflow-y: auto; padding: 8px 12px; }

  .nav-item {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 12px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.88rem;
    font-weight: 500;
    color: var(--text-secondary);
    transition: all 0.15s;
    margin-bottom: 2px;
    border: none;
    background: none;
    width: 100%;
    text-align: left;
    font-family: inherit;
  }
  .nav-item:hover { background: var(--sidebar-hover-bg); color: var(--text-primary); }
  .nav-item.active { background: var(--sidebar-active-bg); color: var(--accent); }
  .nav-item.active .nav-icon { color: var(--accent); }
  .nav-icon { width: 20px; height: 20px; flex-shrink: 0; opacity: 0.6; }
  .nav-item.active .nav-icon { opacity: 1; }
  .nav-item:hover .nav-icon { opacity: 0.9; }
  .nav-item svg { width: 20px; height: 20px; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
  .nav-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--text-heading);
    margin-left: auto;
    opacity: 0;
    transition: opacity 0.2s;
  }
  .nav-item.active .nav-dot { opacity: 1; }

  /* Sidebar Footer */
  .sidebar-footer {
    padding: 12px;
    border-top: 1px solid var(--border-color);
  }
  .theme-toggle {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 12px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--text-secondary);
    transition: all 0.15s;
    border: none;
    background: none;
    width: 100%;
    text-align: left;
    font-family: inherit;
  }
  .theme-toggle:hover { background: var(--sidebar-hover-bg); color: var(--text-primary); }
  .theme-toggle svg { width: 20px; height: 20px; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }

  .sidebar-info {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 12px;
    border-radius: 8px;
    margin-top: 4px;
  }
  .sidebar-info-avatar {
    width: 32px; height: 32px; border-radius: 8px;
    background: var(--text-heading);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem; font-weight: 700; color: var(--bg-body);
  }
  .sidebar-info-text { font-size: 0.78rem; color: var(--text-secondary); line-height: 1.3; }
  .sidebar-info-text strong { color: var(--text-primary); font-weight: 600; display: block; }

  /* ── Main Content ──────────────────────────────────── */
  .main {
    margin-left: 260px;
    flex: 1;
    min-height: 100vh;
    background: var(--bg-main);
    transition: background var(--transition-speed);
  }

  .topbar {
    padding: 16px 32px;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--bg-sidebar);
    transition: background var(--transition-speed), border-color var(--transition-speed);
  }
  .topbar-breadcrumb {
    display: flex; align-items: center; gap: 8px;
    font-size: 0.85rem; color: var(--text-secondary);
  }
  .topbar-breadcrumb .sep { color: var(--text-muted); }
  .topbar-breadcrumb .current { color: var(--text-primary); font-weight: 600; }
  .topbar-right { display: flex; align-items: center; gap: 12px; }
  .topbar-badge {
    font-size: 0.7rem; font-weight: 600;
    padding: 4px 10px; border-radius: 6px;
    text-transform: uppercase; letter-spacing: 0.05em;
    background: var(--accent-glow);
    color: var(--accent);
  }

  /* ── Split Pane Layout ────────────────────────────── */
  .content-wrap {
    display: flex;
    height: calc(100vh - 53px);
    overflow: hidden;
  }
  .pane-left {
    flex: 1;
    overflow-y: auto;
    padding: 32px;
    min-width: 0;
  }
  .pane-left-inner {
    max-width: 600px;
    margin: 0 auto;
  }
  .has-result .pane-left {
    flex: 0 0 42%;
    max-width: 42%;
    border-right: 1px solid var(--border-color);
  }
  .pane-right {
    display: none;
    flex: 1;
    overflow-y: auto;
    padding: 32px;
    min-width: 0;
  }
  .has-result .pane-right {
    display: block;
  }
  .pane-right-inner {
    max-width: 700px;
    margin: 0 auto;
  }
  .pane-right-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border-color);
  }
  .pane-right-header h2 {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-heading);
    letter-spacing: -0.01em;
  }
  .pane-right-header .close-pane {
    width: 32px; height: 32px;
    border-radius: 6px;
    border: 1px solid var(--border-color);
    background: var(--bg-card);
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    color: var(--text-secondary);
  }
  .pane-right-header .close-pane:hover {
    background: var(--bg-card-hover);
    color: var(--text-primary);
  }
  .pane-right-header .close-pane svg {
    width: 16px; height: 16px; stroke: currentColor;
    fill: none; stroke-width: 2; stroke-linecap: round;
  }

  @media (max-width: 768px) {
    .content-wrap { flex-direction: column; height: auto; }
    .has-result .pane-left { flex: none; max-width: 100%; border-right: none; border-bottom: 1px solid var(--border-color); }
    .has-result .pane-right { display: block; }
  }

  .page-header {
    margin-bottom: 28px;
  }
  .page-header h1 {
    font-size: 1.5rem; font-weight: 700;
    color: var(--text-heading);
    letter-spacing: -0.02em; margin-bottom: 6px;
  }
  .page-header p {
    font-size: 0.88rem; color: var(--text-secondary);
  }

  /* ── Card ───────────────────────────────────────────── */
  .card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 28px;
    margin-bottom: 20px;
    transition: background var(--transition-speed), border-color var(--transition-speed);
    box-shadow: var(--shadow);
  }

  /* ── Upload Box ─────────────────────────────────────── */
  .upload-box {
    border: 2px dashed var(--border-light);
    border-radius: 10px;
    padding: 40px 24px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;
    background: var(--bg-upload);
    display: block;
  }
  .upload-box:hover { border-color: var(--accent); background: var(--accent-subtle); }
  .upload-box.dragover { border-color: var(--accent); background: var(--accent-subtle); }
  .upload-box.has-file { border-color: var(--accent); border-style: solid; background: var(--accent-subtle); }
  .upload-icon {
    width: 48px; height: 48px; border-radius: 10px;
    background: var(--sidebar-hover-bg);
    display: inline-flex;
    align-items: center; justify-content: center;
    margin-bottom: 14px; transition: all 0.3s;
  }
  .upload-icon svg { width: 22px; height: 22px; stroke: var(--text-muted); fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; transition: all 0.3s; }
  .upload-box:hover .upload-icon { background: var(--accent-glow); }
  .upload-box:hover .upload-icon svg { stroke: var(--accent); }
  .upload-box.has-file .upload-icon { background: var(--accent-glow); }
  .upload-box.has-file .upload-icon svg { stroke: var(--accent); }
  .upload-text { font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 4px; }
  .upload-text strong { color: var(--accent); font-weight: 600; }
  .upload-hint { font-size: 0.75rem; color: var(--text-muted); }
  input[type="file"] { display: none; }
  .file-name {
    text-align: center; font-size: 0.82rem;
    color: var(--accent); margin: 14px 0;
    min-height: 20px; font-weight: 500;
  }

  /* ── Buttons ────────────────────────────────────────── */
  .btn {
    display: block; width: 100%;
    padding: 12px 24px;
    background: var(--accent);
    color: var(--btn-text) !important; border: none; border-radius: 10px;
    font-family: inherit; font-size: 0.9rem;
    font-weight: 600; letter-spacing: 0.01em;
    cursor: pointer; transition: all 0.2s;
    position: relative;
  }
  .btn:hover { background: var(--accent-hover); transform: translateY(-1px); box-shadow: 0 4px 16px var(--accent-glow); }
  .btn:active { transform: translateY(0); }
  .btn:disabled { background: var(--border-color); color: var(--text-muted); cursor: not-allowed; transform: none; box-shadow: none; }
  .btn.loading { pointer-events: none; background: var(--border-color); color: var(--text-muted); }
  .btn.loading::after {
    content: ''; display: inline-block;
    width: 14px; height: 14px;
    border: 2px solid transparent; border-top-color: var(--text-muted);
    border-radius: 50%; animation: spin 0.7s linear infinite;
    margin-left: 8px; vertical-align: middle;
  }

  .btn-danger { background: var(--danger); }
  .btn-danger:hover { background: #dc2626; box-shadow: 0 4px 16px rgba(239,68,68,0.2); }

  /* ── Tab content ────────────────────────────────────── */
  .tab-content { display: none; }
  .tab-content.active { display: block; }

  /* ── Divider ────────────────────────────────────────── */
  .divider { height: 1px; background: var(--border-color); margin: 28px 0; }

  /* ── Result Image ───────────────────────────────────── */
  .result-image { width: 100%; border-radius: 10px; border: 1px solid var(--border-color); display: block; }

  /* ── Status ─────────────────────────────────────────── */
  .status {
    margin-top: 20px; padding: 14px 18px;
    border-radius: 10px; font-size: 0.85rem;
    font-weight: 600; display: flex;
    align-items: center; gap: 10px;
  }
  .status-icon {
    width: 20px; height: 20px; border-radius: 50%;
    display: inline-flex; align-items: center;
    justify-content: center; flex-shrink: 0;
  }
  .status-pass { background: var(--success-bg); border: 1px solid var(--success-border); color: var(--accent); }
  .status-pass .status-icon { background: var(--accent); color: #fff; }
  .status-fail { background: var(--danger-bg); border: 1px solid var(--danger-border); color: var(--danger); }
  .status-fail .status-icon { background: var(--danger); color: #fff; }
  .status-info { background: var(--info-bg); border: 1px solid var(--info-border); color: var(--info); }
  .status-info .status-icon { background: var(--info); color: #fff; }

  .section-title {
    font-size: 0.72rem; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: var(--text-muted); margin: 24px 0 12px;
  }

  /* ── PPE List ───────────────────────────────────────── */
  .ppe-list { list-style: none; }
  .ppe-row {
    display: flex; align-items: center;
    justify-content: space-between;
    padding: 10px 14px; border-radius: 8px;
    margin-bottom: 2px; font-size: 0.85rem;
    transition: background 0.15s;
  }
  .ppe-row:hover { background: var(--bg-card-hover); }
  .ppe-row .left { display: flex; align-items: center; gap: 10px; }
  .ppe-row .dot { width: 8px; height: 8px; border-radius: 50%; }
  .dot-on { background: var(--accent); box-shadow: 0 0 8px var(--accent-glow); }
  .dot-off { background: var(--danger); box-shadow: 0 0 8px rgba(239, 68, 68, 0.2); }
  .ppe-row .name { letter-spacing: 0.01em; font-weight: 500; }
  .ppe-row .name.found { color: var(--text-primary); }
  .ppe-row .name.missing { color: var(--text-muted); }
  .right-side { display: flex; align-items: center; gap: 8px; }
  .badge {
    font-size: 0.62rem; font-weight: 600;
    letter-spacing: 0.05em; padding: 3px 8px;
    border-radius: 5px; text-transform: uppercase;
  }
  .badge-found { background: var(--accent-glow); color: var(--accent); }
  .badge-missing { background: var(--danger-bg); color: var(--danger); }
  .badge-face { background: var(--purple-bg); color: var(--purple); }

  /* ── Stats ──────────────────────────────────────────── */
  .stats {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 12px; margin-top: 20px;
  }
  .stat-card {
    background: var(--bg-input); border: 1px solid var(--border-color);
    border-radius: 10px; padding: 18px 14px;
    text-align: center; transition: border-color 0.2s, background var(--transition-speed);
  }
  .stat-card:hover { border-color: var(--border-light); }
  .stat-num { font-size: 1.75rem; font-weight: 700; color: var(--text-heading); line-height: 1; }
  .stat-label {
    font-size: 0.65rem; font-weight: 500;
    letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--text-muted); margin-top: 6px;
  }
  .stat-card:nth-child(1) .stat-num { color: var(--text-heading); }
  .stat-card:nth-child(2) .stat-num { color: var(--danger); }
  .stat-card:nth-child(3) .stat-num { color: var(--text-heading); }
  .stat-card:nth-child(4) .stat-num { color: var(--text-heading); }

  /* ── Video Frames Gallery ───────────────────────────── */
  .frames-gallery {
    display: grid; grid-template-columns: repeat(2, 1fr);
    gap: 14px; margin-top: 14px;
  }
  .frame-card {
    background: var(--bg-input); border: 1px solid var(--border-color);
    border-radius: 10px; overflow: hidden;
    transition: border-color 0.2s;
  }
  .frame-card:hover { border-color: var(--accent); }
  .frame-card img { width: 100%; display: block; }
  .frame-info {
    padding: 10px 14px; font-size: 0.78rem;
    display: flex; justify-content: space-between;
    align-items: center;
  }
  .frame-time { color: var(--text-secondary); font-weight: 500; }
  .frame-badge {
    font-size: 0.62rem; font-weight: 600;
    padding: 3px 8px; border-radius: 5px;
    text-transform: uppercase;
  }
  .frame-compliant { background: var(--accent-glow); color: var(--accent); }
  .frame-violation { background: var(--danger-bg); color: var(--danger); }

  /* ── Face List ──────────────────────────────────────── */
  .face-row {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 14px; border-radius: 8px;
    margin-bottom: 2px; font-size: 0.85rem;
  }
  .face-row:hover { background: var(--bg-card-hover); }
  .face-avatar {
    width: 34px; height: 34px; border-radius: 8px;
    background: var(--purple-bg); display: flex;
    align-items: center; justify-content: center;
    font-size: 0.72rem; font-weight: 700; color: var(--purple);
  }
  .face-name { color: var(--text-primary); font-weight: 500; }
  .face-conf { color: var(--text-secondary); font-size: 0.75rem; }

  /* ── Preview ────────────────────────────────────────── */
  .preview-container { margin: 14px 0; text-align: center; display: none; }
  .preview-container.show { display: block; }
  .preview-image { max-width: 100%; max-height: 200px; border-radius: 8px; border: 1px solid var(--border-color); object-fit: contain; }
  .preview-video { max-width: 100%; max-height: 200px; border-radius: 8px; border: 1px solid var(--border-color); }

  /* ── Footer ─────────────────────────────────────────── */
  .footer { text-align: center; font-size: 0.68rem; color: var(--text-muted); margin-top: 40px; letter-spacing: 0.04em; }

  /* ── Animations ─────────────────────────────────────── */
  @keyframes spin { to { transform: rotate(360deg); } }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }

  /* ── Image Modal / Lightbox ──────────────────────────── */
  .modal-overlay {
    display: none;
    position: fixed;
    inset: 0;
    z-index: 1000;
    background: rgba(0, 0, 0, 0.85);
    align-items: center;
    justify-content: center;
    padding: 24px;
    cursor: pointer;
  }
  .modal-overlay.show { display: flex; }
  .modal-content {
    position: relative;
    max-width: 90vw;
    max-height: 90vh;
    cursor: default;
  }
  .modal-content img {
    max-width: 100%;
    max-height: 85vh;
    border-radius: 10px;
    display: block;
    box-shadow: 0 8px 40px rgba(0, 0, 0, 0.5);
  }
  .modal-close {
    position: absolute;
    top: -14px; right: -14px;
    width: 36px; height: 36px;
    border-radius: 50%;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    color: var(--text-primary);
    z-index: 1001;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  }
  .modal-close:hover { background: var(--bg-card-hover); }
  .modal-close svg { width: 18px; height: 18px; stroke: currentColor; fill: none; stroke-width: 2; stroke-linecap: round; }
  .modal-info {
    text-align: center;
    margin-top: 12px;
    font-size: 0.82rem;
    color: #ccc;
  }

  .frame-card img { cursor: pointer; }
  .frame-card img:hover { opacity: 0.85; }
  .result-image { cursor: pointer; }
  .result-image:hover { opacity: 0.9; }

  /* ── Live Camera Specific ───────────────────────────── */
  .live-header { text-align: center; margin-bottom: 20px; }
  .live-header p:first-of-type { color: var(--text-heading); font-weight: 600; font-size: 1rem; margin-bottom: 4px; }
  .live-header p:last-of-type { color: var(--text-secondary); font-size: 0.82rem; }
  .live-controls { display: flex; gap: 10px; margin-bottom: 18px; }
  .live-controls .btn { flex: 1; }
  .live-feed-wrap {
    position: relative; border-radius: 10px;
    overflow: hidden; border: 1px solid var(--border-color);
  }
  .live-feed-img { width: 100%; display: block; background: var(--bg-body); min-height: 300px; }
  .live-overlay {
    position: absolute; top: 10px; padding: 5px 10px;
    background: rgba(0,0,0,0.7); border-radius: 6px;
    font-size: 0.72rem; font-weight: 600; color: #fff;
    display: flex; align-items: center; gap: 5px;
  }
  .live-overlay.left { left: 10px; }
  .live-overlay.right { right: 10px; color: #0ff; }
  .live-dot { width: 7px; height: 7px; border-radius: 50%; background: #ef4444; animation: pulse 1.5s infinite; }
  .live-stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 14px; }

  /* ── Mobile Sidebar ─────────────────────────────────── */
  .sidebar-toggle {
    display: none; position: fixed; top: 12px; left: 12px;
    z-index: 200; width: 40px; height: 40px;
    border-radius: 8px; border: 1px solid var(--border-color);
    background: var(--bg-sidebar); cursor: pointer;
    align-items: center; justify-content: center;
    color: var(--text-primary);
  }
  .sidebar-toggle svg { width: 20px; height: 20px; stroke: currentColor; fill: none; stroke-width: 2; }
  .sidebar-overlay {
    display: none; position: fixed; inset: 0;
    background: rgba(0,0,0,0.5); z-index: 90;
  }

  @media (max-width: 768px) {
    .sidebar { transform: translateX(-100%); transition: transform 0.3s; }
    .sidebar.open { transform: translateX(0); }
    .sidebar-toggle { display: flex; }
    .sidebar-overlay.show { display: block; }
    .main { margin-left: 0; }
    .content { padding: 20px 16px; padding-top: 60px; }
    .topbar { padding-left: 60px; }
    .stats { grid-template-columns: repeat(2, 1fr); }
    .frames-gallery { grid-template-columns: 1fr; }
    .live-stats-grid { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>

<!-- Mobile Sidebar Toggle -->
<button class="sidebar-toggle" id="sidebarToggle" onclick="toggleSidebar()">
  <svg viewBox="0 0 24 24"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
</button>
<div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>

<!-- Sidebar -->
<aside class="sidebar" id="sidebar">
  <div class="sidebar-brand">
    <div>
      <div class="brand-name">SafetyVision</div>
      <div class="brand-sub">PPE Detection System</div>
    </div>
  </div>

  <div class="sidebar-section">Analysis</div>
  <nav class="sidebar-nav">
    <button class="nav-item active" onclick="switchTab('image', this)">
      <svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
      Image Detection
      <span class="nav-dot"></span>
    </button>
    <button class="nav-item" onclick="switchTab('video', this)">
      <svg viewBox="0 0 24 24"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>
      Video Detection
      <span class="nav-dot"></span>
    </button>
    <button class="nav-item" onclick="switchTab('live', this)">
      <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/></svg>
      Live Camera
      <span class="nav-dot"></span>
    </button>
  </nav>

  <div class="sidebar-footer">
    <button class="theme-toggle" id="themeToggle" onclick="toggleTheme()">
      <svg id="themeIcon" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
      <span id="themeLabel">Light Mode</span>
    </button>
  </div>
</aside>

<!-- Main Content -->
<div class="main">
  <div class="topbar">
    <div class="topbar-breadcrumb">
      <span>Home</span>
      <span class="sep">/</span>
      <span class="current" id="breadcrumbCurrent">Image Detection</span>
    </div>
    <div class="topbar-right"></div>
  </div>

  <div class="content-wrap {% if result %}has-result{% endif %}">
    <!-- ── Left Pane: Upload Forms ────────────────────── -->
    <div class="pane-left">
      <div class="pane-left-inner">

        <!-- Image Tab -->
        <div class="tab-content active" id="tab-image">
          <div class="page-header">
            <h1>Image Detection</h1>
            <p>Upload an image to detect PPE compliance and identify workers</p>
          </div>
          <div class="card">
            <form method="POST" enctype="multipart/form-data" id="imageForm" action="/">
              <input type="hidden" name="type" value="image">
              <label class="upload-box" id="imageDropArea">
                <div class="upload-icon">
                  <svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                </div>
                <p class="upload-text"><strong>Click to upload</strong> or drag and drop</p>
                <p class="upload-hint">JPG, PNG up to 16 MB</p>
                <input type="file" name="image" id="imageFileInput" accept="image/jpeg,image/png">
              </label>
              <div class="preview-container" id="imagePreviewContainer">
                <img id="imagePreview" class="preview-image" alt="Preview">
              </div>
              <div class="file-name" id="imageFileName"></div>
              <button type="submit" class="btn" id="imageSubmitBtn" disabled>Analyze Image</button>
            </form>
          </div>
        </div>

        <!-- Video Tab -->
        <div class="tab-content" id="tab-video">
          <div class="page-header">
            <h1>Video Detection</h1>
            <p>Upload a video to analyze PPE compliance across frames</p>
          </div>
          <div class="card">
            <form method="POST" enctype="multipart/form-data" id="videoForm" action="/video">
              <label class="upload-box" id="videoDropArea">
                <div class="upload-icon">
                  <svg viewBox="0 0 24 24"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>
                </div>
                <p class="upload-text"><strong>Click to upload video</strong> or drag and drop</p>
                <p class="upload-hint">MP4, AVI, MOV up to 100 MB</p>
                <input type="file" name="video" id="videoFileInput" accept="video/mp4,video/avi,video/quicktime,video/x-msvideo,video/x-matroska">
              </label>
              <div class="preview-container" id="videoPreviewContainer">
                <video id="videoPreview" class="preview-video" controls muted></video>
              </div>
              <div class="file-name" id="videoFileName"></div>
              <button type="submit" class="btn" id="videoSubmitBtn" disabled>Analyze Video</button>
            </form>
          </div>
        </div>

        <!-- Live Camera Tab -->
        <div class="tab-content" id="tab-live">
          <div class="page-header">
            <h1>Live Camera</h1>
            <p>Real-time PPE and face detection from your webcam</p>
          </div>
          <div class="card">
            <div class="live-controls">
              <button class="btn" id="startCamBtn" onclick="startLive()">Start Camera</button>
              <button class="btn" id="stopCamBtn" onclick="stopLive()" disabled style="background:var(--border-color); color:var(--text-muted);">Stop Camera</button>
            </div>
            <div id="liveFeedContainer" style="display:none;">
              <div class="live-feed-wrap">
                <img id="liveFeed" class="live-feed-img" alt="Live Feed">
                <div class="live-overlay left" id="liveIndicator">
                  <div class="live-dot"></div>
                  <span>LIVE</span>
                </div>
                <div class="live-overlay right" id="liveFps">FPS: --</div>
              </div>
              <div id="liveStatus" style="margin-top:14px;">
                <div class="live-stats-grid">
                  <div class="stat-card"><div class="stat-num" id="liveFaceCount">0</div><div class="stat-label">Faces</div></div>
                  <div class="stat-card"><div class="stat-num" id="livePpeCount">0</div><div class="stat-label">PPE Found</div></div>
                  <div class="stat-card"><div class="stat-num" id="liveCompliance" style="color:var(--accent);">--</div><div class="stat-label">Status</div></div>
                </div>
                <div class="card" style="margin-top:14px; padding:18px;">
                  <p class="section-title" style="margin-top:0;">Live PPE Status</p>
                  <ul class="ppe-list" id="livePpeList">
                    <li class="ppe-row"><div class="left"><span class="dot dot-off"></span><span class="name missing">Helmet</span></div><div class="right-side"><span class="badge badge-missing">Waiting</span></div></li>
                    <li class="ppe-row"><div class="left"><span class="dot dot-off"></span><span class="name missing">Gloves</span></div><div class="right-side"><span class="badge badge-missing">Waiting</span></div></li>
                    <li class="ppe-row"><div class="left"><span class="dot dot-off"></span><span class="name missing">Vest</span></div><div class="right-side"><span class="badge badge-missing">Waiting</span></div></li>
                    <li class="ppe-row"><div class="left"><span class="dot dot-off"></span><span class="name missing">Boots</span></div><div class="right-side"><span class="badge badge-missing">Waiting</span></div></li>
                    <li class="ppe-row"><div class="left"><span class="dot dot-off"></span><span class="name missing">Goggles</span></div><div class="right-side"><span class="badge badge-missing">Waiting</span></div></li>
                  </ul>
                </div>
                <div class="card" style="margin-top:14px; padding:18px;">
                  <p class="section-title" style="margin-top:0;">Detected Faces</p>
                  <div id="liveFaceList">
                    <p style="color:var(--text-muted); font-size:0.82rem; text-align:center; padding:12px;">No faces detected yet</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {% if error %}
        <div class="status status-fail">
          <span class="status-icon"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></span>
          {{ error }}
        </div>
        {% endif %}

        <p class="footer">YOLOv8 PPE Detection &middot; MTCNN + FaceNet Face Recognition</p>
      </div>
    </div>

    <!-- ── Right Pane: Results ────────────────────────── -->
    <div class="pane-right">
      <div class="pane-right-inner">

        {% if result and result.mode == 'image' %}
        <div class="pane-right-header">
          <h2>Detection Results</h2>
        </div>

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

        {% if result.faces %}
        <div class="card" style="margin-top:20px">
          <p class="section-title" style="margin-top:0">Faces Detected</p>
          {% for face in result.faces %}
          <div class="face-row">
            <div class="face-avatar">{{ face.name[0] }}</div>
            <div>
              <div class="face-name">{{ face.name }}</div>
              <div class="face-conf">Confidence: {{ face.confidence }}</div>
            </div>
            <span class="badge badge-face">{{ face.status }}</span>
          </div>
          {% endfor %}
        </div>
        {% endif %}

        <div class="card" style="margin-top:20px">
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
          <div class="stat-card"><div class="stat-num">{{ result.detected_count }}</div><div class="stat-label">PPE Found</div></div>
          <div class="stat-card"><div class="stat-num">{{ result.missing_count }}</div><div class="stat-label">Missing</div></div>
          <div class="stat-card"><div class="stat-num">{{ result.face_count }}</div><div class="stat-label">Faces</div></div>
          <div class="stat-card"><div class="stat-num">{{ result.total_objects }}</div><div class="stat-label">Objects</div></div>
        </div>
        {% endif %}

        {% if result and result.mode == 'video' %}
        <div class="pane-right-header">
          <h2>Video Analysis Results</h2>
        </div>

        <div class="status status-info">
          <span class="status-icon"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg></span>
          Video analyzed: {{ result.video_info.duration }}s &middot; {{ result.video_info.total_frames }} frames &middot; {{ result.frames_analyzed }} sampled
        </div>

        <div class="stats">
          <div class="stat-card"><div class="stat-num">{{ result.frames_analyzed }}</div><div class="stat-label">Frames</div></div>
          <div class="stat-card"><div class="stat-num">{{ result.violation_frames }}</div><div class="stat-label">Violations</div></div>
          <div class="stat-card"><div class="stat-num">{{ result.total_faces }}</div><div class="stat-label">Faces</div></div>
          <div class="stat-card"><div class="stat-num">{{ result.compliance_pct }}%</div><div class="stat-label">Compliant</div></div>
        </div>

        {% if result.faces_summary %}
        <div class="card" style="margin-top:20px">
          <p class="section-title" style="margin-top:0">Workers Detected</p>
          {% for face in result.faces_summary %}
          <div class="face-row">
            <div class="face-avatar">{{ face.name[0] }}</div>
            <div>
              <div class="face-name">{{ face.name }}</div>
              <div class="face-conf">Seen in {{ face.frame_count }} frame(s) &middot; Avg confidence: {{ face.avg_conf }}</div>
            </div>
            <span class="badge badge-face">{{ face.status }}</span>
          </div>
          {% endfor %}
        </div>
        {% endif %}

        <div class="card" style="margin-top:20px">
          <p class="section-title" style="margin-top:0">Analyzed Frames</p>
          <div class="frames-gallery">
            {% for frame in result.frames %}
            <div class="frame-card">
              <img src="data:image/jpeg;base64,{{ frame.image_b64 }}" alt="Frame at {{ frame.time }}s">
              <div class="frame-info">
                <span class="frame-time">{{ frame.time }}s</span>
                <div>
                  {% if frame.faces > 0 %}<span class="frame-badge" style="background:var(--purple-bg);color:var(--purple);margin-right:4px">{{ frame.faces }} face(s)</span>{% endif %}
                  {% if frame.compliant %}
                  <span class="frame-badge frame-compliant">OK</span>
                  {% else %}
                  <span class="frame-badge frame-violation">{{ frame.missing | join(', ') }}</span>
                  {% endif %}
                </div>
              </div>
            </div>
            {% endfor %}
          </div>
        </div>
        {% endif %}

      </div>
    </div>
  </div>
</div>

<!-- Image Modal -->
<div class="modal-overlay" id="imageModal" onclick="closeModal(event)">
  <div class="modal-content">
    <button class="modal-close" onclick="closeModal(event, true)">
      <svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
    </button>
    <img id="modalImage" src="" alt="Full view">
    <div class="modal-info" id="modalInfo"></div>
  </div>
</div>

<script>
  // ── Theme ──────────────────────────────────────────────
  function getTheme() { return localStorage.getItem('sv-theme') || 'dark'; }
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const icon = document.getElementById('themeIcon');
    const label = document.getElementById('themeLabel');
    if (theme === 'dark') {
      icon.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>';
      label.textContent = 'Light Mode';
    } else {
      icon.innerHTML = '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>';
      label.textContent = 'Dark Mode';
    }
  }
  function toggleTheme() {
    const next = getTheme() === 'dark' ? 'light' : 'dark';
    localStorage.setItem('sv-theme', next);
    applyTheme(next);
  }
  applyTheme(getTheme());

  // ── Sidebar (mobile) ──────────────────────────────────
  function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
    document.getElementById('sidebarOverlay').classList.toggle('show');
  }

  // ── Tab switching ─────────────────────────────────────
  const tabNames = { image: 'Image Detection', video: 'Video Detection', live: 'Live Camera' };
  function switchTab(tab, navEl) {
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-' + tab).classList.add('active');
    if (navEl) navEl.classList.add('active');
    document.getElementById('breadcrumbCurrent').textContent = tabNames[tab] || tab;
    // Close mobile sidebar
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('sidebarOverlay').classList.remove('show');
  }

  // ── Image Upload ──────────────────────────────────────
  const imageFileInput = document.getElementById('imageFileInput');
  const imageFileName = document.getElementById('imageFileName');
  const imageSubmitBtn = document.getElementById('imageSubmitBtn');
  const imageDropArea = document.getElementById('imageDropArea');
  const imageForm = document.getElementById('imageForm');
  const imagePreviewContainer = document.getElementById('imagePreviewContainer');
  const imagePreview = document.getElementById('imagePreview');

  imageFileInput.addEventListener('change', function() {
    if (this.files.length > 0) {
      imageFileName.textContent = this.files[0].name;
      imageSubmitBtn.disabled = false;
      imageDropArea.classList.add('has-file');
      const reader = new FileReader();
      reader.onload = e => { imagePreview.src = e.target.result; imagePreviewContainer.classList.add('show'); };
      reader.readAsDataURL(this.files[0]);
    }
  });
  imageForm.addEventListener('submit', function() { imageSubmitBtn.classList.add('loading'); imageSubmitBtn.textContent = 'Analyzing'; });

  // ── Video Upload ──────────────────────────────────────
  const videoFileInput = document.getElementById('videoFileInput');
  const videoFileName = document.getElementById('videoFileName');
  const videoSubmitBtn = document.getElementById('videoSubmitBtn');
  const videoDropArea = document.getElementById('videoDropArea');
  const videoForm = document.getElementById('videoForm');
  const videoPreviewContainer = document.getElementById('videoPreviewContainer');
  const videoPreview = document.getElementById('videoPreview');

  videoFileInput.addEventListener('change', function() {
    if (this.files.length > 0) {
      const file = this.files[0];
      videoFileName.textContent = file.name + ' (' + (file.size / (1024*1024)).toFixed(1) + ' MB)';
      videoSubmitBtn.disabled = false;
      videoDropArea.classList.add('has-file');
      const url = URL.createObjectURL(file);
      videoPreview.src = url;
      videoPreviewContainer.classList.add('show');
    }
  });
  videoForm.addEventListener('submit', function() { videoSubmitBtn.classList.add('loading'); videoSubmitBtn.textContent = 'Analyzing video...'; });

  // ── Drag & Drop ───────────────────────────────────────
  function setupDragDrop(dropArea, fileInput) {
    ['dragover','dragenter'].forEach(e => {
      dropArea.addEventListener(e, ev => { ev.preventDefault(); dropArea.classList.add('dragover'); });
    });
    ['dragleave','drop'].forEach(e => {
      dropArea.addEventListener(e, ev => { ev.preventDefault(); dropArea.classList.remove('dragover'); });
    });
    dropArea.addEventListener('drop', ev => {
      ev.preventDefault();
      fileInput.files = ev.dataTransfer.files;
      fileInput.dispatchEvent(new Event('change'));
    });
  }
  setupDragDrop(imageDropArea, imageFileInput);
  setupDragDrop(videoDropArea, videoFileInput);

  // ── Live Camera ───────────────────────────────────────
  let liveStatusInterval = null;

  function startLive() {
    fetch('/live/start', {method: 'POST'}).then(r => r.json()).then(data => {
      if (data.status === 'ok' || data.status === 'already_running') {
        document.getElementById('liveFeedContainer').style.display = 'block';
        document.getElementById('liveFeed').src = '/live_feed?' + Date.now();
        document.getElementById('startCamBtn').disabled = true;
        document.getElementById('startCamBtn').style.background = 'var(--border-color)';
        document.getElementById('startCamBtn').style.color = 'var(--text-muted)';
        document.getElementById('stopCamBtn').disabled = false;
        document.getElementById('stopCamBtn').style.background = 'var(--danger)';
        document.getElementById('stopCamBtn').style.color = '#fff';
        liveStatusInterval = setInterval(updateLiveStatus, 500);
      } else {
        alert('Failed to start camera: ' + (data.message || 'Unknown error'));
      }
    }).catch(e => alert('Error: ' + e));
  }

  function stopLive() {
    fetch('/live/stop', {method: 'POST'}).then(r => r.json()).then(data => {
      document.getElementById('liveFeed').src = '';
      document.getElementById('liveFeedContainer').style.display = 'none';
      document.getElementById('startCamBtn').disabled = false;
      document.getElementById('startCamBtn').style.background = 'var(--accent)';
      document.getElementById('startCamBtn').style.color = '#fff';
      document.getElementById('stopCamBtn').disabled = true;
      document.getElementById('stopCamBtn').style.background = 'var(--border-color)';
      document.getElementById('stopCamBtn').style.color = 'var(--text-muted)';
      if (liveStatusInterval) { clearInterval(liveStatusInterval); liveStatusInterval = null; }
    });
  }

  function updateLiveStatus() {
    fetch('/live/status').then(r => r.json()).then(s => {
      document.getElementById('liveFps').textContent = 'FPS: ' + (s.fps || 0).toFixed(1);
      document.getElementById('liveFaceCount').textContent = s.faces ? s.faces.length : 0;
      document.getElementById('livePpeCount').textContent = s.ppe_found ? s.ppe_found.length : 0;

      const comp = document.getElementById('liveCompliance');
      if (s.compliant) {
        comp.textContent = 'OK';
        comp.style.color = 'var(--accent)';
      } else {
        comp.textContent = 'FAIL';
        comp.style.color = 'var(--danger)';
      }

      const ppeItems = ['Helmet','Gloves','Vest','Boots','Goggles'];
      const found = new Set(s.ppe_found || []);
      let ppeHtml = '';
      ppeItems.forEach(item => {
        const ok = found.has(item);
        ppeHtml += '<li class="ppe-row"><div class="left">' +
          '<span class="dot ' + (ok ? 'dot-on' : 'dot-off') + '"></span>' +
          '<span class="name ' + (ok ? 'found' : 'missing') + '">' + item + '</span></div>' +
          '<div class="right-side"><span class="badge ' + (ok ? 'badge-found">Found' : 'badge-missing">Missing') + '</span></div></li>';
      });
      document.getElementById('livePpeList').innerHTML = ppeHtml;

      const faces = s.faces || [];
      if (faces.length === 0) {
        document.getElementById('liveFaceList').innerHTML = '<p style="color:var(--text-muted);font-size:0.82rem;text-align:center;padding:12px;">No faces detected</p>';
      } else {
        let fHtml = '';
        faces.forEach(f => {
          fHtml += '<div class="face-row">' +
            '<div class="face-avatar">' + (f.name ? f.name[0] : '?') + '</div>' +
            '<div><div class="face-name">' + f.name + '</div>' +
            '<div class="face-conf">Confidence: ' + f.confidence + '</div></div>' +
            '<span class="badge badge-face">' + f.status + '</span></div>';
        });
        document.getElementById('liveFaceList').innerHTML = fHtml;
      }
    }).catch(() => {});
  }

  window.addEventListener('beforeunload', () => { fetch('/live/stop', {method:'POST'}); });

  // ── Image Modal / Lightbox ────────────────────────────
  function openModal(imgSrc, info) {
    document.getElementById('modalImage').src = imgSrc;
    document.getElementById('modalInfo').textContent = info || '';
    document.getElementById('imageModal').classList.add('show');
    document.body.style.overflow = 'hidden';
  }
  function closeModal(e, force) {
    if (force || e.target === document.getElementById('imageModal')) {
      document.getElementById('imageModal').classList.remove('show');
      document.body.style.overflow = '';
    }
  }
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      document.getElementById('imageModal').classList.remove('show');
      document.body.style.overflow = '';
    }
  });

  // Attach click to all frame-card images and result images
  document.querySelectorAll('.frame-card img').forEach(img => {
    img.addEventListener('click', () => {
      const info = img.closest('.frame-card');
      const time = info ? info.querySelector('.frame-time') : null;
      openModal(img.src, time ? 'Frame at ' + time.textContent : '');
    });
  });
  document.querySelectorAll('.result-image').forEach(img => {
    img.addEventListener('click', () => openModal(img.src, 'Detection Result'));
  });
</script>
</body>
</html>
"""


IMG_SIZE = 640


def run_face_detection(frame):
    """Run face detection on a frame. Returns list of face info dicts."""
    if face_system is None:
        return []

    try:
        face_results = face_system.identify_faces_in_frame(frame)
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

    # Face Detection
    faces = run_face_detection(frame)
    if face_system:
        try:
            face_det_results = face_system.identify_faces_in_frame(frame)
            frame = face_system.draw_face_detections(frame, face_det_results)
        except Exception:
            pass

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

    # Sample 1 frame per second, max 20 frames
    sample_interval = max(1, int(fps))
    sample_positions = list(range(0, total_frames, sample_interval))[:20]

    frames_data = []
    all_faces = {}  # {name: {'count': N, 'total_conf': float, 'status': str}}
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

        # PPE detection
        detections = ppe_detector.detect_ppe(frame)
        annotated = ppe_detector.draw_detections(frame.copy(), detections)

        detected_names = {d.class_name for d in detections}
        missing = list(REQUIRED_PPE - detected_names)
        is_compliant = len(missing) == 0
        if is_compliant:
            compliant_count += 1

        # Face detection
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

        # Encode annotated frame
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

    # Build faces summary
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
    return render_template_string(HTML, result=result, error=error)


@app.route('/video', methods=['POST'])
def video_upload():
    result = None
    error = None
    file = request.files.get('video')
    if not file or not file.filename:
        return render_template_string(HTML, result=None, error="No video file uploaded")

    # Save uploaded video to temp file
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

    return render_template_string(HTML, result=result, error=error)


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

        # FPS calculation
        fps_count += 1
        elapsed = time.time() - fps_start
        if elapsed >= 1.0:
            current_fps = fps_count / elapsed
            fps_count = 0
            fps_start = time.time()

        annotated = frame.copy()

        # PPE Detection (every frame — YOLO is fast)
        try:
            detections = live_ppe_detector.detect_ppe(frame)
            annotated = live_ppe_detector.draw_detections(annotated, detections)
            detected_names = [d.class_name for d in detections]
            missing = list(REQUIRED_PPE - set(detected_names))
            is_compliant = len(missing) == 0
        except Exception:
            detected_names = []
            missing = list(REQUIRED_PPE)
            is_compliant = False

        # Face Detection (every N frames for performance)
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
                            'status': 'Identified'
                        })
                    else:
                        faces_info.append({
                            'name': 'Unknown',
                            'confidence': f"{face_det.confidence:.2f}",
                            'status': 'Unknown'
                        })
            except Exception:
                cached_face_results = []

        # Draw cached faces
        if face_system and cached_face_results:
            try:
                annotated = face_system.draw_face_detections(annotated, cached_face_results)
            except Exception:
                pass

        # Build face info from cache if not freshly detected
        if not faces_info and cached_face_results:
            for face_det, worker in cached_face_results:
                if worker:
                    faces_info.append({
                        'name': worker.worker_name,
                        'confidence': f"{worker.confidence:.2f}",
                        'status': 'Identified'
                    })
                else:
                    faces_info.append({
                        'name': 'Unknown',
                        'confidence': f"{face_det.confidence:.2f}",
                        'status': 'Unknown'
                    })

        # Draw FPS + status on frame
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

        # Update shared status for polling
        live_camera['last_status'] = {
            'faces': faces_info,
            'ppe_found': detected_names,
            'missing_ppe': missing,
            'compliant': is_compliant,
            'fps': round(current_fps, 1)
        }

        # Encode as JPEG and yield as MJPEG frame
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

    with live_camera['lock']:
        live_camera['cap'] = cap
        live_camera['running'] = True
        live_camera['frame_count'] = 0
        live_camera['cached_faces'] = []

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


if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  PPE Detection & Face Recognition Web UI")
    print("  http://localhost:5000")
    print(f"  Face Recognition: {'ACTIVE' if face_system else 'DISABLED'}")
    print("=" * 50 + "\n")
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
