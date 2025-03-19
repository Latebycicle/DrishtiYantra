import React, { useState } from 'react';
import { View, Text, Button, Image, Alert } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { recognizeText } from './apiService';

const TextRecognitionScreen = () => {
  const [image, setImage] = useState(null);
  const [recognizedText, setRecognizedText] = useState('');

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 1,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri); // Set selected image URI
    }
  };

  const handleTextRecognition = async () => {
    if (!image) {
      Alert.alert('Please select an image first.');
      return;
    }

    try {
      const result = await recognizeText(image); // Send image URI to the backend
      setRecognizedText(result.text); // Assuming 'text' is returned by the backend
    } catch (error) {
      Alert.alert('Error recognizing text.');
    }
  };

  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Button title="Pick an Image" onPress={pickImage} />
      {image && <Image source={{ uri: image }} style={{ width: 200, height: 200 }} />}
      <Button title="Recognize Text" onPress={handleTextRecognition} />
      {recognizedText ? <Text>Recognized Text: {recognizedText}</Text> : null}
    </View>
  );
};

export default TextRecognitionScreen;
