"""
Application Configuration

Centralized configuration management using Pydantic Settings.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Application
    app_name: str = "VendorPay AI"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/vendorpay_ai"
    database_echo: bool = False
    
    # Supabase
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]
    cors_origins: str = '["http://localhost:3000", "http://localhost:8000"]'
    cors_allow_credentials: bool = True
    cors_allow_methods: str = '["*"]'
    cors_allow_headers: str = '["*"]'
    
    # File Processing
    max_file_size_mb: int = 50
    allowed_file_types: str = "pdf,csv,xlsx,xls,jpg,jpeg,png,tiff"
    
    # OCR Configuration
    tesseract_cmd: str = "tesseract"
    tesseract_config: str = "--oem 3 --psm 6"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    log_level: str = "INFO"
    
    # Testing
    testing: bool = False
    
    # Email Configuration
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # External APIs
    plaid_client_id: Optional[str] = None
    plaid_secret: Optional[str] = None
    plaid_environment: str = "sandbox"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings based on environment.
    
    Returns:
        Settings: Application configuration
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()
    return Settings()


# Global settings instance
settings = get_settings()