from flask import Flask, render_template, request, jsonify
from ypld import download_playlist
import threading
import os

app = Flask(__name__)

# Configure for production
port = int(os.environ.get("PORT", 8000))

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
    
    thread = threading.Thread(
        target=download_playlist,
        args=(playlist_url, resolution, format_type)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Download started successfully'})

# Add this for production
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port)
    