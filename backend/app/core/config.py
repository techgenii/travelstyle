"""
Configuration settings for TravelStyle AI application.
Manages environment variables and application configuration.
"""

from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


def _load_env_file() -> None:
    """Load environment file from the backend directory."""
    config_dir = Path(__file__).parent.resolve()
    # Go up to the backend directory (assuming config.py is in backend/app/core/)
    backend_dir = config_dir.parent.parent
    env_path = backend_dir / ".env"

    print(f".env file exists: {env_path.exists()}")

    # Load .env from the backend directory
    load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TravelStyle AI"
    VERSION: str = "1.0.0"

    # External API Keys
    OPENAI_API_KEY: str = ""
    OPENAI_ORG_ID: str | None = None
    QLOO_API_KEY: str = ""
    OPENWEATHER_API_KEY: str = ""
    EXCHANGE_API_KEY: str = ""

    # Supabase Configuration
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # API URLs
    QLOO_BASE_URL: str = "https://hackathon.api.qloo.com/v2/"
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/"
    EXCHANGE_BASE_URL: str = "https://v6.exchangerate-api.com/v6/"

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }


# Load environment variables
_load_env_file()

# Create settings instance
settings = Settings()
