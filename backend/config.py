"""
Configuration management for KashRock Data Stream service.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Service configuration
    app_name: str = "KashRock Data Stream"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    
    # Database configuration
    database_url: str = Field(
        default="postgresql+asyncpg://user:pass@localhost/kashrock_stream",
        env="DATABASE_URL"
    )
    
    # Redis configuration
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    
    # External APIs
    odds_api_key: Optional[str] = Field(default=None, env="ODDS_API_KEY")
    espn_api_key: Optional[str] = Field(default=None, env="ESPN_API_KEY")
    
    # Streaming configuration
    stream_batch_size: int = Field(default=100, env="STREAM_BATCH_SIZE")
    stream_interval: float = Field(default=1.0, env="STREAM_INTERVAL")
    max_connections: int = Field(default=1000, env="MAX_CONNECTIONS")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="json",
        env="LOG_FORMAT"
    )
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-here",
        env="SECRET_KEY"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    # Google OAuth client ID for verifying Google ID tokens
    google_client_id: Optional[str] = Field(
        default=None,
        env="GOOGLE_CLIENT_ID"
    )
    
    # Monitoring
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    # Feature flags
    enable_betting_features: bool = Field(default=False, env="ENABLE_BETTING_FEATURES")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment."""
    global _settings
    _settings = Settings()
    return _settings
