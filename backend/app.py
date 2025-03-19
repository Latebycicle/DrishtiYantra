import os
import ssl
import cv2
import numpy as np
import colorsys
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from PIL import Image
import io

# Disable SSL certificate verification for downloading models
ssl._create_default_https_context = ssl._create_unverified_context

app = FastAPI(title="DrishtiYantra API", description="API for image processing and accessibility features")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create directories if they don't exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("audio", exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory="uploads"), name="static")

@app.get("/")
async def read_root():
    return {"message": "Welcome to DrishtiYantra API", "version": "1.0.0"}

# Color detection feature
@app.post("/detect-color/")
async def detect_color(file: UploadFile = File(...)):
    """
    Detect the average color in an image and return the color name.
    """
    try:
        # Read and validate the image
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Convert to OpenCV format
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Save the uploaded image
        filename = f"uploads/{file.filename}"
        with open(filename, "wb") as f:
            f.write(contents)
        
        # Calculate the average color
        avg_color = average_image_color(img)
        
        # Convert RGB to HSI
        hsi_color = rgb_to_hsi(avg_color)
        
        # Get color name
        color_name = get_color_name(hsi_color[0])  # Using hue to determine color name
        
        return {
            "rgb_color": avg_color,
            "hsi_color": hsi_color,
            "color_name": color_name,
            "image_url": f"/static/{file.filename}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

def average_image_color(img):
    """
    Calculate the average color of an image.
    
    Args:
        img: OpenCV image array
        
    Returns:
        Tuple (R, G, B) with average color values
    """
    # Resize image for faster processing (optional)
    img_small = cv2.resize(img, (100, 100))
    
    # Convert BGR to RGB (OpenCV uses BGR by default)
    img_rgb = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)
    
    # Calculate average
    avg_color_per_row = np.average(img_rgb, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)
    
    # Convert to integers
    avg_color = tuple(int(val) for val in avg_color)
    
    return avg_color

def rgb_to_hsi(rgb):
    """
    Convert RGB color to HSI (Hue, Saturation, Intensity).
    
    Args:
        rgb: Tuple (R, G, B) with values from 0 to 255
        
    Returns:
        Tuple (H, S, I) where H is in degrees (0-360), S and I are in range [0, 1]
    """
    r, g, b = rgb
    
    # Normalize RGB values to range [0, 1]
    r, g, b = r/255.0, g/255.0, b/255.0
    
    # Convert to HSI using colorsys (which returns HLS)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    
    # Convert hue to degrees
    h = h * 360
    
    # Intensity is the same as lightness in HLS
    i = l
    
    return (h, s, i)

def get_color_name(hue):
    """
    Get the color name based on the hue value.
    
    Args:
        hue: Hue value in degrees (0-360)
        
    Returns:
        String with the color name
    """
    colors = ["red", "orange", "yellow", "green", "cyan", "azure", "blue", "violet", "purple"]
    
    # Map hue to color name
    color_index = int(hue / 40) % 9
    return colors[color_index]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)