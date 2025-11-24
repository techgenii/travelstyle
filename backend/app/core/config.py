# This file is part of TravelSytle AI.
#
# Copyright (C) 2025  Trailyn Ventures, LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
    VISUALCROSSING_API_KEY: str = ""
    EXCHANGE_API_KEY: str = ""

    # Supabase Configuration
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # API URLs
    QLOO_BASE_URL: str = "https://hackathon.api.qloo.com/v2/"
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/"
    EXCHANGE_BASE_URL: str = "https://v6.exchangerate-api.com/v6/"
    VISUALCROSSING_BASE_URL: str = (
        "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
    )

    # Environment
    TS_ENVIRONMENT: str = "production"  # development, staging, production

    # Cookie settings
    COOKIE_SECURE: bool = True  # Set to False for local development
    COOKIE_SAME_SITE: str = (
        "None"  # Required for cross-origin cookie sending (requires secure=True)
    )

    # CORS Configuration
    CORS_ORIGINS: str = "*"  # Comma-separated list of allowed origins, or "*" for all
    # Example: "http://localhost:5173,https://yourdomain.com,https://bolt.new"

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",  # Ignore extra environment variables not defined in the model
    }


# Load environment variables
_load_env_file()

# Create settings instance
settings = Settings()
