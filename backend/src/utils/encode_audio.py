"""
Encodes audio files into embedding vectors using the CLAP model.
"""

import os
import warnings

import librosa
import torch
from dotenv import load_dotenv
from transformers import ClapProcessor, ClapModel

warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

# Model parameters
MODEL_NAME = os.getenv("MODEL_NAME", "laion/clap-htsat-unfused")

# Check if GPU is available and working
device = "cpu"  # Default to CPU
model = None
processor = None

def _initialize_model():
    """Initialize the CLAP model with proper error handling."""
    global model, processor, device

    if model is not None:
        return  # Already initialized

    try:
        # Try CUDA first if available
        if torch.cuda.is_available():
            try:
                device = "cuda"
                model = ClapModel.from_pretrained(MODEL_NAME).to(device)
                processor = ClapProcessor.from_pretrained(MODEL_NAME)
                model.eval()

                # Test CUDA with a small operation
                test_tensor = torch.zeros(1, 1).to(device)
                _ = test_tensor + 1
                print(f"CLAP model loaded successfully on {device}")
                return

            except Exception as cuda_error:
                print(f"CUDA initialization failed: {cuda_error}")
                print("Falling back to CPU...")
                # Clean up any partially loaded CUDA model
                if model is not None:
                    del model
                    model = None
                torch.cuda.empty_cache() if torch.cuda.is_available() else None

        # Fall back to CPU
        device = "cpu"
        model = ClapModel.from_pretrained(MODEL_NAME).to(device)
        processor = ClapProcessor.from_pretrained(MODEL_NAME)
        model.eval()
        print(f"CLAP model loaded successfully on {device}")

    except Exception as e:
        print(f"Failed to initialize CLAP model: {e}")
        model = None
        processor = None
        device = "cpu"

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

    # Initialize model if not already done
    _initialize_model()

    if model is None or processor is None:
        print("CLAP model not available - cannot encode audio")
        return None

    # Load audio file
    audio, sr, duration = load_audio_file(file_path)

    if audio is None:
        print("Failed to load audio file")
        return None

    try:
        # Encode audio
        with torch.no_grad():
            inputs = processor(audios=[audio], return_tensors="pt")
            # Move only the audio inputs to the correct device
            audio_inputs = {}
            for key, value in inputs.items():
                if isinstance(value, torch.Tensor):
                    audio_inputs[key] = value.to(device)
                else:
                    audio_inputs[key] = value

            embedding = model.get_audio_features(**audio_inputs)
            embedding = embedding.cpu().numpy()[0]

        # Return embedding
        return embedding

    except Exception as e:
        print(f"Error during audio encoding: {e}")
        return None


if __name__ == "__main__":
    # Test model initialization
    print("Testing CLAP model initialization...")
    _initialize_model()

    if model is not None:
        print(f"Model successfully loaded on {device}")
    else:
        print("Model initialization failed")
