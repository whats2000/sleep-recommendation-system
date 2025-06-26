from datetime import datetime
from typing import List

from pydantic import BaseModel


class FormData(BaseModel):
    """User form data structure based on the form design."""
    stress_level: str
    physical_symptoms: List[str]
    emotional_state: str
    sleep_goal: str
    sound_preferences: List[str]
    rhythm_preference: str
    sound_sensitivities: List[str]
    playback_mode: str
    guided_voice: str
    sleep_theme: str
    timestamp: datetime
