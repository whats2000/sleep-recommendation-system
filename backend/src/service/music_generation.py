"""
MusicGen service for generating reference audio from prompts.
"""

import os
import tempfile
from typing import Optional, Dict, Any

import torch
import scipy.io.wavfile
from transformers.pipelines import pipeline


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
        self.synthesiser = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()
    
    def _load_model(self):
        """Load the MusicGen pipeline."""
        try:
            print(f"Loading MusicGen pipeline: {self.model_name}")
            self.synthesiser = pipeline(
                "text-to-audio",
                self.model_name,
                device=0 if self.device == "cuda" else -1  # 0 for GPU, -1 for CPU
            )
            print(f"MusicGen pipeline loaded successfully on {self.device}")
        except Exception as e:
            print(f"Error loading MusicGen pipeline: {e}")
            print("CRITICAL: MusicGen pipeline failed to load. System will not return fake data.")
            self.synthesiser = None

    def _sanitize_prompt(self, prompt: str) -> str:
        """
        Sanitize the prompt to ensure it works well with MusicGen.

        Args:
            prompt: Raw prompt from LLM

        Returns:
            Cleaned prompt safe for MusicGen
        """
        import re

        # Remove any quotes or special formatting
        sanitized = prompt.strip().strip('"').strip("'")

        # Remove any line breaks and extra whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized)

        # Remove any special characters that might cause issues
        sanitized = re.sub(r'[^\w\s,.-]', '', sanitized)

        # Ensure it's not too long (MusicGen works best with shorter prompts)
        if len(sanitized) > 100:
            # Truncate at word boundary
            words = sanitized.split()
            truncated_words = []
            char_count = 0
            for word in words:
                if char_count + len(word) + 1 > 100:  # +1 for space
                    break
                truncated_words.append(word)
                char_count += len(word) + 1
            sanitized = ' '.join(truncated_words)

        # If the prompt is empty or too short, use a fallback
        if len(sanitized.strip()) < 10:
            sanitized = "ambient music, slow tempo, peaceful, relaxing"

        return sanitized

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
            if not self.synthesiser:
                print("Pipeline not loaded, attempting to reload...")
                self._load_model()

                if not self.synthesiser:
                    raise RuntimeError("MusicGen pipeline not available - cannot generate real audio. Refusing to return fake data to users.")

            print("Generating audio with transformers pipeline...")

            # Limit duration to prevent memory issues
            max_duration = 15  # Limit to 15 seconds maximum
            actual_duration = min(duration, max_duration)

            print(f"Audio generation: duration={actual_duration}s")
            print(f"Original prompt: '{prompt}'")

            # Sanitize the prompt to ensure it works with MusicGen
            sanitized_prompt = self._sanitize_prompt(prompt)
            print(f"Sanitized prompt: '{sanitized_prompt}'")

            # Generate audio using the pipeline
            print("Calling pipeline...")
            music = self.synthesiser(sanitized_prompt)

            # Check if generation was successful
            if music is None or "audio" not in music:
                raise RuntimeError("Audio generation failed - pipeline returned None or invalid result")

            audio_data = music["audio"]
            sampling_rate = music["sampling_rate"]

            print(f"Audio generated successfully, shape: {audio_data.shape}, sample rate: {sampling_rate}")
            
            # Save to file
            if output_dir is None:
                output_dir = tempfile.gettempdir()

            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"generated_audio_{hash(prompt) % 10000}.wav")

            # Save using scipy (handles the format conversion automatically)
            scipy.io.wavfile.write(output_path, rate=sampling_rate, data=audio_data)
            
            print(f"Generated audio saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error generating audio: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded pipeline."""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "pipeline_loaded": self.synthesiser is not None,
            "cuda_available": torch.cuda.is_available()
        }
    
    def cleanup(self):
        """Clean up pipeline resources."""
        if self.synthesiser:
            del self.synthesiser
            self.synthesiser = None

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
