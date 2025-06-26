"""
Main LangGraph recommendation pipeline implementation.
"""

import uuid
from typing import Dict, Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.config import RunnableConfig

from src.nodes import (
    state_analysis_agent,
    emotion_recognition_agent,
    preference_analysis_agent,
    requirement_integration_agent,
    prompt_generation_agent
)
from src.state import RecommendationState, FormData, StateAnalysis, EmotionAnalysis, PreferenceAnalysis


class RecommendationPipeline:
    """
    Main LangGraph pipeline for the music recommendation system.
    
    Implements the multi-agent workflow as described in the documentation:
    1. State Analysis Agent
    2. Emotion Recognition Agent  
    3. Preference Analysis Agent
    4. Requirement Integration Agent
    5. Prompt Generation Agent
    """
    
    def __init__(self, enable_checkpointing: bool = True):
        """Initialize the recommendation pipeline."""
        self.enable_checkpointing = enable_checkpointing
        self.memory = MemorySaver() if enable_checkpointing else None
        self.graph = self._build_graph()
    
    def _build_graph(self) -> CompiledStateGraph:
        """Build the LangGraph workflow."""
        # Create the state graph
        graph_builder = StateGraph(RecommendationState)
        
        # Add all agent nodes (using different names to avoid state key conflicts)
        graph_builder.add_node("analyze_state", state_analysis_agent)
        graph_builder.add_node("recognize_emotion", emotion_recognition_agent)
        graph_builder.add_node("analyze_preferences", preference_analysis_agent)
        graph_builder.add_node("integrate_requirements", requirement_integration_agent)
        graph_builder.add_node("generate_prompt", prompt_generation_agent)

        # Set entry point to state analysis
        graph_builder.add_edge(START, "analyze_state")

        # Add conditional edges for parallel processing of the first three agents
        graph_builder.add_conditional_edges(
            "analyze_state",
            self._route_after_state_analysis,
            {
                "recognize_emotion": "recognize_emotion",
                "analyze_preferences": "analyze_preferences"
            }
        )

        # Both emotion and preference analysis lead to integration
        graph_builder.add_edge("recognize_emotion", "integrate_requirements")
        graph_builder.add_edge("analyze_preferences", "integrate_requirements")

        # Integration leads to prompt generation
        graph_builder.add_edge("integrate_requirements", "generate_prompt")

        # Prompt generation leads to end
        graph_builder.add_edge("generate_prompt", END)
        
        # Compile the graph
        if self.enable_checkpointing and self.memory:
            return graph_builder.compile(checkpointer=self.memory)
        else:
            return graph_builder.compile()

    @staticmethod
    def _route_after_state_analysis(state: RecommendationState) -> str:
        """
        Route to the next agents after state analysis.
        For simplicity, we'll process emotion and preference analysis in sequence.
        """
        # Check if state analysis completed successfully
        if state.get("processing_status") == "state_analysis_complete":
            return "recognize_emotion"
        else:
            # If state analysis failed, we could handle error routing here
            return "recognize_emotion"  # Continue anyway for robustness
    
    def process_form_data(self, form_data_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user form data through the recommendation pipeline.
        
        Args:
            form_data_dict: Dictionary containing form data
            
        Returns:
            Dictionary containing the final recommendation state
        """
        session_id = str(uuid.uuid4())

        try:
            # Create FormData object
            form_data = FormData(**form_data_dict)
            
            # Create the initial state
            initial_state: RecommendationState = {
                "form_data": form_data,
                "state_analysis": None,
                "emotion_analysis": None,
                "preference_analysis": None,
                "integrated_requirements": None,
                "generated_prompt": None,
                "reference_audio_path": None,
                "audio_embedding": None,
                "similar_tracks": None,
                "recommendations": None,
                "session_id": session_id,
                "processing_status": "initialized",
                "error_messages": [],
                "processing_time": {}
            }
            
            # Configure for checkpointing if enabled
            config = RunnableConfig(
                configurable={"thread_id": session_id}
            ) if self.enable_checkpointing else None
            
            # Run the pipeline
            if config:
                final_state = self.graph.invoke(initial_state, config)
            else:
                final_state = self.graph.invoke(initial_state)
            
            return self._format_response(final_state)
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Pipeline processing error: {str(e)}",
                "session_id": session_id if 'session_id' in locals() else None
            }

    @staticmethod
    def _format_response(final_state: RecommendationState) -> Dict[str, Any]:
        """Format the final state into a response."""
        try:
            success = final_state.get("processing_status") == "prompt_generation_complete"
            
            response = {
                "success": success,
                "session_id": final_state.get("session_id"),
                "processing_status": final_state.get("processing_status"),
                "processing_time": final_state.get("processing_time", {}),
                "error_messages": final_state.get("error_messages", [])
            }
            
            if success and final_state.get("generated_prompt"):
                generated_prompt = final_state["generated_prompt"]
                response["generated_prompt"] = {
                    "musicgen_prompt": generated_prompt.musicgen_prompt,
                    "prompt_components": generated_prompt.prompt_components,
                    "generation_parameters": generated_prompt.generation_parameters,
                    "expected_duration": generated_prompt.expected_duration
                }
                
                # Include analysis results for debugging/transparency
                if final_state.get("state_analysis"):
                    response["state_analysis"] = StateAnalysis(
                        stress_assessment=final_state["state_analysis"].stress_assessment,
                        urgency_level=final_state["state_analysis"].urgency_level,
                        recommendations=final_state["state_analysis"].recommendations,
                        physical_state_summary= final_state["state_analysis"].physical_state_summary
                    ).model_dump()
                
                if final_state.get("emotion_analysis"):
                    response["emotion_analysis"] = EmotionAnalysis(
                        primary_emotion=final_state["emotion_analysis"].primary_emotion,
                        emotion_intensity=final_state["emotion_analysis"].emotion_intensity,
                        regulation_strategy=final_state["emotion_analysis"].regulation_strategy,
                        target_mood=final_state["emotion_analysis"].target_mood,
                    ).model_dump()
                
                if final_state.get("preference_analysis"):
                    response["preference_analysis"] = PreferenceAnalysis(
                        preferred_genres=final_state["preference_analysis"].preferred_genres,
                        preferred_instruments=final_state["preference_analysis"].preferred_instruments,
                        tempo_preference=final_state["preference_analysis"].tempo_preference,
                        forbidden_elements=final_state["preference_analysis"].forbidden_elements,
                        preference_matrix=final_state["preference_analysis"].preference_matrix
                    ).model_dump()
            
            return response
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Response formatting error: {str(e)}",
                "session_id": final_state.get("session_id") if final_state else None
            }
    
    def get_pipeline_status(self, session_id: str) -> Dict[str, Any]:
        """Get the current status of a pipeline session."""
        if not self.enable_checkpointing or not self.memory:
            return {"error": "Checkpointing not enabled"}
        
        try:
            config = RunnableConfig(
                configurable={
                    "thread_id": session_id,
                }
            )
            snapshot = self.graph.get_state(config)
            
            return {
                "session_id": session_id,
                "current_state": snapshot.values if snapshot else None,
                "next_steps": snapshot.next if snapshot else None
            }
        except Exception as e:
            return {"error": f"Status retrieval error: {str(e)}"}
