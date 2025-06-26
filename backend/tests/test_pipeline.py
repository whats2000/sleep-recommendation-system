"""
Tests for the LangGraph recommendation pipeline.
"""

import pytest
from datetime import datetime
import sys
from pathlib import Path

from src.state import FormData, RecommendationState
from src.pipeline import RecommendationPipeline


class TestRecommendationPipeline:
    """Test cases for the recommendation pipeline."""
    
    @pytest.fixture
    def sample_form_data(self):
        """Sample form data for testing."""
        return {
            "stress_level": "中度壓力",
            "physical_symptoms": ["頭腦過度活躍", "肌肉緊繃"],
            "emotional_state": "焦慮",
            "sleep_goal": "快速入眠",
            "sound_preferences": ["樂器聲（鋼琴、古典、弦樂）"],
            "rhythm_preference": "超慢（冥想般，幾乎無節奏）",
            "sound_sensitivities": ["高頻刺耳聲"],
            "playback_mode": "逐漸淡出（10~20分鐘入睡）",
            "guided_voice": "否，只需要純音樂",
            "sleep_theme": "平靜如水（穩定神經）",
            "timestamp": datetime.now()
        }
    
    @pytest.fixture
    def pipeline(self):
        """Create a pipeline instance for testing."""
        return RecommendationPipeline(enable_checkpointing=False)
    
    def test_form_data_creation(self, sample_form_data):
        """Test FormData object creation."""
        form_data = FormData(**sample_form_data)
        
        assert form_data.stress_level == "中度壓力"
        assert form_data.emotional_state == "焦慮"
        assert form_data.sleep_goal == "快速入眠"
        assert len(form_data.physical_symptoms) == 2
        assert len(form_data.sound_preferences) == 1
    
    def test_pipeline_initialization(self, pipeline):
        """Test pipeline initialization."""
        assert pipeline is not None
        assert pipeline.graph is not None
        assert not pipeline.enable_checkpointing
    
    def test_pipeline_process_form_data(self, pipeline, sample_form_data):
        """Test processing form data through the pipeline."""
        result = pipeline.process_form_data(sample_form_data)
        
        # Check basic structure
        assert "success" in result
        assert "session_id" in result
        
        # If successful, check for expected fields
        if result["success"]:
            assert "generated_prompt" in result
            assert "processing_time" in result
            
            # Check generated prompt structure
            prompt = result["generated_prompt"]
            assert "musicgen_prompt" in prompt
            assert "prompt_components" in prompt
            assert "generation_parameters" in prompt
            assert "expected_duration" in prompt
        else:
            # If failed, should have error information
            assert "error" in result or "error_messages" in result
    
    def test_pipeline_with_minimal_data(self, pipeline):
        """Test pipeline with minimal required data."""
        minimal_data = {
            "stress_level": "稍微有點壓力",
            "physical_symptoms": [],
            "emotional_state": "平靜",
            "sleep_goal": "維持整夜好眠",
            "sound_preferences": [],
            "rhythm_preference": "緩慢穩定（放鬆心跳）",
            "sound_sensitivities": [],
            "playback_mode": "無偏好",
            "guided_voice": "否，只需要純音樂",
            "sleep_theme": "AI自動推薦",
            "timestamp": datetime.now()
        }
        
        result = pipeline.process_form_data(minimal_data)
        
        # Should still work with minimal data
        assert "success" in result
        assert "session_id" in result
    
    def test_pipeline_error_handling(self, pipeline):
        """Test pipeline error handling with invalid data."""
        invalid_data = {
            "stress_level": "invalid_level",
            # Missing required fields
        }
        
        result = pipeline.process_form_data(invalid_data)
        
        # Should handle errors gracefully
        assert "success" in result
        if not result["success"]:
            assert "error" in result or "error_messages" in result


if __name__ == "__main__":
    # Run a simple test
    pipeline = RecommendationPipeline(enable_checkpointing=False)
    
    sample_data = {
        "stress_level": "中度壓力",
        "physical_symptoms": ["頭腦過度活躍"],
        "emotional_state": "焦慮",
        "sleep_goal": "快速入眠",
        "sound_preferences": ["樂器聲（鋼琴、古典、弦樂）"],
        "rhythm_preference": "超慢（冥想般，幾乎無節奏）",
        "sound_sensitivities": [],
        "playback_mode": "逐漸淡出（10~20分鐘入睡）",
        "guided_voice": "否，只需要純音樂",
        "sleep_theme": "平靜如水（穩定神經）",
        "timestamp": datetime.now()
    }
    
    print("Testing pipeline with sample data...")
    result = pipeline.process_form_data(sample_data)
    
    print(f"Success: {result.get('success')}")
    if result.get("success"):
        print(f"Generated prompt: {result.get('generated_prompt', {}).get('musicgen_prompt', 'N/A')}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    print("Test completed.")
