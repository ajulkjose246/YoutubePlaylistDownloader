from flask import Flask, render_template, request, jsonify
from ypld import download_playlist
import threading
import os

app = Flask(__name__)

# Configure downloads directory
downloads_dir = os.path.join(os.getcwd(), 'downloads')
if not os.path.exists(downloads_dir):
    os.makedirs(downloads_dir)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def start_download():
    try:
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
    