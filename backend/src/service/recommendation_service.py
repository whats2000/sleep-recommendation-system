"""
Main recommendation service that integrates the LangGraph pipeline with music generation and vector search.
"""

import os
import time
from typing import Dict, Any, List, Optional

from src.pipeline import RecommendationPipeline
from src.service.music_generation import MusicGenerationService
from src.utils.encode_audio import encode_audio
from src.utils.vector_search import search_similar_tracks


class RecommendationService:
    """
    Main service that orchestrates the complete recommendation workflow:
    1. Process form data through LangGraph pipeline
    2. Generate reference audio using MusicGen
    3. Encode audio using CLAP
    4. Search for similar tracks
    5. Return top recommendations
    """
    
    def __init__(self, audio_output_dir: Optional[str] = None):
        """
        Initialize the recommendation service.
        
        Args:
            audio_output_dir: Directory to store generated audio files
        """
        self.pipeline = RecommendationPipeline(enable_checkpointing=True)
        self.music_gen_service = MusicGenerationService()
        self.audio_output_dir = audio_output_dir or os.path.join(os.getcwd(), "generated_audio")
        
        # Ensure output directory exists
        os.makedirs(self.audio_output_dir, exist_ok=True)
    
    def get_recommendations(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get music recommendations based on user form data.
        
        Args:
            form_data: User form data dictionary
            
        Returns:
            Dictionary containing recommendations and metadata
        """
        start_time = time.time()
        
        try:
            # Step 1: Process form data through LangGraph pipeline
            print("Step 1: Processing form data through LangGraph pipeline...")
            pipeline_result = self.pipeline.process_form_data(form_data)
            
            if not pipeline_result.get("success"):
                return {
                    "success": False,
                    "error": "Pipeline processing failed",
                    "details": pipeline_result,
                    "processing_time": time.time() - start_time
                }
            
            generated_prompt = pipeline_result.get("generated_prompt")
            if not generated_prompt:
                return {
                    "success": False,
                    "error": "No prompt generated",
                    "details": pipeline_result,
                    "processing_time": time.time() - start_time
                }
            
            # Step 2: Generate reference audio using MusicGen
            print("Step 2: Generating reference audio...")
            audio_path = self._generate_reference_audio(generated_prompt)
            
            if not audio_path:
                return {
                    "success": False,
                    "error": "Audio generation failed",
                    "pipeline_result": pipeline_result,
                    "processing_time": time.time() - start_time
                }
            
            # Step 3: Encode audio using CLAP
            print("Step 3: Encoding audio with CLAP...")
            audio_embedding = self._encode_audio(audio_path)
            
            if audio_embedding is None:
                return {
                    "success": False,
                    "error": "Audio encoding failed",
                    "pipeline_result": pipeline_result,
                    "audio_path": audio_path,
                    "processing_time": time.time() - start_time
                }
            
            # Step 4: Search for similar tracks
            print("Step 4: Searching for similar tracks...")
            similar_tracks = self._search_similar_tracks(audio_embedding)
            
            # Step 5: Format final recommendations
            recommendations = self._format_recommendations(
                similar_tracks, 
                pipeline_result, 
                audio_path,
                audio_embedding
            )
            
            total_time = time.time() - start_time
            
            return {
                "success": True,
                "session_id": pipeline_result.get("session_id"),
                "recommendations": recommendations,
                "pipeline_analysis": {
                    "state_analysis": pipeline_result.get("state_analysis"),
                    "emotion_analysis": pipeline_result.get("emotion_analysis"),
                    "preference_analysis": pipeline_result.get("preference_analysis")
                },
                "generated_prompt": generated_prompt,
                "reference_audio_path": audio_path,
                "processing_time": total_time,
                "processing_breakdown": pipeline_result.get("processing_time", {})
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Recommendation service error: {str(e)}",
                "processing_time": time.time() - start_time
            }
    
    def _generate_reference_audio(self, generated_prompt: Dict[str, Any]) -> Optional[str]:
        """Generate reference audio from the prompt."""
        try:
            prompt_text = generated_prompt["musicgen_prompt"]
            duration = generated_prompt.get("expected_duration", 30)
            guidance_scale = generated_prompt.get("generation_parameters", {}).get("guidance_scale", 3.0)
            
            audio_path = self.music_gen_service.generate_audio(
                prompt=prompt_text,
                duration=duration,
                guidance_scale=guidance_scale,
                output_dir=self.audio_output_dir
            )
            
            return audio_path
            
        except Exception as e:
            print(f"Error in reference audio generation: {e}")
            return None

    @staticmethod
    def _encode_audio(audio_path: str) -> Optional[List[float]]:
        """Encode audio file using CLAP."""
        try:
            embedding = encode_audio(audio_path)
            if embedding is not None:
                return embedding.tolist()
            return None
            
        except Exception as e:
            print(f"Error in audio encoding: {e}")
            return None

    @staticmethod
    def _search_similar_tracks(audio_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar tracks using vector similarity."""
        try:
            similar_tracks = search_similar_tracks(audio_embedding, top_k=top_k)
            return similar_tracks
            
        except Exception as e:
            print(f"Error in similarity search: {e}")
            return []
    
    def _format_recommendations(
        self, 
        similar_tracks: List[Dict[str, Any]], 
        pipeline_result: Dict[str, Any],
        audio_path: str,
        audio_embedding: List[float]
    ) -> List[Dict[str, Any]]:
        """Format the final recommendations."""
        recommendations = []
        
        for i, track in enumerate(similar_tracks):
            recommendation = {
                "rank": i + 1,
                "track_id": track.get("track_id", f"track_{i}"),
                "title": track.get("title", f"Recommended Track {i+1}"),
                "artist": track.get("artist", "Unknown Artist"),
                "file_path": track.get("file_path"),
                "similarity_score": track.get("similarity_score", 0.0),
                "metadata": track.get("metadata", {}),
                "recommendation_reason": self._generate_recommendation_reason(
                    track, pipeline_result, i + 1
                )
            }
            recommendations.append(recommendation)
        
        return recommendations

    @staticmethod
    def _generate_recommendation_reason(
        track: Dict[str, Any], 
        pipeline_result: Dict[str, Any], 
        rank: int
    ) -> str:
        """Generate a human-readable reason for the recommendation."""
        try:
            state_analysis = pipeline_result.get("state_analysis", {})
            emotion_analysis = pipeline_result.get("emotion_analysis", {})
            
            stress_level = state_analysis.get("stress_assessment", "moderate")
            target_mood = emotion_analysis.get("target_mood", "calm")
            similarity_score = track.get("similarity_score", 0.0)
            
            if rank == 1:
                reason = f"Top match for your {stress_level} stress level and desire for {target_mood} mood"
            elif similarity_score > 0.8:
                reason = f"Highly similar to your preferences with {similarity_score:.1%} match"
            elif similarity_score > 0.6:
                reason = f"Good match for {target_mood} mood with {similarity_score:.1%} similarity"
            else:
                reason = f"Alternative option that may help achieve {target_mood} state"
            
            return reason
            
        except Exception as e:
            return f"Recommended based on your preferences (rank #{rank})"
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get the status of all service components."""
        return {
            "pipeline_status": "ready",
            "music_generation": self.music_gen_service.get_model_info(),
            "audio_output_dir": self.audio_output_dir,
            "clap_encoding": "available",
            "vector_search": "available"
        }
    
    def cleanup(self):
        """Clean up service resources."""
        self.music_gen_service.cleanup()
        print("Recommendation service cleaned up")
