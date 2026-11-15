"""
Configuration management for the Social Media Scraper.
Reads settings from environment variables or .env file with default fallbacks.
"""
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # Browser Automation Settings
    headless: bool = Field(default=True, description="Run browser in headless mode")
    request_timeout: int = Field(default=30, description="Timeout in seconds for page requests")
    min_delay: float = Field(default=2.0, description="Minimum human-like random delay in seconds")
    max_delay: float = Field(default=5.0, description="Maximum human-like random delay in seconds")
    
    # Path & Storage Settings
    output_dir: Path = Field(default=BASE_DIR / "data")
    sessions_dir: Path = Field(default=BASE_DIR / "sessions")
    default_output_format: str = Field(default="json", description="json, csv, or sqlite")
    
    # Optional Proxy
    proxy_url: str | None = Field(default=None, description="Optional HTTP/SOCKS proxy")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
