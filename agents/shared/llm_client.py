"""
Ollama LLM client wrapper
Provides a consistent interface to local Ollama inference for all agents.
"""

import os
from langchain_ollama import ChatOllama

OLLAMA_HOST  = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "phi4-mini")


def get_llm(model: str = None, temperature: float = 0.1) -> ChatOllama:
    """
    Returns a ChatOllama instance.
    Low temperature default (0.1) is intentional for safety-critical
    automotive config review — we want deterministic, conservative output.
    """
    return ChatOllama(
        base_url=OLLAMA_HOST,
        model=model or DEFAULT_MODEL,
        temperature=temperature,
    )
