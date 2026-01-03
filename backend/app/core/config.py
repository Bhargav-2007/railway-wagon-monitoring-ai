"""
Application configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Railway Wagon Monitoring System"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI-powered motion blur mitigation for high-speed wagon monitoring"
    
    # Security
    SECRET_KEY: str = "railway-secret-key-dev-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database - SQLite by default
    DATABASE_URL: str = "sqlite:///./railway_monitoring.db"
    
    # Redis (optional)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]
    
    # File Storage
    UPLOAD_DIR: str = "data/uploads"
    PROCESSED_DIR: str = "data/processed"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # AI Pipeline
    AI_DEVICE: str = "cpu"
    ENABLE_BLUR_DETECTION: bool = True
    ENABLE_DEBLURRING: bool = True
    ENABLE_LOW_LIGHT: bool = True
    ENABLE_OCR: bool = True
    ENABLE_DAMAGE_DETECTION: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # IMPORTANT: Ignore extra fields from .env


# Global settings instance
settings = Settings()
