from typing import List, Dict, Any, Optional

from pydantic import BaseModel
from typing_extensions import TypedDict

from src.state.form_data import FormData


class StateAnalysis(BaseModel):
    """Results from the State Analysis Agent."""
    stress_assessment: str
    urgency_level: str
    physical_state_summary: str
    recommendations: List[str]


class EmotionAnalysis(BaseModel):
    """Results from the Emotion Recognition Agent."""
    primary_emotion: str
    emotion_intensity: str
    regulation_strategy: str
    target_mood: str


class PreferenceAnalysis(BaseModel):
    """Results from the Preference Analysis Agent."""
    preferred_genres: List[str]
    preferred_instruments: List[str]
    tempo_preference: str
    forbidden_elements: List[str]
    preference_matrix: Dict[str, float]


class IntegratedRequirements(BaseModel):
    """Results from the Requirement Integration Agent."""
    unified_requirements: Dict[str, Any]
    priority_ranking: List[str]
    conflict_resolutions: List[str]
    final_specifications: Dict[str, Any]


class GeneratedPrompt(BaseModel):
    """Results from the Prompt Generation Agent."""
    musicgen_prompt: str
    prompt_components: Dict[str, str]
    generation_parameters: Dict[str, Any]
    expected_duration: int


class RecommendationState(TypedDict):
    """
    Main state object for the LangGraph pipeline.
    This holds all data as it flows through the multi-agent workflow.
    """
    # Input data
    form_data: Optional[FormData]

    # Agent analysis results
    state_analysis: Optional[StateAnalysis]
    emotion_analysis: Optional[EmotionAnalysis]
    preference_analysis: Optional[PreferenceAnalysis]
    integrated_requirements: Optional[IntegratedRequirements]
    generated_prompt: Optional[GeneratedPrompt]

    # Music generation and search results
    reference_audio_path: Optional[str]
    audio_embedding: Optional[List[float]]
    similar_tracks: Optional[List[Dict[str, Any]]]
    recommendations: Optional[List[Dict[str, Any]]]

    # Metadata
    session_id: str
    processing_status: str
    error_messages: List[str]
    processing_time: Dict[str, float]
