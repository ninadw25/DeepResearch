from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Loads application settings from environment variables.
    """
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    GROQ_API_KEY: str
    GOOGLE_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    TAVILY_API_KEY : Optional[str]
    
    LANGFUSE_PUBLIC_KEY : Optional[str]
    LANGFUSE_SECRET_KEY : Optional[str]
    LANGFUSE_HOST : Optional[str]
    
    # LLM_PROVIDER: str = "groq" 
    LLM_PROVIDER: str = "google" 
    # LLM_PROVIDER: str = "ollama"
    # LLM_PROVIDER: str = "openrouter" 

settings = Settings()