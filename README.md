# Voice Transcription Mobile App

A React Native mobile app that records audio and sends it to a Flask backend for transcription using Whisper AI.

## 🏗️ Architecture

- **React Native Mobile App**: Records audio and uploads to server
- **Flask Backend**: Handles audio transcription using Whisper AI
- **LLM Pipeline**: Processes transcribed text through Claude AI

## 📱 Mobile App Setup

### Prerequisites

- Node.js (v16 or higher)
- Expo CLI: `npm install -g @expo/cli`
- iOS Simulator (for iOS) or Android Studio (for Android)

### Installation

1. Install dependencies:

```bash
npm install
```

2. Start the development server:

```bash
npm start
```

3. Run on device/simulator:

- Press `i` for iOS simulator
- Press `a` for Android emulator
- Scan QR code with Expo Go app on your phone

### Configuration

Update the server URL in `components/VoiceTranscription.js`:

```javascript
const SERVER_URL = "http://YOUR_COMPUTER_IP:5001";
```

To find your computer's IP address:

- **Mac/Linux**: `ifconfig` or `ip addr`
- **Windows**: `ipconfig`

## 🖥️ Backend Setup

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Start the Flask server:

```bash
python app.py
```

The server will run on `http://0.0.0.0:5001`

## 🚀 Usage

### Mobile App

1. Open the app on your device
2. Grant microphone permissions when prompted
3. Tap the red "Record" button to start recording
4. Tap "Stop" when finished
5. View the transcription in the text area

### Web Interface

1. Open `http://localhost:5001` in your browser
2. Click "Start Recording" to begin
3. Click "Stop Recording" when done
4. View the transcription

## 📁 Project Structure

```
BerkeleyAIHackathon/
├── app.py                 # Flask backend server
├── LLMPipeline.py         # Claude AI processing pipeline
├── audio_transcription.py # Standalone audio transcription
├── package.json           # React Native dependencies
├── App.js                 # Main React Native app
├── components/
│   └── VoiceTranscription.js  # Audio recording component
├── static/
│   └── index.html         # Web interface
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔧 Troubleshooting

### Common Issues

1. **Connection Error**: Make sure your phone and computer are on the same WiFi network
2. **Permission Denied**: Grant microphone permissions in your device settings
3. **Server Not Found**: Check that the Flask server is running and the IP address is correct

### Network Configuration

- Ensure your computer's firewall allows connections on port 5001
- For Android, you may need to use `adb reverse tcp:5001 tcp:5001`

## 🎯 Features

- ✅ Real-time audio recording
- ✅ High-quality audio capture
- ✅ Automatic transcription with Whisper AI
- ✅ Beautiful mobile UI
- ✅ Cross-platform (iOS & Android)
- ✅ Web interface backup
- ✅ Error handling and user feedback

## 🔮 Next Steps

- [ ] Add offline recording capability
- [ ] Implement push notifications
- [ ] Add audio playback
- [ ] Support for multiple languages
- [ ] Integration with LLM pipeline for task processing

## 📄 License

This project is part of the Berkeley AI Hackathon.
