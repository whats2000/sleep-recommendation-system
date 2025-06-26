"""
MusicGen service for generating reference audio from prompts.
"""

import os
import torch
import torchaudio
import tempfile
from typing import Optional, Dict, Any
from transformers import MusicgenForConditionalGeneration, AutoProcessor


class MusicGenerationService:
    """
    Service for generating music using Facebook's MusicGen model.
    
    This service takes the generated prompts from the LangGraph pipeline
    and creates reference audio files for vector similarity search.
    """
    
    def __init__(self, model_name: str = "facebook/musicgen-small"):
        """
        Initialize the MusicGen service.
        
        Args:
            model_name: HuggingFace model name for MusicGen
        """
        self.model_name = model_name
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()
    
    def _load_model(self):
        """Load the MusicGen model and processor."""
        try:
            print(f"Loading MusicGen model: {self.model_name}")
            self.processor = AutoProcessor.from_pretrained(self.model_name)
            self.model = MusicgenForConditionalGeneration.from_pretrained(self.model_name)
            self.model.to(self.device)
            print(f"MusicGen model loaded successfully on {self.device}")
        except Exception as e:
            print(f"Error loading MusicGen model: {e}")
            print("MusicGen service will operate in mock mode")
            self.model = None
            self.processor = None
    
    def generate_audio(
        self, 
        prompt: str, 
        duration: int = 30,
        guidance_scale: float = 3.0,
        output_dir: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate audio from a text prompt.
        
        Args:
            prompt: Text description for music generation
            duration: Duration in seconds
            guidance_scale: Guidance scale for generation
            output_dir: Directory to save the generated audio
            
        Returns:
            Path to the generated audio file, or None if generation failed
        """
        try:
            if not self.model or not self.processor:
                return self._generate_mock_audio(prompt, duration, output_dir)
            
            # Prepare inputs
            inputs = self.processor(
                text=[prompt],
                padding=True,
                return_tensors="pt"
            ).to(self.device)
            
            # Calculate max_new_tokens based on duration
            # MusicGen typically generates at 32kHz, so we need duration * 32000 tokens
            sample_rate = self.model.config.audio_encoder.sampling_rate
            max_new_tokens = int(duration * sample_rate / self.model.config.audio_encoder.hop_length)
            
            # Generate audio
            with torch.no_grad():
                audio_values = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    guidance_scale=guidance_scale,
                    do_sample=True,
                    temperature=1.0
                )
            
            # Convert to audio format
            audio = audio_values[0].cpu()
            
            # Save to file
            if output_dir is None:
                output_dir = tempfile.gettempdir()
            
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"generated_audio_{hash(prompt) % 10000}.wav")
            
            # Save the audio file
            torchaudio.save(
                output_path,
                audio.unsqueeze(0),
                sample_rate
            )
            
            print(f"Generated audio saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error generating audio: {e}")
            return self._generate_mock_audio(prompt, duration, output_dir)

    @staticmethod
    def _generate_mock_audio(
        prompt: str, 
        duration: int = 30,
        output_dir: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate mock audio for development/testing when MusicGen is not available.
        
        Creates a simple sine wave audio file.
        """
        try:
            import numpy as np
            
            if output_dir is None:
                output_dir = tempfile.gettempdir()
            
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"mock_audio_{hash(prompt) % 10000}.wav")
            
            # Generate simple sine wave based on prompt characteristics
            sample_rate = 32000
            t = np.linspace(0, duration, int(sample_rate * duration))
            
            # Create a simple harmonic based on prompt content
            base_freq = 220  # A3
            if "calm" in prompt.lower() or "peaceful" in prompt.lower():
                base_freq = 174  # Lower frequency for calm
            elif "energetic" in prompt.lower() or "upbeat" in prompt.lower():
                base_freq = 440  # Higher frequency for energy
            
            # Generate simple harmonic content
            audio = (
                0.3 * np.sin(2 * np.pi * base_freq * t) +
                0.2 * np.sin(2 * np.pi * base_freq * 1.5 * t) +
                0.1 * np.sin(2 * np.pi * base_freq * 2 * t)
            )
            
            # Apply fade in/out
            fade_samples = int(0.1 * sample_rate)  # 0.1 second fade
            audio[:fade_samples] *= np.linspace(0, 1, fade_samples)
            audio[-fade_samples:] *= np.linspace(1, 0, fade_samples)
            
            # Convert to tensor and save
            audio_tensor = torch.from_numpy(audio).float().unsqueeze(0)
            torchaudio.save(output_path, audio_tensor, sample_rate)
            
            print(f"Mock audio generated and saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error generating mock audio: {e}")
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "model_loaded": self.model is not None,
            "processor_loaded": self.processor is not None,
            "cuda_available": torch.cuda.is_available()
        }
    
    def cleanup(self):
        """Clean up model resources."""
        if self.model:
            del self.model
            self.model = None
        if self.processor:
            del self.processor
            self.processor = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        print("MusicGen service cleaned up")
