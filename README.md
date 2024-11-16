# YouTube Playlist Downloader

This project is a Python-based YouTube Playlist Downloader that lets users download an entire YouTube playlist in either MP3 or MP4 format, with selectable resolution for video downloads. The downloaded files are organized into a playlist-specific folder for easy access.

## Features
- **Download MP3**: Download audio-only files from each video in the playlist.
- **Download MP4**: Download video files with selectable resolutions (240p, 360p, 480p, 720p, 1080p, 1440p, 2160p).
- **File Organization**: Downloads are saved into a dedicated directory named after the playlist.
- **Automatic Retry**: Downloads are retried up to 5 times if they fail.
- **Progress Tracking**: Shows download progress percentage in the terminal.

## Requirements
- **Python 3.7+**
- **ffmpeg**: Required for MP4 downloads and merging audio and video streams.
