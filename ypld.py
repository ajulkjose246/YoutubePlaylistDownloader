import os
import re
from pytubefix import Playlist, YouTube
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_fixed

# Function to sanitize filenames
def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '-', filename)


def download_playlist(playlist_url, resolution, format_type):
    # Check if ffmpeg is available for any downloads (both MP4 and MP3)
    if os.system("ffmpeg -version") != 0:
        print("Error: ffmpeg is not installed or not in PATH")
        print("Please install ffmpeg and add it to your system PATH")
        print("Download ffmpeg from: https://ffmpeg.org/download.html")
        return

    playlist = Playlist(playlist_url)
    playlist_name = sanitize_filename(playlist.title)
    
    # Create downloads directory if it doesn't exist
    downloads_dir = "downloads"
    if not os.path.exists(downloads_dir):
        os.mkdir(downloads_dir)
    
    # Create playlist directory inside downloads
    playlist_dir = os.path.join(downloads_dir, playlist_name)
    if not os.path.exists(playlist_dir):
        os.mkdir(playlist_dir)

    for video in tqdm(playlist.videos, desc="Downloading playlist", unit="video"):
        try:
            yt = YouTube(video.watch_url, on_progress_callback=progress_function)
            
            if format_type == 'mp3':
                # Handle MP3 download
                try:
                    audio_stream = yt.streams.get_audio_only()
                except Exception as e:
                    print(f"\nSkipping {video.title}: {str(e)}")
                    print("----------------------------------")
                    continue

                audio_filename = sanitize_filename(f"{yt.title}[ajulkjose.in].mp3")
                audio_path = os.path.join(playlist_dir, audio_filename)
                temp_audio = "temp_audio.mp4"  # Temporary file for audio download
                
                if os.path.exists(audio_path):
                    print(f"{audio_filename} already exists")
                    continue
                    
                print(f"Downloading audio: {yt.title}")
                try:
                    # Download audio to temporary file
                    audio_stream.download(filename=temp_audio)
                    
                    # Convert to MP3 using ffmpeg
                    ffmpeg_result = os.system(
                        f'ffmpeg -y -i "{temp_audio}" -vn -ab 128k -ar 44100 -f mp3 "{audio_path}" -loglevel quiet -stats'
                    )
                    
                    # Clean up temporary file
                    if os.path.exists(temp_audio):
                        os.remove(temp_audio)
                        
                    if ffmpeg_result != 0:
                        print(f"Error converting {yt.title} to MP3")
                        continue
                        
                except Exception as e:
                    print(f"Error downloading {yt.title}: {str(e)}")
                    if os.path.exists(temp_audio):
                        os.remove(temp_audio)
                    continue

            else:
                # Handle MP4 download
                video_streams = yt.streams.filter(res=resolution)
                video_filename = sanitize_filename(f"{yt.title}[ajulkjose.in].mp4")
                video_path = os.path.join(playlist_dir, video_filename)

                if os.path.exists(video_path):
                    print(f"{video_filename} already exists")
                    continue

                if not video_streams:
                    highest_resolution_stream = yt.streams.get_highest_resolution()
                    video_name = sanitize_filename(highest_resolution_stream.default_filename)
                    print(f"Downloading {video_name} in {highest_resolution_stream.resolution}")
                    download_with_retries(highest_resolution_stream, video_path)
                else:
                    video_stream = video_streams.first()
                    video_name = sanitize_filename(video_stream.default_filename)
                    print(f"Downloading video for {video_name} in {resolution}")
                    
                    try:
                        download_with_retries(video_stream, "video.mp4")
                        audio_stream = yt.streams.get_audio_only()
                        print(f"Downloading audio for {video_name}")
                        download_with_retries(audio_stream, "audio.mp4")

                        if os.path.exists("video.mp4") and os.path.exists("audio.mp4"):
                            ffmpeg_result = os.system(
                                "ffmpeg -y -i video.mp4 -i audio.mp4 -c:v copy -c:a aac final.mp4 -loglevel quiet -stats")
                            
                            if ffmpeg_result == 0 and os.path.exists("final.mp4"):
                                os.rename("final.mp4", video_path)
                            else:
                                print("Error: Failed to merge video and audio files")
                                continue

                        # Cleanup temporary files
                        for temp_file in ["video.mp4", "audio.mp4"]:
                            if os.path.exists(temp_file):
                                os.remove(temp_file)

                    except Exception as e:
                        print(f"Error processing {video_name}: {str(e)}")
                        continue

            print("----------------------------------")

        except Exception as e:
            print(f"\nError processing video: {str(e)}")
            print("----------------------------------")
            continue


@retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
def download_with_retries(stream, filename):
    stream.download(filename=filename)


def progress_function(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    print(f"Downloading... {percentage_of_completion:.2f}% complete", end="\r")


if __name__ == "__main__":
    playlist_url = input("Enter the playlist url: ")
    format_type = input("Select format type (mp3/mp4): ").lower()
    
    if format_type == 'mp4':
        resolutions = ["240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]
        resolution = input(f"Please select a resolution {resolutions}: ")
    else:
        resolution = None
        
    download_playlist(playlist_url, resolution, format_type)