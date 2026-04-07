# SafetyVision - Workplace PPE Detection System

A real-time **Personal Protective Equipment (PPE) detection system** that uses AI to monitor worker safety compliance. It detects 5 PPE items, identifies workers by face, and sends email alerts for violations.

---

## What This System Does

| Feature | Description |
|---------|-------------|
| **PPE Detection** | Detects Helmet, Gloves, Vest, Boots, Goggles using YOLOv8 |
| **Face Recognition** | Identifies registered workers using FaceNet |
| **Live Camera** | Real-time monitoring from webcam |
| **Image Analysis** | Upload and analyze single images |
| **Video Analysis** | Upload and analyze video files |
| **Worker Registration** | Register workers with name, email, and face capture |
| **Email Alerts** | Send violation emails via Gmail SMTP |

---

## Prerequisites

Before starting, make sure you have:

- **Python 3.10 or higher** - Download from [python.org](https://www.python.org/downloads/)
- **Webcam** (optional) - For live camera and face registration
- **Gmail Account** (optional) - For sending violation email alerts

---

## Setup Guide (Step by Step)

### Step 1: Extract the Project

Extract the zip file to any folder, for example:
```
C:\Users\YourName\Desktop\workers_Safety
```

### Step 2: Open Terminal

Open **Command Prompt** or **PowerShell** and navigate to the project folder:
```bash
cd C:\Users\YourName\Desktop\workers_Safety
```

### Step 3: Create Virtual Environment

```bash
python -m venv venv
```

### Step 4: Activate Virtual Environment

**Windows (Command Prompt):**
```bash
venv\Scripts\activate
```

**Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

You should see `(venv)` at the beginning of your terminal line.

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install PyTorch, OpenCV, YOLO, Flask, and other required libraries. This may take 5-10 minutes depending on your internet speed.

### Step 6: Configure Environment File

Copy the example environment file:
```bash
copy .env.example .env
```

Open `.env` in any text editor and update the email settings (optional - only needed for email alerts):
```
SENDER_EMAIL=your.email@gmail.com
SENDER_PASSWORD=your_app_password_here
```

> **How to get Gmail App Password:**
> 1. Go to [myaccount.google.com](https://myaccount.google.com)
> 2. Security > 2-Step Verification (turn ON if not already)
> 3. Search "App passwords" in Google Account settings
> 4. Create a new app password for "Mail"
> 5. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)
> 6. Paste it as `SENDER_PASSWORD` in `.env`

### Step 7: Run the Application

```bash
python web_app.py
```

You should see:
```
==================================================
  PPE Detection & Face Recognition Web UI
  http://localhost:5000
  Face Recognition: ACTIVE
  Email System:     ACTIVE
==================================================
```

### Step 8: Open in Browser

Open your web browser and go to:
```
http://localhost:5000
```

---

## How to Use

### 1. Image Detection
- Click **Image Detection** in the sidebar
- Upload a JPG/PNG image of a worker
- Click **Analyze Image**
- See PPE detection results on the right

### 2. Video Detection
- Click **Video Detection** in the sidebar
- Upload an MP4/AVI video file
- Click **Analyze Video**
- View frame-by-frame analysis results

### 3. Live Camera
- Click **Live Camera** in the sidebar
- Click **Start Camera**
- The system shows real-time PPE detection and face identification
- If a registered worker has missing PPE, click **Send Email** to alert them
- Unregistered faces show "Please register face" message

### 4. Register Workers
- Click **Register Workers** in the sidebar
- Enter worker's **Full Name** and **Email Address**
- Click **Open Camera** to start the webcam
- Click **Capture Photo** 5-10 times from different angles
- Click **Register Worker** to save
- The worker can now be identified in Live Camera mode

---

## Project Structure

```
workers_Safety/
|
|-- web_app.py                  # Main application (run this)
|-- main.py                     # CLI mode (alternative entry point)
|-- requirements.txt            # Python dependencies
|-- .env                        # Configuration (email, thresholds)
|
|-- templates/
|   |-- index.html              # Web page template
|
|-- static/
|   |-- css/style.css           # Styles
|   |-- js/app.js               # Frontend JavaScript
|
|-- models/
|   |-- best.pt                 # Trained YOLOv8 PPE detection model
|
|-- ppe_detection/              # PPE detection module (YOLOv8)
|   |-- inference.py            # Detection logic
|   |-- ppe_classes.py          # PPE class definitions
|   |-- yolo_model.py           # Model training script
|
|-- face_recognition/           # Face recognition module (FaceNet)
|   |-- face_detection.py       # MTCNN face detector
|   |-- face_embedding.py       # FaceNet embedding extractor
|   |-- face_database.py        # Worker embedding storage (.pkl)
|   |-- worker_identification.py# Main orchestrator
|
|-- worker_management/          # Worker database operations
|   |-- models.py               # SQLAlchemy ORM models
|   |-- db_operations.py        # CRUD operations
|   |-- worker_registry.py      # Worker registration API
|
|-- notification_system/        # Email notification module
|   |-- email_sender.py         # SMTP email sender
|   |-- email_templates.py      # HTML email templates
|   |-- notification_queue.py   # Violation queue
|
|-- monitoring/                 # Real-time monitoring
|   |-- video_processor.py      # Main processing pipeline
|   |-- compliance_checker.py   # PPE compliance validation
|   |-- violation_logger.py     # Violation logging
|
|-- config/                     # Configuration
|   |-- settings.py             # Environment variable loader
|   |-- database.py             # SQLAlchemy database setup
|   |-- email_config.py         # Email configuration
|
|-- api/                        # REST API endpoints
|   |-- app.py                  # Flask API factory
|   |-- routes.py               # API routes
|   |-- middleware.py            # Error handlers
|
|-- worker_embeddings/          # Stored face data (.pkl files)
|-- violations/                 # Violation screenshots
|-- logs/                       # Application logs
```

---

## Technologies Used

| Technology | Purpose |
|-----------|---------|
| **Python 3.10+** | Programming language |
| **YOLOv8** (Ultralytics) | PPE object detection |
| **FaceNet** (facenet-pytorch) | Face embedding extraction |
| **MTCNN** | Face detection |
| **Flask** | Web framework |
| **OpenCV** | Image/video processing |
| **SQLAlchemy** | Database ORM (SQLite) |
| **SMTP (Gmail)** | Email notifications |
| **PyTorch** | Deep learning framework |

---

## PPE Classes Detected

| Class | Color (in detection) |
|-------|---------------------|
| Helmet | Green |
| Gloves | Blue |
| Vest | Magenta |
| Boots | Red |
| Goggles | Cyan |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again |
| Camera shows black screen | Close other apps using the webcam, restart the app |
| Email not sending | Check `.env` credentials, use Gmail App Password (not regular password) |
| Email in spam folder | Check recipient's spam/junk folder |
| `CUDA not available` | System will use CPU automatically (slower but works) |
| Port 5000 in use | Change port: `python web_app.py` and edit `app.run(port=5001)` |
| Face not recognized | Register with more photos (5-10) from different angles and lighting |

---

## Stopping the Application

Press `Ctrl + C` in the terminal to stop the server.

---

---
