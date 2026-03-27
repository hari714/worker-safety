"""
Generate PDF Setup Guide for PPE Detection System - Beginner Friendly
Run: python generate_setup_guide.py
"""
from fpdf import FPDF


class SetupGuidePDF(FPDF):
    BLUE = (59, 130, 246)
    DARK = (30, 30, 40)
    GRAY = (100, 100, 120)
    WHITE = (255, 255, 255)
    LIGHT_BG = (245, 245, 250)
    GREEN = (34, 197, 94)
    RED = (239, 68, 68)
    ORANGE = (245, 158, 11)

    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(*self.GRAY)
            self.cell(0, 10, 'PPE Detection System - Setup Guide', align='L')
            self.cell(0, 10, f'Page {self.page_no()}', align='R', new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(*self.BLUE)
            self.set_line_width(0.3)
            self.line(10, 18, 200, 18)
            self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(*self.GRAY)
        self.cell(0, 10, 'PPE Detection - Workplace Safety System', align='C')

    def cover_page(self):
        self.add_page()
        self.ln(40)
        self.set_fill_color(*self.BLUE)
        self.rect(10, 55, 190, 3, 'F')
        self.ln(15)
        self.set_font('Helvetica', 'B', 34)
        self.set_text_color(*self.DARK)
        self.cell(0, 16, 'PPE Detection System', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        self.set_font('Helvetica', '', 16)
        self.set_text_color(*self.GRAY)
        self.cell(0, 10, 'Complete Setup & Installation Guide', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        self.set_font('Helvetica', 'I', 11)
        self.set_text_color(*self.BLUE)
        self.cell(0, 8, 'Step-by-step instructions for beginners', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(12)
        # Info box
        self.set_fill_color(*self.LIGHT_BG)
        self.set_draw_color(200, 200, 220)
        y = self.get_y()
        self.rect(35, y, 140, 55, 'DF')
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*self.DARK)
        self.set_xy(40, y + 8)
        self.cell(130, 7, 'Project Details', align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_font('Helvetica', '', 10)
        details = [
            ('Version', '1.0'),
            ('Python Required', '3.10 or newer'),
            ('Framework', 'Flask + YOLOv8 + OpenCV'),
            ('Date', 'March 2026'),
        ]
        for label, value in details:
            self.set_xy(50, self.get_y())
            self.set_font('Helvetica', 'B', 9)
            self.cell(40, 7, label + ':')
            self.set_font('Helvetica', '', 9)
            self.cell(60, 7, value, new_x="LMARGIN", new_y="NEXT")
        self.ln(30)
        self.set_fill_color(*self.BLUE)
        self.rect(10, 260, 190, 3, 'F')

    def section_title(self, number, title):
        self.ln(6)
        self.set_fill_color(*self.BLUE)
        self.set_text_color(*self.WHITE)
        self.set_font('Helvetica', 'B', 13)
        self.cell(0, 11, f'  Step {number}:  {title}', fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def sub_title(self, title):
        self.ln(3)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(*self.BLUE)
        self.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(*self.DARK)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def bold_text(self, text):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*self.DARK)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def step_instruction(self, number, text):
        """Numbered sub-step like 1.1, 1.2 etc."""
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*self.BLUE)
        x = self.get_x()
        self.cell(8, 6, str(number))
        self.set_font('Helvetica', '', 10)
        self.set_text_color(*self.DARK)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def code_block(self, code):
        self.set_fill_color(240, 240, 245)
        self.set_draw_color(200, 200, 210)
        self.set_font('Courier', '', 9)
        self.set_text_color(40, 40, 60)
        y = self.get_y()
        lines = code.strip().split('\n')
        block_h = len(lines) * 5.5 + 10
        if y + block_h > 270:
            self.add_page()
            y = self.get_y()
        self.rect(12, y, 186, block_h, 'DF')
        self.set_fill_color(*self.BLUE)
        self.rect(12, y, 2.5, block_h, 'F')
        self.set_xy(18, y + 5)
        for line in lines:
            self.cell(0, 5.5, line, new_x="LMARGIN", new_y="NEXT")
            self.set_x(18)
        self.ln(5)

    def what_you_see(self, text):
        """Show expected output"""
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(*self.GREEN)
        self.cell(0, 6, 'What you should see:', new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*self.DARK)
        self.ln(1)

    def bullet(self, text, indent=15):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(*self.DARK)
        self.set_x(indent)
        self.cell(5, 6, '-')
        self.multi_cell(0, 6, text)
        self.ln(1)

    def numbered_item(self, num, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(*self.DARK)
        self.set_x(15)
        self.set_font('Helvetica', 'B', 10)
        self.cell(8, 6, f'{num}.')
        self.set_font('Helvetica', '', 10)
        self.multi_cell(0, 6, text)
        self.ln(1)

    def note_box(self, text, color='blue'):
        if color == 'blue':
            bg = (235, 245, 255)
            border_c = self.BLUE
            label = 'NOTE'
        elif color == 'green':
            bg = (235, 255, 245)
            border_c = self.GREEN
            label = 'TIP'
        elif color == 'orange':
            bg = (255, 248, 235)
            border_c = self.ORANGE
            label = 'IMPORTANT'
        else:
            bg = (255, 240, 240)
            border_c = self.RED
            label = 'WARNING'
        self.set_fill_color(*bg)
        y = self.get_y()
        self.set_font('Helvetica', '', 9)
        self.set_text_color(*self.DARK)
        lines = len(text) / 80 + 1.5
        h = max(lines * 5.5 + 12, 16)
        if y + h > 270:
            self.add_page()
            y = self.get_y()
        self.rect(12, y, 186, h, 'F')
        self.set_fill_color(*border_c)
        self.rect(12, y, 2.5, h, 'F')
        self.set_xy(18, y + 3)
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(*border_c)
        self.cell(0, 5, label, new_x="LMARGIN", new_y="NEXT")
        self.set_x(18)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(*self.DARK)
        self.multi_cell(176, 5.5, text)
        self.set_y(y + h + 4)

    def file_tree(self, lines):
        self.set_fill_color(245, 245, 250)
        self.set_draw_color(200, 200, 210)
        y = self.get_y()
        block_h = len(lines) * 5 + 8
        if y + block_h > 270:
            self.add_page()
            y = self.get_y()
        self.rect(12, y, 186, block_h, 'DF')
        self.set_fill_color(*self.BLUE)
        self.rect(12, y, 2.5, block_h, 'F')
        self.set_font('Courier', '', 8)
        self.set_text_color(60, 60, 80)
        self.set_xy(18, y + 4)
        for line in lines:
            self.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")
            self.set_x(18)
        self.ln(4)


def build_guide():
    pdf = SetupGuidePDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ===== COVER =====
    pdf.cover_page()

    # ===== TABLE OF CONTENTS =====
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(*pdf.DARK)
    pdf.cell(0, 12, 'Table of Contents', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_fill_color(*pdf.BLUE)
    pdf.rect(10, pdf.get_y(), 60, 1, 'F')
    pdf.ln(8)
    toc = [
        ('1', 'Install Python (if not installed)'),
        ('2', 'Extract the ZIP File'),
        ('3', 'Open Command Prompt / Terminal'),
        ('4', 'Go to the Project Folder'),
        ('5', 'Create a Virtual Environment'),
        ('6', 'Activate the Virtual Environment'),
        ('7', 'Install Required Packages'),
        ('8', 'Set Up the Configuration File'),
        ('9', 'Run the Application'),
        ('10', 'Open in Your Browser'),
        ('11', 'How to Upload & Detect PPE'),
        ('12', 'How to Stop the Application'),
        ('13', 'Common Errors & Fixes'),
        ('14', 'Project Files Explained'),
        ('15', 'Quick Reference Card'),
    ]
    for num, title in toc:
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(*pdf.DARK)
        w = 14 if len(num) < 2 else 18
        pdf.cell(w, 8, f'Step {num}.')
        pdf.set_text_color(*pdf.BLUE)
        pdf.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")

    # ===== STEP 1: INSTALL PYTHON =====
    pdf.add_page()
    pdf.section_title('1', 'Install Python (If Not Already Installed)')

    pdf.body_text('Python is the programming language this project is built with. You need it installed on your computer before anything else.')

    pdf.sub_title('How to check if Python is already installed:')
    pdf.body_text('Open Command Prompt (see Step 3 for how) and type:')
    pdf.code_block('python --version')
    pdf.body_text('If you see something like "Python 3.12.0" or any version 3.10+, you are good. Skip to Step 2.')
    pdf.body_text('If you see an error like "python is not recognized", follow the steps below to install it.')

    pdf.sub_title('How to install Python on Windows:')
    pdf.numbered_item(1, 'Open your web browser (Chrome, Edge, etc.)')
    pdf.numbered_item(2, 'Go to:  https://www.python.org/downloads/')
    pdf.numbered_item(3, 'Click the big yellow button that says "Download Python 3.x.x"')
    pdf.numbered_item(4, 'Open the downloaded file (python-3.x.x-amd64.exe)')
    pdf.ln(2)
    pdf.note_box('VERY IMPORTANT: On the first screen of the installer, there is a checkbox at the bottom that says "Add python.exe to PATH". You MUST check this box! If you miss it, Python will not work from the command prompt.', 'red')
    pdf.ln(2)
    pdf.numbered_item(5, 'After checking "Add python.exe to PATH", click "Install Now"')
    pdf.numbered_item(6, 'Wait for installation to complete, then click "Close"')
    pdf.numbered_item(7, 'Close and reopen Command Prompt, then verify:')
    pdf.code_block('python --version')
    pdf.body_text('You should now see the Python version number.')

    pdf.sub_title('How to install Python on macOS:')
    pdf.numbered_item(1, 'Go to:  https://www.python.org/downloads/')
    pdf.numbered_item(2, 'Download the macOS installer (.pkg file)')
    pdf.numbered_item(3, 'Double-click the downloaded file and follow the wizard')
    pdf.numbered_item(4, 'Open Terminal (search "Terminal" in Spotlight) and verify:')
    pdf.code_block('python3 --version')

    # ===== STEP 2: EXTRACT ZIP =====
    pdf.add_page()
    pdf.section_title('2', 'Extract the ZIP File')

    pdf.body_text('You received a file called "PPE_Detection_System.zip". This contains the entire project. You need to extract (unzip) it first.')

    pdf.sub_title('On Windows:')
    pdf.numbered_item(1, 'Find the file "PPE_Detection_System.zip" (probably in your Downloads folder)')
    pdf.numbered_item(2, 'Right-click on the ZIP file')
    pdf.numbered_item(3, 'Click "Extract All..."')
    pdf.numbered_item(4, 'Choose where to save it (Desktop is fine for now)')
    pdf.numbered_item(5, 'Click "Extract"')
    pdf.numbered_item(6, 'A new folder called "PPE_Detection_System" will appear')

    pdf.sub_title('On macOS:')
    pdf.numbered_item(1, 'Find the ZIP file in Finder')
    pdf.numbered_item(2, 'Double-click it. It will automatically extract.')

    pdf.ln(2)
    pdf.note_box('After extraction, you should see a folder named "PPE_Detection_System" containing files like web_app.py, main.py, requirements.txt, and a "models" folder. If you see these files, you are on the right track!', 'green')

    # ===== STEP 3: OPEN COMMAND PROMPT =====
    pdf.section_title('3', 'Open Command Prompt / Terminal')

    pdf.body_text('You need to use the command line (a text-based interface) to set up the project. Don\'t worry, just type exactly what is shown in this guide!')

    pdf.sub_title('On Windows (3 ways, pick any one):')
    pdf.bold_text('Way 1 (Easiest):')
    pdf.numbered_item(1, 'Open the extracted "PPE_Detection_System" folder in File Explorer')
    pdf.numbered_item(2, 'Click on the address bar at the top (where it shows the folder path)')
    pdf.numbered_item(3, 'Type "cmd" and press Enter')
    pdf.numbered_item(4, 'A black Command Prompt window opens, already in the right folder!')

    pdf.ln(2)
    pdf.bold_text('Way 2:')
    pdf.numbered_item(1, 'Press the Windows key on your keyboard')
    pdf.numbered_item(2, 'Type "cmd"')
    pdf.numbered_item(3, 'Click "Command Prompt" from the results')

    pdf.ln(2)
    pdf.bold_text('Way 3:')
    pdf.numbered_item(1, 'Press Windows + R keys together')
    pdf.numbered_item(2, 'Type "cmd" and press Enter')

    pdf.sub_title('On macOS:')
    pdf.numbered_item(1, 'Press Command + Space to open Spotlight')
    pdf.numbered_item(2, 'Type "Terminal" and press Enter')

    # ===== STEP 4: GO TO PROJECT FOLDER =====
    pdf.add_page()
    pdf.section_title('4', 'Go to the Project Folder')

    pdf.body_text('If you used "Way 1" from Step 3 (typed cmd in the address bar), you are already in the right folder! Skip to Step 5.')
    pdf.body_text('Otherwise, you need to navigate to the project folder using the "cd" command:')

    pdf.sub_title('If you extracted to the Desktop (Windows):')
    pdf.code_block('cd %USERPROFILE%\\Desktop\\PPE_Detection_System')

    pdf.sub_title('If you extracted to Downloads (Windows):')
    pdf.code_block('cd %USERPROFILE%\\Downloads\\PPE_Detection_System')

    pdf.sub_title('If you extracted to Desktop (macOS):')
    pdf.code_block('cd ~/Desktop/PPE_Detection_System')

    pdf.sub_title('How to verify you are in the right folder:')
    pdf.body_text('Type this command and press Enter:')
    pdf.code_block('dir')
    pdf.body_text('(On macOS/Linux, use "ls" instead of "dir")')
    pdf.ln(1)
    pdf.body_text('You should see files like:')
    pdf.code_block('web_app.py\nmain.py\nrequirements.txt\nmodels/\nconfig/')
    pdf.note_box('If you see these files listed, you are in the correct folder. If not, the path might be wrong. Double-check where you extracted the ZIP file.', 'green')

    # ===== STEP 5: CREATE VIRTUAL ENVIRONMENT =====
    pdf.section_title('5', 'Create a Virtual Environment')

    pdf.body_text('A virtual environment is like a clean, separate workspace for this project. It keeps this project\'s packages separate from other Python projects on your computer.')
    pdf.body_text('Type this command and press Enter:')

    pdf.sub_title('Windows:')
    pdf.code_block('python -m venv venv')

    pdf.sub_title('macOS / Linux:')
    pdf.code_block('python3 -m venv venv')

    pdf.body_text('This will take 10-30 seconds. You won\'t see any output. That is normal.')
    pdf.body_text('When it is done, a new folder called "venv" will appear inside your project folder.')

    pdf.note_box('If you get an error like "python is not recognized", go back to Step 1 and install Python. Make sure you checked "Add python.exe to PATH" during installation.', 'red')

    # ===== STEP 6: ACTIVATE VIRTUAL ENVIRONMENT =====
    pdf.add_page()
    pdf.section_title('6', 'Activate the Virtual Environment')

    pdf.body_text('After creating the virtual environment, you must activate it. This tells your computer to use the project\'s own packages.')

    pdf.sub_title('Windows (Command Prompt):')
    pdf.code_block('venv\\Scripts\\activate')

    pdf.sub_title('Windows (PowerShell):')
    pdf.code_block('venv\\Scripts\\Activate.ps1')

    pdf.note_box('PowerShell users: If you get a red error about "execution policy", run this command first and try again:\n  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser', 'orange')

    pdf.sub_title('macOS / Linux:')
    pdf.code_block('source venv/bin/activate')

    pdf.sub_title('How to know it worked:')
    pdf.body_text('Look at the beginning of your command line. You should see "(venv)" at the start:')
    pdf.code_block('(venv) C:\\Users\\YourName\\Desktop\\PPE_Detection_System>')
    pdf.body_text('The "(venv)" means the virtual environment is active. You MUST see this before continuing!')

    pdf.note_box('EVERY TIME you close and reopen the Command Prompt, you need to activate the virtual environment again using the command above. The "(venv)" will disappear when you close the window.', 'orange')

    # ===== STEP 7: INSTALL PACKAGES =====
    pdf.section_title('7', 'Install Required Packages')

    pdf.body_text('Now install all the libraries the project needs. Make sure you see "(venv)" at the start of your command line, then type:')
    pdf.code_block('pip install -r requirements.txt')

    pdf.body_text('Press Enter and wait. You will see a lot of text scrolling. This is normal!')

    pdf.sub_title('What is happening:')
    pdf.bullet('It is downloading and installing about 20+ packages from the internet')
    pdf.bullet('The biggest one is PyTorch (about 2 GB) - this will take time')
    pdf.bullet('Total time: 5 to 15 minutes depending on your internet speed')
    pdf.bullet('Do NOT close the window while it is installing')

    pdf.sub_title('How to know it finished successfully:')
    pdf.body_text('At the end, you should see a message like:')
    pdf.code_block('Successfully installed Flask-2.3.0 numpy-1.24.0 torch-2.0.0 ...')
    pdf.body_text('If you see "Successfully installed", everything is good!')

    pdf.note_box('If you see red error text, check: (1) Is your internet working? (2) Is "(venv)" showing? (3) Try running the command again. Sometimes downloads fail on the first try.', 'red')

    # ===== STEP 8: CONFIGURATION =====
    pdf.add_page()
    pdf.section_title('8', 'Set Up the Configuration File')

    pdf.body_text('The project needs a small configuration file called ".env" to know where to find things. A template is already provided.')
    pdf.body_text('Type this command to create the configuration file:')

    pdf.sub_title('Windows:')
    pdf.code_block('copy .env.example .env')

    pdf.sub_title('macOS / Linux:')
    pdf.code_block('cp .env.example .env')

    pdf.body_text('That\'s it! The default settings work out of the box. No editing needed.')

    pdf.note_box('The default configuration is ready to use for PPE detection. You do NOT need to change anything in the .env file unless you want to set up email notifications (which is optional).', 'green')

    # ===== STEP 9: RUN THE APP =====
    pdf.section_title('9', 'Run the Application')

    pdf.body_text('Everything is set up! Now let\'s start the PPE Detection web application.')
    pdf.body_text('Make sure "(venv)" is showing in your command line, then type:')
    pdf.code_block('python web_app.py')

    pdf.sub_title('What you should see:')
    pdf.code_block('========================================\n  PPE Detection Web UI\n  http://localhost:5000\n========================================')

    pdf.body_text('If you see this message, the application is running! Do NOT close this Command Prompt window, it must stay open while you use the app.')

    pdf.note_box('The command prompt will look like it is "stuck" or "frozen". This is normal! It means the server is running and waiting for requests. Leave it open.', 'green')

    # ===== STEP 10: OPEN BROWSER =====
    pdf.section_title('10', 'Open in Your Browser')

    pdf.body_text('Now open any web browser (Chrome, Edge, Firefox) and go to this address:')
    pdf.code_block('http://localhost:5000')

    pdf.sub_title('How to do it:')
    pdf.numbered_item(1, 'Open Chrome / Edge / Firefox')
    pdf.numbered_item(2, 'Click on the address bar at the top')
    pdf.numbered_item(3, 'Type:  localhost:5000')
    pdf.numbered_item(4, 'Press Enter')
    pdf.ln(2)
    pdf.body_text('You should see the PPE Detection web page with a blue upload area and an "Analyze Image" button!')

    pdf.note_box('If the page doesn\'t load, make sure: (1) The Command Prompt from Step 9 is still open and showing the message. (2) You typed the address correctly: localhost:5000 (no spaces). (3) Try http://127.0.0.1:5000 as an alternative.', 'orange')

    # ===== STEP 11: HOW TO USE =====
    pdf.add_page()
    pdf.section_title('11', 'How to Upload & Detect PPE')

    pdf.body_text('Now you can upload a photo of a worker and the system will detect what Personal Protective Equipment (PPE) they are wearing or missing.')

    pdf.sub_title('Uploading an Image:')
    pdf.numbered_item(1, 'Click the upload area (the dashed box with the upload icon)')
    pdf.numbered_item(2, 'A file browser window will open')
    pdf.numbered_item(3, 'Select a JPG or PNG image of a worker (max size: 16 MB)')
    pdf.numbered_item(4, 'Click "Open"')
    pdf.numbered_item(5, 'You will see a small preview of your image and the filename')

    pdf.sub_title('OR drag and drop:')
    pdf.bullet('You can also drag an image file from File Explorer and drop it onto the upload area')

    pdf.sub_title('Analyzing the Image:')
    pdf.numbered_item(1, 'After uploading, click the "Analyze Image" button')
    pdf.numbered_item(2, 'Wait 2-5 seconds (the button will show "Analyzing...")')
    pdf.numbered_item(3, 'The results will appear below')

    pdf.sub_title('Understanding the Results:')
    pdf.ln(1)
    pdf.bold_text('1. Annotated Image')
    pdf.body_text('The original image is shown with white boxes drawn around detected PPE items. Each box has a label showing what was found and the confidence percentage.')
    pdf.bold_text('2. Compliance Status')
    pdf.bullet('GREEN "Compliant" = All 5 PPE items were detected. The worker is safe.')
    pdf.bullet('RED "Non-Compliant" = One or more PPE items are missing. Shows which items are missing.')
    pdf.bold_text('3. PPE Checklist')
    pdf.body_text('A list of all 5 PPE items showing:')
    pdf.bullet('Green dot + "Found" = The item was detected in the image')
    pdf.bullet('Red dot + "Missing" = The item was NOT detected')
    pdf.bold_text('4. Statistics')
    pdf.body_text('Three numbers showing: how many items detected, how many missing, total objects found.')

    pdf.sub_title('The 5 PPE Items the System Detects:')
    pdf.numbered_item(1, 'Helmet - Hard hat for head protection')
    pdf.numbered_item(2, 'Gloves - Protective gloves for hand safety')
    pdf.numbered_item(3, 'Vest - High-visibility reflective vest')
    pdf.numbered_item(4, 'Boots - Safety boots / steel-toe shoes')
    pdf.numbered_item(5, 'Goggles - Safety glasses / eye protection')

    # ===== STEP 12: STOP THE APP =====
    pdf.add_page()
    pdf.section_title('12', 'How to Stop the Application')

    pdf.body_text('When you are done using the PPE Detection system:')
    pdf.numbered_item(1, 'Go to the Command Prompt window where the server is running')
    pdf.numbered_item(2, 'Press   Ctrl + C   (hold the Ctrl key and press C)')
    pdf.numbered_item(3, 'The server will stop and you will get your command prompt back')
    pdf.ln(2)
    pdf.body_text('To start it again later, you need to:')
    pdf.numbered_item(1, 'Open Command Prompt')
    pdf.numbered_item(2, 'Navigate to the project folder (Step 4)')
    pdf.numbered_item(3, 'Activate the virtual environment (Step 6)')
    pdf.numbered_item(4, 'Run: python web_app.py (Step 9)')

    pdf.ln(2)
    pdf.note_box('Quick restart commands (copy-paste these 3 lines one by one):\n\n  cd %USERPROFILE%\\Desktop\\PPE_Detection_System\n  venv\\Scripts\\activate\n  python web_app.py', 'green')

    # ===== STEP 13: TROUBLESHOOTING =====
    pdf.section_title('13', 'Common Errors & How to Fix Them')

    pdf.sub_title('Error: "python is not recognized"')
    pdf.body_text('Python is not installed or not in your PATH.')
    pdf.bold_text('Fix: Go back to Step 1. Reinstall Python and CHECK the "Add to PATH" box.')

    pdf.sub_title('Error: "No module named flask" (or any other module)')
    pdf.body_text('The packages are not installed, or the virtual environment is not active.')
    pdf.bold_text('Fix: Make sure you see "(venv)" in your command line. If not:')
    pdf.code_block('venv\\Scripts\\activate\npip install -r requirements.txt')

    pdf.sub_title('Error: "Port 5000 already in use"')
    pdf.body_text('Another program is using port 5000, or you already have the app running.')
    pdf.bold_text('Fix: Either close the other instance, or change the port. Open web_app.py in Notepad, find the last line, and change 5000 to 8080:')
    pdf.code_block('app.run(debug=False, host="0.0.0.0", port=8080)')
    pdf.body_text('Then open http://localhost:8080 in your browser instead.')

    pdf.add_page()
    pdf.sub_title('Error: "Could not read image"')
    pdf.body_text('The uploaded file is not a valid image.')
    pdf.bold_text('Fix: Make sure your file is a real .jpg or .png image. Try a different photo.')

    pdf.sub_title('Error: pip install fails with red text')
    pdf.body_text('Usually a network issue or permissions problem.')
    pdf.bold_text('Fix:')
    pdf.numbered_item(1, 'Check your internet connection')
    pdf.numbered_item(2, 'Try running again: pip install -r requirements.txt')
    pdf.numbered_item(3, 'If on work/school network, try from a different network')

    pdf.sub_title('The page shows but detection is wrong / not finding PPE')
    pdf.bullet('The model works best with clear, well-lit photos')
    pdf.bullet('Workers should be reasonably close to the camera (not tiny in the distance)')
    pdf.bullet('The confidence threshold is set to 50% by default')

    pdf.sub_title('PowerShell: "running scripts is disabled on this system"')
    pdf.bold_text('Fix: Run this command in PowerShell, then try activating again:')
    pdf.code_block('Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser')

    # ===== STEP 14: PROJECT FILES =====
    pdf.section_title('14', 'Project Files Explained')

    pdf.body_text('Here is what each file and folder in the project does:')
    pdf.file_tree([
        'PPE_Detection_System/',
        '|',
        '|-- web_app.py            << MAIN FILE - The web application you run',
        '|-- main.py               << Alternative CLI entry point',
        '|-- requirements.txt      << List of packages to install',
        '|-- .env.example          << Configuration template',
        '|-- .env                  << Your configuration (created in Step 8)',
        '|-- train_ppe.py          << For retraining the model (advanced)',
        '|',
        '|-- models/',
        '|   |-- ppe_detection_best.pt   << The trained AI model (6 MB)',
        '|',
        '|-- api/                  << REST API code',
        '|-- config/               << Settings & database config',
        '|-- ppe_detection/        << Detection logic code',
        '|-- face_recognition/     << Worker face ID (advanced)',
        '|-- worker_management/    << Worker database',
        '|-- monitoring/           << Compliance checking',
        '|-- notification_system/  << Email alerts',
        '|-- utils/                << Helper functions',
        '|-- tests/                << Test files',
        '|-- venv/                 << Virtual environment (created in Step 5)',
    ])

    # ===== STEP 15: QUICK REFERENCE CARD =====
    pdf.add_page()
    pdf.section_title('15', 'Quick Reference Card')
    pdf.body_text('Keep this page handy! These are all the commands you need:')
    pdf.ln(2)

    # First time setup box
    pdf.set_fill_color(*pdf.LIGHT_BG)
    pdf.set_draw_color(*pdf.BLUE)
    y = pdf.get_y()
    pdf.rect(12, y, 186, 78, 'DF')
    pdf.set_fill_color(*pdf.BLUE)
    pdf.rect(12, y, 186, 10, 'F')
    pdf.set_xy(14, y + 2)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(*pdf.WHITE)
    pdf.cell(0, 7, 'FIRST TIME SETUP (do this once)', new_x="LMARGIN", new_y="NEXT")
    pdf.set_xy(18, y + 15)
    pdf.set_font('Courier', '', 9)
    pdf.set_text_color(*pdf.DARK)
    cmds = [
        'Step 1:  Extract the ZIP file to your Desktop',
        'Step 2:  Open Command Prompt (type "cmd" in folder address bar)',
        'Step 3:  python -m venv venv',
        'Step 4:  venv\\Scripts\\activate',
        'Step 5:  pip install -r requirements.txt',
        'Step 6:  copy .env.example .env',
        'Step 7:  python web_app.py',
        'Step 8:  Open browser -> localhost:5000',
    ]
    for cmd in cmds:
        pdf.cell(0, 7, cmd, new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(18)

    pdf.ln(8)

    # Every time box
    y = pdf.get_y()
    pdf.set_fill_color(235, 255, 245)
    pdf.set_draw_color(*pdf.GREEN)
    pdf.rect(12, y, 186, 48, 'DF')
    pdf.set_fill_color(*pdf.GREEN)
    pdf.rect(12, y, 186, 10, 'F')
    pdf.set_xy(14, y + 2)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(*pdf.WHITE)
    pdf.cell(0, 7, 'EVERY TIME YOU WANT TO USE IT (after first setup)', new_x="LMARGIN", new_y="NEXT")
    pdf.set_xy(18, y + 15)
    pdf.set_font('Courier', '', 9)
    pdf.set_text_color(*pdf.DARK)
    cmds2 = [
        'Step 1:  Open Command Prompt',
        'Step 2:  cd %USERPROFILE%\\Desktop\\PPE_Detection_System',
        'Step 3:  venv\\Scripts\\activate',
        'Step 4:  python web_app.py',
        'Step 5:  Open browser -> localhost:5000',
    ]
    for cmd in cmds2:
        pdf.cell(0, 7, cmd, new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(18)

    pdf.ln(8)

    # Stop box
    y = pdf.get_y()
    pdf.set_fill_color(255, 240, 240)
    pdf.set_draw_color(*pdf.RED)
    pdf.rect(12, y, 186, 20, 'DF')
    pdf.set_fill_color(*pdf.RED)
    pdf.rect(12, y, 186, 10, 'F')
    pdf.set_xy(14, y + 2)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(*pdf.WHITE)
    pdf.cell(0, 7, 'TO STOP THE APPLICATION', new_x="LMARGIN", new_y="NEXT")
    pdf.set_xy(18, y + 14)
    pdf.set_font('Courier', '', 9)
    pdf.set_text_color(*pdf.DARK)
    pdf.cell(0, 7, 'Press  Ctrl + C  in the Command Prompt window', new_x="LMARGIN", new_y="NEXT")

    # Save
    output_path = 'PPE_Detection_Setup_Guide.pdf'
    pdf.output(output_path)
    print(f'Setup guide saved: {output_path}')
    return output_path


if __name__ == '__main__':
    build_guide()
