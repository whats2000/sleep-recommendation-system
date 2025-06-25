"""
Encode music utils
"""

import os
import warnings

import librosa
import numpy as np
import torch
from dotenv import load_dotenv
from transformers import ClapProcessor, ClapModel

warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

# Model parameters
MODEL_NAME = os.getenv("MODEL_NAME", "laion/clap-htsat-unfused")

def load_audio_file(file_path, target_sr=48000):
    """Load an audio file using librosa."""
    try:
        # Load audio file with librosa
        audio, sr = librosa.load(file_path, sr=target_sr, mono=True)
        duration = librosa.get_duration(y=audio, sr=sr)
        return audio, sr, duration
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}")
        return None, None, None

def encode_audio(file_path, model_name=MODEL_NAME):
    """Encode audio file and return embedding vector."""
    # Check if GPU is available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # Load model and processor
    print(f"Loading CLAP model: {model_name}")
    model = ClapModel.from_pretrained(model_name).to(device)
    processor = ClapProcessor.from_pretrained(model_name)
    model.eval()

    # Load audio file
    print(f"Loading audio file: {file_path}")
    audio, sr, duration = load_audio_file(file_path)

    if audio is None:
        print("Failed to load audio file")
        return None

    # Encode audio
    print("Encoding audio with CLAP model")
    with torch.no_grad():
        inputs = processor(audios=[audio], return_tensors="pt").to(device)
        embedding = model.get_audio_features(**inputs)
        embedding = embedding.cpu().numpy()[0]

    return embedding
