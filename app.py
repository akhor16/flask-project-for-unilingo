from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import requests
import tempfile
import base64
from io import BytesIO
import uuid

# Import heavy dependencies with error handling
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError as e:
    print(f"OpenCV not available: {e}")
    CV2_AVAILABLE = False

try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError as e:
    print(f"MoviePy not available: {e}")
    MOVIEPY_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError as e:
    print(f"PIL not available: {e}")
    PIL_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError as e:
    print(f"SpeechRecognition not available: {e}")
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError as e:
    print(f"gTTS not available: {e}")
    GTTS_AVAILABLE = False

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError as e:
    print(f"pytesseract not available: {e}")
    PYTESSERACT_AVAILABLE = False

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

def is_youtube_url(url):
    """Check if URL is a YouTube URL"""
    youtube_domains = ['youtube.com', 'youtu.be', 'www.youtube.com', 'm.youtube.com']
    return any(domain in url.lower() for domain in youtube_domains)

def get_video_info(url):
    """Get video duration and height"""
    try:
        # Check if it's a YouTube URL
        if is_youtube_url(url):
            return {"duration": 0, "height": 0, "error": "YouTube URLs are not supported. Please use direct MP4 video URLs or upload your video to a file sharing service."}
        
        if not CV2_AVAILABLE:
            return {"duration": 0, "height": 0, "error": "Video processing not available - OpenCV not installed"}
        
        # Download video with proper headers and timeout
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, stream=True, headers=headers, timeout=30)
        
        # Handle specific HTTP errors
        if response.status_code == 402:
            return {"duration": 0, "height": 0, "error": "Video URL requires payment or has expired"}
        elif response.status_code == 403:
            return {"duration": 0, "height": 0, "error": "Video URL access forbidden"}
        elif response.status_code == 404:
            return {"duration": 0, "height": 0, "error": "Video URL not found"}
        
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        if 'video' not in content_type and 'mp4' not in content_type:
            return {"duration": 0, "height": 0, "error": f"URL does not appear to be a video file. Content type: {content_type}"}
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        
        # Download in chunks
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                temp_file.write(chunk)
        temp_file.close()
        
        # Verify file was downloaded completely
        if os.path.getsize(temp_file.name) == 0:
            os.unlink(temp_file.name)
            return {"duration": 0, "height": 0, "error": "Video file is empty"}
        
        # Get video info using OpenCV
        cap = cv2.VideoCapture(temp_file.name)
        
        if not cap.isOpened():
            cap.release()
            os.unlink(temp_file.name)
            return {"duration": 0, "height": 0, "error": "Could not open video file - may not be a valid MP4"}
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        os.unlink(temp_file.name)
        
        return {"duration": duration, "height": height}
    except requests.exceptions.RequestException as e:
        print(f"Network error getting video info: {e}")
        return {"duration": 0, "height": 0, "error": f"Network error: {str(e)}"}
    except Exception as e:
        print(f"Error getting video info: {e}")
        return {"duration": 0, "height": 0, "error": f"Processing error: {str(e)}"}

def extract_audio_segment(url, start_time=30, end_time=45):
    """Extract audio segment from video"""
    try:
        if not MOVIEPY_AVAILABLE:
            return None
            
        # Download video with proper headers and timeout
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, stream=True, headers=headers, timeout=30)
        response.raise_for_status()
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        
        # Download in chunks
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                temp_file.write(chunk)
        temp_file.close()
        
        # Verify file was downloaded completely
        if os.path.getsize(temp_file.name) == 0:
            os.unlink(temp_file.name)
            return None
        
        # Extract audio segment
        video = VideoFileClip(temp_file.name)
        
        # Check if video has audio
        if video.audio is None:
            video.close()
            os.unlink(temp_file.name)
            return None
        
        # Ensure we don't exceed video duration
        video_duration = video.duration
        if start_time >= video_duration:
            video.close()
            os.unlink(temp_file.name)
            return None
        
        # Adjust end_time to not exceed video duration
        end_time = min(end_time, video_duration)
        
        # Ensure we have at least some audio to extract
        if end_time <= start_time:
            video.close()
            os.unlink(temp_file.name)
            return None
        
        print(f"Extracting audio from {start_time}s to {end_time}s (duration: {end_time - start_time}s)")
        audio_segment = video.subclip(start_time, end_time)
        
        # Save audio segment as WAV for speech recognition
        audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        audio_segment.audio.write_audiofile(audio_file.name, verbose=False, logger=None, codec='pcm_s16le')
        
        video.close()
        audio_segment.close()
        os.unlink(temp_file.name)
        
        return audio_file.name
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return None

def transcribe_audio(audio_file):
    """Transcribe audio to text using speech recognition"""
    try:
        if not SPEECH_RECOGNITION_AVAILABLE:
            return "Speech recognition not available"
            
        # Check if audio file exists and has content
        if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
            return "No audio content found"
        
        r = sr.Recognizer()
        
        # Try multiple approaches for better transcription
        all_text = []
        
        # Method 1: Try to transcribe the entire audio at once
        try:
            with sr.AudioFile(audio_file) as source:
                # Adjust for ambient noise with longer duration
                r.adjust_for_ambient_noise(source, duration=1.0)
                audio = r.record(source)
                text = r.recognize_google(audio, language='en-US')
                if text.strip():
                    all_text.append(text)
        except Exception as e:
            print(f"Full audio transcription failed: {e}")
        
        # Method 2: Try with different noise adjustment
        try:
            with sr.AudioFile(audio_file) as source:
                # Try with shorter noise adjustment
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.record(source)
                text = r.recognize_google(audio, language='en-US')
                if text.strip() and text not in all_text:
                    all_text.append(text)
        except Exception as e:
            print(f"Alternative transcription failed: {e}")
        
        # Method 3: Try without noise adjustment
        try:
            with sr.AudioFile(audio_file) as source:
                audio = r.record(source)
                text = r.recognize_google(audio, language='en-US')
                if text.strip() and text not in all_text:
                    all_text.append(text)
        except Exception as e:
            print(f"No noise adjustment transcription failed: {e}")
        
        # Method 4: Try with minimal noise adjustment
        try:
            with sr.AudioFile(audio_file) as source:
                r.adjust_for_ambient_noise(source, duration=0.1)
                audio = r.record(source)
                text = r.recognize_google(audio, language='en-US')
                if text.strip() and text not in all_text:
                    all_text.append(text)
        except Exception as e:
            print(f"Minimal noise transcription failed: {e}")
        
        # Return the best result
        if all_text:
            # Return the longest transcription (most likely to be complete)
            return max(all_text, key=len)
        else:
            return "No speech detected in the audio"
            
    except sr.UnknownValueError:
        return "Could not understand the audio - audio may be too quiet or unclear"
    except sr.RequestError as e:
        return f"Speech recognition service error: {e}"
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return "Could not transcribe audio"

def translate_text(text, target_language='es'):
    """Translate text using Google Translate (free API)"""
    try:
        # Simple translation using Google Translate API (free tier)
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            'client': 'gtx',
            'sl': 'en',
            'tl': target_language,
            'dt': 't',
            'q': text
        }
        
        response = requests.get(url, params=params)
        result = response.json()
        
        if result and len(result) > 0 and len(result[0]) > 0:
            return result[0][0][0]
        return text
    except Exception as e:
        print(f"Error translating text: {e}")
        return text

def text_to_speech(text, language='es'):
    """Convert text to speech"""
    try:
        if not GTTS_AVAILABLE:
            return None
            
        tts = gTTS(text=text, lang=language, slow=False)
        audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts.save(audio_file.name)
        return audio_file.name
    except Exception as e:
        print(f"Error with text-to-speech: {e}")
        return None

def extract_first_frame(url):
    """Extract first frame from video"""
    try:
        if not CV2_AVAILABLE or not PIL_AVAILABLE:
            return None
            
        # Download video with proper headers and timeout
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, stream=True, headers=headers, timeout=30)
        response.raise_for_status()
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        
        # Download in chunks
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                temp_file.write(chunk)
        temp_file.close()
        
        # Verify file was downloaded completely
        if os.path.getsize(temp_file.name) == 0:
            os.unlink(temp_file.name)
            return None
        
        # Extract first frame
        cap = cv2.VideoCapture(temp_file.name)
        
        if not cap.isOpened():
            cap.release()
            os.unlink(temp_file.name)
            return None
        
        ret, frame = cap.read()
        
        if ret and frame is not None:
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

def extract_multiple_frames_for_ocr(url, num_frames=5):
    """Extract multiple frames from video for better OCR coverage"""
    try:
        # Download video with proper headers and timeout
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, stream=True, headers=headers, timeout=30)
        response.raise_for_status()
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        
        # Download in chunks
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                temp_file.write(chunk)
        temp_file.close()
        
        # Verify file was downloaded completely
        if os.path.getsize(temp_file.name) == 0:
            os.unlink(temp_file.name)
            return []
        
        # Extract multiple frames
        cap = cv2.VideoCapture(temp_file.name)
        
        if not cap.isOpened():
            cap.release()
            os.unlink(temp_file.name)
            return []
        
        # Get video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        
        frame_files = []
        
        # Extract frames at different time points
        time_points = [0, duration/4, duration/2, 3*duration/4, duration-1] if duration > 0 else [0]
        
        for i, time_point in enumerate(time_points[:num_frames]):
            # Set frame position
            cap.set(cv2.CAP_PROP_POS_MSEC, time_point * 1000)
            ret, frame = cap.read()
            
            if ret and frame is not None:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame_rgb)
                
                # Save image
                image_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'_frame_{i}.png')
                image.save(image_file.name)
                frame_files.append(image_file.name)
        
        cap.release()
        os.unlink(temp_file.name)
        return frame_files
        
    except Exception as e:
        print(f"Error extracting multiple frames: {e}")
        return []

def perform_ocr(image_file):
    """Perform OCR on image"""
    try:
        if not PYTESSERACT_AVAILABLE or not PIL_AVAILABLE:
            return "OCR not available on this platform - Tesseract not installed"
            
        # Try to set tesseract path for different systems
        import platform
        system = platform.system()
        
        if system == "Windows":
            possible_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME', '')),
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
        elif system == "Linux":
            # For deployment platforms like Railway/Heroku
            try:
                pytesseract.pytesseract.tesseract_cmd = 'tesseract'
            except:
                pass
        
        # Test if tesseract is actually available
        try:
            pytesseract.get_tesseract_version()
        except Exception as e:
            return f"Tesseract not properly installed: {str(e)}"
        
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image)
        return text.strip() if text.strip() else "No text detected in the image"
    except Exception as e:
        print(f"Error performing OCR: {e}")
        return f"OCR not available on this platform. Error: {str(e)}"

@app.route('/')
def index():
    """Main page"""
    data = load_data()
    return render_template('index.html', 
                         current_url=data.get('current_video_url', ''),
                         video_info=data.get('video_info', {}))

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return jsonify({
        "status": "healthy", 
        "message": "Video Processing App is running",
        "dependencies": {
            "opencv": CV2_AVAILABLE,
            "moviepy": MOVIEPY_AVAILABLE,
            "pil": PIL_AVAILABLE,
            "speech_recognition": SPEECH_RECOGNITION_AVAILABLE,
            "gtts": GTTS_AVAILABLE,
            "pytesseract": PYTESSERACT_AVAILABLE
        }
    })

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

@app.route('/play_audio')
def play_audio():
    """Extract and return audio segment"""
    data = load_data()
    url = data.get('current_video_url')
    
    if not url:
        return jsonify({'error': 'No video URL'}), 400
    
    audio_file = extract_audio_segment(url)
    if audio_file:
        return send_file(audio_file, as_attachment=False, mimetype='audio/wav')
    else:
        return jsonify({'error': 'Could not extract audio'}), 500

@app.route('/download_audio')
def download_audio():
    """Download audio segment"""
    data = load_data()
    url = data.get('current_video_url')
    
    if not url:
        return jsonify({'error': 'No video URL'}), 400
    
    audio_file = extract_audio_segment(url)
    if audio_file:
        return send_file(audio_file, as_attachment=True, 
                        download_name='audio_segment.wav', mimetype='audio/wav')
    else:
        return jsonify({'error': 'Could not extract audio'}), 500

@app.route('/translate_audio')
def translate_audio():
    """Transcribe and translate audio"""
    data = load_data()
    url = data.get('current_video_url')
    
    if not url:
        return jsonify({'error': 'No video URL'}), 400
    
    # Extract audio
    audio_file = extract_audio_segment(url)
    if not audio_file:
        return jsonify({'error': 'Could not extract audio'}), 500
    
    try:
        # Transcribe
        transcribed_text = transcribe_audio(audio_file)
        
        # Translate
        translated_text = translate_text(transcribed_text, 'es')
        
        # Clean up
        os.unlink(audio_file)
        
        return jsonify({
            'transcribed': transcribed_text,
            'translated': translated_text
        })
    except Exception as e:
        if os.path.exists(audio_file):
            os.unlink(audio_file)
        return jsonify({'error': str(e)}), 500

@app.route('/speak_spanish')
def speak_spanish():
    """Generate Spanish speech"""
    data = load_data()
    url = data.get('current_video_url')
    
    if not url:
        return jsonify({'error': 'No video URL'}), 400
    
    # Get translated text
    audio_file = extract_audio_segment(url)
    if not audio_file:
        return jsonify({'error': 'Could not extract audio'}), 500
    
    try:
        transcribed_text = transcribe_audio(audio_file)
        translated_text = translate_text(transcribed_text, 'es')
        
        # Generate speech
        speech_file = text_to_speech(translated_text, 'es')
        
        # Clean up
        os.unlink(audio_file)
        
        if speech_file:
            return send_file(speech_file, as_attachment=False, mimetype='audio/mpeg')
        else:
            return jsonify({'error': 'Could not generate speech'}), 500
    except Exception as e:
        if os.path.exists(audio_file):
            os.unlink(audio_file)
        return jsonify({'error': str(e)}), 500

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

@app.route('/debug_audio')
def debug_audio():
    """Debug audio extraction and transcription"""
    data = load_data()
    url = data.get('current_video_url')
    
    if not url:
        return jsonify({'error': 'No video URL'}), 400
    
    try:
        # Extract audio
        audio_file = extract_audio_segment(url)
        if not audio_file:
            return jsonify({'error': 'Could not extract audio'}), 500
        
        # Get file size
        file_size = os.path.getsize(audio_file)
        
        # Try transcription
        transcribed_text = transcribe_audio(audio_file)
        
        # Clean up
        os.unlink(audio_file)
        
        return jsonify({
            'audio_file_size': file_size,
            'transcribed_text': transcribed_text,
            'message': 'Audio extraction and transcription completed'
        })
    except Exception as e:
        if 'audio_file' in locals() and os.path.exists(audio_file):
            os.unlink(audio_file)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
