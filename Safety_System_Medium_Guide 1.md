# Workplace Safety and Access Control System
## Medium Level Guide (Technical + Non-Technical)

---

## System Overview

### What is It?

An **AI-powered safety monitoring system** that uses:
- **Cameras** to watch work areas
- **Face Recognition** to identify workers
- **PPE Detection** to check safety equipment
- **Email Alerts** to notify of violations



## System Architecture (Simplified)

### What Components Work Together:

```
┌─────────────────────────────────────────────────┐
│              INPUT LAYER                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Webcam   │  │ IP Cam   │  │ Video    │     │
│  │          │  │          │  │ Feed     │     │
│  └──────────┘  └──────────┘  └──────────┘     │
└──────────┬──────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────┐
│        PROCESSING LAYER (AI Engine)             │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  1. FACE DETECTION                       │  │
│  │     (Where are people?)                  │  │
│  └──────────────────────────────────────────┘  │
│                    │                            │
│                    ▼                            │
│  ┌──────────────────────────────────────────┐  │
│  │  2. FACE RECOGNITION                     │  │
│  │     (Who are they?)                      │  │
│  └──────────────────────────────────────────┘  │
│                    │                            │
│                    ▼                            │
│  ┌──────────────────────────────────────────┐  │
│  │  3. PPE DETECTION                        │  │
│  │     (Are they wearing equipment?)        │  │
│  └──────────────────────────────────────────┘  │
│                    │                            │
│                    ▼                            │
│  ┌──────────────────────────────────────────┐  │
│  │  4. COMPLIANCE CHECK                     │  │
│  │     (Missing anything?)                  │  │
│  └──────────────────────────────────────────┘  │
└──────────┬──────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────┐
│        ACTION LAYER                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │Database  │  │Email     │  │Dashboard │     │
│  │(Storage) │  │(Alert)   │  │(Reports) │     │
│  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────┘
```

---

## Core Technologies Used

### 1. Face Detection & Recognition

**What it does:**
- Detects human faces in camera feed
- Compares to database of registered workers
- Identifies WHO is working

**How it works:**
```
Camera Image → Face Detection → Face Recognition → Worker ID
    ↓              ↓                  ↓              ↓
Frame        Find faces          Match to DB     "John Smith"
captured     locations           (95% accuracy)  (EMP-001)
```

**Technical Details:**
- Uses MTCNN or RetinaFace algorithms
- FaceNet embeddings for matching
- 512-dimensional face vectors
- Real-time processing (<1 second)

---

### 2. PPE Detection (YOLOv8)

**What it does:**
- Detects 5 types of safety equipment
- Locates each item on worker's body
- Checks if all required items present

**The 5 Items Detected:**
```
┌─────────────────────────────────────────┐
│ Class 0: HELMET (Head protection)       │
│ Class 1: GLOVES (Hand protection)       │
│ Class 2: SHOES (Foot protection)        │
│ Class 3: GLASSES (Eye protection)       │
│ Class 4: VEST (Visibility/torso)        │
└─────────────────────────────────────────┘
```

**How YOLO Works:**
```
Input Image (640x640)
    ↓
Feature Extraction (CNN backbone)
    ↓
Multi-scale Feature Fusion
    ↓
Object Detection & Classification
    ↓
Bounding Boxes + Confidence Scores
    ↓
Output: [Helmet:0.98, Gloves:0.95, Shoes:0.92, Glasses:X, Vest:0.91]
    ↓
Missing: Glasses → VIOLATION
```

**Technical Specs:**
- YOLOv8n (nano model) for speed
- Confidence threshold: 0.5
- Input: Real-time video frames
- Output: <50ms per frame processing
- Accuracy: 95%+ on trained dataset



## Data Flow Diagram

### From Detection to Action

```
CAMERA FEED
    │
    ▼
┌─────────────────────┐
│ FRAME PREPROCESSOR  │
│ • Resize            │
│ • Normalize         │
│ • Color convert     │
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌──────────┐ ┌──────────┐
│  FACE    │ │   PPE    │
│ DETECTOR │ │ DETECTOR │
└────┬─────┘ └────┬─────┘
     │            │
     ▼            ▼
┌──────────┐ ┌──────────┐
│   FACE   │ │COMPLIANCE│
│  MATCHER │ │  CHECKER │
└────┬─────┘ └────┬─────┘
     │            │
     └────┬───────┘
          │
          ▼
    ┌──────────────┐
    │ VIOLATION?   │
    └────┬─────┬───┘
         │     │
      YES│     │NO
         │     └──→ [GREEN STATUS]
         │          [Continue work]
         ▼
    ┌──────────────────┐
    │ LOG VIOLATION    │
    │ • Database       │
    │ • Timestamp      │
    │ • Photo save     │
    └────┬─────────────┘
         │
         ▼
    ┌──────────────────┐
    │ SEND EMAIL       │
    │ • Generate HTML  │
    │ • SMTP send      │
    │ • Log delivery   │
    └────┬─────────────┘
         │
         ▼
    ┌──────────────────┐
    │ [RED STATUS]     │
    │ [Alert worker]   │
    └──────────────────┘
```


