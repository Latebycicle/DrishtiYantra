#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import ssl
from PIL import Image

# Disable SSL certificate verification for downloading models
ssl._create_default_https_context = ssl._create_unverified_context

def test_ocr_with_easyocr():
    """Test OCR using EasyOCR directly without AksharaJaana"""
    try:
        import easyocr
        import cv2
        import numpy as np
        
        print("Successfully imported EasyOCR, OpenCV and NumPy")
        print(f"NumPy version: {np.__version__}")
        print(f"OpenCV version: {cv2.__version__}")
        
        # Path to the Kannada text image
        image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "public", "KannadaText.png")
        
        print(f"Testing OCR with image: {image_path}")
        print(f"Image exists: {os.path.exists(image_path)}")
        
        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Failed to read image at path: {image_path}")
            return None
            
        print(f"Image shape: {image.shape}")
        
        # Initialize EasyOCR reader for Kannada
        print("Initializing EasyOCR reader for Kannada...")
        reader = easyocr.Reader(['kn'])  # 'kn' is the language code for Kannada
        
        # Perform OCR
        print("Performing OCR...")
        results = reader.readtext(image)
        
        # Extract text
        text = ' '.join([result[1] for result in results])
        
        print("\nExtracted Kannada text:")
        print("-" * 50)
        print(text)
        print("-" * 50)
        
        return text
        
    except ImportError as e:
        print(f"ImportError: {str(e)}")
        print("Please make sure EasyOCR and its dependencies are installed.")
        return None
    except Exception as e:
        print(f"Error during OCR: {str(e)}")
        return None

if __name__ == "__main__":
    print("=" * 50)
    print("Direct EasyOCR Test for Kannada")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print("-" * 50)
    
    # Test OCR
    extracted_text = test_ocr_with_easyocr()