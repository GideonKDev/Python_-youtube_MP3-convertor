"""
main.py - Complete YouTube to MP3 Converter GUI
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import time
from converter import youtube_to_mp3, get_video_info, batch_download
from batch_processor import read_urls_from_file, save_batch_results, validate_urls

class YouTubeToMP3Converter:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("YouTube to MP3 Converter Pro")
        self.window.geometry("800x600")
        self.window.configure(bg="#f0f0f0")
        
        # Set icon (if available)
        try:
            self.window.iconbitmap('assets/icon.ico')
        except:
            pass
        
        # Variables
        self.output_folder = tk.StringVar(value=os.path.join(os.getcwd(), "downloads"))
        self.quality = tk.StringVar(value="192")
        self.downloading = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title_frame = tk.Frame(self.window, bg="#f0f0f0")
        title_frame.pack(pady=20)
        
        tk.Label(title_frame, text="🎵 YouTube to MP3 Converter", 
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
            if 'error' in info:
                self.log_message(f"Error: {info['error']}", "red")
                return
            
            self.log_message(f"Title: {info['title']}", "green")
            
            # Download
            result = youtube_to_mp3(
                url, 
                self.output_folder.get(), 
                self.quality.get()
            )
            
            if result['success']:
                self.log_message(f"✓ Download complete: {result['filename']}", "green")
                
                # Show success message
                self.window.after(0, lambda: messagebox.showinfo(
                    "Success", 
                    f"Download complete!\n\n"
                    f"Title: {result['title']}\n"
                    f"Saved to: {result['filename']}"
                ))
            else:
                self.log_message(f"✗ Download failed: {result.get('error', 'Unknown error')}", "red")
                
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
            successes = sum(1 for r in results if r.get('success', False))
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
        
        self.window.mainloop()

def main():
    """Main entry point"""
    app = YouTubeToMP3Converter()
    app.run()

if __name__ == "__main__":
    main()