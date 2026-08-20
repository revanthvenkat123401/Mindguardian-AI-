"""Configuration management for MindGuardian AI Backend"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Application
    APP_NAME: str = "MindGuardian AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://mindguardian:password@localhost:5432/mindguardian_db"
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_EXPIRE: int = 3600  # 1 hour
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # JWT
    JWT_SECRET_KEY: str = "your-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:8000",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000",
        "*"  # Allow all origins for development
    ]
    
    # LLM
    LLM_ENDPOINT: str = "http://localhost:11434"
    LLM_MODEL: str = "llama2"
    LLM_TIMEOUT: int = 60
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    REPORT_DIR: str = "./reports"
    
    # Data Retention
    SESSION_RETENTION_DAYS: int = 90  # Keep sessions for 90 days
    AUTO_DELETE_EXPIRED: bool = True
    
    # Privacy
    ENCRYPT_SENSITIVE_DATA: bool = True
    DATA_ANONYMIZATION: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
