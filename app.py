from flask import Flask, render_template, request, jsonify, Response
from ypld import download_playlist
import threading
import os
import queue
import json

app = Flask(__name__)

# Global progress tracking
progress_queues = {}

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

@app.route('/download', methods=['POST'])
def start_download():
    try:
        data = request.json
        playlist_url = data.get('playlist_url')
        format_type = data.get('format_type')
        resolution = data.get('resolution')
        download_location = data.get('download_location')
        
        if not playlist_url:
            return jsonify({'error': 'Playlist URL is required'}), 400
        
        if not download_location:
            return jsonify({'error': 'Download location is required'}), 400
        
        # Create a new queue for this download
        progress_queues[playlist_url] = queue.Queue()
        
        thread = threading.Thread(
            target=download_playlist,
            args=(playlist_url, resolution, format_type, download_location, progress_queues[playlist_url])
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
    