
# Workplace Safety and Access Control Using YOLO PPE and Face Detection

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technical Stack](#technical-stack)
4. [Dataset Requirements](#dataset-requirements)
5. [Module 1: PPE Detection](#module-1-ppe-detection)
6. [Module 2: Face Recognition & Worker Identification](#module-2-face-recognition--worker-identification)
7. [Module 3: Email Notification System](#module-3-email-notification-system)
8. [Module 4: Database Management](#module-4-database-management)
9. [Complete Implementation Guide](#complete-implementation-guide)
10. [Deployment Guide](#deployment-guide)
11. [API Endpoints](#api-endpoints)
12. [Testing & Validation](#testing--validation)

---

## Project Overview

### Objectives
- **Real-time PPE Detection**: Identify if workers are wearing:
  - Safety Helmet
  - Safety Gloves
  - Safety Shoes
  - Protection Glasses
  - Safety Vest

- **Worker Identification**: Use face recognition to identify specific workers
- **Automated Alerts**: Send email notifications to workers not wearing required PPE
- **Compliance Tracking**: Maintain database of safety violations
- **Historical Analysis**: Track safety compliance over time

### Key Features
✓ Real-time video stream processing
✓ Multi-class PPE detection using YOLOv8
✓ Face recognition for worker identification
✓ Automated email notifications
✓ Database logging of violations
✓ Dashboard for safety monitoring
✓ Compliance reports generation
✓ Worker management system

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     INPUT SOURCES                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Webcam      │  │  IP Camera   │  │  Video File  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│            FRAME PREPROCESSING & ENHANCEMENT                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Resize | Color Conversion | Normalization              │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   ┌─────────────┐   ┌──────────────┐   ┌──────────────┐
   │ PPE Detection│   │ Face Detection│  │Face Recognition│
   │  (YOLOv8)   │   │  (MTCNN/SSD) │  │ (FaceNet/ArcFace)
   │  Classes:   │   │              │  │                │
   │  - Helmet   │   │ Detect faces │  │ Identify worker│
   │  - Gloves   │   │ in frame     │  │ ID from DB     │
   │  - Shoes    │   │              │  │                │
   │  - Glasses  │   │              │  │                │
   │  - Vest     │   │              │  │                │
   └─────┬───────┘   └──────┬───────┘  └────────┬───────┘
         │                  │                   │
         └──────────────────┼───────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│         COMPLIANCE VERIFICATION ENGINE                           │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ 1. Match detected PPE with detected face                 │   │
│ │ 2. Verify all required PPE present for worker            │   │
│ │ 3. Generate violation flag if PPE missing                │   │
│ │ 4. Retrieve worker details from database                 │   │
│ └──────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
   │ Compliant    │  │ Non-Compliant│  │ Email        │
   │ Workers      │  │ Workers      │  │ Notification │
   │ ✓ Log to DB  │  │ ✗ Log to DB  │  │ System       │
   └──────────────┘  └──────┬───────┘  └──────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  OUTPUT & STORAGE                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Database    │  │  Email Alert │  │  Dashboard   │          │
│  │  (PostgreSQL)│  │  (SMTP)      │  │  (Web UI)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Module Breakdown

```
WORKSPACE_SAFETY_SYSTEM/
├── ppe_detection/
│   ├── yolo_model.py          # YOLOv8 PPE detection
│   ├── ppe_classes.py         # PPE class definitions
│   └── inference.py           # Real-time inference
│
├── face_recognition/
│   ├── face_detection.py      # MTCNN/SSD face detection
│   ├── face_embedding.py      # FaceNet embeddings
│   ├── worker_identification.py # Match face to worker
│   └── face_database.py       # Store face encodings
│
├── worker_management/
│   ├── models.py              # Database models
│   ├── db_operations.py       # CRUD operations
│   └── worker_registry.py     # Worker database
│
├── notification_system/
│   ├── email_sender.py        # SMTP email service
│   ├── email_templates.py     # Email templates
│   └── notification_queue.py  # Queue management
│
├── monitoring/
│   ├── video_processor.py     # Main processing loop
│   ├── compliance_checker.py  # Verify PPE status
│   └── violation_logger.py    # Log violations
│
├── api/
│   ├── app.py                 # Flask/FastAPI app
│   ├── routes.py              # API endpoints
│   └── middleware.py          # Authentication
│
├── web_dashboard/
│   ├── templates/             # HTML templates
│   ├── static/                # CSS/JS files
│   └── routes.py              # Dashboard routes
│
├── config/
│   ├── settings.py            # Configuration
│   ├── database.py            # DB connection
│   └── email_config.py        # Email settings
│
├── utils/
│   ├── logger.py              # Logging
│   ├── helpers.py             # Helper functions
│   └── validators.py          # Input validation
│
└── tests/
    ├── test_ppe_detection.py
    ├── test_face_recognition.py
    └── test_email_system.py
```

---

## Technical Stack

### Core Technologies

| Component | Technology | Version |
|-----------|-----------|---------|
| **PPE Detection** | YOLOv8 | Latest |
| **Face Detection** | MTCNN / RetinaFace | Latest |
| **Face Recognition** | FaceNet / ArcFace | Latest |
| **Backend Framework** | Flask/FastAPI | 3.8+ |
| **Database** | PostgreSQL | 13+ |
| **Email Service** | SMTP (Gmail/Office365) | - |
| **Frontend** | React/HTML5/CSS3 | Latest |
| **Containerization** | Docker | Latest |
| **Message Queue** | Celery + Redis | Latest |

### Python Libraries

```
# Core ML/CV Libraries
torch==2.0.0
torchvision==0.15.0
opencv-python==4.8.0
ultralytics==8.0.0          # YOLOv8
mtcnn==0.1.1                # Face detection
face-recognition==1.3.5     # Face recognition
facenet-pytorch==2.2.9      # FaceNet embeddings

# Web Framework
Flask==2.3.0
Flask-CORS==4.0.0
FastAPI==0.104.0
uvicorn==0.24.0

# Database
SQLAlchemy==2.0.0
psycopg2-binary==2.9.0
alembic==1.12.0             # Database migrations

# Email & Notifications
smtplib==3.13.0
python-dotenv==1.0.0
celery==5.3.0
redis==5.0.0

# Data Processing
numpy==1.24.0
pandas==2.0.0
Pillow==10.0.0

# Utilities
requests==2.31.0
pydantic==2.0.0
python-dateutil==2.8.2

# Monitoring & Logging
structlog==23.1.0
prometheus-client==0.17.0

# Testing
pytest==7.4.0
pytest-cov==4.1.0
```

---

## Dataset Requirements

### 1. PPE Detection Dataset

#### Data Collection Strategy

```
DATASET_STRUCTURE/
├── helmet/
│   ├── train/
│   │   ├── images/          (70% of data)
│   │   └── labels/          (YOLO format)
│   ├── val/                 (15% of data)
│   └── test/                (15% of data)
│
├── gloves/
│   ├── train/
│   ├── val/
│   └── test/
│
├── shoes/
├── glasses/
└── vest/
```

#### Image Requirements for PPE Detection

| Class | Min Images | Image Size | Lighting Variations |
|-------|-----------|-----------|-------------------|
| Helmet | 1000 | 640x640 | Day, night, indoor, outdoor |
| Gloves | 800 | 640x640 | Different types, colors |
| Shoes | 800 | 640x640 | Different brands, styles |
| Glasses | 600 | 640x640 | Various types, tints |
| Vest | 900 | 640x640 | Different colors |
| **Total** | **4100** | | |

#### Data Sources

```
1. Open Datasets
   - Safety Helmet Detection Dataset (Kaggle)
   - Hard Hat Detection (GitHub)

2. Custom Collection
   - Company premises footage
   - Staged construction site videos
   - Diverse worker demographics

3. Synthetic Data
   - Generated using Blender
   - Data augmentation (rotation, blur, noise)
```

#### YOLO Format Labels

```
# Each image has corresponding .txt file
# Format: <class_id> <x_center> <y_center> <width> <height>
# Normalized coordinates (0-1)

Example: labels/image001.txt
0 0.5 0.4 0.3 0.2    # Helmet at center
1 0.2 0.8 0.1 0.15   # Gloves at bottom-left
2 0.85 0.9 0.15 0.15 # Shoes at bottom-right
3 0.6 0.3 0.08 0.12  # Glasses
4 0.5 0.5 0.4 0.3    # Vest covering body
```

### 2. Face Recognition Dataset

#### Face Database Structure

```
WORKER_FACES/
├── worker_001/
│   ├── image_001.jpg
│   ├── image_002.jpg
│   ├── image_003.jpg
│   └── ... (10-20 images)
│
├── worker_002/
│   ├── image_001.jpg
│   └── ...
│
└── worker_n/
    └── ...
```

#### Face Image Requirements

| Requirement | Specification |
|------------|--------------|
| **Images per worker** | 10-20 (minimum) |
| **Image Resolution** | 224x224 or higher |
| **Face Size in Image** | At least 80x80 pixels |
| **Angle Variation** | Front, 30°, 45° views |
| **Lighting** | Natural, artificial, side-lit |
| **Background** | Plain or office/factory environment |
| **Expression** | Neutral, slight smile |
| **Occlusion** | Minimal (can have PPE like helmet) |

---

## Module 1: PPE Detection

### YOLOv8 Training Guide

#### Step 1: Environment Setup

```python
# install_requirements.py
import subprocess
import sys

def install_dependencies():
    """Install all required packages"""
    packages = [
        'ultralytics==8.0.0',
        'opencv-python==4.8.0',
        'torch==2.0.0',
        'torchvision==0.15.0',
    ]

    for package in packages:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

if __name__ == '__main__':
    install_dependencies()
```

#### Step 2: Prepare Dataset in YOLO Format

```python
# prepare_dataset.py
import os
import shutil
from pathlib import Path
import yaml

class YOLODatasetPreparer:
    """Prepare dataset for YOLO training"""

    def __init__(self, root_dir, train_ratio=0.7, val_ratio=0.15):
        self.root_dir = Path(root_dir)
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio

    def create_dataset_structure(self):
        """Create YOLO dataset structure"""
        dataset_dir = self.root_dir / 'dataset'

        for split in ['train', 'val', 'test']:
            (dataset_dir / split / 'images').mkdir(parents=True, exist_ok=True)
            (dataset_dir / split / 'labels').mkdir(parents=True, exist_ok=True)

    def create_yaml_config(self, output_path='data.yaml'):
        """Create dataset YAML configuration"""
        data_config = {
            'path': str(self.root_dir / 'dataset'),
            'train': 'train/images',
            'val': 'val/images',
            'test': 'test/images',
            'nc': 5,  # Number of classes
            'names': {
                0: 'helmet',
                1: 'gloves',
                2: 'shoes',
                3: 'glasses',
                4: 'vest'
            }
        }

        with open(output_path, 'w') as f:
            yaml.dump(data_config, f)

        return data_config
```

#### Step 3: Train YOLOv8 Model

```python
# train_ppe_model.py
from ultralytics import YOLO
import torch

class PPEModelTrainer:
    """Train YOLOv8 for PPE detection"""

    def __init__(self, model_size='m'):
        """
        Initialize trainer

        Args:
            model_size: 'n' (nano), 's' (small), 'm' (medium), 'l' (large)
        """
        self.model = YOLO(f'yolov8{model_size}.pt')  # Pre-trained model
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def train(self, data_yaml, epochs=100, batch_size=16, img_size=640):
        """
        Train YOLOv8 model

        Args:
            data_yaml: Path to dataset YAML file
            epochs: Number of training epochs
            batch_size: Batch size for training
            img_size: Input image size
        """

        results = self.model.train(
            data=data_yaml,
            epochs=epochs,
            imgsz=img_size,
            batch=batch_size,
            device=self.device,
            patience=20,  # Early stopping patience
            save=True,
            save_period=5,

            # Augmentation parameters
            hsv_h=0.015,
            hsv_s=0.7,
            hsv_v=0.4,
            degrees=10,
            translate=0.1,
            scale=0.5,
            flipud=0.5,
            fliplr=0.5,
            mosaic=1.0,

            # Training parameters
            lr0=0.01,
            lrf=0.01,
            momentum=0.937,
            weight_decay=0.0005,

            # Validation
            val=True,
            save_conf=True,

            # Callbacks
            verbose=True,
            project='runs/detect',
            name='ppe_detection'
        )

        return results

    def validate(self, model_path, data_yaml):
        """Validate trained model"""
        model = YOLO(model_path)
        metrics = model.val(data=data_yaml)
        return metrics

    def test(self, model_path, test_images_dir):
        """Test on test set"""
        model = YOLO(model_path)
        results = model.predict(source=test_images_dir, conf=0.5)
        return results

# Usage
if __name__ == '__main__':
    trainer = PPEModelTrainer(model_size='m')

    # Train model
    trainer.train(
        data_yaml='data.yaml',
        epochs=100,
        batch_size=32,
        img_size=640
    )
```

#### Step 4: Real-time PPE Detection

```python
# ppe_detection.py
from ultralytics import YOLO
import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class PPEDetection:
    """PPE Detection result"""
    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    x_center: float
    y_center: float

class PPEDetector:
    """Real-time PPE Detection using YOLOv8"""

    # PPE Classes
    CLASS_NAMES = {
        0: 'helmet',
        1: 'gloves',
        2: 'shoes',
        3: 'glasses',
        4: 'vest'
    }

    REQUIRED_PPE = {
        'helmet', 'gloves', 'shoes', 'glasses', 'vest'
    }

    def __init__(self, model_path, confidence_threshold=0.5):
        """
        Initialize PPE Detector

        Args:
            model_path: Path to trained YOLOv8 model
            confidence_threshold: Minimum confidence for detection
        """
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold

    def detect_ppe(self, frame) -> List[PPEDetection]:
        """
        Detect PPE in frame

        Args:
            frame: Input image/frame (numpy array)

        Returns:
            List of PPEDetection objects
        """
        results = self.model(frame, verbose=False)[0]
        detections = []

        for detection in results.boxes:
            # Get bounding box
            x1, y1, x2, y2 = detection.xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # Get class and confidence
            class_id = int(detection.cls[0].cpu().numpy())
            confidence = float(detection.conf[0].cpu().numpy())

            # Skip low confidence detections
            if confidence < self.confidence_threshold:
                continue

            # Calculate center
            x_center = (x1 + x2) / 2
            y_center = (y1 + y2) / 2

            ppe_detection = PPEDetection(
                class_id=class_id,
                class_name=self.CLASS_NAMES.get(class_id, 'unknown'),
                confidence=confidence,
                bbox=(x1, y1, x2, y2),
                x_center=x_center,
                y_center=y_center
            )

            detections.append(ppe_detection)

        return detections

    def draw_detections(self, frame, detections: List[PPEDetection]):
        """
        Draw detected PPE on frame

        Args:
            frame: Input image
            detections: List of PPEDetection objects

        Returns:
            Frame with drawings
        """
        colors = {
            'helmet': (0, 255, 0),      # Green
            'gloves': (255, 0, 0),      # Blue
            'shoes': (0, 0, 255),       # Red
            'glasses': (255, 255, 0),   # Cyan
            'vest': (255, 0, 255)       # Magenta
        }

        for detection in detections:
            x1, y1, x2, y2 = detection.bbox
            class_name = detection.class_name
            confidence = detection.confidence

            color = colors.get(class_name, (255, 255, 255))

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            cv2.putText(
                frame, label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, color, 2
            )

        return frame

    def check_ppe_compliance(self, detections: List[PPEDetection]) -> Tuple[bool, set]:
        """
        Check if all required PPE is present

        Args:
            detections: List of PPEDetection objects

        Returns:
            (is_compliant, missing_ppe)
        """
        detected_ppe = {d.class_name for d in detections}
        missing_ppe = self.REQUIRED_PPE - detected_ppe
        is_compliant = len(missing_ppe) == 0

        return is_compliant, missing_ppe
```

---

## Module 2: Face Recognition & Worker Identification

### Face Detection and Recognition Pipeline

```python
# face_recognition_system.py
import cv2
import numpy as np
from mtcnn import MTCNN
from facenet_pytorch import InceptionResnetV1
import torch
from sklearn.metrics.pairwise import cosine_similarity
from dataclasses import dataclass
from typing import Optional, List, Tuple
import pickle
import os

@dataclass
class FaceDetection:
    """Face Detection result"""
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    confidence: float
    landmarks: dict  # facial landmarks

@dataclass
class WorkerIdentification:
    """Worker Identification result"""
    worker_id: str
    worker_name: str
    confidence: float
    email: str

class FaceRecognitionSystem:
    """Complete face detection and recognition system"""

    def __init__(self, embeddings_dir='worker_embeddings'):
        """
        Initialize Face Recognition System

        Args:
            embeddings_dir: Directory to store/load worker face embeddings
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Initialize face detector (MTCNN)
        self.face_detector = MTCNN(keep_all=False, device=self.device)

        # Initialize face embedding model (FaceNet)
        self.facenet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)

        # Load worker embeddings database
        self.embeddings_dir = embeddings_dir
        self.worker_embeddings = self._load_worker_embeddings()

        # Similarity threshold
        self.similarity_threshold = 0.6

    def _load_worker_embeddings(self) -> dict:
        """Load pre-computed worker face embeddings"""
        embeddings = {}

        if os.path.exists(self.embeddings_dir):
            for file in os.listdir(self.embeddings_dir):
                if file.endswith('.pkl'):
                    worker_id = file.replace('.pkl', '')
                    with open(os.path.join(self.embeddings_dir, file), 'rb') as f:
                        embeddings[worker_id] = pickle.load(f)

        return embeddings

    def detect_faces(self, frame) -> List[FaceDetection]:
        """
        Detect faces in frame using MTCNN

        Args:
            frame: Input image

        Returns:
            List of FaceDetection objects
        """
        # MTCNN expects PIL Image or numpy array
        # Convert BGR to RGB for face detection
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces
        boxes, probs, landmarks = self.face_detector.detect(
            frame_rgb,
            landmarks=True
        )

        detections = []

        if boxes is not None:
            for i, (box, prob, landmark) in enumerate(zip(boxes, probs, landmarks)):
                # Convert to int
                x, y, w, h = int(box[0]), int(box[1]), \
                             int(box[2] - box[0]), int(box[3] - box[1])

                detection = FaceDetection(
                    bbox=(x, y, w, h),
                    confidence=float(prob),
                    landmarks={
                        'left_eye': landmark[0],
                        'right_eye': landmark[1],
                        'nose': landmark[2],
                        'left_mouth': landmark[3],
                        'right_mouth': landmark[4]
                    }
                )

                detections.append(detection)

        return detections

    def extract_face_embedding(self, frame, face_detection: FaceDetection):
        """
        Extract face embedding from detected face

        Args:
            frame: Input image
            face_detection: FaceDetection object

        Returns:
            Face embedding vector (512-dimensional)
        """
        x, y, w, h = face_detection.bbox

        # Extract face region
        face_roi = frame[y:y+h, x:x+w]

        # Resize to 160x160 (required by FaceNet)
        face_roi = cv2.resize(face_roi, (160, 160))

        # Normalize
        face_roi = face_roi.astype(np.float32) / 255.0

        # Convert to tensor
        face_tensor = torch.from_numpy(face_roi).permute(2, 0, 1).unsqueeze(0)
        face_tensor = face_tensor.to(self.device)

        # Extract embedding
        with torch.no_grad():
            embedding = self.facenet(face_tensor)

        return embedding.cpu().numpy().flatten()

    def identify_worker(self, embedding) -> Optional[WorkerIdentification]:
        """
        Identify worker from face embedding

        Args:
            embedding: Face embedding vector

        Returns:
            WorkerIdentification object or None
        """
        if not self.worker_embeddings:
            return None

        best_match = None
        best_score = 0

        for worker_id, stored_embedding in self.worker_embeddings.items():
            # Calculate cosine similarity
            similarity = cosine_similarity(
                [embedding],
                [stored_embedding['embedding']]
            )[0][0]

            if similarity > best_score:
                best_score = similarity
                best_match = worker_id

        # Check if confidence meets threshold
        if best_score >= self.similarity_threshold:
            worker_info = self.worker_embeddings[best_match]['info']

            return WorkerIdentification(
                worker_id=best_match,
                worker_name=worker_info['name'],
                confidence=float(best_score),
                email=worker_info['email']
            )

        return None

    def register_worker(self, worker_id: str, worker_name: str,
                       worker_email: str, images_list: list):
        """
        Register new worker in system

        Args:
            worker_id: Unique worker ID
            worker_name: Worker's name
            worker_email: Worker's email
            images_list: List of face images (numpy arrays)
        """
        embeddings = []

        for image in images_list:
            # Detect face
            face_detections = self.detect_faces(image)

            if face_detections:
                # Extract embedding
                embedding = self.extract_face_embedding(image, face_detections[0])
                embeddings.append(embedding)

        if embeddings:
            # Average embedding from multiple images
            avg_embedding = np.mean(embeddings, axis=0)

            # Save to file
            worker_data = {
                'embedding': avg_embedding,
                'info': {
                    'name': worker_name,
                    'email': worker_email,
                    'id': worker_id
                }
            }

            os.makedirs(self.embeddings_dir, exist_ok=True)
            with open(f'{self.embeddings_dir}/{worker_id}.pkl', 'wb') as f:
                pickle.dump(worker_data, f)

            # Update in-memory database
            self.worker_embeddings[worker_id] = worker_data

            return True

        return False

    def draw_face_detections(self, frame, detections: List[FaceDetection],
                            identifications: dict = None):
        """
        Draw face detections and identifications on frame

        Args:
            frame: Input image
            detections: List of FaceDetection objects
            identifications: Dict mapping detection index to WorkerIdentification

        Returns:
            Frame with drawings
        """
        for idx, detection in enumerate(detections):
            x, y, w, h = detection.bbox

            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Draw label
            label = f"Face: {detection.confidence:.2f}"
            if identifications and idx in identifications:
                worker = identifications[idx]
                label = f"{worker.worker_name} ({worker.confidence:.2f})"

            cv2.putText(
                frame, label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 255, 0), 2
            )

        return frame
```

---

## Module 3: Email Notification System

### Email Sending and Template System

```python
# email_notification_system.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
import os
from typing import List, Optional
from dataclasses import dataclass
import logging

@dataclass
class ViolationRecord:
    """Safety violation record"""
    worker_id: str
    worker_name: str
    worker_email: str
    timestamp: datetime
    missing_ppe: set
    violation_count: int
    image_path: Optional[str] = None

class EmailNotificationSystem:
    """Email notification system for safety violations"""

    def __init__(self, sender_email: str, sender_password: str,
                 smtp_server: str = 'smtp.gmail.com', smtp_port: int = 587):
        """
        Initialize Email Notification System

        Args:
            sender_email: Sender's email address
            sender_password: Sender's email password/app password
            smtp_server: SMTP server address
            smtp_port: SMTP port
        """
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

        self.logger = logging.getLogger(__name__)

    def create_violation_email(self, violation: ViolationRecord) -> MIMEMultipart:
        """
        Create violation email

        Args:
            violation: ViolationRecord object

        Returns:
            MIMEMultipart email object
        """
        message = MIMEMultipart('alternative')
        message['Subject'] = f"⚠️ Safety Alert: Missing PPE Detection - {violation.worker_name}"
        message['From'] = self.sender_email
        message['To'] = violation.worker_email

        # Create HTML content
        html_content = self._get_html_template(violation)

        # Attach HTML
        html_part = MIMEText(html_content, 'html')
        message.attach(html_part)

        # Attach image if available
        if violation.image_path and os.path.exists(violation.image_path):
            try:
                with open(violation.image_path, 'rb') as attachment:
                    image_data = attachment.read()
                    image_part = MIMEImage(image_data)
                    image_part.add_header('Content-ID', '<violation_image>')
                    image_part.add_header('Content-Disposition', 'inline')
                    message.attach(image_part)
            except Exception as e:
                self.logger.error(f"Failed to attach image: {e}")

        return message

    def _get_html_template(self, violation: ViolationRecord) -> str:
        """
        Get HTML email template

        Args:
            violation: ViolationRecord object

        Returns:
            HTML content
        """
        missing_ppe_list = '<br>'.join(
            [f"• {ppe.upper()}" for ppe in sorted(violation.missing_ppe)]
        )

        html = f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f5f5f5;
                        margin: 0;
                        padding: 0;
                    }}
                    .container {{
                        background-color: white;
                        margin: 20px auto;
                        padding: 20px;
                        border-radius: 8px;
                        max-width: 600px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        background-color: #d32f2f;
                        color: white;
                        padding: 20px;
                        border-radius: 8px 8px 0 0;
                        text-align: center;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 24px;
                    }}
                    .content {{
                        padding: 20px;
                    }}
                    .alert-box {{
                        background-color: #fff3cd;
                        border-left: 4px solid #ffc107;
                        padding: 15px;
                        margin: 15px 0;
                        border-radius: 4px;
                    }}
                    .violation-details {{
                        background-color: #f5f5f5;
                        padding: 15px;
                        border-radius: 4px;
                        margin: 15px 0;
                    }}
                    .ppe-list {{
                        margin: 10px 0;
                        line-height: 1.8;
                    }}
                    .timestamp {{
                        color: #666;
                        font-size: 12px;
                        margin: 10px 0;
                    }}
                    .action-button {{
                        background-color: #4CAF50;
                        color: white;
                        padding: 12px 30px;
                        text-decoration: none;
                        border-radius: 4px;
                        display: inline-block;
                        margin: 15px 0;
                    }}
                    .footer {{
                        background-color: #f5f5f5;
                        padding: 15px;
                        text-align: center;
                        font-size: 12px;
                        color: #666;
                        border-radius: 0 0 8px 8px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>⚠️ Safety Alert</h1>
                    </div>

                    <div class="content">
                        <p>Dear <strong>{violation.worker_name}</strong>,</p>

                        <p>This is an automated safety notification from the Workplace Safety
                        Monitoring System. A safety violation has been detected.</p>

                        <div class="alert-box">
                            <strong>Missing Personal Protective Equipment (PPE):</strong>
                            <div class="ppe-list">
                                {missing_ppe_list}
                            </div>
                        </div>

                        <div class="violation-details">
                            <h3>Violation Details:</h3>
                            <p><strong>Date & Time:</strong> {violation.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                            <p><strong>Worker ID:</strong> {violation.worker_id}</p>
                            <p><strong>Violation Count (Today):</strong> {violation.violation_count}</p>
                        </div>

                        <div style="margin: 20px 0;">
                            <p><strong>Action Required:</strong></p>
                            <p>Please ensure you are wearing all required Personal Protective Equipment
                            before continuing work. Missing PPE includes:</p>
                            <ul>
                                <li>Safety Helmet</li>
                                <li>Safety Gloves</li>
                                <li>Safety Shoes</li>
                                <li>Protection Glasses</li>
                                <li>Safety Vest</li>
                            </ul>
                        </div>

                        <a href="#" class="action-button">Acknowledge Alert</a>

                        <p style="color: #666; font-size: 12px; margin-top: 20px;">
                            <strong>Note:</strong> This is an automated message. Please contact your Safety
                            Manager if you believe this notification was sent in error.
                        </p>
                    </div>

                    <div class="footer">
                        <p>Workplace Safety Monitoring System</p>
                        <p>© 2024 Safety Department. All rights reserved.</p>
                    </div>
                </div>
            </body>
        </html>
        """

        return html

    def send_email(self, violation: ViolationRecord) -> bool:
        """
        Send violation email to worker

        Args:
            violation: ViolationRecord object

        Returns:
            True if email sent successfully
        """
        try:
            # Create email
            message = self.create_violation_email(violation)

            # Connect to SMTP server
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            self.logger.info(f"Email sent to {violation.worker_email}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False

    def send_daily_report_email(self, recipient_email: str,
                               violations: List[ViolationRecord]) -> bool:
        """
        Send daily safety report

        Args:
            recipient_email: Manager's email
            violations: List of violations for the day

        Returns:
            True if email sent successfully
        """
        try:
            message = MIMEMultipart('alternative')
            message['Subject'] = f"Daily Safety Report - {datetime.now().strftime('%Y-%m-%d')}"
            message['From'] = self.sender_email
            message['To'] = recipient_email

            # Create report content
            html_content = self._get_daily_report_template(violations)

            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            self.logger.info(f"Daily report sent to {recipient_email}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send daily report: {e}")
            return False

    def _get_daily_report_template(self, violations: List[ViolationRecord]) -> str:
        """Generate daily report HTML"""

        violation_rows = ""
        for v in violations:
            missing_ppe = ", ".join(sorted(v.missing_ppe))
            violation_rows += f"""
            <tr>
                <td>{v.worker_name}</td>
                <td>{v.worker_id}</td>
                <td>{v.timestamp.strftime('%H:%M:%S')}</td>
                <td>{missing_ppe}</td>
                <td>{v.violation_count}</td>
            </tr>
            """

        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                    th {{ background-color: #4CAF50; color: white; }}
                    tr:nth-child(even) {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <h2>Daily Safety Report</h2>
                <p>Report Date: {datetime.now().strftime('%Y-%m-%d')}</p>
                <p>Total Violations: {len(violations)}</p>

                <table>
                    <tr>
                        <th>Worker Name</th>
                        <th>Worker ID</th>
                        <th>Time</th>
                        <th>Missing PPE</th>
                        <th>Count</th>
                    </tr>
                    {violation_rows}
                </table>

                <p>This report was automatically generated by the Safety Monitoring System.</p>
            </body>
        </html>
        """

        return html

# Configuration for Gmail
"""
Gmail Setup Instructions:

1. Enable 2-Factor Authentication:
   - Go to myaccount.google.com
   - Click "Security"
   - Enable "2-Step Verification"

2. Generate App Password:
   - Go to myaccount.google.com
   - Click "Security"
   - Find "App passwords"
   - Select "Mail" and "Windows Computer"
   - Google will generate 16-character password
   - Use this as sender_password

3. Environment Variables:
   SENDER_EMAIL="your.email@gmail.com"
   SENDER_PASSWORD="xxxx xxxx xxxx xxxx"
"""
```

---

## Module 4: Database Management

### Database Schema and Operations

```python
# models.py - SQLAlchemy Models
from sqlalchemy import Column, String, DateTime, Integer, Float, Boolean, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class Worker(Base):
    """Worker information table"""
    __tablename__ = 'workers'

    worker_id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    department = Column(String(100))
    position = Column(String(100))
    is_active = Column(Boolean, default=True)
    date_registered = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime)

    # Indices
    __table_args__ = (
        Index('idx_email', 'email'),
        Index('idx_department', 'department'),
    )

class ViolationLog(Base):
    """Violation logging table"""
    __tablename__ = 'violation_logs'

    violation_id = Column(Integer, primary_key=True, autoincrement=True)
    worker_id = Column(String(50), ForeignKey('workers.worker_id'))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    missing_ppe = Column(Text)  # JSON string of missing PPE
    image_path = Column(String(255))
    email_sent = Column(Boolean, default=False)
    email_sent_time = Column(DateTime)
    severity = Column(Enum(SeverityLevel), default='medium')

    # Indices
    __table_args__ = (
        Index('idx_worker_timestamp', 'worker_id', 'timestamp'),
        Index('idx_timestamp', 'timestamp'),
    )

class ComplianceReport(Base):
    """Daily compliance report"""
    __tablename__ = 'compliance_reports'

    report_id = Column(Integer, primary_key=True, autoincrement=True)
    report_date = Column(DateTime, index=True)
    total_violations = Column(Integer)
    total_workers_checked = Column(Integer)
    compliance_rate = Column(Float)  # Percentage
    critical_violations = Column(Integer)
    medium_violations = Column(Integer)
    low_violations = Column(Integer)

class WorkerFaceEmbedding(Base):
    """Store face embeddings for each worker"""
    __tablename__ = 'worker_face_embeddings'

    embedding_id = Column(Integer, primary_key=True, autoincrement=True)
    worker_id = Column(String(50), ForeignKey('workers.worker_id'), index=True)
    embedding_vector = Column(Text)  # Serialized numpy array
    image_path = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

# Database operations
class DatabaseOperations:
    """Database CRUD operations"""

    def __init__(self, database_url):
        """Initialize database connection"""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)

        # Create all tables
        Base.metadata.create_all(self.engine)

    def add_worker(self, worker_id: str, name: str, email: str,
                   phone: str = None, department: str = None, position: str = None) -> bool:
        """Add new worker"""
        try:
            session = self.Session()
            worker = Worker(
                worker_id=worker_id,
                name=name,
                email=email,
                phone=phone,
                department=department,
                position=position
            )
            session.add(worker)
            session.commit()
            session.close()
            return True
        except Exception as e:
            print(f"Error adding worker: {e}")
            return False

    def log_violation(self, worker_id: str, missing_ppe: set,
                     image_path: str = None, severity: str = 'medium') -> bool:
        """Log PPE violation"""
        try:
            session = self.Session()

            import json
            violation = ViolationLog(
                worker_id=worker_id,
                missing_ppe=json.dumps(list(missing_ppe)),
                image_path=image_path,
                severity=severity
            )

            session.add(violation)
            session.commit()
            session.close()
            return True
        except Exception as e:
            print(f"Error logging violation: {e}")
            return False

    def get_worker_by_id(self, worker_id: str):
        """Retrieve worker information"""
        session = self.Session()
        worker = session.query(Worker).filter_by(worker_id=worker_id).first()
        session.close()
        return worker

    def get_violations_today(self, worker_id: str = None):
        """Get violations from today"""
        from datetime import date
        from sqlalchemy import and_

        session = self.Session()
        today = date.today()

        query = session.query(ViolationLog).filter(
            and_(
                ViolationLog.timestamp >= datetime.combine(today, datetime.min.time()),
                ViolationLog.timestamp <= datetime.combine(today, datetime.max.time())
            )
        )

        if worker_id:
            query = query.filter_by(worker_id=worker_id)

        violations = query.all()
        session.close()
        return violations

    def update_email_sent(self, violation_id: int) -> bool:
        """Mark email as sent"""
        try:
            session = self.Session()
            violation = session.query(ViolationLog).filter_by(violation_id=violation_id).first()

            if violation:
                violation.email_sent = True
                violation.email_sent_time = datetime.utcnow()
                session.commit()
                session.close()
                return True

            session.close()
            return False
        except Exception as e:
            print(f"Error updating email sent: {e}")
            return False
```

---

## Complete Implementation Guide

### Step 1: Project Setup

```bash
# Create project directory
mkdir workplace_safety_system
cd workplace_safety_system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create directory structure
mkdir -p {ppe_detection,face_recognition,worker_management,notification_system,monitoring,api,web_dashboard,config,utils,tests,models,datasets}

# Create requirements.txt
cat > requirements.txt << 'EOF'
# Core ML/CV
torch==2.0.0
torchvision==0.15.0
ultralytics==8.0.0
opencv-python==4.8.0
mtcnn==0.1.1
facenet-pytorch==2.2.9
numpy==1.24.0
Pillow==10.0.0

# Database
SQLAlchemy==2.0.0
psycopg2-binary==2.9.0
alembic==1.12.0

# Web Framework
Flask==2.3.0
Flask-CORS==4.0.0
python-dotenv==1.0.0

# Email
python-smtplib==3.13.0

# Task Queue
celery==5.3.0
redis==5.0.0

# Utilities
requests==2.31.0
pydantic==2.0.0

# Logging
structlog==23.1.0

# Testing
pytest==7.4.0
EOF

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configuration File

```python
# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://username:password@localhost:5432/safety_db'
)

# Email Configuration
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))

# Model Paths
PPE_MODEL_PATH = os.getenv('PPE_MODEL_PATH', 'models/ppe_detection_best.pt')
FACE_EMBEDDING_DIR = os.getenv('FACE_EMBEDDING_DIR', 'models/face_embeddings')

# Camera/Video Settings
CAMERA_ID = int(os.getenv('CAMERA_ID', 0))
VIDEO_FPS = int(os.getenv('VIDEO_FPS', 30))
FRAME_WIDTH = int(os.getenv('FRAME_WIDTH', 1280))
FRAME_HEIGHT = int(os.getenv('FRAME_HEIGHT', 720))

# Detection Settings
PPE_CONFIDENCE_THRESHOLD = float(os.getenv('PPE_CONFIDENCE_THRESHOLD', 0.5))
FACE_CONFIDENCE_THRESHOLD = float(os.getenv('FACE_CONFIDENCE_THRESHOLD', 0.6))
SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', 0.6))

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/safety_system.log')

# Create .env file template
ENV_TEMPLATE = """
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/safety_db

# Email
SENDER_EMAIL=your.email@gmail.com
SENDER_PASSWORD=your_app_password_16_chars

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
"""
```

### Step 3: Main Processing Loop

```python
# monitoring/video_processor.py
import cv2
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import json

from ppe_detection.ppe_detection import PPEDetector
from face_recognition.face_recognition_system import FaceRecognitionSystem
from worker_management.models import DatabaseOperations
from notification_system.email_notification_system import EmailNotificationSystem, ViolationRecord
from config.settings import *

class WorkplaceSafetyMonitor:
    """Main monitoring system"""

    def __init__(self, db_url, email_config):
        """Initialize monitoring system"""
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.ppe_detector = PPEDetector(PPE_MODEL_PATH, PPE_CONFIDENCE_THRESHOLD)
        self.face_recognition = FaceRecognitionSystem(FACE_EMBEDDING_DIR)
        self.database = DatabaseOperations(db_url)
        self.email_service = EmailNotificationSystem(
            email_config['sender_email'],
            email_config['sender_password']
        )

        # Track violations per worker per day
        self.daily_violations = defaultdict(int)
        self.last_email_sent = {}
        self.email_cooldown = timedelta(minutes=15)  # Don't spam emails

    def process_frame(self, frame):
        """
        Process single frame

        Args:
            frame: Input image frame

        Returns:
            Processed frame with annotations
        """
        try:
            # Detect PPE
            ppe_detections = self.ppe_detector.detect_ppe(frame)
            frame = self.ppe_detector.draw_detections(frame, ppe_detections)

            # Detect faces
            face_detections = self.face_recognition.detect_faces(frame)

            # Identify workers and check compliance
            worker_violations = {}

            for face_idx, face_detection in enumerate(face_detections):
                # Extract embedding
                embedding = self.face_recognition.extract_face_embedding(frame, face_detection)

                # Identify worker
                worker = self.face_recognition.identify_worker(embedding)

                if worker:
                    # Check PPE compliance for this worker
                    is_compliant, missing_ppe = self.ppe_detector.check_ppe_compliance(ppe_detections)

                    if not is_compliant:
                        worker_violations[worker.worker_id] = {
                            'worker': worker,
                            'missing_ppe': missing_ppe
                        }

                        # Log and send notification
                        self._handle_violation(worker, missing_ppe, frame)

                    # Draw worker info
                    x, y, w, h = face_detection.bbox
                    label = f"{worker.worker_name} - Compliant: {is_compliant}"
                    color = (0, 255, 0) if is_compliant else (0, 0, 255)
                    cv2.putText(frame, label, (x, y - 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Draw frame timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cv2.putText(frame, f"Time: {timestamp}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            return frame

        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")
            return frame

    def _handle_violation(self, worker, missing_ppe, frame):
        """Handle PPE violation"""
        try:
            worker_id = worker.worker_id

            # Increment violation count
            self.daily_violations[worker_id] += 1

            # Save violation image
            image_filename = f"violations/{worker_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            os.makedirs('violations', exist_ok=True)
            cv2.imwrite(image_filename, frame)

            # Log to database
            self.database.log_violation(worker_id, missing_ppe, image_filename)

            # Send email (with cooldown)
            if self._should_send_email(worker_id):
                violation_record = ViolationRecord(
                    worker_id=worker_id,
                    worker_name=worker.worker_name,
                    worker_email=worker.email,
                    timestamp=datetime.now(),
                    missing_ppe=missing_ppe,
                    violation_count=self.daily_violations[worker_id],
                    image_path=image_filename
                )

                if self.email_service.send_email(violation_record):
                    self.last_email_sent[worker_id] = datetime.now()
                    self.database.update_email_sent(violation_record.violation_id)

        except Exception as e:
            self.logger.error(f"Error handling violation: {e}")

    def _should_send_email(self, worker_id: str) -> bool:
        """Check if email should be sent (cooldown check)"""
        if worker_id not in self.last_email_sent:
            return True

        time_since_last_email = datetime.now() - self.last_email_sent[worker_id]
        return time_since_last_email >= self.email_cooldown

    def run_from_webcam(self):
        """Run monitoring from webcam"""
        cap = cv2.VideoCapture(CAMERA_ID)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, VIDEO_FPS)

        self.logger.info("Starting webcam monitoring...")

        try:
            while True:
                ret, frame = cap.read()

                if not ret:
                    break

                # Process frame
                processed_frame = self.process_frame(frame)

                # Display
                cv2.imshow('Workplace Safety Monitor', processed_frame)

                # Exit on 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            cap.release()
            cv2.destroyAllWindows()

    def run_from_video(self, video_path: str):
        """Run monitoring from video file"""
        cap = cv2.VideoCapture(video_path)

        self.logger.info(f"Processing video: {video_path}")

        try:
            while True:
                ret, frame = cap.read()

                if not ret:
                    break

                # Process frame
                processed_frame = self.process_frame(frame)

                # Display
                cv2.imshow('Workplace Safety Monitor', processed_frame)

                # Exit on 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            cap.release()
            cv2.destroyAllWindows()
```

---

## Module 5: Flask API Endpoints

```python
# api/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime, timedelta

from worker_management.models import DatabaseOperations
from monitoring.video_processor import WorkplaceSafetyMonitor
from config.settings import *

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize database
db = DatabaseOperations(DATABASE_URL)

# Initialize monitor
email_config = {
    'sender_email': SENDER_EMAIL,
    'sender_password': SENDER_PASSWORD
}
monitor = WorkplaceSafetyMonitor(DATABASE_URL, email_config)

# ========== WORKER MANAGEMENT ENDPOINTS ==========

@app.route('/api/workers', methods=['GET'])
def get_workers():
    """Get all workers"""
    try:
        session = db.Session()
        workers = session.query(Worker).all()
        session.close()

        return jsonify({
            'status': 'success',
            'data': [{
                'worker_id': w.worker_id,
                'name': w.name,
                'email': w.email,
                'department': w.department,
                'position': w.position
            } for w in workers]
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/workers', methods=['POST'])
def add_worker():
    """Add new worker"""
    try:
        data = request.json

        db.add_worker(
            worker_id=data['worker_id'],
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            department=data.get('department'),
            position=data.get('position')
        )

        return jsonify({
            'status': 'success',
            'message': 'Worker added successfully'
        }), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/workers/<worker_id>', methods=['GET'])
def get_worker(worker_id):
    """Get worker by ID"""
    try:
        worker = db.get_worker_by_id(worker_id)

        if not worker:
            return jsonify({'status': 'error', 'message': 'Worker not found'}), 404

        return jsonify({
            'status': 'success',
            'data': {
                'worker_id': worker.worker_id,
                'name': worker.name,
                'email': worker.email,
                'department': worker.department,
                'position': worker.position,
                'last_seen': worker.last_seen.isoformat() if worker.last_seen else None
            }
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ========== VIOLATION ENDPOINTS ==========

@app.route('/api/violations/today', methods=['GET'])
def get_today_violations():
    """Get violations from today"""
    try:
        worker_id = request.args.get('worker_id')
        violations = db.get_violations_today(worker_id)

        return jsonify({
            'status': 'success',
            'data': [{
                'violation_id': v.violation_id,
                'worker_id': v.worker_id,
                'timestamp': v.timestamp.isoformat(),
                'missing_ppe': json.loads(v.missing_ppe),
                'email_sent': v.email_sent
            } for v in violations]
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/violations/<int:violation_id>', methods=['GET'])
def get_violation(violation_id):
    """Get specific violation"""
    try:
        session = db.Session()
        violation = session.query(ViolationLog).filter_by(violation_id=violation_id).first()
        session.close()

        if not violation:
            return jsonify({'status': 'error', 'message': 'Violation not found'}), 404

        return jsonify({
            'status': 'success',
            'data': {
                'violation_id': violation.violation_id,
                'worker_id': violation.worker_id,
                'timestamp': violation.timestamp.isoformat(),
                'missing_ppe': json.loads(violation.missing_ppe),
                'image_path': violation.image_path,
                'email_sent': violation.email_sent
            }
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ========== STATISTICS ENDPOINTS ==========

@app.route('/api/statistics/daily', methods=['GET'])
def get_daily_stats():
    """Get daily statistics"""
    try:
        date = request.args.get('date')  # Format: YYYY-MM-DD

        if not date:
            date = datetime.now().strftime('%Y-%m-%d')

        violations = db.get_violations_today()

        stats = {
            'total_violations': len(violations),
            'unique_workers': len(set(v.worker_id for v in violations)),
            'missing_ppe_count': {}
        }

        for violation in violations:
            missing = json.loads(violation.missing_ppe)
            for ppe in missing:
                stats['missing_ppe_count'][ppe] = stats['missing_ppe_count'].get(ppe, 0) + 1

        return jsonify({
            'status': 'success',
            'date': date,
            'data': stats
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/statistics/worker/<worker_id>', methods=['GET'])
def get_worker_stats(worker_id):
    """Get worker statistics"""
    try:
        days = int(request.args.get('days', 7))

        session = db.Session()

        # Get violations in past N days
        start_date = datetime.now() - timedelta(days=days)
        violations = session.query(ViolationLog).filter(
            and_(
                ViolationLog.worker_id == worker_id,
                ViolationLog.timestamp >= start_date
            )
        ).all()

        # Calculate stats
        stats = {
            'total_violations': len(violations),
            'violations_by_date': {},
            'missing_ppe_summary': {}
        }

        for violation in violations:
            date_key = violation.timestamp.strftime('%Y-%m-%d')
            stats['violations_by_date'][date_key] = stats['violations_by_date'].get(date_key, 0) + 1

            missing = json.loads(violation.missing_ppe)
            for ppe in missing:
                stats['missing_ppe_summary'][ppe] = stats['missing_ppe_summary'].get(ppe, 0) + 1

        session.close()

        return jsonify({
            'status': 'success',
            'worker_id': worker_id,
            'period_days': days,
            'data': stats
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ========== FACE REGISTRATION ENDPOINTS ==========

@app.route('/api/workers/<worker_id>/register-face', methods=['POST'])
def register_worker_face(worker_id):
    """Register worker face"""
    try:
        if 'images' not in request.files:
            return jsonify({'status': 'error', 'message': 'No images provided'}), 400

        images = request.files.getlist('images')
        worker_name = request.form.get('name')
        worker_email = request.form.get('email')

        # Process images
        image_arrays = []
        for image_file in images:
            import io
            img_array = cv2.imdecode(
                np.frombuffer(image_file.read(), np.uint8),
                cv2.IMREAD_COLOR
            )
            image_arrays.append(img_array)

        # Register faces
        success = monitor.face_recognition.register_worker(
            worker_id, worker_name, worker_email, image_arrays
        )

        if success:
            return jsonify({
                'status': 'success',
                'message': 'Face registered successfully'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to register face'
            }), 400

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ========== HEALTH CHECK ==========

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

---

## Deployment Guide

### Option 1: Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs violations models

# Expose API port
EXPOSE 5000

# Run application
CMD ["python", "-m", "api.app"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: safety_user
      POSTGRES_PASSWORD: safety_password
      POSTGRES_DB: safety_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  safety_system:
    build: .
    environment:
      DATABASE_URL: postgresql://safety_user:safety_password@postgres:5432/safety_db
      SENDER_EMAIL: ${SENDER_EMAIL}
      SENDER_PASSWORD: ${SENDER_PASSWORD}
      PPE_MODEL_PATH: models/ppe_detection_best.pt
      FACE_EMBEDDING_DIR: models/face_embeddings
    volumes:
      - ./logs:/app/logs
      - ./violations:/app/violations
      - ./models:/app/models
    ports:
      - "5000:5000"
    depends_on:
      - postgres
      - redis
    command: python -m api.app

volumes:
  postgres_data:
```

### Option 2: Linux Systemd Service

```ini
# /etc/systemd/system/safety-monitor.service
[Unit]
Description=Workplace Safety Monitoring System
After=network.target postgresql.service

[Service]
Type=simple
User=safety
WorkingDirectory=/opt/safety_system
Environment="PATH=/opt/safety_system/venv/bin"
ExecStart=/opt/safety_system/venv/bin/python -m api.app
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/workers` | Get all workers |
| POST | `/api/workers` | Add new worker |
| GET | `/api/workers/<id>` | Get worker details |
| GET | `/api/violations/today` | Get today's violations |
| GET | `/api/violations/<id>` | Get violation details |
| GET | `/api/statistics/daily` | Get daily statistics |
| GET | `/api/statistics/worker/<id>` | Get worker statistics |
| POST | `/api/workers/<id>/register-face` | Register worker face |
| GET | `/api/health` | Health check |

---

## Testing & Validation

```python
# tests/test_ppe_detection.py
import pytest
import cv2
import numpy as np
from ppe_detection.ppe_detection import PPEDetector

@pytest.fixture
def ppe_detector():
    return PPEDetector('models/ppe_detection_best.pt')

def test_ppe_detection(ppe_detector):
    """Test PPE detection"""
    # Create dummy frame
    frame = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)

    # Detect PPE
    detections = ppe_detector.detect_ppe(frame)

    # Assert
    assert isinstance(detections, list)

def test_ppe_compliance(ppe_detector):
    """Test PPE compliance check"""
    # Dummy detections
    class DummyDetection:
        class_name = 'helmet'

    detections = [DummyDetection()]
    is_compliant, missing = ppe_detector.check_ppe_compliance(detections)

    assert not is_compliant
    assert len(missing) > 0
```

---

## Conclusion

This comprehensive documentation provides:
✅ Complete system architecture
✅ All required modules and code
✅ Database schema and operations
✅ API endpoints
✅ Email notification system
✅ Docker deployment
✅ Testing framework

**Next Steps:**
1. Set up PostgreSQL database
2. Train YOLOv8 model on your PPE dataset
3. Register worker faces in the system
4. Configure email credentials
5. Deploy using Docker or systemd
6. Access API and web dashboard

---

## Support & Troubleshooting

### Common Issues

**Issue: Model inference is slow**
- Solution: Use smaller model (yolov8n instead of yolov8x)
- Use GPU instead of CPU
- Optimize frame resolution

**Issue: Face recognition accuracy low**
- Solution: Register more images per worker (15-20)
- Ensure good lighting in training images
- Use diverse angles and expressions

**Issue: Emails not sending**
- Solution: Check Gmail app password generation
- Verify SMTP credentials
- Check firewall/proxy settings
- Enable "Less secure apps" if needed

---

**Created:** 2024
**Last Updated:** 2024
**Version:** 1.0
```
