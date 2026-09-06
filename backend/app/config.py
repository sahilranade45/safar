"""
Safar — Centralized Configuration

Loads settings from environment variables / .env file.
Validates required values at startup.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env from project root (safar/.env)
_project_root = Path(__file__).resolve().parent.parent.parent
_env_path = _project_root / ".env"
load_dotenv(dotenv_path=_env_path)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- Required ---
    gemini_api_key: str = ""

    # --- Optional with defaults ---
    gemini_model: str = "gemini-2.0-flash"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:5173"

    # --- Timeouts ---
    llm_timeout_seconds: int = 60
    weather_api_timeout_seconds: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def is_api_key_configured(self) -> bool:
        """Check if a real API key is set (not placeholder)."""
        return bool(
            self.gemini_api_key
            and self.gemini_api_key != "your_api_key_here"
        )


# Singleton settings instance
settings = Settings()
