from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

DOWNLOAD_FOLDER = os.path.join(os.path.expanduser('~'), 'Downloads')

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', 'best')
    
    if not url:
        return jsonify({'success': False, 'error': 'No URL provided'}), 400

    print(f"Downloading {url}...")

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best' if quality == '4k' else 'best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return jsonify({
                'success': True, 
                'title': info.get('title', 'Video'),
                'filepath': filename
            })
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting yt-dlp Server on port 5000...")
    print(f"Downloads will be saved to: {DOWNLOAD_FOLDER}")
    app.run(port=5000)
