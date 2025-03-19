import React, { useState, useEffect, useRef } from 'react';
import { View, StyleSheet, Text, Button, Alert } from 'react-native';
import { Camera, CameraView } from 'expo-camera';  // Use CameraView here
import * as Speech from 'expo-speech';
import { RootStackParamList } from '../navigation/types';
import { StackScreenProps } from '@react-navigation/stack';
import { recognizeText } from '../apiService'; // Ensure you have this API service file

type Props = StackScreenProps<RootStackParamList, 'TextToSpeech'>;

const TextToSpeechScreen = () => {
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [cameraReady, setCameraReady] = useState(false);
  const [recognizedText, setRecognizedText] = useState('');
  const cameraRef = useRef<CameraView>(null);  // Using CameraView ref

  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);

  const handleCameraReady = () => {
    setCameraReady(true);
  };

  const capturePhoto = async () => {
    if (!cameraReady || !cameraRef.current) {
      Alert.alert('Camera not ready');
      return;
    }
  
    try {
      const photo = await cameraRef.current.takePictureAsync();
  
      // Check if photo is defined before proceeding
      if (photo && photo.uri) {
        await recognizeTextFromImage(photo.uri); // Call function to recognize text from image
      } else {
        Alert.alert('Failed to capture photo');
      }
    } catch (error) {
      Alert.alert('Error capturing photo');
    }
  };

  const recognizeTextFromImage = async (imageUri: string) => {
    try {
      const result = await recognizeText(imageUri); // Send image URI to the backend
      setRecognizedText(result.text); // Assuming 'text' is returned by the backend
      speakText(result.text);
    } catch (error) {
      Alert.alert('Error recognizing text.');
    }
  };

  const speakText = (text: string) => {
    Speech.speak(text, {
      language: 'en',
      rate: 1.0,
      pitch: 1.0,
    });
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
        facing="back"  // Same as in Color Detection, ensuring camera is set up properly
        onCameraReady={handleCameraReady}
        ref={cameraRef}  // Properly using ref here
      >
        <View style={styles.overlay}>
          <Text style={styles.overlayText}>Point the camera at text</Text>
        </View>
      </CameraView>

      <View style={styles.textContainer}>
        <Text style={styles.recognizedText}>
          {recognizedText || 'No text recognized yet.'}
        </Text>
      </View>

      <View style={styles.buttonContainer}>
        <Button title="Capture & Recognize Text" onPress={capturePhoto} />
        <Button
          title="Speak Text"
          onPress={() => speakText(recognizedText)}
          disabled={!recognizedText}
        />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  camera: {
    flex: 1,
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
    padding: 20,
    backgroundColor: '#f0f0f0',
  },
  recognizedText: {
    fontSize: 16,
    color: '#333',
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 20,
  },
});

export default TextToSpeechScreen;
