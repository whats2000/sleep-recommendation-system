"""
Shared LLM utilities for agent nodes.
"""

import os
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_llm():
    """Initialize and return the LLM for agent nodes."""
    # Try to use OpenAI first, fallback to other models if needed
    try:
        openai_key = os.getenv("OPENAI_API_KEY")
        google_key = os.getenv("GOOGLE_API_KEY")

        if openai_key and openai_key != "your_openai_api_key_here":
            print("Initializing OpenAI LLM...")
            return init_chat_model("openai:gpt-4o-mini")
        elif google_key and google_key != "your_google_api_key_here":
            print("Initializing Google Gemini LLM...")
            return init_chat_model("google_genai:gemini-2.0-flash")
        else:
            raise ValueError("No valid API key found for LLM initialization")
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        print("Running in mock mode - LLM responses will be simulated")
        # For development, we can use a mock LLM
        return None


# Global LLM instance
llm = get_llm()
