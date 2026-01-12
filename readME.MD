# YouTube to MP3 Converter

A Python-based desktop application designed to convert YouTube videos into high-quality MP3 audio files. This tool provides a clean graphical user interface (GUI) and supports both single and batch do[...]

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

*After running `python create_exe.py`, the built executable can be found in the project's `dist/` directory.*
