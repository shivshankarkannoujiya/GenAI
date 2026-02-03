from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    api_v1_prefix: str = "/api/v1"
    project_name: str = "LeetCode Test Case Generator"
    version: str = "1.0.0"
    description: str = "AI-powered test case generation for coding problems"

    environment: str = "development"
    debug: bool = True

    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 2000

    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # Rate Limiting (for future implementation)
    rate_limit_enabled: bool = False
    rate_limit_requests: int = 100
    rate_limit_period: int = 3600  # 1 hour in seconds

    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    # Test Case Generation Limits
    max_test_cases_per_request: int = 20
    min_test_cases_per_request: int = 1
    default_test_cases: int = 5

    # Request timeouts
    openai_timeout: int = 30  # seconds

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    Returns:
        Settings instance
    """
    return Settings()
