import os
from utils import image_to_text

def test_ocr():
    # Path to the Kannada text image
    image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                             "public", "KannadaText.png")
    
    print(f"Testing OCR with image: {image_path}")
    print(f"Image exists: {os.path.exists(image_path)}")
    
    # Extract text from the image
    result = image_to_text(image_path)
    
    if result["success"]:
        print("\nExtracted text:")
        print("-" * 50)
        print(result["text"])
        print("-" * 50)
    else:
        print(f"\nError during OCR: {result.get('error', 'Unknown error')}")
        
        # Check if AksharaJaana is available
        try:
            from AksharaJaana.main import OCREngine
            print("AksharaJaana is installed but OCR failed.")
        except ImportError:
            print("AksharaJaana is not installed. Consider installing it with:")
            print("pip install AksharaJaana")

if __name__ == "__main__":
    test_ocr()