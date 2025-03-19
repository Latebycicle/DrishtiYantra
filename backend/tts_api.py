#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf
import os
from pydantic import BaseModel
from fastapi.responses import FileResponse
import ssl
from datetime import datetime

# Disable SSL certificate verification for downloading models
ssl._create_default_https_context = ssl._create_unverified_context

app = FastAPI(title="TTS API", description="API for Text-to-Speech conversion in Kannada")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create audio directory if it doesn't exist
os.makedirs("audio", exist_ok=True)

# Initialize models and tokenizers
device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load models and tokenizers globally
model = None
tokenizer = None
description_tokenizer = None

def load_models():
    global model, tokenizer, description_tokenizer
    if model is None:
        print("Loading models and tokenizers...")
        model = ParlerTTSForConditionalGeneration.from_pretrained("ai4bharat/indic-parler-tts").to(device)
        tokenizer = AutoTokenizer.from_pretrained("ai4bharat/indic-parler-tts")
        description_tokenizer = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)

def cleanup_old_files(directory="audio", max_files=10):
    """Clean up old audio files, keeping only the most recent ones"""
    try:
        files = [(f, os.path.getmtime(os.path.join(directory, f))) 
                for f in os.listdir(directory) if f.endswith('.wav')]
        if len(files) > max_files:
            files.sort(key=lambda x: x[1])  # Sort by modification time
            for f, _ in files[:-max_files]:  # Remove all but the most recent files
                try:
                    os.remove(os.path.join(directory, f))
                except OSError:
                    pass
    except Exception as e:
        print(f"Error during cleanup: {e}")

class TTSRequest(BaseModel):
    text: str
    voice_description: str = "Anu's voice is monotone yet slightly clear in delivery, with a very close recording that almost has no background noise."

@app.get("/")
async def read_root():
    return {"message": "TTS API is running", "version": "1.0.0"}

@app.post("/tts/")
async def text_to_speech(request: TTSRequest):
    """
    Convert Kannada text to speech
    """
    try:
        # Ensure models are loaded
        if model is None:
            load_models()
            
        print(f"Converting text to speech: {request.text}")
        
        # Generate unique filename using timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        output_path = f"audio/tts_output_{timestamp}.wav"
        
        # Prepare inputs
        description_input_ids = description_tokenizer(request.voice_description, return_tensors="pt").to(device)
        prompt_input_ids = tokenizer(request.text, return_tensors="pt").to(device)
        
        # Generate audio
        print("Generating audio...")
        generation = model.generate(
            input_ids=description_input_ids.input_ids,
            attention_mask=description_input_ids.attention_mask,
            prompt_input_ids=prompt_input_ids.input_ids,
            prompt_attention_mask=prompt_input_ids.attention_mask
        )
        
        # Convert to audio array and save
        audio_arr = generation.cpu().numpy().squeeze()
        sf.write(output_path, audio_arr, model.config.sampling_rate)
        
        # Clean up old files
        cleanup_old_files()
        

        #RETURNS THE AUDIO FILE HERE TO THE OUTPUT PATH WITH THE FILENAME SET
        return FileResponse(
            output_path,
            media_type="audio/wav",
            filename=f"tts_output_{timestamp}.wav"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during TTS conversion: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)