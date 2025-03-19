#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import ssl
import cv2
import numpy as np
import colorsys
from datetime import datetime
import torch
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import io
import easyocr
import tempfile
import shutil
from pydantic import BaseModel
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf

# Disable SSL certificate verification for downloading models
ssl._create_default_https_context = ssl._create_unverified_context

app = FastAPI(title="DrishtiYantra Backend API", description="Unified API for color detection, OCR, and TTS services")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("audio", exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory="uploads"), name="static")

# Initialize TTS models and tokenizers globally
device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

tts_model = None
tts_tokenizer = None
description_tokenizer = None

# =============== Helper Functions ===============

def load_tts_models():
    """Initialize TTS models if not already loaded"""
    global tts_model, tts_tokenizer, description_tokenizer
    if tts_model is None:
        print("Loading TTS models and tokenizers...")
        tts_model = ParlerTTSForConditionalGeneration.from_pretrained("ai4bharat/indic-parler-tts").to(device)
        tts_tokenizer = AutoTokenizer.from_pretrained("ai4bharat/indic-parler-tts")
        description_tokenizer = AutoTokenizer.from_pretrained(tts_model.config.text_encoder._name_or_path)

def cleanup_old_files(directory="audio", max_files=10):
    """Clean up old audio files, keeping only the most recent ones"""
    try:
        files = [(f, os.path.getmtime(os.path.join(directory, f))) 
                for f in os.listdir(directory) if f.endswith('.wav')]
        if len(files) > max_files:
            files.sort(key=lambda x: x[1])
            for f, _ in files[:-max_files]:
                try:
                    os.remove(os.path.join(directory, f))
                except OSError:
                    pass
    except Exception as e:
        print(f"Error during cleanup: {e}")

def average_image_color(image_path):
    """Get the average color of an image."""
    try:
        img = Image.open(image_path)
        img = img.resize((100, 100))
        pixels = img.getdata()
        total_r = 0
        total_g = 0
        total_b = 0
        count = 0

        for pixel in pixels:
            if isinstance(pixel, tuple) and len(pixel) >= 3:
                total_r += pixel[0]
                total_g += pixel[1]
                total_b += pixel[2]
                count += 1

        if count > 0:
            avg_r = int(total_r / count)
            avg_g = int(total_g / count)
            avg_b = int(total_b / count)
            return {"success": True, "color": (avg_r, avg_g, avg_b)}
        else:
            return {"success": False, "error": "Could not process image pixels"}

    except FileNotFoundError:
        return {"success": False, "error": f"Image file not found at {image_path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def rgb_to_hsi(rgb):
    """Convert RGB color to HSI."""
    r, g, b = rgb
    if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
        return {"success": False, "error": "Invalid RGB values. Values must be between 0 and 255."}

    r, g, b = r/255.0, g/255.0, b/255.0
    
    mx = max(r, g, b)
    mn = min(r, g, b)
    
    l = (mx + mn) / 2
    
    if mx == mn:
        h = 0
        s = 0
    else:
        d = mx - mn
        s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
        
        if mx == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif mx == g:
            h = (b - r) / d + 2
        else:
            h = (r - g) / d + 4
            
        h /= 6
    
    h = h * 360
    
    return {"success": True, "color": (h, s, l)}

def get_color_name(hue):
    """Get the color name from hue value."""
    colors = ["red", "orange", "yellow", "green", "cyan", "azure", "blue", "violet", "purple"]
    color_index = int(hue / 40) % 9
    return colors[color_index]

async def perform_ocr(image_data: bytes):
    """Perform OCR on the given image data"""
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
            
        # Initialize EasyOCR reader for Kannada
        reader = easyocr.Reader(['kn'])
        
        # Perform OCR
        results = reader.readtext(image)
        
        # Extract text
        text = ' '.join([result[1] for result in results])
        
        return text
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during OCR: {str(e)}")

# =============== API Models ===============

class TTSRequest(BaseModel):
    text: str
    voice_description: str = "Anu's voice is monotone yet slightly clear in delivery, with a very close recording that almost has no background noise."

# =============== API Routes ===============

@app.get("/")
async def read_root():
    return {
        "message": "DrishtiYantra Unified API",
        "version": "1.0.0",
        "services": ["color-detection", "ocr", "tts"]
    }

# Color Detection Endpoints
@app.post("/detect-color")
async def detect_color(file: UploadFile = File(...)):
    """Detect the average color of an uploaded image"""
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    
    try:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name
        temp_file.close()
        
        color_result = average_image_color(temp_file_path)
        
        if not color_result["success"]:
            raise HTTPException(status_code=500, detail=color_result.get("error", "Error processing image"))
        
        rgb = color_result["color"]
        
        hsi_result = rgb_to_hsi(rgb)
        
        if not hsi_result["success"]:
            raise HTTPException(status_code=500, detail=hsi_result.get("error", "Error converting to HSI"))
        
        hsi = hsi_result["color"]
        
        color_name = get_color_name(hsi[0])
        
        return {
            "rgb": {
                "r": rgb[0],
                "g": rgb[1],
                "b": rgb[2]
            },
            "hsi": {
                "h": hsi[0],
                "s": hsi[1],
                "i": hsi[2]
            },
            "color_name": color_name,
            "hex_code": f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
    
    finally:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

# OCR Endpoints
@app.post("/ocr/")
async def ocr_endpoint(file: UploadFile = File(...)):
    """Perform OCR on uploaded images"""
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")
        
        extracted_text = await perform_ocr(contents)
        
        return {
            "status": "success",
            "text": extracted_text
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# TTS Endpoints
@app.post("/tts/")
async def text_to_speech(request: TTSRequest):
    """Convert Kannada text to speech"""
    try:
        # Ensure models are loaded
        if tts_model is None:
            load_tts_models()
            
        print(f"Converting text to speech: {request.text}")
        
        # Generate unique filename using timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        output_path = f"audio/tts_output_{timestamp}.wav"
        
        # Prepare inputs
        description_input_ids = description_tokenizer(request.voice_description, return_tensors="pt").to(device)
        prompt_input_ids = tts_tokenizer(request.text, return_tensors="pt").to(device)
        
        # Generate audio
        print("Generating audio...")
        generation = tts_model.generate(
            input_ids=description_input_ids.input_ids,
            attention_mask=description_input_ids.attention_mask,
            prompt_input_ids=prompt_input_ids.input_ids,
            prompt_attention_mask=prompt_input_ids.attention_mask
        )
        
        # Convert to audio array and save
        audio_arr = generation.cpu().numpy().squeeze()
        sf.write(output_path, audio_arr, tts_model.config.sampling_rate)
        
        # Clean up old files
        cleanup_old_files()
        
        return FileResponse(
            output_path,
            media_type="audio/wav",
            filename=f"tts_output_{timestamp}.wav"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during TTS conversion: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8020)