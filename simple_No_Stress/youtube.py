#create a software that converts youtube links to mp3 audio

import yt_dlp
import os

def youtube_to_mp3(url, output_folder="mp3_downloads"):
    # Create folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == "__main__":
    youtube_url = input("Enter the YouTube URL: ")
    youtube_to_mp3(youtube_url)
    print("Download complete ")
