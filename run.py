"""
run.py - Launcher for YouTube to MP3 Converter
"""
import os
import sys
import subprocess

def check_dependencies():
    """Check and install required dependencies"""
    try:
        import yt_dlp
        print("✓ yt-dlp is already installed")
    except ImportError:
        print("Installing yt-dlp...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
            print("✓ yt-dlp installed successfully")
        except Exception as e:
            print(f"✗ Failed to install yt-dlp: {e}")
            print("\nPlease install manually:")
            print("pip install yt-dlp")
            input("\nPress Enter to exit...")
            sys.exit(1)
    
    # Check for FFmpeg
    print("\nChecking for FFmpeg...")
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✓ FFmpeg is available")
    except:
        print("⚠ FFmpeg not found in PATH")
        print("\nFFmpeg is required for audio conversion.")
        print("Download from: https://ffmpeg.org/download.html")
        print("Then add ffmpeg.exe to this folder or add to system PATH")
        print("\nYou can continue, but audio conversion may fail.")

def main():
    print("=" * 50)
    print("YouTube to MP3 Converter")
    print("=" * 50)
    print()
    
    # Check dependencies
    check_dependencies()
    
    print("\n" + "=" * 50)
    print("Starting GUI application...")
    print("=" * 50)
    
    try:
        from main import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure all files are in the same directory:")
        print("  - main.py")
        print("  - converter.py")
        print("  - batch_processor.py")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()