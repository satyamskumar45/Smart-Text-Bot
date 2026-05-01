"""Backend application settings loaded from environment variables."""

import json
import os
import platform
from pathlib import Path

from dotenv import load_dotenv

from core.exceptions import ConfigurationError

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def load_supported_languages():
    languages_path = Path(__file__).parent / "languages.json"
    try:
        if not languages_path.exists():
            raise FileNotFoundError(f"languages.json not found at {languages_path}")
        with open(languages_path, "r", encoding="utf-8") as f:
            languages_list = json.load(f)
        return {entry["code"].lower(): entry["name"] for entry in languages_list}
    except Exception as exc:
        raise ConfigurationError(f"Unable to load supported languages: {exc}")


class Settings:
    TESSERACT_PATH = os.getenv("TESSERACT_PATH", "").strip()
    TESSERACT_WINDOWS_FALLBACK = os.getenv(
        "TESSERACT_WINDOWS_FALLBACK",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    ).strip()

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRES_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRES_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRES_DAYS", "7"))
    REMEMBER_ME_EXPIRES_DAYS = int(os.getenv("REMEMBER_ME_EXPIRES_DAYS", "30"))
    JWT_COOKIE_NAME = os.getenv("JWT_COOKIE_NAME", "smarttextbot_refresh")
    JWT_COOKIE_SECURE = os.getenv("FLASK_ENV", "development") == "production"
    GUEST_SESSION_LIFETIME_HOURS = int(os.getenv("GUEST_SESSION_LIFETIME_HOURS", "24"))

    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "True").lower() in ("1", "true", "yes")
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "90"))

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    SUPPORTED_LANGUAGES = load_supported_languages()

    @classmethod
    def get_language_name(cls, code: str) -> str:
        return cls.SUPPORTED_LANGUAGES.get(code.lower(), code.upper())

    @classmethod
    def is_windows(cls) -> bool:
        return platform.system().lower() == "windows"
