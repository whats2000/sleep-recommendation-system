"""
Encodes audio files into embedding vectors using the CLAP model.
"""

import os
import warnings

import librosa
import torch
from dotenv import load_dotenv
from torch import device
from transformers import ClapProcessor, ClapModel

warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

# Model parameters
MODEL_NAME = os.getenv("MODEL_NAME", "laion/clap-htsat-unfused")

# Check if GPU is available
device = "cuda" if torch.cuda.is_available() else "cpu"
model = ClapModel.from_pretrained(MODEL_NAME).to(device)
processor = ClapProcessor.from_pretrained(MODEL_NAME)
model.eval()

def load_audio_file(file_path: str, target_sr=48000):
    """Load an audio file using librosa."""
    try:
        # Load audio file with librosa
        audio, sr = librosa.load(file_path, sr=target_sr, mono=True)
        duration = librosa.get_duration(y=audio, sr=sr)
        return audio, sr, duration
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}")
        return None, None, None

def encode_audio(file_path: str):
    """Encode audio file and return embedding vector."""
    
    # Load audio file
    audio, sr, duration = load_audio_file(file_path)
    
    if audio is None:
        print("Failed to load audio file")
        return None
    
    # Encode audio
    with torch.no_grad():
        inputs = processor(audios=[audio], return_tensors="pt").to(device)
        embedding = model.get_audio_features(**inputs)
        embedding = embedding.cpu().numpy()[0]
    
    # Return embedding
    return embedding
