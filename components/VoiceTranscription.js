import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';

const SERVER_URL = 'http://10.56.148.120:5001'; // Change this to your server IP

export default function VoiceTranscription() {
  const [recording, setRecording] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [timer, setTimer] = useState(null);

  useEffect(() => {
    // Request permissions on component mount
    requestPermissions();
    return () => {
      if (timer) clearInterval(timer);
    };
  }, []);

  const requestPermissions = async () => {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission needed', 'Audio recording permission is required');
      }
    } catch (error) {
      console.error('Error requesting permissions:', error);
    }
  };

  const startRecording = async () => {
    try {
      setIsProcessing(true);
      
      // Configure audio mode
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
        staysActiveInBackground: true,
        shouldDuckAndroid: true,
        playThroughEarpieceAndroid: false,
      });

      // Start recording
      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      
      setRecording(recording);
      setIsRecording(true);
      setIsProcessing(false);
      setRecordingTime(0);
      
      // Start timer
      const interval = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      setTimer(interval);

      console.log('Recording started');
    } catch (error) {
      console.error('Error starting recording:', error);
      Alert.alert('Error', 'Failed to start recording');
      setIsProcessing(false);
    }
  };

  const stopRecording = async () => {
    try {
      setIsProcessing(true);
      
      if (timer) {
        clearInterval(timer);
        setTimer(null);
      }

      if (recording) {
        await recording.stopAndUnloadAsync();
        const uri = recording.getURI();
        setRecording(null);
        setIsRecording(false);
        
        // Upload and transcribe
        await uploadAndTranscribe(uri);
      }
    } catch (error) {
      console.error('Error stopping recording:', error);
      Alert.alert('Error', 'Failed to stop recording');
      setIsProcessing(false);
    }
  };

  const uploadAndTranscribe = async (audioUri) => {
    try {
      console.log('📤 Starting audio upload to:', SERVER_URL);
      console.log('📁 Audio URI:', audioUri);
      
      // Get file info to determine correct MIME type
      const fileInfo = await FileSystem.getInfoAsync(audioUri);
      console.log('📊 File info:', fileInfo);
      
      // Determine MIME type based on file extension
      let mimeType = 'audio/m4a'; // Default for Expo Audio
      if (audioUri.endsWith('.wav')) {
        mimeType = 'audio/wav';
      } else if (audioUri.endsWith('.m4a')) {
        mimeType = 'audio/m4a';
      } else if (audioUri.endsWith('.mp3')) {
        mimeType = 'audio/mp3';
      }
      
      console.log('🎵 Using MIME type:', mimeType);

      // Create form data
      const formData = new FormData();
      formData.append('audio', {
        uri: audioUri,
        type: mimeType,
        name: 'recording.m4a'
      });

      console.log('📤 Sending request to server...');

      // Upload to server
      const response = await fetch(`${SERVER_URL}/transcribe`, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('📥 Response status:', response.status);
      console.log('📥 Response headers:', response.headers);

      if (response.ok) {
        const result = await response.json();
        console.log('✅ Transcription result:', result);
        setTranscription(result.transcription || 'No transcription available');
      } else {
        const errorText = await response.text();
        console.error('❌ Server error response:', errorText);
        throw new Error(`Server error: ${response.status} - ${errorText}`);
      }
    } catch (error) {
      console.error('❌ Error uploading audio:', error);
      Alert.alert('Error', `Failed to transcribe audio: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const clearTranscription = () => {
    setTranscription('');
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>🎤 Voice Transcription</Text>
        <Text style={styles.subtitle}>Tap to record your voice</Text>
      </View>

      <View style={styles.controls}>
        <TouchableOpacity
          style={[
            styles.recordButton,
            isRecording && styles.recordButtonRecording,
            isProcessing && styles.recordButtonDisabled
          ]}
          onPress={isRecording ? stopRecording : startRecording}
          disabled={isProcessing}
        >
          {isProcessing ? (
            <ActivityIndicator color="white" size="large" />
          ) : (
            <Text style={styles.recordButtonText}>
              {isRecording ? '⏹️ Stop' : '🎙️ Record'}
            </Text>
          )}
        </TouchableOpacity>

        {isRecording && (
          <View style={styles.recordingInfo}>
            <View style={styles.recordingDot} />
            <Text style={styles.recordingText}>
              Recording... {formatTime(recordingTime)}
            </Text>
          </View>
        )}
      </View>

      <View style={styles.transcriptionContainer}>
        <View style={styles.transcriptionHeader}>
          <Text style={styles.transcriptionTitle}>Transcription</Text>
          {transcription ? (
            <TouchableOpacity onPress={clearTranscription}>
              <Text style={styles.clearButton}>Clear</Text>
            </TouchableOpacity>
          ) : null}
        </View>
        
        <ScrollView style={styles.transcriptionArea}>
          <Text style={styles.transcriptionText}>
            {transcription || 'Your transcribed text will appear here...'}
          </Text>
        </ScrollView>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 40,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  controls: {
    alignItems: 'center',
    marginBottom: 30,
  },
  recordButton: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#ff6b6b',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  recordButtonRecording: {
    backgroundColor: '#2c3e50',
  },
  recordButtonDisabled: {
    opacity: 0.6,
  },
  recordButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  recordingInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 20,
  },
  recordingDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#ff6b6b',
    marginRight: 10,
  },
  recordingText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  transcriptionContainer: {
    flex: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 15,
    padding: 20,
  },
  transcriptionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  transcriptionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: 'white',
  },
  clearButton: {
    color: '#ff6b6b',
    fontSize: 16,
    fontWeight: 'bold',
  },
  transcriptionArea: {
    flex: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 10,
    padding: 15,
  },
  transcriptionText: {
    fontSize: 16,
    lineHeight: 24,
    color: 'white',
  },
}); 