from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from matcher import AudioMatcher
import time

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

# Configuration
UPLOAD_FOLDER = 'data/uploads'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a'}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/identify', methods=['POST'])
def identify():
    """Handle audio file upload and identification."""
    
    # Check if file was uploaded
    if 'audio_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['audio_file']
    
    # Check if filename is empty
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check if file type is allowed
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload MP3, WAV, or M4A'}), 400
    
    try:
        # Save the uploaded file
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time()))
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Initialize matcher
        matcher = AudioMatcher()
        
        # Match the audio clip
        result = matcher.match_clip(filepath, min_confidence=5)
        
        matcher.close()
        
        # Clean up uploaded file
        os.remove(filepath)
        
        # Return results
        if result:
            return jsonify({
                'success': True,
                'title': result['title'],
                'type': result['type'],
                'season': result['season'],
                'episode': result['episode'],
                'timestamp': result['time_offset_formatted'],
                'timestamp_seconds': result['time_offset_seconds'],
                'confidence': result['confidence'],
                'total_matches': result['total_matches']
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Could not identify the audio. Try a clip with more distinctive audio (music, action scenes).'
            })
    
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🎵 MEDIA RECOGNITION WEB SERVER")
    print("="*70)
    print("\n🌐 Server starting at: http://127.0.0.1:5000")
    print("📝 Press CTRL+C to stop the server\n")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)