# YouTube to MP3 Converter

A Python-based desktop application designed to convert YouTube videos into high-quality MP3 audio files. This tool provides a clean graphical user interface (GUI) and supports both single and batch download

---

## Key Features

* **User-Friendly GUI:** Built with Tkinter for a native desktop experience.
* **Processing Modes:** Supports both single URL and batch URL processing.
* **Custom Quality:** Selectable MP3 audio quality (128kbps, 192kbps, 320kbps).
* **Progress Tracking:** Real-time feedback during the download/conversion process.
* **File Integration:** Import URLs directly from `.txt` files.
* **Smart Naming:** Automatic metadata handling for clean output filenames.
* **Portable:** Build support for standalone Windows executables.

---

## System Requirements

* **Python:** 3.6 or higher
* **FFmpeg:** Required for audio conversion (must be in system PATH)
* **OS:** Windows (Linux and macOS supported with minor adjustments)

---

## 🛠 Installation

### Method 1: Run from Source Code

1.  **Install Python:** Download from [python.org](https://www.python.org).
2.  **Install FFmpeg:** Download from [ffmpeg.org](https://ffmpeg.org).
3.  **Clone the repository:**
    ```bash
    git clone [https://github.com/GideonKDev/Python_-youtube_MP3-convertor.git](https://github.com/GideonKDev/Python_-youtube_MP3-convertor.git)
    cd Python_-youtube_MP3-convertor
    ```
4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Launch the application:**
    ```bash
    python run.py
    ```

### Method 2: Standalone Executable
1.  Download the latest release from the **GitHub Releases** page.
2.  Extract the downloaded ZIP file.
3.  open the dist folder
4.  Run `YouTube2MP3.exe`.
5.  *Note: Ensure FFmpeg is installed and accessible via system PATH.*
6.  Run the 'create_shortcut' as administrator to create a shortcut on your PC

*After building the executable yourself (e.g., using `python create_exe.py`), the generated executable will be located in the `dist/` directory of the project.*

---

## Usage Guidelines

### Single Download
1.  Enter a YouTube URL in the **Single Download** section.
2.  Select the preferred audio quality.
3.  Choose the destination folder (default: `downloads/`).
4.  Click **Download MP3**.

### Batch Download
1.  Paste multiple URLs (one per line) or click **Import** to load a `.txt` file.
2.  Select desired quality and output directory.
3.  Click **Download All**.

### Building the Executable
To generate your own standalone Windows executable:
```bash
python create_exe.py

```
## Legal Disclaimer & Copyright Notice

### **Important Legal Information**

**THIS SOFTWARE IS PROVIDED FOR EDUCATIONAL AND PERSONAL USE ONLY.**

### **User Responsibilities**

By using this software, you acknowledge and agree that:

1. **Copyright Compliance**: You are solely responsible for ensuring that any content you download does not infringe upon copyright laws.
2. **YouTube Terms of Service**: You must comply with YouTube's Terms of Service, which prohibit unauthorized downloading of content unless explicitly permitted.
3. **Fair Use Doctrine**: If applicable in your jurisdiction, only download content under fair use provisions for:
   - Personal/educational research
   - Criticism or commentary
   - News reporting
   - Teaching/scholarship

### **Permitted Uses**

You may only use this software to download:

- Content you own or have created
- Content with explicit permission from the copyright holder
- Public domain content
- Creative Commons licensed content (check specific license terms)
- Content where downloading is explicitly allowed by the platform

### **Prohibited Uses**

Do NOT use this software for:

- Commercial redistribution of copyrighted content
- Mass downloading of copyrighted material
- Circumventing digital rights management (DRM)
- Downloading content you do not have rights to
- Any activity that violates local copyright laws

### **Developer's Stance**

The developer:
- Does not condone or encourage copyright infringement
- Assumes no responsibility for misuse of this software
- Provides this tool for legitimate, legal purposes only
- Encourages users to support content creators through official channels

### **Support Content Creators**

Consider these alternatives to support creators:
- Watch videos on YouTube (generates ad revenue)
- Subscribe to YouTube Premium
- Use official music services (Spotify, Apple Music, etc.)
- Purchase content through legitimate platforms
- Support creators via Patreon, merchandise, or donations

### **Legal Consequences**

Unauthorized downloading may result in:
- Copyright infringement notices
- Legal action from copyright holders
- Account suspension on platforms
- Fines or other penalties under applicable laws

### **Regional Laws**

Copyright laws vary by country/region. Familiarize yourself with:
- The Digital Millennium Copyright Act (DMCA) in the US
- The Copyright Directive in the EU
- Local copyright legislation in your jurisdiction

---

**By using this software, you certify that you will only download content you have explicit rights to, and accept full responsibility for your actions.**

*After running `python create_exe.py`, the built executable can be found in the project's `dist/` directory.*
