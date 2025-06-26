"""
State Analysis Agent for the LangGraph recommendation pipeline.
"""

import time
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

from src.state import RecommendationState, StateAnalysis
from src.nodes.llm_utils import llm


def state_analysis_agent(state: RecommendationState) -> Dict[str, Any]:
    """
    State Analysis Agent - Analyzes user's physiological and psychological state.
    
    Input: stress_level, physical_symptoms, emotional_state
    Output: state assessment, urgency level, recommendations
    """
    start_time = time.time()
    
    try:
        form_data = state["form_data"]
        if not form_data:
            raise ValueError("No form data available for state analysis")
        
        # Create analysis prompt
        system_prompt = """You are a sleep wellness expert analyzing a user's current state.
        Analyze the user's stress level, physical symptoms, and emotional state to provide:
        1. Overall stress assessment (low/moderate/high/critical)
        2. Urgency level for intervention (low/medium/high)
        3. Physical state summary
        4. Specific recommendations for sleep preparation
        
        Be concise and focus on actionable insights."""
        
        user_prompt = f"""
        User's current state:
        - Stress Level: {form_data.stress_level}
        - Physical Symptoms: {', '.join(form_data.physical_symptoms)}
        - Emotional State: {form_data.emotional_state}
        
        Please provide your analysis in the following format:
        Stress Assessment: [assessment]
        Urgency Level: [level]
        Physical State Summary: [summary]
        Recommendations: [list of 2-3 specific recommendations]
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
            Stress Assessment: {form_data.stress_level}
            Urgency Level: medium
            Physical State Summary: User experiencing {', '.join(form_data.physical_symptoms[:2])}
            Recommendations: Deep breathing exercises, Progressive muscle relaxation, Calming music therapy
            """
        
        # Parse the response (simplified parsing)
        lines = str(analysis_text).strip().split('\n')
        stress_assessment = "moderate"
        urgency_level = "medium"
        physical_state_summary = "Mixed physical symptoms reported"
        recommendations = ["Deep breathing", "Muscle relaxation", "Calming environment"]
        
        for line in lines:
            if "Stress Assessment:" in line:
                stress_assessment = line.split(":", 1)[1].strip()
            elif "Urgency Level:" in line:
                urgency_level = line.split(":", 1)[1].strip()
            elif "Physical State Summary:" in line:
                physical_state_summary = line.split(":", 1)[1].strip()
            elif "Recommendations:" in line:
                rec_text = line.split(":", 1)[1].strip()
                recommendations = [r.strip() for r in rec_text.split(',')]
        
        state_analysis = StateAnalysis(
            stress_assessment=stress_assessment,
            urgency_level=urgency_level,
            physical_state_summary=physical_state_summary,
            recommendations=recommendations
        )
        
        processing_time = state.get("processing_time", {})
        processing_time["state_analysis"] = time.time() - start_time
        
        return {
            "state_analysis": state_analysis,
            "processing_status": "state_analysis_complete",
            "processing_time": processing_time
        }
        
    except Exception as e:
        error_messages = state.get("error_messages", [])
        error_messages.append(f"State analysis error: {str(e)}")
        return {
            "error_messages": error_messages,
            "processing_status": "state_analysis_failed"
        }
