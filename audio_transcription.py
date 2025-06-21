import warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")
import whisper
import sounddevice as sd
import numpy as np

model = whisper.load_model("base")  # or "small", "medium", "large"

def record_audio(duration=5, fs=16000):
    print("🎙️ Speak now...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    return recording.flatten()

def transcribe_audio(audio, fs=16000):
    # Save temp WAV
    import tempfile
    import scipy.io.wavfile
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        scipy.io.wavfile.write(f.name, fs, audio.astype(np.float32))
        result = model.transcribe(f.name)
    return result["text"]

def full_flow():
    audio = record_audio(duration=5)
    text = transcribe_audio(audio)
    print("📝 Transcription:", text)
    return text

# Pipe into your pipeline
# get_response(text) ← from your LLM chain

full_flow()