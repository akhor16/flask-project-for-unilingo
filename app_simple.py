from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import requests
import cv2
import numpy as np
import tempfile
import base64
from io import BytesIO
from PIL import Image
import speech_recognition as sr
from gtts import gTTS
import pytesseract
import uuid

app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
DATA_FILE = 'video_data.json'

def load_data():
    """Load persistent data from file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"current_video_url": "", "video_info": {}}

def save_data(data):
    """Save data to file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def get_video_info(url):
    """Get video duration and height"""
    try:
        # Download video temporarily
        response = requests.get(url, stream=True)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
        temp_file.close()
        
        # Get video info using OpenCV
        cap = cv2.VideoCapture(temp_file.name)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        os.unlink(temp_file.name)
        
        return {"duration": duration, "height": height}
    except Exception as e:
        print(f"Error getting video info: {e}")
        return {"duration": 0, "height": 0}

def extract_first_frame(url):
    """Extract first frame from video"""
    try:
        # Download video temporarily
        response = requests.get(url, stream=True)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
        temp_file.close()
        
        # Extract first frame
        cap = cv2.VideoCapture(temp_file.name)
        ret, frame = cap.read()
        
        if ret:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            
            # Save image
            image_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            image.save(image_file.name)
            
            cap.release()
            os.unlink(temp_file.name)
            return image_file.name
        
        cap.release()
        os.unlink(temp_file.name)
        return None
    except Exception as e:
        print(f"Error extracting first frame: {e}")
        return None

def perform_ocr(image_file):
    """Perform OCR on image"""
    try:
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        print(f"Error performing OCR: {e}")
        return "Could not perform OCR"

@app.route('/')
def index():
    """Main page"""
    data = load_data()
    return render_template('index.html', 
                         current_url=data.get('current_video_url', ''),
                         video_info=data.get('video_info', {}))

@app.route('/submit_url', methods=['POST'])
def submit_url():
    """Handle video URL submission"""
    url = request.json.get('url', '')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    # Get video info
    video_info = get_video_info(url)
    
    # Save data
    data = load_data()
    data['current_video_url'] = url
    data['video_info'] = video_info
    save_data(data)
    
    return jsonify({'success': True, 'video_info': video_info})

@app.route('/first_frame')
def first_frame():
    """Get first frame as image"""
    data = load_data()
    url = data.get('current_video_url')
    
    if not url:
        return jsonify({'error': 'No video URL'}), 400
    
    image_file = extract_first_frame(url)
    if image_file:
        return send_file(image_file, as_attachment=False, mimetype='image/png')
    else:
        return jsonify({'error': 'Could not extract first frame'}), 500

@app.route('/download_frame')
def download_frame():
    """Download first frame"""
    data = load_data()
    url = data.get('current_video_url')
    
    if not url:
        return jsonify({'error': 'No video URL'}), 400
    
    image_file = extract_first_frame(url)
    if image_file:
        return send_file(image_file, as_attachment=True, 
                        download_name='first_frame.png', mimetype='image/png')
    else:
        return jsonify({'error': 'Could not extract first frame'}), 500

@app.route('/ocr_text')
def ocr_text():
    """Perform OCR on first frame"""
    data = load_data()
    url = data.get('current_video_url')
    
    if not url:
        return jsonify({'error': 'No video URL'}), 400
    
    image_file = extract_first_frame(url)
    if not image_file:
        return jsonify({'error': 'Could not extract first frame'}), 500
    
    try:
        ocr_result = perform_ocr(image_file)
        os.unlink(image_file)
        return jsonify({'ocr_text': ocr_result})
    except Exception as e:
        if os.path.exists(image_file):
            os.unlink(image_file)
        return jsonify({'error': str(e)}), 500

# Placeholder routes for audio features (will show "coming soon" messages)
@app.route('/play_audio')
def play_audio():
    return jsonify({'error': 'Audio features require moviepy - install with: pip install moviepy==1.0.3'}), 501

@app.route('/download_audio')
def download_audio():
    return jsonify({'error': 'Audio features require moviepy - install with: pip install moviepy==1.0.3'}), 501

@app.route('/translate_audio')
def translate_audio():
    return jsonify({'error': 'Audio features require moviepy - install with: pip install moviepy==1.0.3'}), 501

@app.route('/speak_spanish')
def speak_spanish():
    return jsonify({'error': 'Audio features require moviepy - install with: pip install moviepy==1.0.3'}), 501

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
