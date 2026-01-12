import yt_dlp
import os

def youtube_to_mp3(url, output_folder="mp3_downloads"):
    os.makedirs(output_folder, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            # Add metadata processor for cleaner output
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            },
            # This ensures the final file has .mp3 extension
            {
                'key': 'ExecAfterDownload',
                'exec_cmd': 'ffmpeg -i {} -c copy {}.mp3 && del {}',
                'when': 'after_move',
            }
        ],
        'quiet': False,
        'writethumbnail': True,  # Optional: download thumbnail
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        print(f"Downloaded: {info.get('title', 'Unknown')}")

if __name__ == "__main__":
    youtube_url = input("Enter the YouTube URL: ")
    youtube_to_mp3(youtube_url)
    print("Download complete!")