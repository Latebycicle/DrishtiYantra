import * as FileSystem from 'expo-file-system';
import * as Speech from 'expo-speech';

export const recognizeText = async (imageUri) => {
  try {
    // Create form data for the image upload
    const formData = new FormData();
    
    // Get just the filename from the URI
    const uriParts = imageUri.split('/');
    const fileName = uriParts[uriParts.length - 1];
    
    // Append the file
    formData.append('file', {
      uri: imageUri,
      name: fileName,
      type: 'image/jpeg', 
    });
    
console.log(`Sending image for OCR: ${fileName}`);
    // Make the API call
    // Make the API call
const response = await fetch('http://192.168.0.103:8020/ocr/', {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'multipart/form-data',
      },
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`OCR API error (${response.status}):`, errorText);
      throw new Error(`Server error: ${response.status} - ${errorText}`);
    }
    
    const data = await response.json();
    console.log('OCR response:', data);
    
    return {
      success: true,
      text: data.text
    };
  } catch (error) {
    console.error('Error recognizing text:', error);
    return { 
      success: false, 
      error: error.message 
    };
  }
};

  
export const speakText = async (text, voiceDescription = "Anu's voice is monotone yet slightly clear in delivery, with a very close recording that almost has no background noise.") => {
  try {
    console.log("Calling TTS API for text:", text);
    
    // Try using the API first
    const response = await fetch('http://192.168.0.103:8020/tts/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        voice_description: voiceDescription
      }),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error("TTS API error:", errorText);
      throw new Error(`Server error: ${response.status} - ${errorText}`);
    }
    
    // For React Native, we need to get a blob response and create a local URI
    const blob = await response.blob();
    const fileUri = FileSystem.cacheDirectory + "speech.wav";
    
    // Write the blob to a file
    const fileReader = new FileReader();
    fileReader.readAsDataURL(blob);
    
    return new Promise((resolve, reject) => {
      fileReader.onload = async () => {
        if (typeof fileReader.result === 'string') {
          try {
            const base64Data = fileReader.result.split(',')[1];
            await FileSystem.writeAsStringAsync(fileUri, base64Data, {
              encoding: FileSystem.EncodingType.Base64,
            });
            resolve({
              success: true,
              audioUri: fileUri
            });
          } catch (error) {
            console.error("Error saving audio file:", error);
            reject(error);
          }
        } else {
          reject(new Error("FileReader result is not a string"));
        }
      };
      
      fileReader.onerror = () => {
        reject(new Error("Error reading audio blob"));
      };
    });
  } catch (error) {
    console.error('Error in text-to-speech conversion:', error);
    // We don't call Speech.speak here anymore, we'll handle that in the component
    return { 
      success: false, 
      error: error.message 
    };
  }
};
  
  export const detectColor = async (imageUri) => {
    try {
      // Create form data for the image upload
      const formData = new FormData();
      
      // Get just the filename from the URI
      const uriParts = imageUri.split('/');
      const fileName = uriParts[uriParts.length - 1];
      
      // Append the file
      formData.append('file', {
        uri: imageUri,
        name: fileName,
        type: 'image/jpeg', // Adjust if needed based on your image type
      });
      
      // Make the API call - update the URL to point to your deployed backend
      // For development on same machine use your machine's IP instead of localhost
      const response = await fetch('http://192.168.0.103:8020/detect-color', {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'multipart/form-data',
        },
      });
      
      if (!response.ok) {
        throw new Error('Server error');
      }
      
      const data = await response.json();
      return {
        success: true,
        color: data.color_name,
        rgb: data.rgb,
        hsi: data.hsi,
        hex: data.hex_code
      };
    } catch (error) {
      console.error('Error detecting color:', error);
      return { 
        success: false, 
        error: error.message 
      };
    }
  };
  
  
  export const changeLanguage = async (language) => {
    // Mock response for testing
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ success: true });
      }, 1000); // Simulate a delay like the API response
    });
  };
  