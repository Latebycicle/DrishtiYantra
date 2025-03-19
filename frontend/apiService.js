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
    // Mock response for testing
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ color: 'Red' });
      }, 1000); // Simulate a delay like the API response
    });
  };
  
  export const changeLanguage = async (language) => {
    // Mock response for testing
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ success: true });
      }, 1000); // Simulate a delay like the API response
    });
  };
  