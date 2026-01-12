# # Example using yt-dlp for educational purposes
import yt_dlp

def youtube_to_mp3(url, output_path="audio.mp3"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_path,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        

if __name__ == "__main__":
    youtube_url = input("Enter the YouTube URL: ")
    output_file = input("Enter the output file name (default: audio.mp3): ") or "audio.mp3"
    youtube_to_mp3(youtube_url, output_file)
    print(f"Downloaded and converted to {output_file}")
