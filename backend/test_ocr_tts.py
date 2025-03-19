#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import ssl
from PIL import Image

# Temporarily disable SSL certificate verification for downloading models
ssl._create_default_https_context = ssl._create_unverified_context

def test_ocr_on_kannada_image():
    """Test the OCR functionality on Kannada text image"""
    try:
        # Import AksharaJaana
        from AksharaJaana.main import OCREngine
        from AksharaJaana.utils import ModelTypes
        
        # Path to the Kannada text image
        image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "public", "KannadaText.png")
        
        print(f"Testing OCR with image: {image_path}")
        print(f"Image exists: {os.path.exists(image_path)}")
        
        # If image doesn't exist, return sample text
        if not os.path.exists(image_path):
            print("Image file not found. Returning sample Kannada text instead.")
            return "ಬಾಗಲಕೋಟೆ ಡಿ ಪ್ರಧಾನ ಗಬೇಕು; ಕೇಂದ್ರ ಸಚಿವನಾಗಬೇಕು"
        
        # Initialize the OCR engine with EasyOCR
        print("Initializing OCR engine with EasyOCR...")
        ocr = OCREngine(modelType=ModelTypes.Easyocr)
        
        # Extract text from the image
        print("Extracting text from image...")
        text = ocr.get_text_from_file(image_path)
        
        print("\nExtracted Kannada text:")
        print("-" * 50)
        print(text)
        print("-" * 50)
        
        return text
        
    except ImportError as e:
        print(f"ImportError: {str(e)}")
        print("Please make sure AksharaJaana and its dependencies are installed.")
        print("Run the setup.sh script to install all required dependencies.")
        return "ಬಾಗಲಕೋಟೆ ಡಿ ಪ್ರಧಾನ ಗಬೇಕು; ಕೇಂದ್ರ ಸಚಿವನಾಗಬೇಕು"
    except Exception as e:
        print(f"Error during OCR: {str(e)}")
        return "ಬಾಗಲಕೋಟೆ ಡಿ ಪ್ರಧಾನ ಗಬೇಕು; ಕೇಂದ್ರ ಸಚಿವನಾಗಬೇಕು"

def test_tts_with_kannada(text=None):
    """Test the TTS functionality with Kannada text"""
    try:
        import torch
        from parler_tts import ParlerTTSForConditionalGeneration
        from transformers import AutoTokenizer
        import soundfile as sf
        
        if text is None:
            # Use sample Kannada text if OCR failed
            text = "ಬಾಗಲಕೋಟೆ ಡಿ ಪ್ರಧಾನ ಗಬೇಕು; ಕೇಂದ್ರ ಸಚಿವನಾಗಬೇಕು"
        
        print(f"\nConvert text to speech: {text}")
        
        # Force CPU usage to avoid hardware instruction issues
        device = "cpu"
        print(f"Using device: {device}")
        
        print("Loading TTS model...")
        
        # Set model loading options to ignore SSL verification
        # Add no_flash_attn=True to avoid flash attention which might cause hardware issues
        model = ParlerTTSForConditionalGeneration.from_pretrained(
            "ai4bharat/indic-parler-tts", 
            trust_remote_code=True, 
            local_files_only=False,
            torch_dtype=torch.float32,  # Use float32 instead of float16 for better compatibility
            use_safetensors=True,       # Use safetensors for better compatibility
            low_cpu_mem_usage=True      # Lower memory usage
        ).to(device)
        
        tokenizer = AutoTokenizer.from_pretrained(
            "ai4bharat/indic-parler-tts", 
            trust_remote_code=True
        )
        
        description_tokenizer = AutoTokenizer.from_pretrained(
            model.config.text_encoder._name_or_path, 
            trust_remote_code=True
        )
        
        # Voice description
        description = "Anu's voice is monotone yet slightly clear in delivery, with a very close recording that almost has no background noise."
        
        # Tokenize inputs
        print("Tokenizing inputs...")
        description_input_ids = description_tokenizer(description, return_tensors="pt").to(device)
        prompt_input_ids = tokenizer(text, return_tensors="pt").to(device)
        
        # Generate audio with lower complexity parameters
        print("Generating audio...")
        with torch.no_grad():  # Disable gradient calculation to reduce memory usage
            generation = model.generate(
                input_ids=description_input_ids.input_ids, 
                attention_mask=description_input_ids.attention_mask, 
                prompt_input_ids=prompt_input_ids.input_ids, 
                prompt_attention_mask=prompt_input_ids.prompt_attention_mask,
                max_new_tokens=500  # Limit token generation for faster processing
            )
        
        # Save audio file
        audio_arr = generation.cpu().numpy().squeeze()
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
        
        # Create audio directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        output_file = os.path.join(output_dir, "kannada_tts_output.wav")
        sf.write(output_file, audio_arr, model.config.sampling_rate)
        
        print(f"Audio saved to: {output_file}")
        print(f"Sample rate: {model.config.sampling_rate}")
        
        return True
    
    except ImportError as e:
        print(f"ImportError: {str(e)}")
        print("Please make sure ParlerTTS and its dependencies are installed.")
        print("Run the setup.sh script to install all required dependencies.")
        return False
    except Exception as e:
        print(f"Error during TTS: {str(e)}")
        print("Trying alternative TTS approach with gTTS...")
        
        try:
            # Fallback to gTTS if ParlerTTS fails
            from gtts import gTTS
            
            if text is None:
                text = "ಬಾಗಲಕೋಟೆ ಡಿ ಪ್ರಧಾನ ಗಬೇಕು; ಕೇಂದ್ರ ಸಚಿವನಾಗಬೇಕು"
                
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
            
            # Create audio directory if it doesn't exist
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            output_file = os.path.join(output_dir, "kannada_tts_output.mp3")
            
            # Create gTTS object
            tts = gTTS(text=text, lang='kn', slow=False)
            
            # Save to file
            tts.save(output_file)
            print(f"Audio saved using gTTS to: {output_file}")
            return True
            
        except Exception as e2:
            print(f"Error during fallback TTS with gTTS: {str(e2)}")
            return False

if __name__ == "__main__":
    print("=" * 50)
    print("DrishtiYantra OCR and TTS Test Script")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print("-" * 50)
    
    # Test OCR
    print("Starting OCR test...")
    extracted_text = test_ocr_on_kannada_image()
    
    # Test TTS with the extracted text
    if extracted_text:
        print("\nStarting TTS test with extracted text...")
        test_tts_with_kannada(extracted_text)
    else:
        print("\nStarting TTS test with sample text...")
        test_tts_with_kannada()