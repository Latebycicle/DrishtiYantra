from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import ssl
from PIL import Image
import easyocr
import cv2
import numpy as np
import io

# Disable SSL certificate verification for downloading models
ssl._create_default_https_context = ssl._create_unverified_context

app = FastAPI(title="OCR API", description="API for Optical Character Recognition")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def perform_ocr(image_data: bytes):
    """Perform OCR on the given image data"""
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
            
        # Initialize EasyOCR reader for Kannada
        reader = easyocr.Reader(['kn'])  # 'kn' is the language code for Kannada
        
        # Perform OCR
        results = reader.readtext(image)
        
        # Extract text
        text = ' '.join([result[1] for result in results])
        
        return text
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during OCR: {str(e)}")

@app.post("/ocr/")
async def ocr_endpoint(file: UploadFile = File(...)):
    """
    Endpoint to perform OCR on uploaded images
    """
    try:
        # Read the uploaded file
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Perform OCR
        extracted_text = await perform_ocr(contents)
        
        return {
            "status": "success",
            "text": extracted_text
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return {"message": "OCR API is running", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)