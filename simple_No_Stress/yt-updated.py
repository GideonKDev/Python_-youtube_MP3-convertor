import sys
import subprocess
import os

def install_requirements():
    """Install required packages if missing"""
    required = ['yt-dlp']
    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install dependencies before importing
install_requirements()

# Now import yt_dlp
import yt_dlp

def youtube_to_mp3(url, output_folder="mp3_downloads"):
    os.makedirs(output_folder, exist_ok=True)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_folder}/%(title)s.mp3',  # Force .mp3 extension
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
        'keepvideo': False,
        'writethumbnail': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            print(f"Downloaded: {info.get('title', 'Unknown')}")n
            print(f"Saved to: {output_folder}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Check if FFmpeg is installed (optional but recommended)
    ffmpeg_check = input("Do you have FFmpeg installed? (y/n): ").lower()
    if ffmpeg_check != 'y':
        print("\nFFmpeg is required for audio conversion.")
        print("Download from: https://ffmpeg.org/download.html")
        print("Add to PATH or place ffmpeg.exe in this folder")
        input("Press Enter after installing FFmpeg...")
    
    youtube_url = input("\nEnter YouTube URL: ").strip()
    youtube_to_mp3(youtube_url)