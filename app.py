from flask import Flask, render_template, request, jsonify
from ypld import download_playlist
import threading
import os

app = Flask(__name__)

# Add this configuration for Python Anywhere
downloads_dir = os.path.join(os.path.expanduser('~'), 'downloads')
if not os.path.exists(downloads_dir):
    os.makedirs(downloads_dir)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def start_download():
    data = request.json
    playlist_url = data.get('playlist_url')
    format_type = data.get('format_type')
    resolution = data.get('resolution')
    
    if not playlist_url:
        return jsonify({'error': 'Playlist URL is required'}), 400
    
    # Start download in background thread
    thread = threading.Thread(
        target=download_playlist,
        args=(playlist_url, resolution, format_type)
    )
    thread.daemon = True  # Make thread daemon so it doesn't block shutdown
    thread.start()
    
    return jsonify({'message': 'Download started successfully'})

# Remove the if __name__ == '__main__' block when deploying to Python Anywhere 