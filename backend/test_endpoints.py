import requests
import os

BASE_URL = 'http://127.0.0.1:8090'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_ocr():
    url = f'{BASE_URL}/ocr'
    file_path = os.path.join(BASE_DIR, 'public', 'KannadaText.png')
    
    with open(file_path, 'rb') as f:
        files = {'file': ('KannadaText.png', f, 'image/png')}
        response = requests.post(url, files=files)
    
    print('OCR Test:', 'Passed' if response.status_code == 200 else 'Failed')
    print('Response:', response.json() if response.status_code == 200 else response.text)

def test_color_detection():
    url = f'{BASE_URL}/color-detection'
    file_path = os.path.join(BASE_DIR, 'public', 'colortest.jpeg')
    
    with open(file_path, 'rb') as f:
        files = {'file': ('colortest.jpeg', f, 'image/jpeg')}
        response = requests.post(url, files=files)
    
    print('Color Detection Test:', 'Passed' if response.status_code == 200 else 'Failed')
    print('Response:', response.json() if response.status_code == 200 else response.text)

def test_tts():
    url = f'{BASE_URL}/tts'
    file_path = os.path.join(BASE_DIR, 'public', 'testtext.txt')
    
    with open(file_path, 'rb') as f:
        files = {'file': ('testtext.txt', f, 'text/plain')}
        response = requests.post(url, files=files)
    
    print('TTS Test:', 'Passed' if response.status_code == 200 else 'Failed')
    print('Response:', response.json() if response.status_code == 200 else response.text)

if __name__ == '__main__':
    print('Testing OCR Endpoint...')
    test_ocr()
    print('\nTesting Color Detection Endpoint...')
    test_color_detection()
    print('\nTesting TTS Endpoint...')
    test_tts()