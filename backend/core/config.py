"""
Orca Job Orchestrator Configuration
Provides centralized configuration management with environment variable support.
"""

import os
from typing import Optional
from pydantic import BaseModel
from cryptography.fernet import Fernet


class Settings(BaseModel):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = "postgresql://postgres:postgres@localhost/orca"
    database_echo: bool = False
    
    # API Configuration
    api_title: str = "Orca Job Orchestrator"
    api_description: str = "A powerful job orchestrator for multi-system command execution"
    api_version: str = "1.0.0"
    debug: bool = False
    
    # Security Configuration
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    encryption_key: Optional[str] = None
    
    # CORS Configuration
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Job Execution Configuration
    max_concurrent_jobs: int = 10
    job_timeout_seconds: int = 300
    connection_timeout_seconds: int = 30
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_encryption_key() -> bytes:
    """
    Get or generate encryption key for password encryption.
    In production, this should be stored securely (e.g., Azure Key Vault).
    """
    if settings.encryption_key:
        return settings.encryption_key.encode()
    
    # Generate a new key if none exists
    key = Fernet.generate_key()
    print(f"Generated new encryption key: {key.decode()}")
    print("Store this key securely and set ENCRYPTION_KEY environment variable")
    return key


def encrypt_password(password: str) -> str:
    """Encrypt a password using Fernet symmetric encryption."""
    f = Fernet(get_encryption_key())
    return f.encrypt(password.encode()).decode()


def decrypt_password(encrypted_password: str) -> str:
    """Decrypt a password using Fernet symmetric encryption."""
    # Remove 'encrypted:' prefix if present
    if encrypted_password.startswith('encrypted:'):
        encrypted_password = encrypted_password[10:]
    
    f = Fernet(get_encryption_key())
    return f.decrypt(encrypted_password.encode()).decode()