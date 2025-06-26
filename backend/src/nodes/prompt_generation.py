"""
Prompt Generation Agent for the LangGraph recommendation pipeline.
"""

import time
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

from src.state import RecommendationState, GeneratedPrompt
from src.nodes.llm_utils import llm


def prompt_generation_agent(state: RecommendationState) -> Dict[str, Any]:
    """
    Prompt Generation Agent - Generates optimized MusicGen prompts.
    
    Input: integrated_requirements
    Output: structured MusicGen prompt, generation parameters
    """
    start_time = time.time()
    
    try:
        integrated_requirements = state.get("integrated_requirements")
        if not integrated_requirements:
            raise ValueError("No integrated requirements available for prompt generation")
        
        system_prompt = """You are a MusicGen prompt engineering specialist.
        Create optimized prompts for the MusicGen model based on integrated requirements.
        
        MusicGen prompt structure should include:
        - Genre and style descriptors
        - Tempo and rhythm specifications
        - Mood and emotional descriptors
        - Instrument specifications
        - Audio characteristics (frequency, dynamics)
        - Duration specifications
        
        Focus on sleep-conducive music generation."""
        
        final_specs = integrated_requirements.final_specifications
        user_prompt = f"""
        Integrated Requirements:
        - Genre: {final_specs.get('genre', 'ambient')}
        - Tempo: {final_specs.get('tempo', 'slow')}
        - Mood: {final_specs.get('mood', 'calming')}
        - Instruments: {final_specs.get('instruments', ['piano'])}
        - Priority: {', '.join(integrated_requirements.priority_ranking)}
        
        Generate a MusicGen prompt in the following format:
        MusicGen Prompt: [detailed prompt for music generation]
        Components: genre=[genre], tempo=[tempo], mood=[mood], instruments=[instruments]
        Parameters: duration=[seconds], sample_rate=[rate], guidance_scale=[scale]
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
            genre = final_specs.get('genre', 'ambient')
            tempo = final_specs.get('tempo', 'slow')
            mood = final_specs.get('mood', 'calming')
            instruments = final_specs.get('instruments', ['piano'])
            
            analysis_text = f"""
            MusicGen Prompt: {genre} music, {tempo} tempo, {mood} atmosphere, featuring {', '.join(instruments)}, soft dynamics, sleep-inducing, peaceful, 432Hz tuning, gentle fade-in
            Components: genre={genre}, tempo={tempo}, mood={mood}, instruments={','.join(instruments)}
            Parameters: duration=30, sample_rate=32000, guidance_scale=3.0
            """
        
        # Parse the response
        lines = str(analysis_text).strip().split('\n')
        musicgen_prompt = ""
        prompt_components = {}
        generation_parameters = {
            "duration": 30,
            "sample_rate": 32000,
            "guidance_scale": 3.0
        }
        
        for line in lines:
            if "MusicGen Prompt:" in line:
                musicgen_prompt = line.split(":", 1)[1].strip()
            elif "Components:" in line:
                comp_text = line.split(":", 1)[1].strip()
                try:
                    # Parse components like "genre=ambient, tempo=slow"
                    for comp in comp_text.split(','):
                        if '=' in comp:
                            key, value = comp.split('=', 1)
                            prompt_components[key.strip()] = value.strip()
                except:
                    pass
            elif "Parameters:" in line:
                param_text = line.split(":", 1)[1].strip()
                try:
                    # Parse parameters like "duration=30, sample_rate=32000"
                    for param in param_text.split(','):
                        if '=' in param:
                            key, value = param.split('=', 1)
                            try:
                                generation_parameters[key.strip()] = float(value.strip())
                            except:
                                generation_parameters[key.strip()] = value.strip()
                except:
                    pass
        
        # Fallback prompt generation if parsing failed
        if not musicgen_prompt:
            genre = final_specs.get('genre', 'ambient')
            tempo = final_specs.get('tempo', 'slow')
            mood = final_specs.get('mood', 'calming')
            instruments = final_specs.get('instruments', ['piano'])
            
            musicgen_prompt = f"{genre} music, {tempo} tempo, {mood} atmosphere, featuring {', '.join(instruments)}, soft dynamics, sleep-inducing, peaceful"
            prompt_components = {
                "genre": genre,
                "tempo": tempo,
                "mood": mood,
                "instruments": ','.join(instruments)
            }
        
        generated_prompt = GeneratedPrompt(
            musicgen_prompt=musicgen_prompt,
            prompt_components=prompt_components,
            generation_parameters=generation_parameters,
            expected_duration=int(generation_parameters.get("duration", 30))
        )
        
        processing_time = state.get("processing_time", {})
        processing_time["prompt_generation"] = time.time() - start_time
        
        return {
            "generated_prompt": generated_prompt,
            "processing_status": "prompt_generation_complete",
            "processing_time": processing_time
        }
        
    except Exception as e:
        error_messages = state.get("error_messages", [])
        error_messages.append(f"Prompt generation error: {str(e)}")
        return {
            "error_messages": error_messages,
            "processing_status": "prompt_generation_failed"
        }
