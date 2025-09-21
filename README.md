# Video Processing Web App

A comprehensive Flask-based web application that processes MP4 videos with advanced features including audio extraction, translation, text-to-speech, and OCR capabilities.

## 🚀 Features

### ✅ All Checkpoints Completed

1. **Video URL Input & Persistence** - Submit MP4 video URLs with persistent storage
2. **Video Information Display** - Shows duration (seconds) and height (pixels)
3. **Audio Playback & Download** - Extract and play audio from 0:30-0:45, with download option
4. **Audio Translation** - Transcribe audio and translate to Spanish using Google APIs
5. **Spanish Text-to-Speech** - Convert translated text to Spanish speech
6. **First Frame Extraction** - Display and download the first frame as an image
7. **OCR Text Detection** - Extract text from the first frame using Tesseract OCR

## 🛠️ Tech Stack

### Backend
- **Flask** - Lightweight Python web framework
- **OpenCV** - Video processing and frame extraction
- **MoviePy** - Audio extraction from videos
- **SpeechRecognition** - Audio transcription using Google Speech API
- **gTTS (Google Text-to-Speech)** - Text-to-speech conversion
- **Pytesseract** - OCR text extraction
- **Pillow (PIL)** - Image processing
- **Requests** - HTTP requests for video downloads

### Frontend
- **HTML5/CSS3** - Modern, responsive design
- **Vanilla JavaScript** - Clean, lightweight client-side functionality
- **CSS Grid/Flexbox** - Responsive layout
- **Gradient Design** - Modern, professional appearance

### APIs Used
- **Google Speech Recognition** - Free audio transcription
- **Google Translate API** - Free text translation
- **Google Text-to-Speech** - Free TTS conversion

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- Tesseract OCR installed on system

### Installation Steps

1. **Clone/Download the project**
```bash
cd flaskProjectForUnilingo
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Tesseract OCR**
   - **Windows**: Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

4. **Run the application**
```bash
python app.py
```

5. **Access the application**
   - Open browser to `http://localhost:5000`

## 🎯 Usage Instructions

1. **Submit Video URL**: Paste an MP4 video URL in the input field and click "Submit URL"
2. **View Video Info**: See duration and height information automatically displayed
3. **Play Audio**: Click "Play Audio" to hear the 15-second segment (0:30-0:45)
4. **Download Audio**: Click "Download Audio" to save the audio segment
5. **Translate**: Click "Translate to Spanish" to see transcription and translation
6. **Spanish Speech**: Click "Speak Spanish Translation" to hear the Spanish version
7. **View Frame**: Click "Show First Frame" to see the first video frame
8. **Download Frame**: Click "Download Frame" to save the first frame image
9. **OCR Text**: Click "Extract Text from Frame" to see detected text

## 🔧 Technical Implementation

### Data Persistence
- Uses JSON file (`video_data.json`) for simple, file-based persistence
- Stores current video URL and metadata
- Survives server restarts and refreshes

### Video Processing
- Downloads videos temporarily for processing
- Uses OpenCV for video metadata extraction
- MoviePy for audio segment extraction
- Automatic cleanup of temporary files

### API Integration
- **Speech Recognition**: Google's free speech-to-text API
- **Translation**: Google Translate's free API endpoint
- **Text-to-Speech**: Google's gTTS library
- **OCR**: Tesseract with Python bindings

### Error Handling
- Comprehensive try-catch blocks
- User-friendly error messages
- Graceful degradation for API failures
- Automatic cleanup of temporary files

## 🌐 Deployment Considerations

### For Production Deployment
1. **Environment Variables**: Store API keys securely
2. **Database**: Replace JSON file with proper database (PostgreSQL/MongoDB)
3. **Caching**: Implement Redis for video processing cache
4. **CDN**: Use CDN for static assets
5. **Load Balancing**: Multiple app instances behind load balancer
6. **Monitoring**: Add logging and monitoring (Sentry, etc.)

### Recommended Platforms
- **Heroku**: Easy deployment with Procfile
- **Railway**: Modern platform with automatic deployments
- **DigitalOcean App Platform**: Scalable with managed databases
- **AWS/GCP**: Full control with containerization

## 🔒 Security & API Keys

### Current Implementation
- Uses free Google APIs (no API keys required)
- Temporary file cleanup prevents disk space issues
- Input validation for URLs
- File size limits (100MB max)

### Production Security
- Environment variables for sensitive data
- API rate limiting
- Input sanitization
- HTTPS enforcement
- CORS configuration

## 📊 Performance Optimizations

### Implemented
- Streaming video downloads
- Temporary file cleanup
- Efficient video processing
- Responsive frontend design

### Future Improvements
- Video processing queue (Celery)
- Result caching
- Progressive loading
- WebSocket for real-time updates

## 🐛 Known Limitations

1. **Video Size**: Limited to 100MB videos
2. **Processing Time**: Large videos may take time to process
3. **API Limits**: Free Google APIs have usage limits
4. **OCR Accuracy**: Depends on image quality and text clarity
5. **Audio Quality**: Transcription accuracy varies with audio quality

## 🚀 Quick Start for Testing

1. Use the provided test URL:
   ```
   https://firebasestorage.googleapis.com/v0/b/testlingo-e48de.appspot.com/o/videolingo.mp4?alt=media&token=28e6cb7d-7906-4fff-8a41-c49191c1074a
   ```

2. All features should work with this test video

## 📝 Development Notes

### Code Quality
- Clean, well-documented Python code
- Separation of concerns (routes, utilities, processing)
- Error handling throughout
- Modern HTML/CSS with responsive design

### Scalability
- Modular design allows easy feature additions
- API endpoints are RESTful
- Frontend is framework-agnostic
- Easy to containerize with Docker

## 🎉 Project Completion

All 7 checkpoints have been successfully implemented:
- ✅ Checkpoint 1: Video URL input with persistence
- ✅ Checkpoint 2: Video duration and height display
- ✅ Checkpoint 3: Audio playback and download (0:30-0:45)
- ✅ Checkpoint 4: Audio translation to Spanish
- ✅ Checkpoint 5: Spanish text-to-speech
- ✅ Checkpoint 6: First frame display and download
- ✅ Checkpoint 7: OCR text extraction

The application is ready for deployment and testing with the provided video URL.

---

**Built with ❤️ using Flask, OpenCV, and modern web technologies**
