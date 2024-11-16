from flask import Flask, render_template, request, jsonify, Response, send_file
from ypld import download_playlist
import threading
import os
import queue
import json
import tempfile
import shutil
import zipfile
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Global progress tracking
progress_queues = {}

# Store temporary download directories
temp_downloads = {}

@app.route('/download-progress')
def download_progress():
    def generate():
        playlist_url = request.args.get('playlist_url')
        if playlist_url not in progress_queues:
            progress_queues[playlist_url] = queue.Queue()
        
        while True:
            try:
                progress_data = progress_queues[playlist_url].get(timeout=1)
                yield f"data: {json.dumps(progress_data)}\n\n"
                
                if progress_data.get('completed', False):
                    break
            except queue.Empty:
                continue
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-download', methods=['POST'])
def start_download():
    try:
        data = request.json
        playlist_url = data.get('playlist_url')
        format_type = data.get('format_type')
        resolution = data.get('resolution')
        
        if not playlist_url:
            return jsonify({'error': 'Playlist URL is required'}), 400

        # Create a temporary directory for this download
        temp_dir = tempfile.mkdtemp()
        temp_downloads[playlist_url] = temp_dir
        
        # Create a new queue for this download
        progress_queues[playlist_url] = queue.Queue()
        
        thread = threading.Thread(
            target=download_playlist,
            args=(playlist_url, resolution, format_type, temp_dir, progress_queues[playlist_url])
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({'message': 'Download started successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download-file')
def download_file():
    try:
        playlist_url = request.args.get('playlist_url')
        if not playlist_url or playlist_url not in temp_downloads:
            return jsonify({'error': 'Invalid download request'}), 400

        temp_dir = temp_downloads[playlist_url]
        
        # Create a zip file of the downloaded content
        zip_path = os.path.join(tempfile.gettempdir(), 'playlist_download.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)

        # Clean up the temporary directory
        shutil.rmtree(temp_dir)
        del temp_downloads[playlist_url]

        return send_file(
            zip_path,
            as_attachment=True,
            download_name='playlist_download.zip',
            mimetype='application/zip'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up the zip file
        if 'zip_path' in locals() and os.path.exists(zip_path):
            os.remove(zip_path)

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
    