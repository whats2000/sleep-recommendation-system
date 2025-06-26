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
        Create CONCISE, optimized prompts for the MusicGen model based on integrated requirements.

        IMPORTANT: Keep prompts under 150 characters for optimal model performance.

        MusicGen prompt structure should include:
        - Genre and style (e.g., "ambient", "classical")
        - Tempo (e.g., "slow", "60 BPM")
        - Mood (e.g., "calming", "peaceful")
        - Key instruments (max 2-3, e.g., "piano", "strings")
        - Brief audio characteristics (e.g., "soft", "warm")

        Focus on sleep-conducive music generation. Be concise and specific."""
        
        final_specs = integrated_requirements.final_specifications
        user_prompt = f"""
        Integrated Requirements:
        - Genre: {final_specs.get('genre', 'ambient')}
        - Tempo: {final_specs.get('tempo', 'slow')}
        - Mood: {final_specs.get('mood', 'calming')}
        - Instruments: {final_specs.get('instruments', ['piano'])}
        - Priority: {', '.join(integrated_requirements.priority_ranking)}

        Generate a CONCISE MusicGen prompt (under 150 characters) in the following format:
        MusicGen Prompt: [concise prompt for music generation - keep it short and focused]
        Components: genre=[genre], tempo=[tempo], mood=[mood], instruments=[instruments]
        Parameters: duration=[seconds], sample_rate=[rate], guidance_scale=[scale]

        Example good prompt: "Ambient piano, slow 60 BPM, peaceful, soft dynamics, sleep-inducing"
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
            
            # Create a concise prompt for mock response
            instruments_str = ', '.join(instruments[:2])  # Limit to 2 instruments for brevity
            analysis_text = f"""
            MusicGen Prompt: {genre} {instruments_str}, {tempo}, {mood}, soft, sleep-inducing
            Components: genre={genre}, tempo={tempo}, mood={mood}, instruments={','.join(instruments)}
            Parameters: duration=15, sample_rate=32000, guidance_scale=3.0
            """
        
        # Parse the response
        lines = str(analysis_text).strip().split('\n')
        musicgen_prompt = ""
        prompt_components = {}
        generation_parameters = {
            "duration": 15,  # Shorter duration to prevent generation errors
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
                            key = key.strip()
                            value = value.strip()

                            # Handle numeric values with units (e.g., "30 seconds", "32000 Hz")
                            try:
                                # Extract just the number part
                                import re
                                numeric_match = re.search(r'(\d+(?:\.\d+)?)', value)
                                if numeric_match:
                                    generation_parameters[key] = float(numeric_match.group(1))
                                else:
                                    generation_parameters[key] = value
                            except:
                                generation_parameters[key] = value
                except:
                    pass
        
        # Fallback prompt generation if parsing failed
        if not musicgen_prompt:
            genre = final_specs.get('genre', 'ambient')
            tempo = final_specs.get('tempo', 'slow')
            mood = final_specs.get('mood', 'calming')
            instruments = final_specs.get('instruments', ['piano'])
            
            # Create concise fallback prompt
            instruments_str = ', '.join(instruments[:2])  # Limit to 2 instruments
            musicgen_prompt = f"{genre} {instruments_str}, {tempo}, {mood}, soft, peaceful"
            prompt_components = {
                "genre": genre,
                "tempo": tempo,
                "mood": mood,
                "instruments": ','.join(instruments)
            }
        
        # Validate and truncate prompt if too long
        if len(musicgen_prompt) > 200:
            print(f"Warning: Generated prompt is {len(musicgen_prompt)} characters, truncating...")
            # Truncate at word boundary
            truncated = musicgen_prompt[:200]
            last_space = truncated.rfind(' ')
            if last_space > 160:  # If we can find a space in reasonable range
                musicgen_prompt = truncated[:last_space]
            else:
                musicgen_prompt = truncated
            print(f"Truncated prompt: {musicgen_prompt}")

        # Safely convert duration to integer
        try:
            duration_value = generation_parameters.get("duration", 30)
            if isinstance(duration_value, str):
                # Extract number from string like "30 seconds"
                import re
                numeric_match = re.search(r'(\d+)', str(duration_value))
                expected_duration = int(numeric_match.group(1)) if numeric_match else 30
            else:
                expected_duration = int(float(duration_value))
        except:
            expected_duration = 30

        generated_prompt = GeneratedPrompt(
            musicgen_prompt=musicgen_prompt,
            prompt_components=prompt_components,
            generation_parameters=generation_parameters,
            expected_duration=expected_duration
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
