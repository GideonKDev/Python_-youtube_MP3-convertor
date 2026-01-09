# YouTube to MP3 Converter

## Overview

YouTube to MP3 Converter is a Python-based desktop application designed to convert YouTube videos into high-quality MP3 audio files. The application provides a clean graphical user interface and supports both single and batch downloads, making it suitable for personal, academic, and educational use.

The project emphasizes usability, modular design, and compliance awareness, and is intended for users who require a simple and efficient audio extraction tool.

---

## Key Features

- Graphical User Interface built with Tkinter
- Single and batch YouTube URL processing
- Selectable MP3 audio quality (128kbps, 192kbps, 320kbps)
- Real-time download progress feedback
- Executable build support for Windows systems
- URL import from text files
- Automatic metadata handling for output filenames

---

## System Requirements

- Python 3.6 or higher
- FFmpeg (required for audio conversion)
- Windows Operating System  
  (Linux and macOS may work with minor modifications)

---

## Installation

### Method 1: Run from Source Code

1. Install Python from https://www.python.org
2. Install FFmpeg from https://ffmpeg.org
3. Clone the repository:
   ```bash
   git clone https://github.com/GideonKDev/Python_-youtube_MP3-convertor.git
   cd Python_-youtube_MP3-convertor
Install required dependencies:

bash
Copy code
pip install -r requirements.txt
Launch the application:

bash
Copy code
python run.py
Method 2: Standalone Executable
Download the latest release from the GitHub Releases page

Extract the downloaded ZIP file

Run YouTube2MP3_Converter.exe

Ensure FFmpeg is installed and accessible via system PATH

Usage Guidelines
Single Download
Launch the application

Enter a YouTube URL in the Single Download section

Select the preferred audio quality

Choose the destination folder (default: downloads/)

Click Download MP3

Batch Download
Paste multiple YouTube URLs (one per line), or

Import URLs from a .txt file

Select the desired audio quality and output directory

Click Download All

Executable Build Process
To generate a standalone Windows executable:

bash
Copy code
python create_exe.py
The executable file will be created in the dist/ directory.

Project Structure
text
Copy code
youtube-to-mp3-converter/
├── main.py              # GUI application entry point
├── converter.py         # Audio extraction and conversion logic
├── batch_processor.py   # Batch processing implementation
├── run.py               # Application launcher
├── create_exe.py        # Executable build script
├── requirements.txt     # Project dependencies
├── LICENSE              # MIT License
├── README.md            # Project documentation
└── assets/
    └── icon.ico         # Application icon
Dependencies
yt-dlp
Core library used for YouTube content extraction

tkinter
Graphical user interface framework (bundled with Python)

Legal and Compliance Notice
This software is provided strictly for educational and lawful use.

Users must ensure compliance with applicable copyright laws

Only content owned by the user or licensed for download may be processed

YouTube’s Terms of Service prohibit unauthorized downloading of content

The developer assumes no responsibility for misuse or violation of third-party terms.

Troubleshooting
FFmpeg Not Detected
Download FFmpeg from https://ffmpeg.org/download.html

Add ffmpeg.exe to the system PATH environment variable

Alternatively, place ffmpeg.exe in the application directory

Missing Python Modules
Install all required dependencies:

bash
Copy code
pip install -r requirements.txt
Ensure Python version 3.6 or higher is installed.

Download Errors
Verify network connectivity

Confirm the YouTube URL is valid and publicly accessible

Ensure the content has not been restricted or removed

Contribution Guidelines
Fork the repository

Create a feature branch:

bash
Copy code
git checkout -b feature-name
Commit changes:

bash
Copy code
git commit -m "Add feature description"
Push the branch:

bash
Copy code
git push origin feature-name
Submit a Pull Request for review

License
This project is licensed under the MIT License.
Refer to the LICENSE file for full licensing details.

Acknowledgments
yt-dlp development team for robust media extraction tools

FFmpeg project for audio processing capabilities

The Python open-source community

Support and Maintenance
For issues, bug reports, or feature requests:

Review the Troubleshooting section

Open an Issue on the GitHub repository

Ensure the application version is up to date

Important Notice:
Only download and use content for which you have explicit permission. Respect intellectual property rights and content creator policies at all times.