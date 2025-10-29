from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "NFA Automation System"
    APP_VERSION: str = "1.0.0"
    
    # Database
    MONGO_URL: str
    DB_NAME: str = "nfa_automation"
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Email
    EMAIL_HOST: str
    EMAIL_PORT: int = 587
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: str
    EMAIL_FROM_NAME: str = "HCIL NFA System"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS
    CORS_ORIGINS: str = "*"
    
    # Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    # SuperAdmin
    SUPERADMIN_USERNAME: str
    SUPERADMIN_PASSWORD: str
    SUPERADMIN_EMAIL: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
