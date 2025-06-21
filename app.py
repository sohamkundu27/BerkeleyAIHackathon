from flask import Flask, render_template, request, jsonify
import os
import tempfile
import sounddevice as sd
import numpy as np
import scipy.io.wavfile
import io
import warnings
import threading
import time

# Suppress the FP16 warning
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

app = Flask(__name__)

# Global variables for recording
recording_thread = None
is_recording = False
audio_chunks = []
fs = 16000

def record_audio():
    """Record audio in a separate thread"""
    global audio_chunks, is_recording
    audio_chunks = []
    
    def callback(indata, frames, time, status):
        if is_recording:
            audio_chunks.append(indata.copy())
    
    with sd.InputStream(callback=callback, channels=1, samplerate=fs):
        while is_recording:
            time.sleep(0.1)

def transcribe_audio(audio_data):
    """Transcribe audio data"""
    try:
        # Import whisper here to avoid circular import
        import whisper
        model = whisper.load_model("base")
        
        # Combine all audio chunks
        if audio_chunks:
            audio = np.concatenate(audio_chunks, axis=0).flatten()
            
            # Save temp WAV and transcribe
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                scipy.io.wavfile.write(f.name, fs, audio.astype(np.float32))
                result = model.transcribe(f.name)
                os.unlink(f.name)  # Clean up temp file
            
            return result["text"]
        else:
            return ""
        
    except Exception as e:
        print(f"Error in transcribe_audio: {e}")
        return ""

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global recording_thread, is_recording
    
    try:
        is_recording = True
        recording_thread = threading.Thread(target=record_audio)
        recording_thread.start()
        
        return jsonify({'status': 'Recording started'})
        
    except Exception as e:
        print(f"Error starting recording: {e}")
        return jsonify({'error': 'Failed to start recording'}), 500

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global recording_thread, is_recording
    
    try:
        is_recording = False
        
        if recording_thread:
            recording_thread.join(timeout=2)
        
        # Transcribe the recorded audio
        transcription = transcribe_audio(audio_chunks)
        
        return jsonify({'transcription': transcription})
        
    except Exception as e:
        print(f"Error stopping recording: {e}")
        return jsonify({'error': 'Failed to stop recording'}), 500

if __name__ == '__main__':
    # Create static folder if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    # Move the HTML file to static folder
    if os.path.exists('index.html'):
        import shutil
        shutil.move('index.html', 'static/index.html')
    
    print("🎤 Voice Transcription Server Starting...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🎙️ Click 'Start Recording' to begin, then 'Stop Recording' when done!")
    
    app.run(debug=True, host='0.0.0.0', port=5001) 