#!/bin/bash

echo "Setting up DrishtiYantra with Python 3.11.1"

# Change to the project directory
cd /Users/akhilr/Documents/Coding/DrishtiYantra

# Check if Python 3.11.1 is installed
if ! command -v python3.11 &> /dev/null; then
    echo "Python 3.11.1 is not installed. Installing via pyenv..."
    
    # Check if pyenv is installed
    if ! command -v pyenv &> /dev/null; then
        echo "Installing pyenv..."
        brew install pyenv
    fi
    
    # Install Python 3.11.1 using pyenv
    pyenv install 3.11.1
    pyenv local 3.11.1
else
    echo "Python 3.11.1 is already installed."
fi

# Remove old virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Removing old virtual environment..."
    rm -rf .venv
fi

# Create a new virtual environment with Python 3.11.1
echo "Creating new virtual environment with Python 3.11.1..."
python3.11 -m venv .venv

# Activate the virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install base requirements
echo "Installing base requirements..."
pip install fastapi uvicorn python-multipart pillow numpy

# Install OCR-related packages
echo "Installing OCR-related packages..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install opencv-python easyocr AksharaJaana

# Install TTS-related packages
echo "Installing TTS-related packages..."
pip install git+https://github.com/huggingface/parler-tts.git
pip install transformers sentencepiece soundfile

echo "Setup complete! Activate the environment with:"
echo "source .venv/bin/activate"