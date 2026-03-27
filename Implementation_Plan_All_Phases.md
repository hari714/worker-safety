# Workplace Safety System — Complete Implementation Plan

## Project: Workplace Safety and Access Control Using YOLO PPE and Face Detection
## Guide: Ms. N. Oviya, M.E., Assistant Professor, Department of CSE

---

## Table of Contents
1. [Phase 1: Project Setup & Environment](#phase-1-project-setup--environment)
2. [Phase 2: Module 1 — PPE Detection (YOLOv8)](#phase-2-module-1--ppe-detection-yolov8)
3. [Phase 3: Module 2 — Face Recognition & Worker Identification](#phase-3-module-2--face-recognition--worker-identification)
4. [Phase 4: Module 3 & 4 — Email Notifications + Database](#phase-4-module-3--4--email-notifications--database)
5. [Phase 5: Module 5 — API + Main Loop + Integration + Testing](#phase-5-module-5--api--main-loop--integration--testing)

---

## System Overview

An AI-powered safety monitoring system with 3 input modes:

| Mode | Input | Live Display |
|------|-------|:---:|
| Image Upload | Single image via API | No |
| Webcam | Camera ID=0, 1280x720, 30fps | Yes (OpenCV window) |
| Video File | .mp4, .avi file path | Yes (OpenCV window) |

### 5 Modules

| Module | Name | Technology |
|:---:|---|---|
| 1 | PPE Detection | YOLOv8 |
| 2 | Face Recognition | MTCNN + FaceNet |
| 3 | Email Notification | SMTP (Gmail) |
| 4 | Database Management | PostgreSQL + SQLAlchemy |
| 5 | Flask REST API | Flask + CORS |

### 3-Layer Architecture

```
INPUT LAYER              PROCESSING LAYER (AI)           ACTION LAYER
┌──────────┐         ┌─────────────────────────┐     ┌──────────────┐
│ Webcam   │         │ 1. Face Detection       │     │ Database     │
│ IP Camera│───────> │ 2. Face Recognition     │────>│ Email Alert  │
│ Video    │         │ 3. PPE Detection        │     │ Dashboard    │
│ Image    │         │ 4. Compliance Check     │     │ REST API     │
└──────────┘         └─────────────────────────┘     └──────────────┘
```

---

# Phase 1: Project Setup & Environment

## 1.1 Objective
Create the entire project skeleton, install all libraries, write configuration files.

## 1.2 Folder Structure

```
WORKSPACE_SAFETY_SYSTEM/
│
├── ppe_detection/
│   ├── __init__.py
│   ├── yolo_model.py            # YOLOv8 PPE training
│   ├── ppe_classes.py           # PPE class definitions & dataclass
│   └── inference.py             # Real-time PPE inference
│
├── face_recognition/
│   ├── __init__.py
│   ├── face_detection.py        # MTCNN face detection
│   ├── face_embedding.py        # FaceNet 512-dim embeddings
│   ├── worker_identification.py # Match face to worker
│   └── face_database.py         # Store/load face encodings (.pkl)
│
├── worker_management/
│   ├── __init__.py
│   ├── models.py                # SQLAlchemy models (4 tables)
│   ├── db_operations.py         # CRUD operations
│   └── worker_registry.py       # Worker registration logic
│
├── notification_system/
│   ├── __init__.py
│   ├── email_sender.py          # SMTP email service
│   ├── email_templates.py       # HTML email templates
│   └── notification_queue.py    # Queue management
│
├── monitoring/
│   ├── __init__.py
│   ├── video_processor.py       # Main processing loop (heart of system)
│   ├── compliance_checker.py    # Verify PPE status
│   └── violation_logger.py      # Log violations
│
├── api/
│   ├── __init__.py
│   ├── app.py                   # Flask application + 9 endpoints
│   ├── routes.py                # API route definitions
│   └── middleware.py            # Authentication middleware
│
├── config/
│   ├── __init__.py
│   ├── settings.py              # All configuration (loads from .env)
│   ├── database.py              # DB connection setup
│   └── email_config.py          # Email settings
│
├── utils/
│   ├── __init__.py
│   ├── logger.py                # Logging setup
│   ├── helpers.py               # Helper functions
│   └── validators.py            # Input validation
│
├── tests/
│   ├── test_ppe_detection.py    # PPE detection tests
│   ├── test_face_recognition.py # Face recognition tests
│   └── test_email_system.py     # Email system tests
│
├── models/                      # Trained model weights saved here
│   └── (ppe_detection_best.pt)
│
├── datasets/
│   └── final_dataset/           # 3,810 images, ready for training
│       ├── data.yaml
│       ├── images/
│       │   ├── train/ (2,667)
│       │   ├── val/ (571)
│       │   └── test/ (572)
│       └── labels/
│           ├── train/ (2,667)
│           ├── val/ (571)
│           └── test/ (572)
│
├── worker_embeddings/           # Face .pkl files stored here
├── violations/                  # Violation screenshots saved here
├── logs/                        # Log files
├── requirements.txt             # All Python dependencies
├── .env                         # Secret credentials
└── main.py                      # Application entry point
```

## 1.3 Python Dependencies (requirements.txt)

```
# Core ML/CV Libraries
torch==2.0.0
torchvision==0.15.0
opencv-python==4.8.0
ultralytics==8.0.0              # YOLOv8
mtcnn==0.1.1                    # Face detection
facenet-pytorch==2.2.9          # FaceNet embeddings

# Web Framework
Flask==2.3.0
Flask-CORS==4.0.0

# Database
SQLAlchemy==2.0.0
psycopg2-binary==2.9.0
alembic==1.12.0

# Email & Config
python-dotenv==1.0.0

# Data Processing
numpy==1.24.0
pandas==2.0.0
Pillow==10.0.0
scikit-learn>=1.0.0

# Utilities
requests==2.31.0
pydantic==2.0.0

# Logging
structlog==23.1.0

# Testing
pytest==7.4.0
pytest-cov==4.1.0
```

## 1.4 Configuration File (config/settings.py)

Loads all settings from `.env` file:

| Setting | Default Value | Description |
|---------|---------------|-------------|
| `DATABASE_URL` | `postgresql://username:password@localhost:5432/safety_db` | PostgreSQL connection |
| `SENDER_EMAIL` | (from .env) | Gmail address for sending alerts |
| `SENDER_PASSWORD` | (from .env) | Gmail App Password (16-char) |
| `SMTP_SERVER` | `smtp.gmail.com` | SMTP server |
| `SMTP_PORT` | `587` | SMTP port (TLS) |
| `PPE_MODEL_PATH` | `models/ppe_detection_best.pt` | Trained YOLOv8 model |
| `FACE_EMBEDDING_DIR` | `models/face_embeddings` | Worker face embeddings |
| `CAMERA_ID` | `0` | Webcam device ID |
| `VIDEO_FPS` | `30` | Frames per second |
| `FRAME_WIDTH` | `1280` | Camera resolution width |
| `FRAME_HEIGHT` | `720` | Camera resolution height |
| `PPE_CONFIDENCE_THRESHOLD` | `0.5` | Min confidence for PPE detection |
| `FACE_CONFIDENCE_THRESHOLD` | `0.6` | Min confidence for face detection |
| `SIMILARITY_THRESHOLD` | `0.6` | Min cosine similarity for face matching |
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_FILE` | `logs/safety_system.log` | Log file path |

## 1.5 Environment File (.env template)

```
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/safety_db

# Email
SENDER_EMAIL=your.email@gmail.com
SENDER_PASSWORD=xxxx_xxxx_xxxx_xxxx

# Model Paths
PPE_MODEL_PATH=models/ppe_detection_best.pt
FACE_EMBEDDING_DIR=models/face_embeddings

# Camera Settings
CAMERA_ID=0
VIDEO_FPS=30
FRAME_WIDTH=1280
FRAME_HEIGHT=720

# Detection Thresholds
PPE_CONFIDENCE_THRESHOLD=0.5
FACE_CONFIDENCE_THRESHOLD=0.6
SIMILARITY_THRESHOLD=0.6

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/safety_system.log
```

## 1.6 Phase 1 Output
- Project structure created with all folders and `__init__.py` files
- All Python libraries installed in virtual environment
- `config/settings.py` loading from `.env`
- `.env` template created
- Dataset already in place at `datasets/final_dataset/`

---

# Phase 2: Module 1 — PPE Detection (YOLOv8)

## 2.1 Objective
Train YOLOv8 model on our dataset and build real-time PPE detector.

## 2.2 Dataset (Already Prepared)

| Split | Images | Labels |
|-------|--------|--------|
| Train | 2,667 | 2,667 |
| Val | 571 | 571 |
| Test | 572 | 572 |
| **Total** | **3,810** | **3,810** |

### Per-Class Instance Count

| Class ID | Class Name | Train | Val | Test | Total |
|:---:|---|:---:|:---:|:---:|:---:|
| 0 | helmet | 5,011 | 1,013 | 1,040 | 7,064 |
| 1 | gloves | 2,186 | 454 | 453 | 3,093 |
| 2 | vest | 3,602 | 714 | 799 | 5,115 |
| 3 | boots | 2,310 | 504 | 555 | 3,369 |
| 4 | goggles | 822 | 185 | 200 | 1,207 |

### data.yaml

```yaml
path: D:/workers_Safety/datasets/final_dataset
train: images/train
val: images/val
test: images/test

nc: 5
names:
  0: helmet
  1: gloves
  2: vest
  3: boots
  4: goggles
```

## 2.3 Training Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| Base Model | `yolov8m.pt` | YOLOv8 Medium (pretrained on COCO) |
| Epochs | 100 | Max training epochs |
| Batch Size | 32 | Images per batch |
| Image Size | 640x640 | Input resolution |
| Patience | 20 | Early stopping (stops if no improvement for 20 epochs) |
| Save Period | 5 | Save checkpoint every 5 epochs |

### Learning Rate & Optimizer

| Parameter | Value |
|-----------|-------|
| lr0 | 0.01 |
| lrf | 0.01 |
| momentum | 0.937 |
| weight_decay | 0.0005 |

### Data Augmentation (Built-in during training)

| Augmentation | Value | What It Does |
|-------------|-------|-------------|
| hsv_h | 0.015 | Hue shift |
| hsv_s | 0.7 | Saturation shift |
| hsv_v | 0.4 | Value/brightness shift |
| degrees | 10 | Random rotation up to 10 degrees |
| translate | 0.1 | Random translation |
| scale | 0.5 | Random scaling |
| flipud | 0.5 | 50% chance vertical flip |
| fliplr | 0.5 | 50% chance horizontal flip |
| mosaic | 1.0 | Mosaic augmentation (combines 4 images) |

## 2.4 Training Code (ppe_detection/yolo_model.py)

```python
from ultralytics import YOLO
import torch

class PPEModelTrainer:
    def __init__(self, model_size='m'):
        self.model = YOLO(f'yolov8{model_size}.pt')
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def train(self, data_yaml, epochs=100, batch_size=32, img_size=640):
        results = self.model.train(
            data=data_yaml, epochs=epochs, imgsz=img_size,
            batch=batch_size, device=self.device, patience=20,
            save=True, save_period=5,
            hsv_h=0.015, hsv_s=0.7, hsv_v=0.4,
            degrees=10, translate=0.1, scale=0.5,
            flipud=0.5, fliplr=0.5, mosaic=1.0,
            lr0=0.01, lrf=0.01, momentum=0.937, weight_decay=0.0005,
            val=True, save_conf=True, verbose=True,
            project='runs/detect', name='ppe_detection'
        )
        return results

    def validate(self, model_path, data_yaml):
        model = YOLO(model_path)
        return model.val(data=data_yaml)

    def test(self, model_path, test_images_dir):
        model = YOLO(model_path)
        return model.predict(source=test_images_dir, conf=0.5)
```

**Training output saved at:** `runs/detect/ppe_detection/weights/best.pt`
**Copy to:** `models/ppe_detection_best.pt`

## 2.5 PPE Detector Classes

### PPEDetection Dataclass (ppe_detection/ppe_classes.py)

```python
@dataclass
class PPEDetection:
    class_id: int                          # 0-4
    class_name: str                        # helmet, gloves, vest, boots, goggles
    confidence: float                      # 0.0 - 1.0
    bbox: Tuple[int, int, int, int]        # x1, y1, x2, y2
    x_center: float                        # bounding box center X
    y_center: float                        # bounding box center Y
```

### PPEDetector Class (ppe_detection/inference.py)

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| `detect_ppe(frame)` | numpy image | List[PPEDetection] | Runs YOLOv8, returns all detections above 0.5 confidence |
| `draw_detections(frame, detections)` | image + detections | annotated image | Draws colored bounding boxes + labels |
| `check_ppe_compliance(detections)` | List[PPEDetection] | (bool, set) | Returns (is_compliant, missing_ppe_set) |

### Bounding Box Colors

| PPE | Color | RGB |
|-----|-------|-----|
| helmet | Green | (0, 255, 0) |
| gloves | Blue | (255, 0, 0) |
| boots | Red | (0, 0, 255) |
| goggles | Cyan | (255, 255, 0) |
| vest | Magenta | (255, 0, 255) |

### Detection Flow Per Frame

```
Camera Frame (numpy array)
       ↓
  model(frame, verbose=False)
       ↓
  For each detection:
    ├── Get bbox (x1, y1, x2, y2)
    ├── Get class_id (0-4)
    ├── Get confidence (0.0-1.0)
    ├── Skip if confidence < 0.5
    └── Create PPEDetection object
       ↓
  Compliance Check:
    detected_ppe = {helmet, gloves, vest, boots}
    required_ppe = {helmet, gloves, vest, boots, goggles}
    missing_ppe  = required - detected = {goggles}
    is_compliant = False (goggles missing)
       ↓
  Output: (False, {"goggles"})
```

## 2.6 Phase 2 Output
- Trained YOLOv8 model at `models/ppe_detection_best.pt`
- PPEDetector class that can detect 5 PPE items in any image/frame
- Compliance checker that identifies missing PPE
- Target accuracy: 95%+

---

# Phase 3: Module 2 — Face Recognition & Worker Identification

## 3.1 Objective
Build face detection + worker identification pipeline using pretrained models (no training needed).

## 3.2 Technology Stack

| Component | Technology | Details |
|-----------|-----------|---------|
| Face Detection | MTCNN | Detects face location + 5 landmarks |
| Face Embedding | FaceNet (InceptionResnetV1) | Pretrained on vggface2, 512-dim output |
| Matching | Cosine Similarity | Threshold: 0.6 |
| Storage | Pickle (.pkl) files | One file per worker |

## 3.3 Face Detection (MTCNN)

### What MTCNN Returns Per Face

| Output | Description |
|--------|-------------|
| bbox | (x, y, width, height) of face |
| confidence | Detection probability (0.0-1.0) |
| landmarks | 5 points: left_eye, right_eye, nose, left_mouth, right_mouth |

### FaceDetection Dataclass

```python
@dataclass
class FaceDetection:
    bbox: Tuple[int, int, int, int]    # x, y, width, height
    confidence: float                   # 0.0 - 1.0
    landmarks: dict                     # 5 facial landmarks
```

## 3.4 Face Embedding (FaceNet)

### Pipeline

```
Detected Face Region (from MTCNN)
       ↓
  Crop face from frame using bbox
       ↓
  Resize to 160x160 pixels
       ↓
  Normalize: pixel_values / 255.0
       ↓
  Convert to PyTorch tensor (C, H, W format)
       ↓
  FaceNet (InceptionResnetV1, pretrained='vggface2')
       ↓
  Output: 512-dimensional embedding vector
       ↓
  [0.023, -0.156, 0.891, ..., 0.445]  (512 floats)
```

### Technical Specs

| Spec | Value |
|------|-------|
| Model | InceptionResnetV1 |
| Pretrained on | vggface2 |
| Input size | 160x160 pixels |
| Output size | 512 dimensions |
| Normalization | /255.0 |
| Processing time | < 1 second |
| Accuracy | ~95% |

## 3.5 Worker Registration (One-time per worker)

### Requirements Per Worker

| Requirement | Value |
|------------|-------|
| Images needed | 10-20 minimum |
| Image resolution | 224x224 or higher |
| Face size in image | At least 80x80 pixels |
| Angle variations | Front, 30 degrees, 45 degrees |
| Lighting | Natural, artificial, side-lit |
| Background | Plain or office/factory environment |
| Expression | Neutral, slight smile |
| Occlusion | Minimal (can have PPE like helmet) |

### Registration Flow

```
10-20 photos of Worker "Ravi" (different angles/lighting)
       ↓
  For each photo:
    ├── MTCNN detects face
    ├── Crop face region
    ├── FaceNet generates 512-dim embedding
    └── Store embedding
       ↓
  Average all embeddings → Single 512-dim vector
       ↓
  Save as worker_embeddings/W001.pkl
  Contains:
    {
      'embedding': [512 floats],
      'info': {
        'name': 'Ravi',
        'email': 'ravi@company.com',
        'id': 'W001'
      }
    }
```

### Face Database Structure

```
worker_embeddings/
├── W001.pkl       # Ravi - averaged 512-dim embedding
├── W002.pkl       # Kumar
├── W003.pkl       # Priya
└── W00N.pkl       # Nth worker
```

## 3.6 Worker Identification (Runtime)

### Matching Flow

```
Live camera frame
       ↓
  MTCNN detects face(s) in frame
       ↓
  For each detected face:
    ├── Crop face → Resize 160x160 → Normalize
    ├── FaceNet generates 512-dim embedding
    ├── Compare with ALL stored worker embeddings
    │   ├── W001.pkl → cosine_similarity = 0.92  ← BEST MATCH
    │   ├── W002.pkl → cosine_similarity = 0.34
    │   └── W003.pkl → cosine_similarity = 0.21
    │
    ├── Best match score (0.92) >= threshold (0.6)?
    │   ├── YES → Worker Identified: "Ravi" (W001), confidence: 0.92
    │   └── NO  → Unknown Person
    └── Return WorkerIdentification object
```

### WorkerIdentification Dataclass

```python
@dataclass
class WorkerIdentification:
    worker_id: str           # "W001"
    worker_name: str         # "Ravi"
    confidence: float        # 0.92
    email: str               # "ravi@company.com"
```

## 3.7 FaceRecognitionSystem Class Methods

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| `detect_faces(frame)` | numpy image | List[FaceDetection] | MTCNN detects all faces in frame |
| `extract_face_embedding(frame, face)` | image + FaceDetection | 512-dim numpy array | FaceNet embedding |
| `identify_worker(embedding)` | 512-dim vector | WorkerIdentification or None | Match against stored workers |
| `register_worker(id, name, email, images)` | worker info + image list | bool (success) | Register new worker |
| `draw_face_detections(frame, detections)` | image + detections | annotated image | Draw face boxes + names |

## 3.8 Phase 3 Output
- Face detection working (MTCNN)
- Face embedding extraction working (FaceNet, 512-dim)
- Worker registration system (save .pkl files)
- Worker identification in real-time (cosine similarity >= 0.6)
- No training needed — all pretrained

---

# Phase 4: Module 3 & 4 — Email Notifications + Database

## 4.1 Objective
Build email alert system for violations and database to store all records.

---

## Module 3: Email Notification System

### 4.2 Email Configuration

| Setting | Value |
|---------|-------|
| SMTP Server | smtp.gmail.com |
| Port | 587 (TLS) |
| Authentication | Gmail App Password (16-character) |
| Requires | Gmail 2-Factor Authentication enabled |
| Env vars | `SENDER_EMAIL`, `SENDER_PASSWORD` |

### Gmail Setup Steps

```
1. Go to myaccount.google.com
2. Click "Security"
3. Enable "2-Step Verification"
4. Go back to "Security" → "App passwords"
5. Select "Mail" + "Windows Computer"
6. Google generates 16-character password
7. Use this as SENDER_PASSWORD in .env
```

### 4.3 Two Email Types

#### Type 1: Violation Alert Email (sent to worker)

**Trigger:** Worker detected with missing PPE
**Cooldown:** 15 minutes per worker (won't send again within 15 min)

**HTML Template Structure:**
```
┌─────────────────────────────────────────┐
│  HEADER (red background, white text)    │
│  "Safety Alert"                         │
├─────────────────────────────────────────┤
│                                         │
│  Dear [Worker Name],                    │
│                                         │
│  This is an automated safety            │
│  notification...                        │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ ALERT BOX (yellow background)   │   │
│  │ Missing PPE:                    │   │
│  │ * HELMET                        │   │
│  │ * GLOVES                        │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ VIOLATION DETAILS (gray bg)     │   │
│  │ Date & Time: 2026-03-10 14:30  │   │
│  │ Worker ID: W001                 │   │
│  │ Violation Count (Today): 3      │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Action Required:                       │
│  Please ensure all PPE is worn:        │
│  - Safety Helmet                        │
│  - Safety Gloves                        │
│  - Safety Shoes                         │
│  - Protection Glasses                   │
│  - Safety Vest                          │
│                                         │
│  [Acknowledge Alert] (green button)     │
│                                         │
├─────────────────────────────────────────┤
│  FOOTER (gray)                          │
│  Workplace Safety Monitoring System     │
└─────────────────────────────────────────┘
```

**Attachments:** Violation screenshot image (inline)

#### Type 2: Daily Summary Report (sent to safety manager)

**Trigger:** Scheduled daily (end of day)

**HTML Template Structure:**
```
┌────────────────────────────────────────────────────┐
│  Daily Safety Report                                │
│  Report Date: 2026-03-10                           │
│  Total Violations: 12                               │
│                                                    │
│  ┌────────┬──────┬───────┬──────────┬───────┐     │
│  │ Worker │ ID   │ Time  │ Missing  │ Count │     │
│  ├────────┼──────┼───────┼──────────┼───────┤     │
│  │ Ravi   │ W001 │ 09:15 │ Helmet   │   3   │     │
│  │ Kumar  │ W002 │ 10:30 │ Gloves   │   1   │     │
│  │ Priya  │ W003 │ 11:45 │ Vest     │   2   │     │
│  └────────┴──────┴───────┴──────────┴───────┘     │
│                                                    │
│  Automatically generated by Safety System          │
└────────────────────────────────────────────────────┘
```

### 4.4 ViolationRecord Dataclass

```python
@dataclass
class ViolationRecord:
    worker_id: str                    # "W001"
    worker_name: str                  # "Ravi"
    worker_email: str                 # "ravi@company.com"
    timestamp: datetime               # 2026-03-10 14:30:00
    missing_ppe: set                  # {"helmet", "gloves"}
    violation_count: int              # 3 (today's count)
    image_path: Optional[str] = None  # "violations/W001_20260310_143000.jpg"
```

### 4.5 EmailNotificationSystem Class Methods

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| `create_violation_email(violation)` | ViolationRecord | MIMEMultipart | Build styled HTML email with image |
| `send_email(violation)` | ViolationRecord | bool | Send violation alert to worker |
| `send_daily_report_email(email, violations)` | manager email + list | bool | Send daily summary to manager |

### 4.6 Email Cooldown Logic

```
Worker W001 violation at 09:15 → Email SENT
Worker W001 violation at 09:20 → Email SKIPPED (within 15 min)
Worker W001 violation at 09:25 → Email SKIPPED (within 15 min)
Worker W001 violation at 09:31 → Email SENT (15 min passed)
```

### Files Created
- `notification_system/email_sender.py` — EmailNotificationSystem class
- `notification_system/email_templates.py` — HTML templates (violation + daily report)

---

## Module 4: Database Management

### 4.7 Database: PostgreSQL 13+ with SQLAlchemy ORM

### 4.8 Four Database Tables

#### Table 1: `workers`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| worker_id | String(50) | **PRIMARY KEY** | Unique worker ID (e.g., "W001") |
| name | String(100) | NOT NULL | Worker full name |
| email | String(100) | UNIQUE, NOT NULL | Worker email address |
| phone | String(20) | nullable | Phone number |
| department | String(100) | nullable | Department name |
| position | String(100) | nullable | Job position/title |
| is_active | Boolean | DEFAULT True | Whether worker is currently active |
| date_registered | DateTime | DEFAULT now() | When worker was added |
| last_seen | DateTime | nullable | Last time detected by camera |

**Indexes:** idx_email (email), idx_department (department)

#### Table 2: `violation_logs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| violation_id | Integer | **PK, AUTO INCREMENT** | Unique violation ID |
| worker_id | String(50) | **FK → workers.worker_id** | Who committed violation |
| timestamp | DateTime | DEFAULT now(), INDEXED | When violation occurred |
| missing_ppe | Text | | JSON string: `["helmet","gloves"]` |
| image_path | String(255) | | Path to violation screenshot |
| email_sent | Boolean | DEFAULT False | Whether email was sent |
| email_sent_time | DateTime | nullable | When email was sent |
| severity | Enum | DEFAULT 'medium' | low / medium / critical |

**Indexes:** idx_worker_timestamp (worker_id + timestamp), idx_timestamp (timestamp)

**Severity Rules:**
| Missing PPE Count | Severity |
|:---:|---|
| 1 item | low |
| 2-3 items | medium |
| 4-5 items | critical |

#### Table 3: `compliance_reports`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| report_id | Integer | **PK, AUTO INCREMENT** | Report ID |
| report_date | DateTime | INDEXED | Date of report |
| total_violations | Integer | | Total violations that day |
| total_workers_checked | Integer | | How many workers were scanned |
| compliance_rate | Float | | Percentage (e.g., 85.5) |
| critical_violations | Integer | | Count of critical violations |
| medium_violations | Integer | | Count of medium violations |
| low_violations | Integer | | Count of low violations |

#### Table 4: `worker_face_embeddings`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| embedding_id | Integer | **PK, AUTO INCREMENT** | Embedding ID |
| worker_id | String(50) | **FK → workers.worker_id**, INDEXED | Which worker |
| embedding_vector | Text | | Serialized 512-dim numpy array |
| image_path | String(255) | | Source face image path |
| created_at | DateTime | DEFAULT now() | When embedding was created |

### 4.9 Entity Relationship

```
┌─────────────┐         ┌──────────────────┐
│   workers    │ 1 --- * │  violation_logs  │
│  (worker_id) │─────────│  (worker_id FK)  │
└──────┬──────┘         └──────────────────┘
       │
       │ 1 --- *
       │
┌──────┴──────────────────┐
│ worker_face_embeddings   │
│ (worker_id FK)           │
└─────────────────────────┘

┌─────────────────┐
│compliance_reports│  (standalone daily reports)
└─────────────────┘
```

### 4.10 DatabaseOperations Class — CRUD Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_worker()` | worker_id, name, email, phone, department, position | bool | Insert new worker into `workers` table |
| `log_violation()` | worker_id, missing_ppe(set), image_path, severity | bool | Insert record into `violation_logs` |
| `get_worker_by_id()` | worker_id | Worker object or None | Fetch worker info |
| `get_violations_today()` | worker_id (optional) | List[ViolationLog] | Get today's violations, optionally filtered by worker |
| `update_email_sent()` | violation_id | bool | Set email_sent=True, email_sent_time=now |

### Files Created
- `worker_management/models.py` — SQLAlchemy models (Worker, ViolationLog, ComplianceReport, WorkerFaceEmbedding)
- `worker_management/db_operations.py` — DatabaseOperations class with all CRUD methods

### 4.11 Phase 4 Output
- Email notification system ready (violation alerts + daily reports)
- 15-minute cooldown per worker implemented
- PostgreSQL database with 4 tables created
- All CRUD operations working

---

# Phase 5: Module 5 — API + Main Loop + Integration + Testing

## 5.1 Objective
Build Flask REST API, wire all modules together in the main processing loop, and write tests.

---

## Flask REST API

### 5.2 API Configuration

| Setting | Value |
|---------|-------|
| Framework | Flask 2.3.0 |
| CORS | Enabled (Flask-CORS) |
| Host | localhost |
| Port | 5000 |
| Format | JSON responses |

### 5.3 Nine API Endpoints

#### Worker Management Endpoints

**1. GET /api/workers** — List all workers
```
Request:  GET http://localhost:5000/api/workers
Response: {
  "status": "success",
  "data": [
    {
      "worker_id": "W001",
      "name": "Ravi",
      "email": "ravi@company.com",
      "department": "Construction",
      "position": "Site Worker"
    },
    ...
  ]
}
```

**2. POST /api/workers** — Add new worker
```
Request:  POST http://localhost:5000/api/workers
Body: {
  "worker_id": "W001",
  "name": "Ravi",
  "email": "ravi@company.com",
  "phone": "9876543210",
  "department": "Construction",
  "position": "Site Worker"
}
Response: {
  "status": "success",
  "message": "Worker added successfully"
}
Status: 201 Created
```

**3. GET /api/workers/<worker_id>** — Get worker details
```
Request:  GET http://localhost:5000/api/workers/W001
Response: {
  "status": "success",
  "data": {
    "worker_id": "W001",
    "name": "Ravi",
    "email": "ravi@company.com",
    "department": "Construction",
    "position": "Site Worker",
    "last_seen": "2026-03-10T14:30:00"
  }
}
```

#### Violation Endpoints

**4. GET /api/violations/today** — Today's violations
```
Request:  GET http://localhost:5000/api/violations/today
          GET http://localhost:5000/api/violations/today?worker_id=W001
Response: {
  "status": "success",
  "data": [
    {
      "violation_id": 1,
      "worker_id": "W001",
      "timestamp": "2026-03-10T09:15:00",
      "missing_ppe": ["helmet", "gloves"],
      "email_sent": true
    },
    ...
  ]
}
```

**5. GET /api/violations/<violation_id>** — Specific violation
```
Request:  GET http://localhost:5000/api/violations/1
Response: {
  "status": "success",
  "data": {
    "violation_id": 1,
    "worker_id": "W001",
    "timestamp": "2026-03-10T09:15:00",
    "missing_ppe": ["helmet", "gloves"],
    "image_path": "violations/W001_20260310_091500.jpg",
    "email_sent": true
  }
}
```

#### Statistics Endpoints

**6. GET /api/statistics/daily** — Daily statistics
```
Request:  GET http://localhost:5000/api/statistics/daily
          GET http://localhost:5000/api/statistics/daily?date=2026-03-10
Response: {
  "status": "success",
  "date": "2026-03-10",
  "data": {
    "total_violations": 12,
    "unique_workers": 5,
    "missing_ppe_count": {
      "helmet": 4,
      "gloves": 3,
      "vest": 2,
      "boots": 2,
      "goggles": 1
    }
  }
}
```

**7. GET /api/statistics/worker/<worker_id>** — Worker stats
```
Request:  GET http://localhost:5000/api/statistics/worker/W001?days=7
Response: {
  "status": "success",
  "worker_id": "W001",
  "period_days": 7,
  "data": {
    "total_violations": 8,
    "violations_by_date": {
      "2026-03-10": 3,
      "2026-03-09": 2,
      "2026-03-08": 3
    },
    "missing_ppe_summary": {
      "helmet": 4,
      "gloves": 3,
      "goggles": 1
    }
  }
}
```

#### Face Registration Endpoint

**8. POST /api/workers/<worker_id>/register-face** — Register worker face
```
Request:  POST http://localhost:5000/api/workers/W001/register-face
          Content-Type: multipart/form-data
          images: [file1.jpg, file2.jpg, ..., file20.jpg]
Response: {
  "status": "success",
  "message": "Face registered successfully for worker W001"
}
```

#### Health Check

**9. GET /api/health** — System health
```
Request:  GET http://localhost:5000/api/health
Response: {
  "status": "healthy",
  "components": {
    "ppe_model": "loaded",
    "face_recognition": "ready",
    "database": "connected",
    "email": "configured"
  }
}
```

### 5.4 API Endpoint Summary Table

| # | Method | Endpoint | Description | Status Code |
|---|--------|----------|-------------|:-----------:|
| 1 | GET | `/api/workers` | List all workers | 200 |
| 2 | POST | `/api/workers` | Add new worker | 201 |
| 3 | GET | `/api/workers/<id>` | Get worker by ID | 200 / 404 |
| 4 | GET | `/api/violations/today` | Today's violations | 200 |
| 5 | GET | `/api/violations/<id>` | Specific violation | 200 / 404 |
| 6 | GET | `/api/statistics/daily` | Daily stats | 200 |
| 7 | GET | `/api/statistics/worker/<id>` | Worker stats (past N days) | 200 |
| 8 | POST | `/api/workers/<id>/register-face` | Register face images | 200 |
| 9 | GET | `/api/health` | System health check | 200 |

---

## Main Processing Loop (WorkplaceSafetyMonitor)

### 5.5 This is Where All 4 Modules Come Together

```
Camera starts (webcam or video file or image)
       ↓
┌─── LOOP (every frame) ───────────────────────────────────────┐
│                                                               │
│  Step 1: Read frame from camera                              │
│       ↓                                                       │
│  Step 2: MODULE 1 — PPE Detection                            │
│     → YOLOv8 detects: helmet, gloves, vest, boots, goggles   │
│     → Draw colored bounding boxes on frame                   │
│       ↓                                                       │
│  Step 3: MODULE 2 — Face Recognition                         │
│     → MTCNN detects face locations                           │
│     → FaceNet extracts 512-dim embeddings                    │
│     → Match against stored worker embeddings                 │
│     → Identify worker (name, ID, email)                      │
│       ↓                                                       │
│  Step 4: Compliance Check                                    │
│     → Compare detected PPE vs required {helmet, gloves,      │
│       vest, boots, goggles}                                  │
│     → Calculate missing_ppe set                              │
│       ↓                                                       │
│  Step 5: If VIOLATION (missing PPE):                         │
│     → Save screenshot: violations/{worker_id}_{timestamp}.jpg│
│     → MODULE 4: Log to database (violation_logs table)       │
│     → MODULE 3: Send email alert (if 15-min cooldown passed) │
│     → Display RED label: "Ravi - Compliant: False"           │
│       ↓                                                       │
│  Step 6: If COMPLIANT (all PPE present):                     │
│     → Display GREEN label: "Ravi - Compliant: True"          │
│       ↓                                                       │
│  Step 7: Display frame with all annotations                  │
│     → Timestamp at top: "Time: 2026-03-10 14:30:00"         │
│     → PPE bounding boxes (colored)                           │
│     → Face boxes with worker names                           │
│     → Compliant/Non-compliant status                         │
│     → Press 'q' to quit                                      │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### 5.6 WorkplaceSafetyMonitor Class

| Method | Description |
|--------|-------------|
| `__init__(db_url, email_config)` | Initialize all 4 modules: PPEDetector, FaceRecognitionSystem, DatabaseOperations, EmailNotificationSystem |
| `process_frame(frame)` | Run full pipeline on single frame (detect PPE → detect face → identify worker → check compliance → handle violations) |
| `_handle_violation(worker, missing_ppe, frame)` | Save image, log to DB, send email with cooldown |
| `_should_send_email(worker_id)` | Check if 15-min cooldown has passed |
| `run_from_webcam()` | Start live monitoring from webcam (CAMERA_ID=0, 1280x720, 30fps) |
| `run_from_video(video_path)` | Process recorded video file |

### 5.7 Three Input Modes

| Mode | Code | Input | Display |
|------|------|-------|---------|
| Webcam | `monitor.run_from_webcam()` | Camera ID=0 | OpenCV window, live |
| Video | `monitor.run_from_video("path.mp4")` | Video file | OpenCV window, playback |
| Image | `monitor.process_frame(image)` | Single numpy image | Returns annotated frame |

---

## Testing

### 5.8 Test Files (pytest)

#### test_ppe_detection.py
```python
# Tests:
# - Model loads successfully from .pt file
# - detect_ppe() returns List[PPEDetection]
# - Each detection has valid class_id (0-4)
# - Each detection has confidence between 0.0-1.0
# - check_ppe_compliance() returns correct missing items
# - Compliance returns True when all 5 PPE detected
# - Compliance returns False + correct set when PPE missing
# - draw_detections() returns valid image (not None)
```

#### test_face_recognition.py
```python
# Tests:
# - MTCNN loads and detects faces
# - FaceNet generates 512-dim embedding
# - Embedding is numpy array of shape (512,)
# - register_worker() saves .pkl file
# - identify_worker() returns correct worker for known face
# - identify_worker() returns None for unknown face
# - Cosine similarity calculation is correct
```

#### test_email_system.py
```python
# Tests:
# - HTML template generates correctly with all fields
# - ViolationRecord dataclass creates properly
# - Daily report template generates table rows
# - Email subject line includes worker name
# - Image attachment works when image_path exists
```

### Files Created
- `api/app.py` — Flask application with 9 endpoints + CORS
- `monitoring/video_processor.py` — WorkplaceSafetyMonitor class
- `main.py` — Application entry point
- `tests/test_ppe_detection.py`
- `tests/test_face_recognition.py`
- `tests/test_email_system.py`

### 5.9 Phase 5 Output
- Flask API running with 9 endpoints
- Main processing loop integrating all 4 modules
- 3 input modes: webcam, video, image
- All tests passing
- Complete working system

---

# Full Phase Summary

| Phase | What | Input | Output |
|:---:|---|---|---|
| **1** | Project setup, environment, config | Nothing | Project skeleton + libraries + .env config |
| **2** | Module 1: PPE Detection | Dataset (3,810 images) | Trained YOLOv8 model + PPEDetector class |
| **3** | Module 2: Face Recognition | Pretrained MTCNN + FaceNet | Face recognition pipeline + worker registration |
| **4** | Module 3+4: Email + Database | Gmail credentials + PostgreSQL | Email alerts + 4 DB tables + CRUD |
| **5** | Module 5: API + Integration + Testing | All modules | Flask API (9 endpoints) + Main loop + Tests |

---

# Technical Stack Summary

| Component | Technology | Version |
|-----------|-----------|---------|
| PPE Detection | YOLOv8 (Ultralytics) | Latest |
| Face Detection | MTCNN | 0.1.1 |
| Face Recognition | FaceNet (InceptionResnetV1) | pretrained vggface2 |
| Backend | Flask | 2.3.0 |
| Database | PostgreSQL + SQLAlchemy | 13+ / 2.0.0 |
| Email | SMTP (Gmail, TLS) | Port 587 |
| Computer Vision | OpenCV | 4.8.0 |
| Deep Learning | PyTorch | 2.0.0 |
| Testing | pytest | 7.4.0 |

---

*Document generated for: Workplace Safety and Access Control Using YOLO PPE and Face Detection*
*All data sourced from project documentation files*
