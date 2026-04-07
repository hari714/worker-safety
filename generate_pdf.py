"""Generate SafetyVision Setup Guide PDF"""
from fpdf import FPDF

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=20)

def title(text):
    pdf.set_font('Helvetica', 'B', 22)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 14, text, new_x='LMARGIN', new_y='NEXT')
    pdf.ln(2)

def heading(text):
    pdf.ln(4)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, text, new_x='LMARGIN', new_y='NEXT')
    pdf.set_draw_color(200, 200, 200)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 170, pdf.get_y())
    pdf.ln(4)

def subheading(text):
    pdf.ln(2)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 8, text, new_x='LMARGIN', new_y='NEXT')
    pdf.ln(1)

def body(text):
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(0, 6, text)
    pdf.ln(2)

def code(text):
    pdf.set_font('Courier', '', 9)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_text_color(30, 30, 30)
    for line in text.strip().split('\n'):
        pdf.cell(0, 6, '  ' + line, new_x='LMARGIN', new_y='NEXT', fill=True)
    pdf.ln(3)

def bullet(text):
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(40, 40, 40)
    x = pdf.get_x()
    pdf.cell(6, 6, '-')
    pdf.multi_cell(0, 6, text)
    pdf.ln(1)

def table_row(cols, bold=False):
    pdf.set_font('Helvetica', 'B' if bold else '', 9)
    col_w = 170 / len(cols)
    for c in cols:
        pdf.cell(col_w, 7, str(c), border=1, align='C' if bold else 'L')
    pdf.ln()


# ── Cover Page ──
pdf.add_page()
pdf.ln(40)
pdf.set_font('Helvetica', 'B', 28)
pdf.set_text_color(20, 20, 20)
pdf.cell(0, 15, 'SafetyVision', align='C', new_x='LMARGIN', new_y='NEXT')
pdf.set_font('Helvetica', '', 14)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 10, 'Workplace PPE Detection System', align='C', new_x='LMARGIN', new_y='NEXT')
pdf.ln(10)
pdf.set_font('Helvetica', '', 11)
pdf.cell(0, 8, 'Setup & Installation Guide', align='C', new_x='LMARGIN', new_y='NEXT')
pdf.ln(20)
pdf.set_font('Helvetica', '', 10)
pdf.set_text_color(120, 120, 120)


# ── Overview Page ──
pdf.add_page()
title('Project Overview')
body('SafetyVision is a real-time Personal Protective Equipment (PPE) detection system that uses AI to monitor worker safety compliance. It detects 5 PPE items, identifies workers by face recognition, and sends email alerts for violations.')

heading('What This System Does')
bullet('PPE Detection - Detects Helmet, Gloves, Vest, Boots, Goggles using YOLOv8')
bullet('Face Recognition - Identifies registered workers using FaceNet')
bullet('Live Camera - Real-time monitoring from webcam')
bullet('Image Analysis - Upload and analyze single images')
bullet('Video Analysis - Upload and analyze video files')
bullet('Worker Registration - Register workers with name, email, and face capture')
bullet('Email Alerts - Send violation emails via Gmail SMTP')

heading('Technologies Used')
table_row(['Technology', 'Purpose'], bold=True)
table_row(['Python 3.10+', 'Programming Language'])
table_row(['YOLOv8 (Ultralytics)', 'PPE Object Detection'])
table_row(['FaceNet (facenet-pytorch)', 'Face Recognition'])
table_row(['MTCNN', 'Face Detection'])
table_row(['Flask', 'Web Framework'])
table_row(['OpenCV', 'Image/Video Processing'])
table_row(['SQLAlchemy', 'Database ORM (SQLite)'])
table_row(['SMTP (Gmail)', 'Email Notifications'])
table_row(['PyTorch', 'Deep Learning Framework'])

heading('PPE Classes Detected')
table_row(['Class', 'Detection Color'], bold=True)
table_row(['Helmet', 'Green'])
table_row(['Gloves', 'Blue'])
table_row(['Vest', 'Magenta'])
table_row(['Boots', 'Red'])
table_row(['Goggles', 'Cyan'])


# ── Setup Guide ──
pdf.add_page()
title('Setup Guide')

heading('Prerequisites')
body('Before starting, make sure you have the following installed on your computer:')
bullet('Python 3.10 or higher - Download from https://www.python.org/downloads/')
bullet('Webcam (optional) - For live camera and face registration features')
bullet('Gmail Account (optional) - For sending violation email alerts')
body('IMPORTANT: When installing Python, check the box "Add Python to PATH" during installation.')

heading('Step 1: Extract the Project')
body('Extract the SafetyVision_Project.zip file to any folder on your computer. For example:')
code('C:\\Users\\YourName\\Desktop\\workers_Safety')

heading('Step 2: Open Terminal')
body('Open Command Prompt or PowerShell and navigate to the project folder:')
code('cd C:\\Users\\YourName\\Desktop\\workers_Safety')

heading('Step 3: Create Virtual Environment')
body('Create a Python virtual environment to keep dependencies isolated:')
code('python -m venv venv')

heading('Step 4: Activate Virtual Environment')
body('Activate the virtual environment:')
subheading('Windows (Command Prompt):')
code('venv\\Scripts\\activate')
subheading('Windows (PowerShell):')
code('venv\\Scripts\\Activate.ps1')
body('You should see (venv) at the beginning of your terminal line. This means the virtual environment is active.')

heading('Step 5: Install Dependencies')
body('Install all required Python packages. This may take 5-10 minutes:')
code('pip install -r requirements.txt')

pdf.add_page()

heading('Step 6: Configure Environment File')
body('Copy the example environment file to create your own configuration:')
code('copy .env.example .env')
body('Open .env in any text editor (Notepad, VS Code) and update the email settings. This is optional and only needed if you want email alerts:')
code('SENDER_EMAIL=your.email@gmail.com\nSENDER_PASSWORD=your_app_password_here')

subheading('How to Get Gmail App Password:')
bullet('Go to myaccount.google.com')
bullet('Navigate to Security > 2-Step Verification (turn ON if not already)')
bullet('Search "App passwords" in Google Account settings')
bullet('Create a new app password for "Mail"')
bullet('Copy the 16-character password (e.g., abcd efgh ijkl mnop)')
bullet('Paste it as SENDER_PASSWORD in your .env file')

heading('Step 7: Run the Application')
body('Start the web application:')
code('python web_app.py')
body('You should see the following output:')
code('==================================================\n  PPE Detection & Face Recognition Web UI\n  http://localhost:5000\n  Face Recognition: ACTIVE\n  Email System:     ACTIVE\n==================================================')

heading('Step 8: Open in Browser')
body('Open your web browser (Chrome, Firefox, Edge) and go to:')
code('http://localhost:5000')
body('The SafetyVision web application will load with 4 tabs in the sidebar.')


# ── How to Use ──
pdf.add_page()
title('How to Use')

heading('1. Image Detection')
bullet('Click "Image Detection" in the sidebar')
bullet('Upload a JPG or PNG image of a worker')
bullet('Click "Analyze Image"')
bullet('View PPE detection results on the right panel')

heading('2. Video Detection')
bullet('Click "Video Detection" in the sidebar')
bullet('Upload an MP4, AVI, or MOV video file')
bullet('Click "Analyze Video"')
bullet('View frame-by-frame analysis results')

heading('3. Live Camera')
bullet('Click "Live Camera" in the sidebar')
bullet('Click "Start Camera" to begin real-time monitoring')
bullet('The system shows PPE detection and face identification in real-time')
bullet('For registered workers with missing PPE, click "Send Email" to alert them')
bullet('Unregistered faces show a "Please register face" message')
bullet('Click "Stop Camera" when done')

heading('4. Register Workers')
bullet('Click "Register Workers" in the sidebar')
bullet("Enter the worker's Full Name and Email Address")
bullet('Click "Open Camera" to start the webcam')
bullet('Click "Capture Photo" 5-10 times from different angles and lighting')
bullet('Click "Register Worker" to save')
bullet('The worker can now be identified by the Live Camera')
bullet('Use the "Delete" button to remove a registered worker')


# ── Project Structure ──
pdf.add_page()
title('Project Structure')

pdf.set_font('Courier', '', 8)
pdf.set_fill_color(245, 245, 245)
structure = [
    'workers_Safety/',
    '|-- web_app.py                  Main application (run this)',
    '|-- main.py                     CLI mode (alternative)',
    '|-- requirements.txt            Python dependencies',
    '|-- .env                        Configuration file',
    '|',
    '|-- templates/',
    '|   |-- index.html              Web page template',
    '|-- static/',
    '|   |-- css/style.css           Styles',
    '|   |-- js/app.js               Frontend JavaScript',
    '|',
    '|-- models/',
    '|   |-- best.pt                 Trained YOLOv8 PPE model',
    '|',
    '|-- ppe_detection/              PPE detection module (YOLOv8)',
    '|-- face_recognition/           Face recognition module (FaceNet)',
    '|-- worker_management/          Worker database operations',
    '|-- notification_system/        Email notification module',
    '|-- monitoring/                 Real-time monitoring',
    '|-- config/                     Configuration files',
    '|-- api/                        REST API endpoints',
    '|',
    '|-- worker_embeddings/          Stored face data',
    '|-- violations/                 Violation screenshots',
    '|-- logs/                       Application logs',
]
for line in structure:
    pdf.cell(0, 5, '  ' + line, new_x='LMARGIN', new_y='NEXT', fill=True)
pdf.ln(4)


# ── Troubleshooting ──
heading('Troubleshooting')
pdf.ln(2)
table_row(['Problem', 'Solution'], bold=True)
table_row(['ModuleNotFoundError', 'Run: pip install -r requirements.txt'])
table_row(['Camera shows black', 'Close other apps using webcam, restart'])
table_row(['Email not sending', 'Check .env, use Gmail App Password'])
table_row(['Email in spam', 'Check spam/junk folder'])
table_row(['CUDA not available', 'System uses CPU automatically (slower)'])
table_row(['Port 5000 in use', 'Edit web_app.py: app.run(port=5001)'])
table_row(['Face not recognized', 'Register with more photos (5-10)'])

pdf.ln(6)
heading('Stopping the Application')
body('Press Ctrl + C in the terminal to stop the server.')


# ── Save ──
out = r'D:\SafetyVision_Setup_Guide.pdf'
pdf.output(out)

import os
print(f'PDF created: {out}')
print(f'Size: {os.path.getsize(out) / 1024:.0f} KB')
