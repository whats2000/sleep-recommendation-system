"""
Requirement Integration Agent for the LangGraph recommendation pipeline.
"""

import time
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

from src.state import RecommendationState, IntegratedRequirements
from src.nodes.llm_utils import llm


def requirement_integration_agent(state: RecommendationState) -> Dict[str, Any]:
    """
    Requirement Integration Agent - Integrates all analysis results into unified requirements.
    
    Input: state_analysis, emotion_analysis, preference_analysis
    Output: unified requirements, priority ranking, conflict resolutions
    """
    start_time = time.time()
    
    try:
        state_analysis = state.get("state_analysis")
        emotion_analysis = state.get("emotion_analysis")
        preference_analysis = state.get("preference_analysis")
        
        if not all([state_analysis, emotion_analysis, preference_analysis]):
            raise ValueError("Missing analysis results for requirement integration")
        
        system_prompt = """You are a music therapy coordinator integrating multiple analyses.
        Combine the state analysis, emotion analysis, and preference analysis to create:
        1. Unified requirements that address all needs
        2. Priority ranking of requirements (most important first)
        3. Conflict resolutions where preferences conflict with therapeutic needs
        4. Final specifications for music generation
        
        Prioritize therapeutic effectiveness while respecting user preferences."""
        
        user_prompt = f"""
        Analysis Results:
        
        State Analysis:
        - Stress Assessment: {state_analysis.stress_assessment}
        - Urgency Level: {state_analysis.urgency_level}
        - Recommendations: {', '.join(state_analysis.recommendations)}
        
        Emotion Analysis:
        - Primary Emotion: {emotion_analysis.primary_emotion}
        - Regulation Strategy: {emotion_analysis.regulation_strategy}
        - Target Mood: {emotion_analysis.target_mood}
        
        Preference Analysis:
        - Preferred Genres: {', '.join(preference_analysis.preferred_genres)}
        - Tempo Preference: {preference_analysis.tempo_preference}
        - Forbidden Elements: {', '.join(preference_analysis.forbidden_elements)}
        
        Please provide integration in the following format:
        Unified Requirements: [key requirements]
        Priority Ranking: [ordered list of priorities]
        Conflict Resolutions: [how conflicts were resolved]
        Final Specifications: genre=[genre], tempo=[tempo], mood=[mood], instruments=[instruments]
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
            Unified Requirements: Stress reduction, Emotion regulation, User preference alignment
            Priority Ranking: Therapeutic effectiveness, User comfort, Preference satisfaction
            Conflict Resolutions: Balanced tempo for both relaxation and preference
            Final Specifications: genre=ambient, tempo=slow, mood=calming, instruments=piano,strings
            """
        
        # Parse the response
        lines = str(analysis_text).strip().split('\n')
        unified_requirements = {
            "stress_reduction": True,
            "emotion_regulation": True,
            "preference_alignment": True
        }
        priority_ranking = ["therapeutic_effectiveness", "user_comfort", "preference_satisfaction"]
        conflict_resolutions = ["Balanced approach between therapy and preferences"]
        final_specifications = {
            "genre": preference_analysis.preferred_genres[0] if preference_analysis.preferred_genres else "ambient",
            "tempo": preference_analysis.tempo_preference,
            "mood": emotion_analysis.target_mood,
            "instruments": preference_analysis.preferred_instruments[:2] if preference_analysis.preferred_instruments else ["piano"]
        }
        
        for line in lines:
            if "Unified Requirements:" in line:
                req_text = line.split(":", 1)[1].strip()
                # Parse requirements into structured format
                unified_requirements = {
                    "primary_goal": req_text,
                    "stress_level": state_analysis.urgency_level,
                    "emotion_target": emotion_analysis.target_mood
                }
            elif "Priority Ranking:" in line:
                priority_text = line.split(":", 1)[1].strip()
                priority_ranking = [p.strip() for p in priority_text.split(',')]
            elif "Conflict Resolutions:" in line:
                resolution_text = line.split(":", 1)[1].strip()
                conflict_resolutions = [resolution_text]
            elif "Final Specifications:" in line:
                spec_text = line.split(":", 1)[1].strip()
                # Parse specifications like "genre=ambient, tempo=slow"
                try:
                    specs = {}
                    for spec in spec_text.split(','):
                        if '=' in spec:
                            key, value = spec.split('=', 1)
                            specs[key.strip()] = value.strip()
                    final_specifications.update(specs)
                except:
                    pass  # Keep default specifications
        
        integrated_requirements = IntegratedRequirements(
            unified_requirements=unified_requirements,
            priority_ranking=priority_ranking,
            conflict_resolutions=conflict_resolutions,
            final_specifications=final_specifications
        )
        
        processing_time = state.get("processing_time", {})
        processing_time["requirement_integration"] = time.time() - start_time
        
        return {
            "integrated_requirements": integrated_requirements,
            "processing_status": "requirement_integration_complete",
            "processing_time": processing_time
        }
        
    except Exception as e:
        error_messages = state.get("error_messages", [])
        error_messages.append(f"Requirement integration error: {str(e)}")
        return {
            "error_messages": error_messages,
            "processing_status": "requirement_integration_failed"
        }
