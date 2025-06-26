"""
Preference Analysis Agent for the LangGraph recommendation pipeline.
"""

import time
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

from src.state import RecommendationState, PreferenceAnalysis
from src.nodes.llm_utils import llm


def preference_analysis_agent(state: RecommendationState) -> Dict[str, Any]:
    """
    Preference Analysis Agent - Analyzes user music preferences and constraints.
    
    Input: sound_preferences, rhythm_preference, sound_sensitivities
    Output: preferred genres, instruments, tempo, forbidden elements
    """
    start_time = time.time()
    
    try:
        form_data = state["form_data"]
        if not form_data:
            raise ValueError("No form data available for preference analysis")
        
        system_prompt = """You are a music therapy specialist analyzing user preferences.
        Analyze the user's sound preferences, rhythm preferences, and sensitivities to provide:
        1. Preferred music genres for sleep
        2. Preferred instruments
        3. Optimal tempo preference
        4. Elements to avoid (forbidden elements)
        5. Preference strength matrix (0.0-1.0 scores)
        
        Focus on sleep-conducive music characteristics."""
        
        user_prompt = f"""
        User's music preferences:
        - Sound Preferences: {', '.join(form_data.sound_preferences)}
        - Rhythm Preference: {form_data.rhythm_preference}
        - Sound Sensitivities: {', '.join(form_data.sound_sensitivities)}
        - Sleep Theme: {form_data.sleep_theme}
        
        Please provide your analysis in the following format:
        Preferred Genres: [list of genres]
        Preferred Instruments: [list of instruments]
        Tempo Preference: [tempo description]
        Forbidden Elements: [list of elements to avoid]
        Preference Matrix: ambient:0.8, classical:0.7, electronic:0.5
        """
        
        if llm:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            response = llm.invoke(messages)
            analysis_text = response.content
        else:
            # Mock response for development
            analysis_text = f"""
            Preferred Genres: ambient, lo-fi, classical
            Preferred Instruments: piano, strings, synthesizer
            Tempo Preference: very slow, 60-80 BPM
            Forbidden Elements: {', '.join(form_data.sound_sensitivities)}
            Preference Matrix: ambient:0.9, classical:0.8, lo-fi:0.7, electronic:0.6
            """
        
        # Parse the response
        lines = str(analysis_text).strip().split('\n')
        preferred_genres = ["ambient", "classical"]
        preferred_instruments = ["piano", "strings"]
        tempo_preference = "very slow"
        forbidden_elements = form_data.sound_sensitivities
        preference_matrix = {"ambient": 0.8, "classical": 0.7}
        
        for line in lines:
            if "Preferred Genres:" in line:
                genres_text = line.split(":", 1)[1].strip()
                preferred_genres = [g.strip() for g in genres_text.split(',')]
            elif "Preferred Instruments:" in line:
                instruments_text = line.split(":", 1)[1].strip()
                preferred_instruments = [i.strip() for i in instruments_text.split(',')]
            elif "Tempo Preference:" in line:
                tempo_preference = line.split(":", 1)[1].strip()
            elif "Forbidden Elements:" in line:
                forbidden_text = line.split(":", 1)[1].strip()
                forbidden_elements = [f.strip() for f in forbidden_text.split(',')]
            elif "Preference Matrix:" in line:
                matrix_text = line.split(":", 1)[1].strip()
                try:
                    # Parse preference matrix like "ambient:0.8, classical:0.7"
                    pairs = matrix_text.split(',')
                    preference_matrix = {}
                    for pair in pairs:
                        if ':' in pair:
                            key, value = pair.split(':', 1)
                            preference_matrix[key.strip()] = float(value.strip())
                except:
                    preference_matrix = {"ambient": 0.8, "classical": 0.7}
        
        preference_analysis = PreferenceAnalysis(
            preferred_genres=preferred_genres,
            preferred_instruments=preferred_instruments,
            tempo_preference=tempo_preference,
            forbidden_elements=forbidden_elements,
            preference_matrix=preference_matrix
        )
        
        processing_time = state.get("processing_time", {})
        processing_time["preference_analysis"] = time.time() - start_time
        
        return {
            "preference_analysis": preference_analysis,
            "processing_status": "preference_analysis_complete",
            "processing_time": processing_time
        }
        
    except Exception as e:
        error_messages = state.get("error_messages", [])
        error_messages.append(f"Preference analysis error: {str(e)}")
        return {
            "error_messages": error_messages,
            "processing_status": "preference_analysis_failed"
        }
