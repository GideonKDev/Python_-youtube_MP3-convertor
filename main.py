"""
main.py - Complete YouTube to MP3 Converter GUI
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import time

# Install yt-dlp if missing
import subprocess
import sys

def install_requirements():
    """Install required packages if missing"""
    required = ['yt-dlp']
    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_requirements()

# Now import yt_dlp
import yt_dlp

# ===========================================
# SIMPLE WORKING CONVERTER FUNCTIONS
# ===========================================

def clean_filename(filename, max_length=200):
    """Remove invalid characters from filename"""
    import re
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    filename = re.sub(r'\s+', ' ', filename)
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length-len(ext)] + ext
    return filename.strip()

def get_video_info(url):
    """Get video information without downloading - SIMPLE VERSION"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # ALWAYS return a dict
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'thumbnail': info.get('thumbnail', ''),
                'view_count': info.get('view_count', 0),
            }
    except Exception as e:
        # ALWAYS return a dict, not a string
        return {'error': str(e)}

def youtube_to_mp3(url, output_folder="downloads", quality='192'):
    """
    SIMPLE WORKING VERSION of YouTube to MP3 converter
    This matches your working code
    """
    os.makedirs(output_folder, exist_ok=True)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality,
        }],
        'quiet': True,
        'keepvideo': False,
        'writethumbnail': False,
    }
    
    # ADD FFMPEG PATH HERE - This is the critical fix
    ffmpeg_path = r"C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-essentials_build\bin"
    
    if os.path.exists(os.path.join(ffmpeg_path, "ffmpeg.exe")):
        ydl_opts['ffmpeg_location'] = ffmpeg_path
        print(f"Using FFmpeg from: {ffmpeg_path}")
    else:
        print(f"Warning: FFmpeg not found at: {ffmpeg_path}")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'audio_download')
            filename = os.path.join(output_folder, f"{clean_filename(title)}.mp3")
            
            return {
                'success': True,
                'filename': filename,
                'title': title,
                'url': url
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'url': url
        }
def batch_download(urls, output_folder="downloads", quality='192'):
    """
    Simple batch download
    """
    results = []
    total = len(urls)
    
    for i, url in enumerate(urls, 1):
        try:
            print(f"[{i}/{total}] Processing: {url[:50]}...")
            result = youtube_to_mp3(url, output_folder, quality)
            results.append(result)
            
            if isinstance(result, dict) and result.get('success'):
                print(f"    ✓ Success: {result.get('title', 'Unknown')}")
            else:
                error_msg = result.get('error', 'Unknown error') if isinstance(result, dict) else str(result)
                print(f"    ✗ Failed: {error_msg}")
                
        except Exception as e:
            results.append({'success': False, 'error': str(e), 'url': url})
            print(f"    ✗ Error: {e}")
    
    return results

# ===========================================
# BATCH PROCESSOR FUNCTIONS
# ===========================================

def read_urls_from_file(filepath):
    """Read URLs from text file"""
    urls = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.append(line)
        return urls
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

def save_batch_results(results, output_file="batch_results.json"):
    """Save batch download results to JSON file"""
    import json
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving results: {e}")
        return False

def validate_urls(urls):
    """Validate YouTube URLs"""
    validated = []
    invalid = []
    
    for url in urls:
        if 'youtube.com/watch' in url or 'youtu.be/' in url:
            validated.append(url)
        else:
            invalid.append(url)
    
    return validated, invalid

# ===========================================
# GUI APPLICATION
# ===========================================

class YouTubeToMP3Converter:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("YouTube to MP3 Converter Pro")
        self.window.geometry("800x600")
        self.window.configure(bg="#f0f0f0")
        
        # Variables
        self.output_folder = tk.StringVar(value=os.path.join(os.getcwd(), "downloads"))
        self.quality = tk.StringVar(value="192")
        self.downloading = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title_frame = tk.Frame(self.window, bg="#f0f0f0")
        title_frame.pack(pady=20)
        
        tk.Label(title_frame, text="YouTube to MP3 Converter", 
                font=("Arial", 20, "bold"), bg="#f0f0f0").pack()
        tk.Label(title_frame, text="Convert YouTube videos to MP3 audio files", 
                font=("Arial", 10), bg="#f0f0f0", fg="#666").pack()
        
        # Main container
        container = tk.Frame(self.window, bg="#f0f0f0")
        container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left panel - Single download
        left_panel = tk.LabelFrame(container, text="Single Download", 
                                  font=("Arial", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # URL input
        tk.Label(left_panel, text="YouTube URL:", bg="#f0f0f0", 
                font=("Arial", 10)).pack(anchor="w", pady=(0, 5))
        self.url_entry = tk.Entry(left_panel, width=40, font=("Arial", 10))
        self.url_entry.pack(fill="x", pady=(0, 10))
        
        # Quality selection
        tk.Label(left_panel, text="Audio Quality:", bg="#f0f0f0", 
                font=("Arial", 10)).pack(anchor="w", pady=(0, 5))
        
        quality_frame = tk.Frame(left_panel, bg="#f0f0f0")
        quality_frame.pack(fill="x", pady=(0, 10))
        
        qualities = [("128 kbps (Small)", "128"), 
                    ("192 kbps (Recommended)", "192"), 
                    ("320 kbps (High)", "320")]
        
        for text, value in qualities:
            rb = tk.Radiobutton(quality_frame, text=text, variable=self.quality, 
                               value=value, bg="#f0f0f0")
            rb.pack(anchor="w")
        
        # Output folder
        tk.Label(left_panel, text="Save to:", bg="#f0f0f0", 
                font=("Arial", 10)).pack(anchor="w", pady=(0, 5))
        
        folder_frame = tk.Frame(left_panel, bg="#f0f0f0")
        folder_frame.pack(fill="x", pady=(0, 10))
        
        tk.Entry(folder_frame, textvariable=self.output_folder, 
                font=("Arial", 10)).pack(side="left", fill="x", expand=True)
        tk.Button(folder_frame, text="Browse", command=self.select_folder, 
                 bg="#4CAF50", fg="white").pack(side="right", padx=(5, 0))
        
        # Single download button
        tk.Button(left_panel, text="Download MP3", command=self.start_single_download,
                 bg="#2196F3", fg="white", font=("Arial", 11, "bold"),
                 height=2, width=20).pack(pady=20)
        
        # Right panel - Batch download
        right_panel = tk.LabelFrame(container, text="Batch Download", 
                                   font=("Arial", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Batch URL input
        tk.Label(right_panel, text="Enter URLs (one per line):", bg="#f0f0f0", 
                font=("Arial", 10)).pack(anchor="w", pady=(0, 5))
        
        self.batch_text = scrolledtext.ScrolledText(right_panel, width=40, height=10,
                                                   font=("Courier", 9))
        self.batch_text.pack(fill="both", expand=True, pady=(0, 10))
        
        # Batch buttons
        button_frame = tk.Frame(right_panel, bg="#f0f0f0")
        button_frame.pack(fill="x", pady=(0, 10))
        
        tk.Button(button_frame, text="Load from File", command=self.load_urls_file,
                 bg="#FF9800", fg="white").pack(side="left", padx=(0, 5))
        tk.Button(button_frame, text="Clear All", command=self.clear_urls,
                 bg="#f44336", fg="white").pack(side="left")
        
        # Batch download button
        tk.Button(right_panel, text="Download All", command=self.start_batch_download,
                 bg="#9C27B0", fg="white", font=("Arial", 11, "bold"),
                 height=2, width=20).pack(pady=10)
        
        # Status area
        status_frame = tk.Frame(self.window, bg="#f0f0f0")
        status_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        tk.Label(status_frame, text="Status:", bg="#f0f0f0", 
                font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=6,
                                                    font=("Courier", 9))
        self.status_text.pack(fill="x")
        self.status_text.config(state="disabled")
        
        # Progress bar
        self.progress = ttk.Progressbar(self.window, mode="indeterminate")
        self.progress.pack(fill="x", padx=20, pady=(0, 10))
        
    def log_message(self, message, color="black"):
        """Add message to status text"""
        self.status_text.config(state="normal")
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert("end", f"[{timestamp}] {message}\n", color)
        self.status_text.see("end")
        self.status_text.config(state="disabled")
        self.window.update()
    
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder.set(folder)
    
    def load_urls_file(self):
        filepath = filedialog.askopenfilename(
            title="Select URLs file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filepath:
            urls = read_urls_from_file(filepath)
            self.batch_text.delete("1.0", "end")
            for url in urls:
                self.batch_text.insert("end", url + "\n")
            self.log_message(f"Loaded {len(urls)} URLs from file", "blue")
    
    def clear_urls(self):
        self.batch_text.delete("1.0", "end")
        self.log_message("URL list cleared", "orange")
    
    def start_single_download(self):
        if self.downloading:
            messagebox.showwarning("Warning", "A download is already in progress")
            return
        
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        # Validate URL
        if 'youtube.com' not in url and 'youtu.be' not in url:
            if messagebox.askyesno("Warning", 
                                  "This doesn't look like a YouTube URL. Continue anyway?"):
                pass
            else:
                return
        
        self.downloading = True
        self.progress.start()
        
        # Start download in separate thread
        thread = threading.Thread(target=self.download_single, args=(url,))
        thread.daemon = True
        thread.start()
    
    def download_single(self, url):
        try:
            self.log_message(f"Starting download: {url[:50]}...", "blue")
            
            # Get video info first
            info = get_video_info(url)
            
            # Check if info is valid
            if isinstance(info, dict) and 'error' in info:
                self.log_message(f"Error: {info['error']}", "red")
                return
            
            if isinstance(info, dict):
                title = info.get('title', 'Unknown Video')
                self.log_message(f"Title: {title}", "green")
            
            # Download - USING THE SIMPLE WORKING VERSION
            result = youtube_to_mp3(
                url, 
                self.output_folder.get(), 
                self.quality.get()
            )
            
            # SAFELY check result - result is ALWAYS a dict from our simple version
            if result.get('success'):
                filename = result.get('filename', 'Unknown')
                title = result.get('title', 'Unknown')
                self.log_message(f"✓ Download complete: {filename}", "green")
                
                # Show success message
                self.window.after(0, lambda: messagebox.showinfo(
                    "Success", 
                    f"Download complete!\n\n"
                    f"Title: {title}\n"
                    f"Saved to: {filename}"
                ))
            else:
                error_msg = result.get('error', 'Unknown error')
                self.log_message(f"✗ Download failed: {error_msg}", "red")
                
        except Exception as e:
            self.log_message(f"✗ Error: {str(e)}", "red")
        finally:
            self.downloading = False
            self.window.after(0, self.progress.stop)
    
    def start_batch_download(self):
        if self.downloading:
            messagebox.showwarning("Warning", "A download is already in progress")
            return
        
        # Get URLs from text widget
        urls_text = self.batch_text.get("1.0", "end").strip()
        if not urls_text:
            messagebox.showerror("Error", "Please enter some URLs")
            return
        
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        # Validate URLs
        valid_urls, invalid_urls = validate_urls(urls)
        
        if invalid_urls:
            msg = f"Found {len(invalid_urls)} invalid URLs:\n"
            msg += "\n".join(invalid_urls[:5])
            if len(invalid_urls) > 5:
                msg += f"\n...and {len(invalid_urls)-5} more"
            
            if not messagebox.askyesno("Warning", 
                                      f"{msg}\n\nContinue with valid URLs only?"):
                return
            urls = valid_urls
        
        if not urls:
            messagebox.showerror("Error", "No valid URLs to download")
            return
        
        self.downloading = True
        self.progress.start()
        
        # Start batch download in thread
        thread = threading.Thread(target=self.download_batch, args=(urls,))
        thread.daemon = True
        thread.start()
    
    def download_batch(self, urls):
        try:
            self.log_message(f"Starting batch download of {len(urls)} URLs...", "blue")
            
            results = batch_download(
                urls, 
                self.output_folder.get(), 
                self.quality.get()
            )
            
            # Count successes
            successes = 0
            for r in results:
                if isinstance(r, dict) and r.get('success'):
                    successes += 1
            failures = len(urls) - successes
            
            self.log_message(f"Batch complete: {successes} succeeded, {failures} failed", 
                           "green" if failures == 0 else "orange")
            
            # Save results
            save_batch_results(results, "batch_results.json")
            self.log_message("Results saved to batch_results.json", "blue")
            
            # Show summary
            self.window.after(0, lambda: messagebox.showinfo(
                "Batch Complete",
                f"Downloaded {successes} of {len(urls)} files\n\n"
                f"Results saved to: batch_results.json"
            ))
            
        except Exception as e:
            self.log_message(f"✗ Batch error: {str(e)}", "red")
        finally:
            self.downloading = False
            self.window.after(0, self.progress.stop)
    
    def run(self):
        # Configure text colors
        self.status_text.tag_config("black", foreground="black")
        self.status_text.tag_config("blue", foreground="blue")
        self.status_text.tag_config("green", foreground="green")
        self.status_text.tag_config("red", foreground="red")
        self.status_text.tag_config("orange", foreground="orange")
        
        # Check for FFmpeg - IMPROVED VERSION
        ffmpeg_path = r"C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"
        
        if os.path.exists(ffmpeg_path):
            self.log_message(f"✓ FFmpeg found: {ffmpeg_path}", "green")
        else:
            self.log_message("✗ FFmpeg not found at expected location", "red")
            self.log_message("Please ensure FFmpeg is installed", "red")
        
        self.window.mainloop()
    

def main():
    """Main entry point"""
    app = YouTubeToMP3Converter()
    app.run()

if __name__ == "__main__":
    main()