from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import tempfile
import sounddevice as sd
import numpy as np
import scipy.io.wavfile
import io
import warnings
import threading
import time
from datetime import datetime

# Suppress the FP16 warning
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variables for recording
recording_thread = None
is_recording = False
audio_chunks = []
fs = 16000

def log_message(message):
    """Helper function to log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def record_audio():
    """Record audio in a separate thread"""
    global audio_chunks, is_recording
    audio_chunks = []
    log_message("🎤 Starting audio recording thread")
    
    def callback(indata, frames, time, status):
        if is_recording:
            audio_chunks.append(indata.copy())
            if len(audio_chunks) % 10 == 0:  # Log every 10 chunks
                log_message(f"📊 Recorded {len(audio_chunks)} audio chunks so far")
    
    with sd.InputStream(callback=callback, channels=1, samplerate=fs):
        while is_recording:
            time.sleep(0.1)

def transcribe_audio(audio_data):
    """Transcribe audio data"""
    try:
        log_message("🔍 Starting audio transcription")
        # Import whisper here to avoid circular import
        import whisper
        model = whisper.load_model("base")
        
        # Combine all audio chunks
        if audio_chunks:
            log_message(f"🎵 Processing {len(audio_chunks)} audio chunks")
            audio = np.concatenate(audio_chunks, axis=0).flatten()
            log_message(f"📏 Audio length: {len(audio)} samples ({len(audio)/fs:.2f} seconds)")
            
            # Save temp WAV and transcribe
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                scipy.io.wavfile.write(f.name, fs, audio.astype(np.float32))
                log_message("🎯 Running Whisper transcription...")
                result = model.transcribe(f.name)
                os.unlink(f.name)  # Clean up temp file
            
            log_message(f"✅ Transcription completed: '{result['text']}'")
            return result["text"]
        else:
            log_message("⚠️ No audio chunks to transcribe")
            return ""
        
    except Exception as e:
        log_message(f"❌ Error in transcribe_audio: {e}")
        return ""

def transcribe_uploaded_file(audio_file):
    """Transcribe uploaded audio file"""
    try:
        log_message(f"📁 Processing uploaded file: {audio_file.filename}")
        log_message(f"📋 File content type: {audio_file.content_type}")
        log_message(f"📋 File size: {len(audio_file.read())} bytes")
        audio_file.seek(0)  # Reset file pointer after reading
        
        # Import whisper here to avoid circular import
        import whisper
        model = whisper.load_model("base")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as f:
            audio_file.save(f.name)
            log_message(f"💾 Saved temporary file: {f.name}")
            
            try:
                log_message("🎯 Running Whisper transcription on uploaded file...")
                result = model.transcribe(f.name)
                log_message(f"✅ Upload transcription completed: '{result['text']}'")
                return result["text"]
            except Exception as transcribe_error:
                log_message(f"❌ Whisper transcription failed: {transcribe_error}")
                # Try with different file extension if m4a fails
                import shutil
                wav_file = f.name.replace('.m4a', '.wav')
                shutil.copy2(f.name, wav_file)
                log_message(f"🔄 Trying with WAV format: {wav_file}")
                try:
                    result = model.transcribe(wav_file)
                    log_message(f"✅ WAV transcription completed: '{result['text']}'")
                    os.unlink(wav_file)  # Clean up WAV file
                    return result["text"]
                except Exception as wav_error:
                    log_message(f"❌ WAV transcription also failed: {wav_error}")
                    os.unlink(wav_file)  # Clean up WAV file
                    raise transcribe_error
            finally:
                os.unlink(f.name)  # Clean up temp file
        
    except Exception as e:
        log_message(f"❌ Error in transcribe_uploaded_file: {e}")
        return f"Transcription failed: {str(e)}"

@app.route('/')
def index():
    log_message("🌐 Homepage requested")
    return app.send_static_file('index.html')

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global recording_thread, is_recording
    
    try:
        log_message("▶️ Start recording request received")
        is_recording = True
        recording_thread = threading.Thread(target=record_audio)
        recording_thread.start()
        log_message("✅ Recording started successfully")
        
        return jsonify({'status': 'Recording started'})
        
    except Exception as e:
        log_message(f"❌ Error starting recording: {e}")
        return jsonify({'error': 'Failed to start recording'}), 500

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global recording_thread, is_recording
    
    try:
        log_message("⏹️ Stop recording request received")
        is_recording = False
        
        if recording_thread:
            recording_thread.join(timeout=2)
        
        log_message(f"📊 Total audio chunks recorded: {len(audio_chunks)}")
        
        # Transcribe the recorded audio
        transcription = transcribe_audio(audio_chunks)
        log_message(f"📝 Final transcription: '{transcription}'")
        return jsonify({'transcription': transcription})
        
    except Exception as e:
        log_message(f"❌ Error stopping recording: {e}")
        return jsonify({'error': 'Failed to stop recording'}), 500

@app.route('/transcribe', methods=['POST'])
def transcribe_upload():
    """Handle file upload from React Native app"""
    try:
        log_message("📤 Transcribe upload request received")
        log_message(f"📋 Request headers: {dict(request.headers)}")
        log_message(f"📋 Request form data: {dict(request.form)}")
        log_message(f"📋 Request files: {list(request.files.keys())}")
        
        if 'audio' not in request.files:
            log_message("❌ No audio file in request.files")
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        log_message(f"📁 Received audio file: {audio_file.filename}")
        
        if audio_file.filename == '':
            log_message("❌ Empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        # Transcribe the uploaded file
        transcription = transcribe_uploaded_file(audio_file)
        
        log_message(f"📤 Sending transcription response: '{transcription}'")
        return jsonify({'transcription': transcription})
        
    except Exception as e:
        log_message(f"❌ Error in transcribe_upload: {e}")
        return jsonify({'error': 'Failed to transcribe audio'}), 500

# Add a new endpoint to receive transcript chunks
@app.route('/receive_transcript', methods=['POST'])
def receive_transcript():
    """Receive transcript chunks from the React Native app"""
    try:
        log_message("📨 Transcript chunk received")
        log_message(f"📋 Request headers: {dict(request.headers)}")
        log_message(f"📋 Request JSON: {request.get_json()}")
        
        data = request.get_json()
        if not data:
            log_message("❌ No JSON data in request")
            return jsonify({'error': 'No data provided'}), 400
        
        transcript_chunk = data.get('transcript', '')
        chunk_id = data.get('id', 'unknown')
        is_final = data.get('isFinal', False)
        
        log_message(f"📝 Transcript chunk {chunk_id}: '{transcript_chunk}' (final: {is_final})")
        
        # Here you can process the transcript chunk as needed
        # For now, just acknowledge receipt
        
        response = {
            'status': 'received',
            'chunk_id': chunk_id,
            'transcript': transcript_chunk,
            'is_final': is_final
        }
        
        log_message(f"✅ Sending acknowledgment for chunk {chunk_id}")
        return jsonify(response)
        
    except Exception as e:
        log_message(f"❌ Error in receive_transcript: {e}")
        return jsonify({'error': 'Failed to process transcript chunk'}), 500

if __name__ == '__main__':
    # Create static folder if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    # Move the HTML file to static folder
    if os.path.exists('index.html'):
        import shutil
        shutil.move('index.html', 'static/index.html')
    
    log_message("🎤 Voice Transcription Server Starting...")
    log_message("📱 Open your browser and go to: http://localhost:5001")
    log_message("📱 For React Native app, use your computer's IP address")
    log_message("🎙️ Click 'Start Recording' to begin, then 'Stop Recording' when done!")
    log_message("📨 New endpoint /receive_transcript available for transcript chunks")
    
    app.run(debug=True, host='0.0.0.0', port=5001) 