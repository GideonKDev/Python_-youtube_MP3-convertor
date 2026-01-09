"""
converter.py - Core YouTube to MP3 conversion functions
"""
import yt_dlp
import os
import re

def clean_filename(filename, max_length=200):
    """Remove invalid characters and limit filename length"""
    # Remove invalid Windows characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    
    # Replace multiple spaces with single space
    filename = re.sub(r'\s+', ' ', filename)
    
    # Trim to max length
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length-len(ext)] + ext
    
    return filename.strip()

def get_video_info(url):
    """Get video information without downloading"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'thumbnail': info.get('thumbnail', ''),
                'view_count': info.get('view_count', 0),
            }
        except Exception as e:
            return {'error': str(e)}

def youtube_to_mp3(url, output_folder="downloads", quality='192', add_metadata=True):
    """
    Convert YouTube video to MP3
    
    Args:
        url: YouTube URL
        output_folder: Where to save the file
        quality: '128', '192', '320'
        add_metadata: Add title, artist metadata
    
    Returns:
        dict: {'success': bool, 'filename': str, 'error': str}
    """
    os.makedirs(output_folder, exist_ok=True)
    
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [],
        }
        
        # Configure postprocessors
        postprocessors = []
        
        # Audio extraction
        postprocessors.append({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality,
        })
        
        # Metadata
        if add_metadata:
            postprocessors.append({
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            })
        
        ydl_opts['postprocessors'] = postprocessors
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get info first to clean filename
            info = ydl.extract_info(url, download=False)
            title = clean_filename(info.get('title', 'audio_download'))
            
            # Set cleaned filename
            ydl.params['outtmpl'] = os.path.join(output_folder, f'{title}.%(ext)s')
            
            # Download
            ydl.download([url])
            
            # Find the downloaded file
            mp3_file = os.path.join(output_folder, f"{title}.mp3")
            if os.path.exists(mp3_file):
                return {
                    'success': True,
                    'filename': mp3_file,
                    'title': info.get('title', 'Unknown'),
                    'size': os.path.getsize(mp3_file) if os.path.exists(mp3_file) else 0,
                }
            else:
                # Check for other possible names
                for file in os.listdir(output_folder):
                    if file.startswith(title) and file.endswith('.mp3'):
                        return {
                            'success': True,
                            'filename': os.path.join(output_folder, file),
                            'title': info.get('title', 'Unknown'),
                        }
                
                return {'success': False, 'error': 'MP3 file not found after conversion'}
                
    except Exception as e:
        return {'success': False, 'error': str(e)}

def batch_download(urls, output_folder="downloads", quality='192'):
    """
    Download multiple URLs
    
    Args:
        urls: List of YouTube URLs
        output_folder: Download directory
    
    Returns:
        list: Results for each download
    """
    results = []
    total = len(urls)
    
    for i, url in enumerate(urls, 1):
        try:
            print(f"[{i}/{total}] Processing: {url[:50]}...")
            result = youtube_to_mp3(url, output_folder, quality)
            results.append(result)
            
            if result['success']:
                print(f"    ✓ Success: {result.get('title', 'Unknown')}")
            else:
                print(f"    ✗ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            results.append({'success': False, 'error': str(e), 'url': url})
            print(f"    ✗ Error: {e}")
    
    return results