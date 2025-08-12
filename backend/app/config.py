from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Loads application settings from environment variables.
    """
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # --- API Keys ---
    # Groq is now the required provider
    GROQ_API_KEY: str
    # Google is now the optional provider
    GOOGLE_API_KEY: Optional[str] = None
    # OpenRouter API key
    OPENROUTER_API_KEY: Optional[str] = None
    TAVILY_API_KEY : Optional[str]
    

    # --- LLM Provider Switch ---
    # Default to "groq" if not specified in .env
    # LLM_PROVIDER: str = "groq" 
    # LLM_PROVIDER: str = "google" 
    LLM_PROVIDER: str = "ollama"
    # LLM_PROVIDER: str = "openrouter" 

# Create a single instance of the settings
settings = Settings()