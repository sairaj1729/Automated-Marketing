from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # MongoDB Configuration
    MONGODB_URL: str
    MONGODB_DATABASE: str = "linkedin_marketing"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # LinkedIn API
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    LINKEDIN_REDIRECT_URI: Optional[str] = None
    
    # AI Service
    AI_API_KEY: Optional[str] = None
    AI_MODEL: str = "gpt-4"
    
    # Alternative AI Services
    OPENROUTER_API_KEY: Optional[str] = None
    TOGETHER_API_KEY: Optional[str] = None
    HUGGING_FACE_API_KEY: Optional[str] = None
    
    # Email Configuration
    EMAIL_HOST: Optional[str] = None
    EMAIL_PORT: int = 587
    EMAIL_USERNAME: Optional[str] = None
    EMAIL_PASSWORD: Optional[str] = None
    EMAIL_USE_TLS: bool = True
    DEFAULT_FROM_EMAIL: str = "noreply@yourdomain.com"
    
    # Frontend URL for CORS
    FRONTEND_URL: str = "http://localhost:8080"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from environment variables

settings = Settings()