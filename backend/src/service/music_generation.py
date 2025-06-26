"""
MusicGen service for generating reference audio from prompts.
"""

import os
import tempfile
from typing import Optional, Dict, Any

import torch
import torchaudio
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
            self.model = MusicgenForConditionalGeneration.from_pretrained(
                self.model_name,
                attn_implementation="eager"
            )
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
                print(f"Model check: model={self.model is not None}, processor={self.processor is not None}")
                print("Attempting to reload model...")
                self._load_model()

                if not self.model or not self.processor:
                    raise RuntimeError("MusicGen model not available - cannot generate real audio. Refusing to return fake data to users.")

            print("Generating audio with transformers...")

            # 1. encode prompt with the tokenizer
            inputs = self.processor(
                text=[prompt],
                padding=True,
                return_tensors="pt",
            ).to(self.device)

            # 2. cap max_length as discussed earlier
            sample_rate = 32_000
            max_model_tokens = 1_280  # safety cap
            tokens_to_generate = min(
                int(duration * sample_rate / 320),
                max_model_tokens,
            )

            # 3. generate
            with torch.no_grad():
                audio_values = self.model.generate(
                    **inputs,
                    max_length=tokens_to_generate,
                    guidance_scale=guidance_scale,
                    do_sample=True,
                    temperature=1.0,
                )

            # Check if generation was successful
            if audio_values is None or len(audio_values) == 0:
                raise RuntimeError("Audio generation failed - model returned None or empty result")

            # 4. grab the waveform
            waveform = audio_values[0].cpu()

            # Validate audio tensor
            if waveform is None:
                raise RuntimeError("Audio generation failed - audio tensor is None")
            
            # Save to file
            if output_dir is None:
                output_dir = tempfile.gettempdir()
            
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"generated_audio_{hash(prompt) % 10000}.wav")

            # Ensure shape = (channels, samples)
            if waveform.dim() == 1:  # (samples) ➜ (1, samples)
                audio_to_save = waveform.unsqueeze(0)
            elif waveform.dim() == 2:  # already (channels, samples)
                audio_to_save = waveform
            elif waveform.dim() == 3:  # (1, channels, samples)
                audio_to_save = waveform.squeeze(0)
            else:
                raise RuntimeError(
                    f"Unexpected waveform dimension: {waveform.shape}"
                )

            torchaudio.save(
                output_path,
                audio_to_save,
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

if __name__ == "__main__":
    # Example usage
    service = MusicGenerationService()
    test_prompt = "A calm and relaxing piano piece"
    audio_path = service.generate_audio(test_prompt, duration=30, guidance_scale=3.0)

    if audio_path:
        print(f"Audio generated successfully: {audio_path}")
    else:
        print("Audio generation failed")

    # Cleanup resources
    service.cleanup()
