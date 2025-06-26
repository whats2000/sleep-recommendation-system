"""
Shared LLM utilities for agent nodes.
"""

import os
from langchain.chat_models import init_chat_model


def get_llm():
    """Initialize and return the LLM for agent nodes."""
    # Try to use OpenAI first, fallback to other models if needed
    try:
        if os.getenv("OPENAI_API_KEY"):
            return init_chat_model("openai:gpt-4o-mini")
        elif os.getenv("GOOGLE_API_KEY"):
            return init_chat_model("google_genai:gemini-2.0-flash")
        else:
            raise ValueError("No API key found for LLM initialization")
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        # For development, we can use a mock LLM
        return None


# Global LLM instance
llm = get_llm()
