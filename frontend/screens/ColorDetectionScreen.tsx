import React, { useState, useEffect, useRef } from 'react';
import { View, StyleSheet, Text, Button, Alert } from 'react-native';
import { CameraView, Camera } from 'expo-camera';
import * as Speech from 'expo-speech';
import NavigationButton from '../components/NavigationButton';
import { StackScreenProps } from '@react-navigation/stack';
import { RootStackParamList } from '../navigation/types';
import { detectColor } from '../apiService';

type Props = StackScreenProps<RootStackParamList, 'ColorDetection'>;

export default function ColorDetectionScreen({ navigation }: Props) {
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [cameraReady, setCameraReady] = useState(false);
  const [detectedColor, setDetectedColor] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);
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

  const captureAndDetectColor = async () => {
    if (!cameraReady || !cameraRef.current || processing) {
      Alert.alert('Camera not ready');
      return;
    }

    setProcessing(true);
    try {
      // Take a picture
      Speech.speak("Capturing image");
      const photo = await cameraRef.current.takePictureAsync();

      // Call API to detect color
      Speech.speak("Detecting color");
      const result = await detectColor(photo.uri);

      if (result.success) {
        setDetectedColor(result.color);
        // Speak the color name
        Speech.speak(`The detected color is ${result.color}`);
      } else {
        Alert.alert('Error', 'Failed to detect color');
        Speech.speak("Failed to detect color");
      }
    } catch (error) {
      Alert.alert('Error', 'Error capturing or processing image');
      Speech.speak("Error processing image");
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
          <Text style={styles.overlayText}>Point the camera at an object</Text>
          {detectedColor && (
            <Text style={styles.colorText}>
              Detected color: {detectedColor}
            </Text>
          )}
        </View>
      </CameraView>
  
      {/* Make sure the button is outside the CameraView */}
      <View style={styles.controlsContainer}>
        <Button
          title={processing ? "Processing..." : "Detect Color"}
          onPress={captureAndDetectColor}
          disabled={processing || !cameraReady}
          color="#2196F3"
        />
        
        <NavigationButton
          label="Back to Home"
          onPress={() => navigation.goBack()}
        />
      </View>
    </View>
  );
  
}

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
  colorText: {
    color: 'white',
    fontSize: 22,
    fontWeight: 'bold',
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    padding: 12,
    borderRadius: 5,
    marginTop: 15,
  },
  buttonContainer: {
    position: 'absolute',
    bottom: 70,
    left: 0,
    right: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    padding: 15,
    alignItems: 'center',
    zIndex: 10
  },

  controlsContainer: {
    position: 'absolute',
    bottom: 70,
    left: 0,
    right: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    padding: 15,
    alignItems: 'center',
    zIndex: 10
  }
});
