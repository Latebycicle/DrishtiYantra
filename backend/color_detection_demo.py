import os
from PIL import Image

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

def main():
    # Path to the Kannada text image
    image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                            "public", "KannadaText.png")
    
    print(f"Analyzing image: {image_path}")
    print(f"Image exists: {os.path.exists(image_path)}")
    
    # Get average color
    color_result = average_image_color(image_path)
    
    if color_result["success"]:
        rgb = color_result["color"]
        print(f"\nAverage RGB color: {rgb}")
        
        # Convert to HSI
        hsi_result = rgb_to_hsi(rgb)
        
        if hsi_result["success"]:
            hsi = hsi_result["color"]
            print(f"HSI values: {hsi}")
            
            # Get color name
            color_name = get_color_name(hsi[0])
            print(f"Detected color: {color_name}")
        else:
            print(f"Error converting to HSI: {hsi_result.get('error')}")
    else:
        print(f"Error getting average color: {color_result.get('error')}")

if __name__ == "__main__":
    main()