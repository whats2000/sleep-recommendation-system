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
            print("CRITICAL: MusicGen model failed to load. System will not return fake data.")
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
                raise RuntimeError("MusicGen model not available - cannot generate real audio. Refusing to return fake data to users.")

            print("Generating audio with transformers...")

            # Prepare inputs
            inputs = self.processor(
                text=[prompt],
                padding=True,
                return_tensors="pt"
            ).to(self.device)

            # Use a simpler approach for token calculation
            # Generate for the specified duration (in seconds)
            sample_rate = 32000  # Standard MusicGen sample rate

            # Generate audio
            with torch.no_grad():
                audio_values = self.model.generate(
                    **inputs,
                    max_length=int(duration * sample_rate / 320),  # Approximate token calculation
                    guidance_scale=guidance_scale,
                    do_sample=True,
                    temperature=1.0
                )

            # Check if generation was successful
            if audio_values is None or len(audio_values) == 0:
                raise RuntimeError("Audio generation failed - model returned None or empty result")

            # Convert to audio format
            audio = audio_values[0].cpu()

            # Validate audio tensor
            if audio is None:
                raise RuntimeError("Audio generation failed - audio tensor is None")
            
            # Save to file
            if output_dir is None:
                output_dir = tempfile.gettempdir()
            
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"generated_audio_{hash(prompt) % 10000}.wav")
            
            # Save the audio file
            # Ensure audio has the right shape (channels, samples)
            if audio.dim() == 1:
                audio = audio.unsqueeze(0)  # Add channel dimension
            elif audio.dim() == 3:
                audio = audio.squeeze(0)    # Remove batch dimension

            torchaudio.save(
                output_path,
                audio,
                int(sample_rate)
            )
            
            print(f"Generated audio saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error generating audio: {e}")
            raise
    
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
