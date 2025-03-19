import React, { useState, useEffect, useRef } from 'react';
import { View, StyleSheet, Text, Button, Alert } from 'react-native';
import { CameraView, Camera } from 'expo-camera';
import * as Speech from 'expo-speech';
import { RootStackParamList } from '../navigation/types';
import { StackScreenProps } from '@react-navigation/stack';

type Props = StackScreenProps<RootStackParamList, 'TextToSpeech'>;

const TextToSpeechScreen = () => {
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [cameraReady, setCameraReady] = useState(false);
  const [recognizedText, setRecognizedText] = useState('');
  const cameraRef = useRef<CameraView>(null);

  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);

  const handleCameraReady = () => {
    setCameraReady(true);
  };

  const recognizeText = async () => {
    if (!cameraReady) {
      Alert.alert('Camera not ready');
      return;
    }

    const simulatedText = 'This is a sample recognized text.';
    setRecognizedText(simulatedText);
    speakText(simulatedText);
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
        facing="back"
        onCameraReady={handleCameraReady}
        ref={cameraRef}
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
        <Button title="Recognize Text" onPress={recognizeText} />
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
