import os
from PIL import Image
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import Optional
import tempfile
import shutil

app = FastAPI(title="Color Detection API", description="API for detecting colors in images")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def average_image_color(image_path):
    """Get the average color of an image."""
    try:
        img = Image.open(image_path)
        # Resize the image to a smaller size for faster processing
        img = img.resize((100, 100))
        pixels = img.getdata()
        total_r = 0
        total_g = 0
        total_b = 0
        count = 0

        for pixel in pixels:
            if isinstance(pixel, tuple) and len(pixel) >= 3:  # Handle different image modes
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
    
    # Simple implementation of RGB to HLS conversion
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
    
    # Convert to degrees for hue
    h = h * 360
    
    return {"success": True, "color": (h, s, l)}

def get_color_name(hue):
    """Get the color name from hue value."""
    colors = ["red", "orange", "yellow", "green", "cyan", "azure", "blue", "violet", "purple"]
    color_index = int(hue / 40) % 9
    return colors[color_index]

@app.get("/")
async def root():
    return {"message": "Welcome to the Color Detection API", "status": "active"}

@app.post("/detect-color")
async def detect_color(file: UploadFile = File(...)):
    """
    Detect the average color of an uploaded image
    
    Returns:
        JSON with RGB values, HSI values, and color name
    """
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    
    try:
        # Write uploaded file to temporary file
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name
        temp_file.close()
        
        # Process the image
        color_result = average_image_color(temp_file_path)
        
        if not color_result["success"]:
            raise HTTPException(status_code=500, detail=color_result.get("error", "Error processing image"))
        
        rgb = color_result["color"]
        
        # Convert to HSI
        hsi_result = rgb_to_hsi(rgb)
        
        if not hsi_result["success"]:
            raise HTTPException(status_code=500, detail=hsi_result.get("error", "Error converting to HSI"))
        
        hsi = hsi_result["color"]
        
        # Get color name
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
        # Clean up the temp file
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

@app.get("/detect-color-from-path")
async def detect_color_from_path(image_path: str):
    """
    Detect the average color of an image from a file path
    
    Args:
        image_path: Path to the image file
        
    Returns:
        JSON with RGB values, HSI values, and color name
    """
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail=f"Image not found at {image_path}")
    
    # Process the image
    color_result = average_image_color(image_path)
    
    if not color_result["success"]:
        raise HTTPException(status_code=500, detail=color_result.get("error", "Error processing image"))
    
    rgb = color_result["color"]
    
    # Convert to HSI
    hsi_result = rgb_to_hsi(rgb)
    
    if not hsi_result["success"]:
        raise HTTPException(status_code=500, detail=hsi_result.get("error", "Error converting to HSI"))
    
    hsi = hsi_result["color"]
    
    # Get color name
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

# Run the API with uvicorn when this file is executed directly
if __name__ == "__main__":
    uvicorn.run("color_detection_api:app", host="0.0.0.0", port=8000, reload=True)