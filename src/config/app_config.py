from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os
from pathlib import Path
import json
import logging
from enum import Enum

class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class AppConfig(BaseSettings):
    """Application configuration loaded from environment variables and secrets."""
    
    # Environment
    ENVIRONMENT: EnvironmentType = EnvironmentType.DEVELOPMENT
    DEBUG: bool = True
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Multi Use AI Agent System"
    VERSION: str = "0.1.0"
    
    # Security - These should be loaded from secure storage in production
    API_KEY: Optional[str] = None
    SECRET_KEY: Optional[str] = None
    
    # Model Configuration - These should be loaded from secure storage in production
    MODEL_NAME: str = "gpt-3.5-turbo"
    OPENAI_API_KEY: Optional[str] = None
    
    # Vector Database - These should be loaded from secure storage in production
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: str = "us-west1-gcp"
    PINECONE_INDEX_NAME: str = "learning-agent-index"
    
    # Caching
    REDIS_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

    def _load_secrets_from_vault(self) -> None:
        """
        Load secrets from a secure vault (e.g., HashiCorp Vault, AWS Secrets Manager).
        This is a placeholder for actual secrets management implementation.
        """
        if self.ENVIRONMENT == EnvironmentType.PRODUCTION:
            # TODO: Implement actual secrets loading from secure storage
            # Example: Load from AWS Secrets Manager
            # secrets = aws_secrets_manager.get_secrets()
            # self.API_KEY = secrets["API_KEY"]
            logging.warning("Production environment detected but secure secrets loading not implemented!")
            return

        # For development, load from local secrets file (not for production use)
        secrets_file = Path(".secrets.json")
        if secrets_file.exists():
            with open(secrets_file) as f:
                secrets = json.load(f)
                for key, value in secrets.items():
                    if hasattr(self, key):
                        setattr(self, key, value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._load_secrets_from_vault()
        
        # Validate required secrets
        if self.ENVIRONMENT == EnvironmentType.PRODUCTION:
            required_secrets = ["API_KEY", "SECRET_KEY", "OPENAI_API_KEY", "PINECONE_API_KEY"]
            missing_secrets = [secret for secret in required_secrets if not getattr(self, secret)]
            if missing_secrets:
                raise ValueError(f"Missing required secrets in production: {missing_secrets}")

@lru_cache()
def get_app_config() -> AppConfig:
    """Get cached application configuration instance."""
    return AppConfig() 