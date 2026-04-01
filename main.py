"""
main.py - YouTube to MP3/MP4 Converter — Modernized Edition
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import time
import subprocess
import sys
import json
import re
import shutil

# ── Auto-install yt-dlp ──────────────────────────────────────────────────────

def install_requirements():
    for package in ['yt-dlp', 'Pillow']:
        try:
            __import__(package.replace('-', '_').split('.')[0])
        except ImportError:
            print(f"Installing {package}…")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

install_requirements()

import yt_dlp
try:
    from PIL import Image, ImageTk
    import urllib.request
    import io
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# ── Helpers ──────────────────────────────────────────────────────────────────

COLORS = {
    "bg":         "#FFFFFF",
    "surface":    "#F7F7F5",
    "border":     "#E5E3DC",
    "accent":     "#5B4FCF",
    "accent_lt":  "#EAE8FB",
    "success":    "#2D9E75",
    "success_lt": "#E1F5EE",
    "danger":     "#C44B2E",
    "danger_lt":  "#FAECE7",
    "warn":       "#B87510",
    "warn_lt":    "#FAEEDA",
    "text":       "#1A1A18",
    "muted":      "#6B6A65",
    "subtle":     "#A8A79F",
    "white":      "#FFFFFF",
}

FONT_FAMILY = "Segoe UI" if sys.platform == "win32" else \
              "SF Pro Text" if sys.platform == "darwin" else "DejaVu Sans"

def find_ffmpeg():
    """Return ffmpeg path: system PATH first, then common install dirs."""
    if shutil.which("ffmpeg"):
        return None  # yt-dlp will find it itself
    candidates = [
        r"C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-essentials_build\bin",
        r"C:\ffmpeg\bin",
        r"C:\Program Files\ffmpeg\bin",
        "/usr/local/bin",
        "/opt/homebrew/bin",
    ]
    for p in candidates:
        if os.path.exists(os.path.join(p, "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")):
            return p
    return None

def clean_filename(filename, max_length=200):
    invalid = r'<>:"/\\|?*'
    for c in invalid:
        filename = filename.replace(c, '')
    filename = re.sub(r'\s+', ' ', filename).strip()
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length - len(ext)] + ext
    return filename

def format_duration(seconds):
    if not seconds:
        return "—"
    h, r = divmod(int(seconds), 3600)
    m, s = divmod(r, 60)
    return f"{h}:{m:02}:{s:02}" if h else f"{m}:{s:02}"

def format_views(n):
    if not n:
        return "—"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M views"
    if n >= 1_000:
        return f"{n/1_000:.0f}K views"
    return f"{n} views"

def validate_urls(urls):
    valid, invalid = [], []
    for url in urls:
        if re.search(r'(youtube\.com|youtu\.be)', url):
            valid.append(url)
        else:
            invalid.append(url)
    return valid, invalid

def is_playlist_or_channel(url):
    return bool(re.search(r'(list=|/playlist|/channel|/@)', url))


# ── Core download logic ───────────────────────────────────────────────────────

def get_video_info(url):
    opts = {'quiet': True, 'no_warnings': True, 'skip_download': True}
    ffmpeg = find_ffmpeg()
    if ffmpeg:
        opts['ffmpeg_location'] = ffmpeg
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title':     info.get('title', 'Unknown'),
                'duration':  info.get('duration', 0),
                'uploader':  info.get('uploader', 'Unknown'),
                'thumbnail': info.get('thumbnail', ''),
                'view_count':info.get('view_count', 0),
                'upload_date': info.get('upload_date', ''),
                'is_playlist': 'entries' in info,
                'entry_count': len(list(info.get('entries', []))) if 'entries' in info else 1,
            }
    except Exception as e:
        return {'error': str(e)}


def build_ydl_opts(output_folder, format_type, quality, progress_hook=None, cancel_event=None):
    opts = {
        'quiet': True,
        'no_warnings': True,
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
    }
    ffmpeg = find_ffmpeg()
    if ffmpeg:
        opts['ffmpeg_location'] = ffmpeg

    if progress_hook:
        opts['progress_hooks'] = [progress_hook]

    if format_type == 'mp3':
        opts['format'] = 'bestaudio/best'
        opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality,
        }]
        opts['keepvideo'] = False
    else:
        quality_map = {
            '360p':  'bestvideo[height<=360]+bestaudio/best[height<=360]',
            '480p':  'bestvideo[height<=480]+bestaudio/best[height<=480]',
            '720p':  'bestvideo[height<=720]+bestaudio/best[height<=720]',
            '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            'best':  'bestvideo+bestaudio/best',
        }
        opts['format'] = quality_map.get(quality, 'bestvideo+bestaudio/best')
        opts['merge_output_format'] = 'mp4'

    return opts


def download_youtube(url, output_folder, format_type, quality,
                     progress_hook=None, cancel_event=None):
    os.makedirs(output_folder, exist_ok=True)

    downloaded_title = [None]

    def _hook(d):
        if cancel_event and cancel_event.is_set():
            raise yt_dlp.utils.DownloadError("Cancelled by user")
        if d.get('status') == 'finished':
            downloaded_title[0] = d.get('info_dict', {}).get('title')
        if progress_hook:
            progress_hook(d)

    opts = build_ydl_opts(output_folder, format_type, quality, _hook, cancel_event)
    ext = 'mp3' if format_type == 'mp3' else 'mp4'

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'download')
            filename = os.path.join(output_folder, f"{clean_filename(title)}.{ext}")
            return {
                'success': True,
                'filename': filename,
                'title': title,
                'format': format_type.upper(),
                'quality': quality,
                'url': url,
            }
    except Exception as e:
        if 'Cancelled' in str(e):
            return {'success': False, 'cancelled': True, 'error': 'Cancelled', 'url': url}
        return {'success': False, 'error': str(e), 'url': url}


def batch_download(urls, output_folder, format_type, quality,
                   per_result_cb=None, progress_hook=None, cancel_event=None):
    results = []
    for i, url in enumerate(urls):
        if cancel_event and cancel_event.is_set():
            break
        result = download_youtube(url, output_folder, format_type, quality,
                                  progress_hook, cancel_event)
        results.append(result)
        if per_result_cb:
            per_result_cb(i + 1, len(urls), result)
    return results


# ── History store ─────────────────────────────────────────────────────────────

HISTORY_FILE = os.path.join(os.path.expanduser("~"), ".yt_converter_history.json")

def load_history():
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_history(history):
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history[-200:], f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def append_history(entry):
    h = load_history()
    h.append(entry)
    save_history(h)


# ── GUI ───────────────────────────────────────────────────────────────────────

# ── Tiny inline icon canvases ─────────────────────────────────────────────────
# These are drawn into tk.Canvas widgets small enough to embed in a Text widget
# via window_create, replacing emoji/Unicode symbols entirely.

def _make_icon(parent, kind, size=13):
    """
    Return a tk.Canvas that draws a crisp flat icon.
    kind: 'ok' (green checkmark), 'fail' (red X), 'warn' (amber triangle/!)
    """
    color_map = {
        'ok':   (COLORS['success'],  COLORS['success_lt']),
        'fail': (COLORS['danger'],   COLORS['danger_lt']),
        'warn': (COLORS['warn'],     COLORS['warn_lt']),
        'info': (COLORS['accent'],   COLORS['accent_lt']),
    }
    fg, bg = color_map.get(kind, (COLORS['muted'], COLORS['surface']))
    c = tk.Canvas(parent, width=size, height=size, bg=COLORS['surface'],
                  highlightthickness=0, bd=0)
    h = size
    if kind == 'ok':
        # Filled circle background
        c.create_oval(1, 1, h-1, h-1, fill=bg, outline=fg, width=1)
        # Checkmark
        m = h * 0.18
        c.create_line(m, h*0.52, h*0.42, h*0.76, h-m, h*0.28,
                      fill=fg, width=1.5, joinstyle="round", capstyle="round")
    elif kind == 'fail':
        c.create_oval(1, 1, h-1, h-1, fill=bg, outline=fg, width=1)
        p = h * 0.28
        c.create_line(p, p, h-p, h-p, fill=fg, width=1.5, capstyle="round")
        c.create_line(h-p, p, p, h-p, fill=fg, width=1.5, capstyle="round")
    elif kind == 'warn':
        # Triangle
        mid = h / 2
        pts = [mid, 1, h-1, h-1, 1, h-1]
        c.create_polygon(pts, fill=bg, outline=fg, width=1)
        # Exclamation
        c.create_line(mid, h*0.38, mid, h*0.65, fill=fg, width=1.5, capstyle="round")
        c.create_oval(mid-1, h*0.72, mid+1, h*0.74+1.5, fill=fg, outline=fg)
    elif kind == 'info':
        c.create_oval(1, 1, h-1, h-1, fill=bg, outline=fg, width=1)
        mid = h / 2
        c.create_line(mid, h*0.28, mid, h*0.35, fill=fg, width=1.5, capstyle="round")
        c.create_line(mid, h*0.44, mid, h*0.74, fill=fg, width=1.5, capstyle="round")
    return c


# Map log colour tags to icon kinds
_TAG_ICON = {
    'success': 'ok',
    'danger':  'fail',
    'warn':    'warn',
    'accent':  'info',
}


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _=None):
        x, y, _, cy = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + self.widget.winfo_height()
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        tk.Label(self.tip, text=self.text, bg="#2C2C2A", fg="white",
                 font=(FONT_FAMILY, 9), padx=8, pady=4).pack()

    def hide(self, _=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


class FlatButton(tk.Label):
    """Flat, styled button using Label for full color control."""
    def __init__(self, parent, text, command=None, bg=None, fg=None,
                 hover_bg=None, font_size=10, padx=16, pady=8, **kw):
        self._bg     = bg       or COLORS['accent']
        self._fg     = fg       or COLORS['white']
        self._hbg    = hover_bg or COLORS['accent']
        self._cmd    = command
        super().__init__(parent, text=text,
                         bg=self._bg, fg=self._fg,
                         font=(FONT_FAMILY, font_size),
                         cursor="hand2", padx=padx, pady=pady,
                         relief="flat", **kw)
        self.bind("<Button-1>", self._click)
        self.bind("<Enter>",    lambda e: self.config(bg=self._hbg))
        self.bind("<Leave>",    lambda e: self.config(bg=self._bg))

    def _click(self, _):
        if self._cmd:
            self._cmd()

    def set_state(self, enabled=True):
        if enabled:
            self.config(bg=self._bg, fg=self._fg, cursor="hand2")
        else:
            self.config(bg=COLORS['border'], fg=COLORS['muted'], cursor="arrow")
            self._cmd = None


class YouTubeConverter:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("YT Converter")
        self.window.geometry("980x720")
        self.window.configure(bg=COLORS['bg'])
        self.window.resizable(True, True)

        # State
        self.output_folder  = tk.StringVar(value=os.path.join(os.getcwd(), "downloads"))
        self.format_type    = tk.StringVar(value="mp3")
        self.mp3_quality    = tk.StringVar(value="192")
        self.mp4_quality    = tk.StringVar(value="720p")
        self.batch_format   = tk.StringVar(value="mp3")
        self.downloading    = False
        self.cancel_event   = threading.Event()
        self._thumb_ref     = None   # keep PhotoImage alive
        self._last_info     = {}
        self._tab           = tk.StringVar(value="single")

        self._build_ui()
        self._check_ffmpeg()
        self._try_paste_from_clipboard()

    # ── UI Build ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header
        hdr = tk.Frame(self.window, bg=COLORS['accent'], height=52)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="YT Converter", bg=COLORS['accent'], fg=COLORS['white'],
                 font=(FONT_FAMILY, 14, "bold")).pack(side="left", padx=20)
        tk.Label(hdr, text="MP3 / MP4 downloader", bg=COLORS['accent'],
                 fg="#C9C6F8", font=(FONT_FAMILY, 10)).pack(side="left")

        # ── Tab bar
        tab_bar = tk.Frame(self.window, bg=COLORS['surface'],
                           highlightbackground=COLORS['border'], highlightthickness=1)
        tab_bar.pack(fill="x")
        self._tab_btns = {}
        for label, key in [("Single Download", "single"),
                            ("Batch Download",  "batch"),
                            ("History",         "history")]:
            btn = tk.Label(tab_bar, text=label, bg=COLORS['surface'], fg=COLORS['muted'],
                           font=(FONT_FAMILY, 10), cursor="hand2", padx=20, pady=10)
            btn.pack(side="left")
            btn.bind("<Button-1>", lambda e, k=key: self._switch_tab(k))
            self._tab_btns[key] = btn

        # ── Pages — must be built before _switch_tab is first called
        self._pages = {}

        single_pg = tk.Frame(self.window, bg=COLORS['bg'])
        self._pages['single']  = single_pg
        self._build_single(single_pg)

        batch_pg = tk.Frame(self.window, bg=COLORS['bg'])
        self._pages['batch']   = batch_pg
        self._build_batch(batch_pg)

        hist_pg = tk.Frame(self.window, bg=COLORS['bg'])
        self._pages['history'] = hist_pg
        self._build_history(hist_pg)

        # Activate default tab now that all pages exist
        self._switch_tab("single")

        # ── Status bar (always visible)
        self._build_status_bar()

    def _switch_tab(self, key):
        for k, btn in self._tab_btns.items():
            if k == key:
                btn.config(fg=COLORS['accent'], bg=COLORS['bg'],
                           font=(FONT_FAMILY, 10, "bold"))
            else:
                btn.config(fg=COLORS['muted'], bg=COLORS['surface'],
                           font=(FONT_FAMILY, 10))
        for k, pg in self._pages.items():
            if k == key:
                pg.pack(fill="both", expand=True)
            else:
                pg.pack_forget()
        self._tab.set(key)

    # ── Single Download page ──────────────────────────────────────────────────

    def _build_single(self, parent):
        outer = tk.Frame(parent, bg=COLORS['bg'])
        outer.pack(fill="both", expand=True, padx=24, pady=20)

        # Left column
        left = tk.Frame(outer, bg=COLORS['bg'])
        left.pack(side="left", fill="both", expand=True, padx=(0, 16))

        # URL row
        url_row = tk.Frame(left, bg=COLORS['bg'])
        url_row.pack(fill="x", pady=(0, 12))
        tk.Label(url_row, text="YouTube URL", bg=COLORS['bg'], fg=COLORS['muted'],
                 font=(FONT_FAMILY, 9)).pack(anchor="w")
        entry_row = tk.Frame(url_row, bg=COLORS['bg'])
        entry_row.pack(fill="x", pady=(4, 0))
        self.url_entry = tk.Entry(entry_row, font=(FONT_FAMILY, 11),
                                  bg=COLORS['surface'], fg=COLORS['text'],
                                  insertbackground=COLORS['text'],
                                  relief="flat", highlightthickness=1,
                                  highlightbackground=COLORS['border'],
                                  highlightcolor=COLORS['accent'])
        self.url_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        self.url_entry.bind("<Return>", lambda e: self._fetch_info())
        FlatButton(entry_row, "Preview", command=self._fetch_info,
                   bg=COLORS['surface'], fg=COLORS['accent'],
                   hover_bg=COLORS['accent_lt'], font_size=9, padx=12, pady=8).pack(side="left")

        # Preview card
        self._prev_card = tk.Frame(left, bg=COLORS['surface'],
                                   highlightbackground=COLORS['border'],
                                   highlightthickness=1)
        self._prev_card.pack(fill="x", pady=(0, 12))
        self._prev_card.pack_propagate(False)
        self._prev_card.config(height=90)
        self._prev_placeholder = tk.Label(self._prev_card,
                                          text="Paste a URL and click Preview to see video info",
                                          bg=COLORS['surface'], fg=COLORS['subtle'],
                                          font=(FONT_FAMILY, 10))
        self._prev_placeholder.pack(expand=True)

        # Format + Quality
        fmt_row = tk.Frame(left, bg=COLORS['bg'])
        fmt_row.pack(fill="x", pady=(0, 8))
        tk.Label(fmt_row, text="Format", bg=COLORS['bg'], fg=COLORS['muted'],
                 font=(FONT_FAMILY, 9)).pack(anchor="w")

        pill_row = tk.Frame(fmt_row, bg=COLORS['bg'])
        pill_row.pack(anchor="w", pady=(4, 0))
        self._fmt_btns = {}
        for label, val in [("MP3 Audio", "mp3"), ("MP4 Video", "mp4")]:
            b = tk.Label(pill_row, text=label, bg=COLORS['surface'], fg=COLORS['muted'],
                         font=(FONT_FAMILY, 9), padx=14, pady=6, cursor="hand2",
                         relief="flat", highlightthickness=1,
                         highlightbackground=COLORS['border'])
            b.pack(side="left", padx=(0, 6))
            b.bind("<Button-1>", lambda e, v=val: self._set_format(v))
            self._fmt_btns[val] = b

        self._quality_row = tk.Frame(left, bg=COLORS['bg'])
        self._quality_row.pack(fill="x", pady=(0, 12))
        self._set_format("mp3")

        # Output folder
        folder_row = tk.Frame(left, bg=COLORS['bg'])
        folder_row.pack(fill="x", pady=(0, 16))
        tk.Label(folder_row, text="Save to", bg=COLORS['bg'], fg=COLORS['muted'],
                 font=(FONT_FAMILY, 9)).pack(anchor="w")
        frow = tk.Frame(folder_row, bg=COLORS['bg'])
        frow.pack(fill="x", pady=(4, 0))
        tk.Entry(frow, textvariable=self.output_folder, font=(FONT_FAMILY, 9),
                 bg=COLORS['surface'], fg=COLORS['text'],
                 relief="flat", highlightthickness=1,
                 highlightbackground=COLORS['border'],
                 highlightcolor=COLORS['accent']).pack(side="left", fill="x", expand=True,
                                                       ipady=6, padx=(0, 8))
        FlatButton(frow, "Browse", command=self._select_folder,
                   bg=COLORS['surface'], fg=COLORS['muted'],
                   hover_bg=COLORS['accent_lt'], font_size=9, padx=10, pady=6).pack(side="left")

        # Action buttons
        btn_row = tk.Frame(left, bg=COLORS['bg'])
        btn_row.pack(fill="x")
        self._dl_btn = FlatButton(btn_row, "Download", command=self._start_single,
                                  font_size=11, padx=24, pady=10)
        self._dl_btn.pack(side="left", padx=(0, 10))
        self._cancel_btn = FlatButton(btn_row, "Cancel", command=self._cancel_download,
                                      bg=COLORS['surface'], fg=COLORS['danger'],
                                      hover_bg=COLORS['danger_lt'],
                                      font_size=10, padx=14, pady=10)
        self._cancel_btn.pack(side="left", padx=(0, 10))
        FlatButton(btn_row, "Open folder", command=self._open_output_folder,
                   bg=COLORS['surface'], fg=COLORS['muted'],
                   hover_bg=COLORS['accent_lt'],
                   font_size=9, padx=12, pady=10).pack(side="left")

        # Right column — log
        right = tk.Frame(outer, bg=COLORS['bg'], width=300)
        right.pack(side="right", fill="both")
        right.pack_propagate(False)
        tk.Label(right, text="Log", bg=COLORS['bg'], fg=COLORS['muted'],
                 font=(FONT_FAMILY, 9)).pack(anchor="w", pady=(0, 4))
        self.log_text = scrolledtext.ScrolledText(
            right, font=("Courier New" if sys.platform == "win32" else "Menlo", 9),
            bg=COLORS['surface'], fg=COLORS['text'],
            relief="flat", highlightthickness=1,
            highlightbackground=COLORS['border'],
            wrap="word", state="disabled")
        self.log_text.pack(fill="both", expand=True)

    def _set_format(self, val):
        self.format_type.set(val)
        for k, b in self._fmt_btns.items():
            if k == val:
                b.config(bg=COLORS['accent_lt'], fg=COLORS['accent'],
                         highlightbackground=COLORS['accent'])
            else:
                b.config(bg=COLORS['surface'], fg=COLORS['muted'],
                         highlightbackground=COLORS['border'])
        self._build_quality_widgets()

    def _build_quality_widgets(self):
        for w in self._quality_row.winfo_children():
            w.destroy()
        tk.Label(self._quality_row, text="Quality", bg=COLORS['bg'], fg=COLORS['muted'],
                 font=(FONT_FAMILY, 9)).pack(anchor="w", pady=(0, 4))
        row = tk.Frame(self._quality_row, bg=COLORS['bg'])
        row.pack(anchor="w")
        if self.format_type.get() == "mp3":
            opts = [("128 kbps", "128"), ("192 kbps", "192"), ("320 kbps", "320")]
            var = self.mp3_quality
        else:
            opts = [("360p", "360p"), ("480p", "480p"), ("720p", "720p"), ("1080p", "1080p"), ("Best", "best")]
            var = self.mp4_quality
        for label, val in opts:
            b = tk.Label(row, text=label, bg=COLORS['surface'], fg=COLORS['muted'],
                         font=(FONT_FAMILY, 9), padx=10, pady=5, cursor="hand2",
                         relief="flat", highlightthickness=1,
                         highlightbackground=COLORS['border'])
            b.pack(side="left", padx=(0, 6))
            b.bind("<Button-1>", lambda e, v=val, var_=var: self._set_quality(var_, v))
            if var.get() == val:
                b.config(bg=COLORS['accent_lt'], fg=COLORS['accent'],
                         highlightbackground=COLORS['accent'])
            setattr(b, '_val', val)
            setattr(b, '_var', var)
        self._quality_pill_row = row

    def _set_quality(self, var, val):
        var.set(val)
        for b in self._quality_pill_row.winfo_children():
            if hasattr(b, '_val'):
                if b._val == val:
                    b.config(bg=COLORS['accent_lt'], fg=COLORS['accent'],
                             highlightbackground=COLORS['accent'])
                else:
                    b.config(bg=COLORS['surface'], fg=COLORS['muted'],
                             highlightbackground=COLORS['border'])

    # ── Batch page ────────────────────────────────────────────────────────────

    def _build_batch(self, parent):
        outer = tk.Frame(parent, bg=COLORS['bg'])
        outer.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(outer, text="URLs (one per line)", bg=COLORS['bg'], fg=COLORS['muted'],
                 font=(FONT_FAMILY, 9)).pack(anchor="w", pady=(0, 4))
        self.batch_text = scrolledtext.ScrolledText(
            outer, font=("Courier New" if sys.platform == "win32" else "Menlo", 10),
            bg=COLORS['surface'], fg=COLORS['text'],
            relief="flat", highlightthickness=1,
            highlightbackground=COLORS['border'],
            height=12, wrap="none")
        self.batch_text.pack(fill="x")

        ctrl = tk.Frame(outer, bg=COLORS['bg'])
        ctrl.pack(fill="x", pady=12)

        # Batch format pills
        tk.Label(ctrl, text="Format:", bg=COLORS['bg'], fg=COLORS['muted'],
                 font=(FONT_FAMILY, 9)).pack(side="left")
        self._batch_fmt_btns = {}
        for label, val in [("MP3", "mp3"), ("MP4", "mp4")]:
            b = tk.Label(ctrl, text=label, bg=COLORS['surface'], fg=COLORS['muted'],
                         font=(FONT_FAMILY, 9), padx=12, pady=5, cursor="hand2",
                         relief="flat", highlightthickness=1,
                         highlightbackground=COLORS['border'])
            b.pack(side="left", padx=(6, 0))
            b.bind("<Button-1>", lambda e, v=val: self._set_batch_format(v))
            self._batch_fmt_btns[val] = b

        # Quality dropdown for batch
        tk.Label(ctrl, text="  Quality:", bg=COLORS['bg'], fg=COLORS['muted'],
                 font=(FONT_FAMILY, 9)).pack(side="left")
        self._batch_quality = tk.StringVar(value="192")
        self._batch_quality_menu = ttk.Combobox(ctrl, textvariable=self._batch_quality,
                                                 font=(FONT_FAMILY, 9), width=12, state="readonly")
        self._batch_quality_menu['values'] = ("128", "192", "320")
        self._batch_quality_menu.pack(side="left", padx=(6, 0))
        self._set_batch_format("mp3")

        FlatButton(ctrl, "Load from file", command=self._load_urls_file,
                   bg=COLORS['surface'], fg=COLORS['muted'],
                   hover_bg=COLORS['accent_lt'], font_size=9, padx=12, pady=6).pack(side="right")
        FlatButton(ctrl, "Clear", command=lambda: self.batch_text.delete("1.0", "end"),
                   bg=COLORS['surface'], fg=COLORS['danger'],
                   hover_bg=COLORS['danger_lt'], font_size=9, padx=12, pady=6).pack(side="right", padx=(0, 8))

        btn_row = tk.Frame(outer, bg=COLORS['bg'])
        btn_row.pack(fill="x", pady=(0, 12))
        FlatButton(btn_row, "Download all", command=self._start_batch,
                   font_size=11, padx=24, pady=10).pack(side="left", padx=(0, 10))
        self._batch_cancel_btn = FlatButton(btn_row, "Cancel", command=self._cancel_download,
                                             bg=COLORS['surface'], fg=COLORS['danger'],
                                             hover_bg=COLORS['danger_lt'],
                                             font_size=10, padx=14, pady=10)
        self._batch_cancel_btn.pack(side="left")

        tk.Label(outer, text="Batch log", bg=COLORS['bg'], fg=COLORS['muted'],
                 font=(FONT_FAMILY, 9)).pack(anchor="w", pady=(0, 4))
        self.batch_log = scrolledtext.ScrolledText(
            outer, font=("Courier New" if sys.platform == "win32" else "Menlo", 9),
            bg=COLORS['surface'], fg=COLORS['text'],
            relief="flat", highlightthickness=1,
            highlightbackground=COLORS['border'],
            height=10, state="disabled")
        self.batch_log.pack(fill="both", expand=True)

    def _set_batch_format(self, val):
        self.batch_format.set(val)
        mp3_opts  = ("128", "192", "320")
        mp4_opts  = ("360p", "480p", "720p", "1080p", "best")
        self._batch_quality_menu['values'] = mp3_opts if val == "mp3" else mp4_opts
        self._batch_quality.set("192" if val == "mp3" else "720p")
        for k, b in self._batch_fmt_btns.items():
            if k == val:
                b.config(bg=COLORS['accent_lt'], fg=COLORS['accent'],
                         highlightbackground=COLORS['accent'])
            else:
                b.config(bg=COLORS['surface'], fg=COLORS['muted'],
                         highlightbackground=COLORS['border'])

    # ── History page ──────────────────────────────────────────────────────────

    def _build_history(self, parent):
        outer = tk.Frame(parent, bg=COLORS['bg'])
        outer.pack(fill="both", expand=True, padx=24, pady=20)
        top = tk.Frame(outer, bg=COLORS['bg'])
        top.pack(fill="x", pady=(0, 8))
        tk.Label(top, text="Download history", bg=COLORS['bg'], fg=COLORS['text'],
                 font=(FONT_FAMILY, 12, "bold")).pack(side="left")
        FlatButton(top, "Refresh", command=self._refresh_history,
                   bg=COLORS['surface'], fg=COLORS['muted'],
                   hover_bg=COLORS['accent_lt'], font_size=9, padx=12, pady=6).pack(side="right")
        FlatButton(top, "Clear history", command=self._clear_history,
                   bg=COLORS['surface'], fg=COLORS['danger'],
                   hover_bg=COLORS['danger_lt'], font_size=9, padx=12, pady=6).pack(side="right", padx=(0, 8))

        cols = ("title", "format", "quality", "time", "status")
        self._hist_tree = ttk.Treeview(outer, columns=cols, show="headings", height=18)
        for col, label, w in [
            ("title",   "Title",    380),
            ("format",  "Format",    70),
            ("quality", "Quality",   80),
            ("time",    "Time",     130),
            ("status",  "Status",   100),
        ]:
            self._hist_tree.heading(col, text=label)
            self._hist_tree.column(col, width=w, anchor="w")

        style = ttk.Style()
        style.configure("Treeview", background=COLORS['surface'], rowheight=26,
                        font=(FONT_FAMILY, 9), borderwidth=0)
        style.configure("Treeview.Heading", font=(FONT_FAMILY, 9, "bold"),
                        background=COLORS['surface'])
        style.map("Treeview", background=[('selected', COLORS['accent_lt'])],
                  foreground=[('selected', COLORS['accent'])])

        sb = ttk.Scrollbar(outer, orient="vertical", command=self._hist_tree.yview)
        self._hist_tree.configure(yscrollcommand=sb.set)
        self._hist_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._refresh_history()

    def _refresh_history(self):
        self._hist_tree.delete(*self._hist_tree.get_children())
        style = ttk.Style()
        style.map("Treeview",
                  background=[('selected', COLORS['accent_lt'])],
                  foreground=[('selected', COLORS['accent'])])
        self._hist_tree.tag_configure('ok',   foreground=COLORS['success'])
        self._hist_tree.tag_configure('fail', foreground=COLORS['danger'])
        for e in reversed(load_history()):
            ok = e.get('success', False)
            status_text = "OK" if ok else "Failed"
            tag = 'ok' if ok else 'fail'
            self._hist_tree.insert("", "end", tags=(tag,), values=(
                e.get('title', e.get('url', '—'))[:60],
                e.get('format', '—'),
                e.get('quality', '—'),
                e.get('time', '—'),
                status_text,
            ))

    def _clear_history(self):
        if messagebox.askyesno("Clear history", "Delete all download history?"):
            save_history([])
            self._refresh_history()

    # ── Status bar ────────────────────────────────────────────────────────────

    def _build_status_bar(self):
        bar = tk.Frame(self.window, bg=COLORS['surface'],
                       highlightbackground=COLORS['border'], highlightthickness=1)
        bar.pack(fill="x", side="bottom")
        self._status_lbl = tk.Label(bar, text="Ready", bg=COLORS['surface'],
                                    fg=COLORS['muted'], font=(FONT_FAMILY, 9),
                                    padx=12, pady=6)
        self._status_lbl.pack(side="left")
        self._speed_lbl = tk.Label(bar, text="", bg=COLORS['surface'],
                                   fg=COLORS['muted'], font=(FONT_FAMILY, 9), padx=12)
        self._speed_lbl.pack(side="left")
        self._progress = ttk.Progressbar(bar, mode="indeterminate", length=200)
        self._progress.pack(side="right", padx=12, pady=6)

        style = ttk.Style()
        style.configure("TProgressbar", troughcolor=COLORS['border'],
                        background=COLORS['accent'], thickness=4)

    def _set_status(self, msg, color=None):
        self._status_lbl.config(text=msg, fg=color or COLORS['muted'])
        self.window.update_idletasks()

    def _set_speed(self, txt):
        self._speed_lbl.config(text=txt)

    # ── Logging ───────────────────────────────────────────────────────────────

    def _log(self, widget, msg, color="text"):
        widget.config(state="normal")
        ts = time.strftime("%H:%M:%S")
        widget.insert("end", f"[{ts}]  ", "muted")
        # Embed icon canvas if this colour has an associated icon
        kind = _TAG_ICON.get(color)
        if kind:
            icon = _make_icon(widget, kind, size=13)
            widget.window_create("end", window=icon, pady=1)
            widget.insert("end", "  ", color)
        widget.insert("end", f"{msg}\n", color)
        widget.see("end")
        widget.config(state="disabled")
        self.window.update_idletasks()

    def log(self, msg, color="text"):
        self._log(self.log_text, msg, color)

    def blog(self, msg, color="text"):
        self._log(self.batch_log, msg, color)

    # ── Video preview ─────────────────────────────────────────────────────────

    def _fetch_info(self):
        url = self.url_entry.get().strip()
        if not url:
            return
        self._set_status("Fetching info…")
        threading.Thread(target=self._do_fetch_info, args=(url,), daemon=True).start()

    def _do_fetch_info(self, url):
        info = get_video_info(url)
        self.window.after(0, lambda: self._show_info(info))

    def _show_info(self, info):
        for w in self._prev_card.winfo_children():
            w.destroy()
        self._prev_card.config(height=100)

        if 'error' in info:
            tk.Label(self._prev_card, text=f"Error: {info['error']}",
                     bg=COLORS['surface'], fg=COLORS['danger'],
                     font=(FONT_FAMILY, 9), wraplength=500).pack(expand=True)
            self._set_status("Could not fetch info", COLORS['danger'])
            return

        self._last_info = info
        inner = tk.Frame(self._prev_card, bg=COLORS['surface'])
        inner.pack(fill="both", expand=True, padx=12, pady=8)

        # Thumbnail
        if PIL_AVAILABLE and info.get('thumbnail'):
            threading.Thread(target=self._load_thumb, args=(info['thumbnail'], inner), daemon=True).start()

        meta = tk.Frame(inner, bg=COLORS['surface'])
        meta.pack(side="left", fill="both", expand=True, padx=(8, 0))
        title = info.get('title', 'Unknown')[:80]
        tk.Label(meta, text=title, bg=COLORS['surface'], fg=COLORS['text'],
                 font=(FONT_FAMILY, 10, "bold"), anchor="w", wraplength=360).pack(anchor="w")
        details = f"{info.get('uploader','—')}  ·  {format_duration(info.get('duration',0))}  ·  {format_views(info.get('view_count',0))}"
        tk.Label(meta, text=details, bg=COLORS['surface'], fg=COLORS['muted'],
                 font=(FONT_FAMILY, 9)).pack(anchor="w", pady=(2, 0))
        if info.get('is_playlist'):
            tk.Label(meta, text=f"Playlist — {info.get('entry_count', '?')} items",
                     bg=COLORS['warn_lt'], fg=COLORS['warn'],
                     font=(FONT_FAMILY, 9), padx=8, pady=2).pack(anchor="w", pady=(4, 0))
        self._set_status(f"Ready — {title[:50]}")

    def _load_thumb(self, url, parent):
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                data = r.read()
            img = Image.open(io.BytesIO(data))
            img.thumbnail((80, 56))
            photo = ImageTk.PhotoImage(img)
            self._thumb_ref = photo
            lbl = tk.Label(parent, image=photo, bg=COLORS['surface'])
            lbl.image = photo
            lbl.pack(side="left")
        except Exception:
            pass

    # ── Folder helpers ────────────────────────────────────────────────────────

    def _select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder.set(folder)

    def _open_output_folder(self):
        path = self.output_folder.get()
        os.makedirs(path, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def _load_urls_file(self):
        path = filedialog.askopenfilename(
            title="Select URL list",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
                self.batch_text.delete("1.0", "end")
                self.batch_text.insert("end", "\n".join(lines) + "\n")
                self.blog(f"Loaded {len(lines)} URLs from file", "success")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ── Clipboard paste ───────────────────────────────────────────────────────

    def _try_paste_from_clipboard(self):
        try:
            clip = self.window.clipboard_get()
            if re.search(r'(youtube\.com|youtu\.be)', clip):
                self.url_entry.delete(0, "end")
                self.url_entry.insert(0, clip.strip())
                self._set_status("URL pasted from clipboard")
        except Exception:
            pass

    # ── Progress hook ─────────────────────────────────────────────────────────

    def _make_progress_hook(self):
        def hook(d):
            status = d.get('status', '')
            if status == 'downloading':
                pct = d.get('_percent_str', '').strip()
                speed = d.get('_speed_str', '').strip()
                eta  = d.get('_eta_str', '').strip()
                msg  = f"Downloading {pct}"
                if speed:
                    msg += f"  ·  {speed}"
                if eta:
                    msg += f"  ·  ETA {eta}"
                self.window.after(0, lambda m=msg: self._set_status(m))
                self.window.after(0, lambda s=speed: self._set_speed(s))
            elif status == 'finished':
                self.window.after(0, lambda: self._set_status("Processing…"))
        return hook

    # ── Cancel ────────────────────────────────────────────────────────────────

    def _cancel_download(self):
        if self.downloading:
            self.cancel_event.set()
            self._set_status("Cancelling…", COLORS['warn'])

    # ── Single download ───────────────────────────────────────────────────────

    def _start_single(self):
        if self.downloading:
            messagebox.showwarning("Busy", "A download is already in progress.")
            return
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL.")
            return
        if 'youtube.com' not in url and 'youtu.be' not in url:
            if not messagebox.askyesno("Not a YouTube URL", "Continue anyway?"):
                return
        self.cancel_event.clear()
        self.downloading = True
        self._progress.start()
        threading.Thread(target=self._run_single, args=(url,), daemon=True).start()

    def _run_single(self, url):
        fmt     = self.format_type.get()
        quality = self.mp3_quality.get() if fmt == "mp3" else self.mp4_quality.get()
        folder  = self.output_folder.get()
        hook    = self._make_progress_hook()

        self.window.after(0, lambda: self.log(f"Starting {fmt.upper()}: {url[:60]}…", "accent"))
        result = download_youtube(url, folder, fmt, quality, hook, self.cancel_event)
        self.window.after(0, lambda: self._on_single_done(result))

    def _on_single_done(self, result):
        self.downloading = False
        self._progress.stop()
        self._set_speed("")
        if result.get('cancelled'):
            self.log("Download cancelled.", "warn")
            self._set_status("Cancelled", COLORS['warn'])
            return
        if result.get('success'):
            title = result.get('title', '—')
            self.log(f"{title}", "success")
            self.log(f"Saved to: {result.get('filename', '—')}", "success")
            self._set_status(f"Done — {title[:50]}", COLORS['success'])
            append_history({**result, 'time': time.strftime("%Y-%m-%d %H:%M")})
            messagebox.showinfo("Done",
                f"Downloaded!\n\n{title}\n{result.get('format')} · {result.get('quality')}\n{result.get('filename')}")
        else:
            err = result.get('error', 'Unknown error')
            self.log(f"{err}", "danger")
            self._set_status(f"Failed: {err[:60]}", COLORS['danger'])
            append_history({**result, 'time': time.strftime("%Y-%m-%d %H:%M")})

    # ── Batch download ────────────────────────────────────────────────────────

    def _start_batch(self):
        if self.downloading:
            messagebox.showwarning("Busy", "A download is already in progress.")
            return
        raw = self.batch_text.get("1.0", "end").strip()
        if not raw:
            messagebox.showerror("Error", "No URLs entered.")
            return
        urls = [u.strip() for u in raw.splitlines() if u.strip()]
        valid, invalid = validate_urls(urls)
        if invalid:
            msg = f"{len(invalid)} invalid URLs will be skipped.\nContinue with {len(valid)} valid URLs?"
            if not messagebox.askyesno("Confirm", msg):
                return
            urls = valid
        if not urls:
            messagebox.showerror("Error", "No valid YouTube URLs found.")
            return
        self.cancel_event.clear()
        self.downloading = True
        self._progress.start()
        threading.Thread(target=self._run_batch, args=(urls,), daemon=True).start()

    def _run_batch(self, urls):
        fmt     = self.batch_format.get()
        quality = self._batch_quality.get()
        folder  = self.output_folder.get()
        hook    = self._make_progress_hook()

        self.window.after(0, lambda: self.blog(
            f"Batch: {len(urls)} URLs · {fmt.upper()} · {quality}", "accent"))

        def per_result(i, total, r):
            if r.get('success'):
                self.window.after(0, lambda r_=r, i_=i, t=total:
                    self.blog(f"[{i_}/{t}]  {r_.get('title','')[:50]}", "success"))
            elif r.get('cancelled'):
                self.window.after(0, lambda i_=i, t=total:
                    self.blog(f"[{i_}/{t}]  Cancelled", "warn"))
            else:
                self.window.after(0, lambda r_=r, i_=i, t=total:
                    self.blog(f"[{i_}/{t}]  {r_.get('error','')}", "danger"))
            entry = {**r, 'format': fmt.upper(), 'quality': quality,
                     'time': time.strftime("%Y-%m-%d %H:%M")}
            append_history(entry)

        results = batch_download(urls, folder, fmt, quality, per_result, hook, self.cancel_event)
        ok  = sum(1 for r in results if r.get('success'))
        fail= len(results) - ok
        self.window.after(0, lambda: self._on_batch_done(ok, fail, len(urls)))

    def _on_batch_done(self, ok, fail, total):
        self.downloading = False
        self._progress.stop()
        self._set_speed("")
        color = "success" if fail == 0 else "warn"
        self.blog(f"Batch done: {ok}/{total} succeeded, {fail} failed.", color)
        self._set_status(f"Batch done: {ok}/{total}", COLORS.get(color, COLORS['muted']))
        self._refresh_history()
        messagebox.showinfo("Batch complete",
            f"{ok} of {total} files downloaded.\n{fail} failed.")

    # ── FFmpeg check ──────────────────────────────────────────────────────────

    def _check_ffmpeg(self):
        if shutil.which("ffmpeg") or find_ffmpeg():
            self.log("FFmpeg detected", "success")
        else:
            self.log("FFmpeg not found — MP3 conversion will fail", "warn")
            self.log("Install from https://ffmpeg.org/download.html", "warn")

    # ── Run ───────────────────────────────────────────────────────────────────

    def run(self):
        for tag, col in [
            ("text",    COLORS['text']),
            ("accent",  COLORS['accent']),
            ("success", COLORS['success']),
            ("danger",  COLORS['danger']),
            ("warn",    COLORS['warn']),
            ("muted",   COLORS['muted']),
        ]:
            self.log_text.tag_config(tag, foreground=col)
            self.batch_log.tag_config(tag, foreground=col)
        self.log("Ready. Paste a URL to get started.", "muted")
        self.window.mainloop()


def main():
    app = YouTubeConverter()
    app.run()

if __name__ == "__main__":
    main()