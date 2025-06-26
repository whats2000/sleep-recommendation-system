"""
Emotion Recognition Agent for the LangGraph recommendation pipeline.
"""

import time
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

from src.state import RecommendationState, EmotionAnalysis
from src.nodes.llm_utils import llm


def emotion_recognition_agent(state: RecommendationState) -> Dict[str, Any]:
    """
    Emotion Recognition Agent - Identifies emotions and regulation needs.
    
    Input: emotional_state, sleep_goal
    Output: emotion labels, regulation strategy, target mood
    """
    start_time = time.time()
    
    try:
        form_data = state["form_data"]
        if not form_data:
            raise ValueError("No form data available for emotion analysis")
        
        system_prompt = """You are an emotion regulation specialist for sleep therapy.
        Analyze the user's emotional state and sleep goals to provide:
        1. Primary emotion identification
        2. Emotion intensity level (low/medium/high)
        3. Regulation strategy needed
        4. Target mood for sleep preparation
        
        Focus on evidence-based emotion regulation techniques."""
        
        user_prompt = f"""
        User's emotional context:
        - Current Emotional State: {form_data.emotional_state}
        - Sleep Goal: {form_data.sleep_goal}
        
        Please provide your analysis in the following format:
        Primary Emotion: [emotion]
        Emotion Intensity: [intensity]
        Regulation Strategy: [strategy]
        Target Mood: [target mood for sleep]
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
            Primary Emotion: {form_data.emotional_state}
            Emotion Intensity: medium
            Regulation Strategy: Mindfulness and breathing techniques
            Target Mood: calm and peaceful
            """
        
        # Parse the response
        lines = str(analysis_text).strip().split('\n')
        primary_emotion = form_data.emotional_state
        emotion_intensity = "medium"
        regulation_strategy = "relaxation techniques"
        target_mood = "calm"
        
        for line in lines:
            if "Primary Emotion:" in line:
                primary_emotion = line.split(":", 1)[1].strip()
            elif "Emotion Intensity:" in line:
                emotion_intensity = line.split(":", 1)[1].strip()
            elif "Regulation Strategy:" in line:
                regulation_strategy = line.split(":", 1)[1].strip()
            elif "Target Mood:" in line:
                target_mood = line.split(":", 1)[1].strip()
        
        emotion_analysis = EmotionAnalysis(
            primary_emotion=primary_emotion,
            emotion_intensity=emotion_intensity,
            regulation_strategy=regulation_strategy,
            target_mood=target_mood
        )
        
        processing_time = state.get("processing_time", {})
        processing_time["emotion_analysis"] = time.time() - start_time
        
        return {
            "emotion_analysis": emotion_analysis,
            "processing_status": "emotion_analysis_complete",
            "processing_time": processing_time
        }
        
    except Exception as e:
        error_messages = state.get("error_messages", [])
        error_messages.append(f"Emotion analysis error: {str(e)}")
        return {
            "error_messages": error_messages,
            "processing_status": "emotion_analysis_failed"
        }
