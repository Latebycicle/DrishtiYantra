export const recognizeText = async (imageUri) => {
    // Mock response for testing
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ text: 'Mock recognized text from the image!' });
      }, 1000); // Simulate a delay like the API response
    });
  };
  
  export const speakText = async (text) => {
    // Mock response for testing
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ success: true });
      }, 1000); // Simulate a delay like the API response
    });
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
      const response = await fetch('http://192.168.0.103:8000/detect-color', {
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
  