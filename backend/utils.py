import os
from PIL import Image

# Global model variables
ocr_model = None
tts_model = None
tts_tokenizer = None
description_tokenizer = None

# Try importing colorsys (standard library module)
try:
    import colorsys
except ImportError:
    # Define simple HSL to RGB conversion if colorsys is not available
    def rgb_to_hls(r, g, b):
        # Simple implementation
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
            
        return h, l, s

# Optional AksharaJaana import
try:
    from AksharaJaana.main import OCREngine
    from AksharaJaana.utils import ModelTypes
    
    def initialize_ocr_model():
        """Initialize the OCR model."""
        global ocr_model
        if ocr_model is None:
            ocr_model = OCREngine(modelType=ModelTypes.Easyocr)
        return ocr_model

    def image_to_text(image_path):
        """Extract text from an image using OCR."""
        model = initialize_ocr_model()
        try:
            text = model.get_text_from_file(image_path)
            return {"text": text, "success": True}
        except Exception as e:
            return {"text": "", "success": False, "error": str(e)}
except ImportError:
    def initialize_ocr_model():
        return None
        
    def image_to_text(image_path):
        return {"text": "", "success": False, "error": "AksharaJaana library not installed"}

# Optional torch and parler-tts import
try:
    import torch
    import soundfile as sf
    from parler_tts import ParlerTTSForConditionalGeneration
    from transformers import AutoTokenizer
    
    def initialize_tts_model():
        """Initialize the TTS model."""
        global tts_model, tts_tokenizer, description_tokenizer
        
        if tts_model is None:
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
            
            tts_model = ParlerTTSForConditionalGeneration.from_pretrained("ai4bharat/indic-parler-tts").to(device)
            tts_tokenizer = AutoTokenizer.from_pretrained("ai4bharat/indic-parler-tts")
            description_tokenizer = AutoTokenizer.from_pretrained(tts_model.config.text_encoder._name_or_path)
        
        return tts_model, tts_tokenizer, description_tokenizer

    def text_to_speech(text, description="Anu's voice is monotone yet slightly clear in delivery, with a very close recording that almost has no background noise.", output_file="output_audio.wav"):
        """Convert text to speech using Parler TTS."""
        try:
            model, tokenizer, desc_tokenizer = initialize_tts_model()
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
            
            description_input_ids = desc_tokenizer(description, return_tensors="pt").to(device)
            prompt_input_ids = tokenizer(text, return_tensors="pt").to(device)
            
            generation = model.generate(
                input_ids=description_input_ids.input_ids, 
                attention_mask=description_input_ids.attention_mask, 
                prompt_input_ids=prompt_input_ids.input_ids, 
                prompt_attention_mask=prompt_input_ids.attention_mask
            )
            
            audio_arr = generation.cpu().numpy().squeeze()
            sf.write(output_file, audio_arr, model.config.sampling_rate)
            
            return {
                "success": True, 
                "output_file": output_file,
                "sample_rate": model.config.sampling_rate
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
except ImportError:
    def initialize_tts_model():
        return None, None, None
        
    def text_to_speech(text, description=None, output_file=None):
        return {"success": False, "error": "TTS libraries (torch, parler-tts) not installed"}

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
    
    try:
        # Use colorsys if available
        if 'colorsys' in globals():
            h, l, s = colorsys.rgb_to_hls(r, g, b)
        else:
            h, l, s = rgb_to_hls(r, g, b)
        
        # Convert to degrees
        h = h * 360
        
        return {"success": True, "color": (h, s, l)}
    except Exception as e:
        return {"success": False, "error": f"Error converting RGB to HSI: {str(e)}"}

def get_color_name(hue):
    """Get the color name from hue value."""
    colors = ["red", "orange", "yellow", "green", "cyan", "azure", "blue", "violet", "purple"]
    color_index = int(hue / 40) % 9
    return colors[color_index]

def detect_color_and_speak(image_path, output_file="color_audio.wav"):
    """Detect the dominant color in an image and convert it to speech."""
    color_result = average_image_color(image_path)
    
    if not color_result["success"]:
        return color_result
    
    rgb = color_result["color"]
    hsi_result = rgb_to_hsi(rgb)
    
    if not hsi_result["success"]:
        return hsi_result
    
    hue = hsi_result["color"][0]
    color_name = get_color_name(hue)
    
    # Convert color name to speech
    speech_result = text_to_speech(color_name, output_file=output_file)
    
    if speech_result["success"]:
        return {
            "success": True,
            "color": {
                "rgb": rgb,
                "hsi": hsi_result["color"],
                "name": color_name
            },
            "audio_file": output_file,
            "sample_rate": speech_result["sample_rate"]
        }
    else:
        return speech_result