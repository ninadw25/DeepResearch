"""
Model configuration handler for dynamic model selection.
"""
import os
from typing import Optional
from app.utils.config import settings

class ModelConfig:
    """Handles dynamic model configuration based on user selection."""
    
    @staticmethod
    def get_model_config(model_provider: str, user_api_key: Optional[str] = None):
        """
        Get model configuration for the specified provider.
        Uses user-provided API key if available, otherwise falls back to environment.
        """
        provider = model_provider.lower()
        
        if provider == "groq":
            api_key = user_api_key or settings.GROQ_API_KEY
            if not api_key:
                raise ValueError("Groq API key is required but not provided")
            return {
                "provider": "groq",
                "api_key": api_key,
                "model": "llama3-8b-8192"  # Default Groq model
            }
            
        elif provider == "google":
            api_key = user_api_key or settings.GOOGLE_API_KEY
            if not api_key:
                raise ValueError("Google API key is required but not provided")
            return {
                "provider": "google",
                "api_key": api_key,
                "model": "gemini-pro"  # Default Gemini model
            }
            
        elif provider == "ollama":
            # Ollama runs locally, no API key needed
            return {
                "provider": "ollama",
                "api_key": None,
                "model": "llama2"  # Default Ollama model
            }
            
        elif provider == "openrouter":
            api_key = user_api_key or settings.OPENROUTER_API_KEY
            if not api_key:
                raise ValueError("OpenRouter API key is required but not provided")
            return {
                "provider": "openrouter",
                "api_key": api_key,
                "model": "openrouter/auto"  # Default OpenRouter model
            }
        else:
            raise ValueError(f"Unsupported model provider: {provider}")
    
    @staticmethod
    def update_environment(model_config: dict):
        """
        Temporarily update environment variables for the current request.
        This allows the existing LangChain setup to work without major changes.
        """
        provider = model_config["provider"]
        api_key = model_config["api_key"]
        
        # Update environment for current process
        if provider == "groq" and api_key:
            os.environ["GROQ_API_KEY"] = api_key
        elif provider == "google" and api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
        elif provider == "openrouter" and api_key:
            os.environ["OPENROUTER_API_KEY"] = api_key
        # Ollama doesn't need API key updates
        
        # Update the LLM_PROVIDER setting
        os.environ["LLM_PROVIDER"] = provider
