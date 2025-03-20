import React, { useState, useEffect, useRef } from 'react';
import { View, StyleSheet, Text, Button, Alert, ScrollView } from 'react-native';
import { Camera, CameraView } from 'expo-camera';
import * as Speech from 'expo-speech';
import { Audio } from 'expo-av';  // Add this import
import { RootStackParamList } from '../navigation/types';
import { StackScreenProps } from '@react-navigation/stack';
import { recognizeText, speakText } from '../apiService';  // Import speakText

type Props = StackScreenProps<RootStackParamList, 'TextToSpeech'>;

const TextToSpeechScreen = ({ navigation }: Props) => {  // Add navigation prop
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [cameraReady, setCameraReady] = useState(false);
  const [recognizedText, setRecognizedText] = useState('');
  const [processing, setProcessing] = useState(false);
  const [sound, setSound] = useState<Audio.Sound | null>(null);
  const cameraRef = useRef<CameraView>(null);

  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
      
      // Also request audio permissions
      await Audio.requestPermissionsAsync();
    })();
    
    // Clean up sound when component unmounts
    return () => {
      if (sound) {
        sound.unloadAsync();
      }
    };
  }, []);

  const handleCameraReady = () => {
    setCameraReady(true);
  };

  const capturePhoto = async () => {
    if (!cameraReady || !cameraRef.current || processing) {
      Alert.alert('Camera not ready');
      return;
    }
  
    setProcessing(true);
    try {
      // Provide feedback
      Speech.speak("Capturing image");
      
      const photo = await cameraRef.current.takePictureAsync();
  
      // Check if photo is defined before proceeding
      if (photo && photo.uri) {
        Speech.speak("Recognizing text");
        await recognizeTextFromImage(photo.uri);
      } else {
        Alert.alert('Failed to capture photo');
      }
    } catch (error) {
      Alert.alert('Error capturing photo');
    } finally {
      setProcessing(false);
    }
  };

  const recognizeTextFromImage = async (imageUri: string) => {
    try {
      const result = await recognizeText(imageUri);
      
      if (result.success && result.text) {
        setRecognizedText(result.text);
        Speech.speak("Text recognized");
      } else {
        setRecognizedText("No text recognized");
        Speech.speak("No text recognized");
      }
    } catch (error) {
      console.error("Error recognizing text:", error);
      Alert.alert('Error recognizing text.');
      setRecognizedText("Error recognizing text");
    }
  };

  const handleSpeakText = async () => {
    if (!recognizedText) {
      Alert.alert('No text to speak');
      return;
    }
    
    setProcessing(true);
    try {
      // Call the API service function
      const result = await speakText(recognizedText);
      
      if (result.success && result.audioUri) {
        // Clean up previous sound
        if (sound) {
          await sound.unloadAsync();
        }
        
        // Create a new sound object
        const { sound: newSound } = await Audio.Sound.createAsync(
          { uri: result.audioUri },
          { shouldPlay: true }
        );
        
        setSound(newSound);
      } else {
        // Fallback to local TTS (which may not support Kannada)
        Speech.speak(recognizedText);
      }
    } catch (error) {
      console.error("Error speaking text:", error);
      // Fall back to local TTS as last resort
      Speech.speak(recognizedText);
    } finally {
      setProcessing(false);
    }
  };

  if (hasPermission === null) {
    return <View style={styles.container}><Text>Requesting camera permission...</Text></View>;
  }

  if (hasPermission === false) {
    return <View style={styles.container}><Text>No access to camera</Text></View>;
  }

  return (
    <View style={styles.container}>
      <CameraView
        style={styles.camera}
        facing="back"
        onCameraReady={handleCameraReady}
        ref={cameraRef}
      >
        <View style={styles.overlay}>
          <Text style={styles.overlayText}>Point the camera at text</Text>
        </View>
      </CameraView>

      <ScrollView style={styles.textContainer}>
        <Text style={styles.recognizedText}>
          {recognizedText || 'No text recognized yet.'}
        </Text>
      </ScrollView>

      <View style={styles.buttonContainer}>
        <Button 
          title={processing ? "Processing..." : "Capture & Recognize Text"} 
          onPress={capturePhoto}
          disabled={processing || !cameraReady}
        />
        <Button
          title="Speak Text"
          onPress={handleSpeakText}
          disabled={!recognizedText || processing}
        />
      </View>
      
      <Button
        title="Back to Home"
        onPress={() => navigation.goBack()}
        color="#777"
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  camera: {
    flex: 1,
    maxHeight: '60%',
  },
  overlay: {
    flex: 1,
    justifyContent: 'flex-end',
    alignItems: 'center',
    marginBottom: 20,
  },
  overlayText: {
    color: 'white',
    fontSize: 18,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    padding: 10,
    borderRadius: 5,
  },
  textContainer: {
    padding: 15,
    backgroundColor: '#f0f0f0',
    maxHeight: '25%',
  },
  recognizedText: {
    fontSize: 16,
    color: '#333',
    lineHeight: 24,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 15,
    backgroundColor: '#fff',
  },
});

export default TextToSpeechScreen;