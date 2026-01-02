"""
Environment Settings Configuration

This module provides centralized configuration for the web automation framework.
All environment-specific settings are managed here.

Author: Senior SDET
Date: 2026-01-02
"""

import os
from typing import Final


class Settings:
    """
    Application settings and configuration.
    
    All settings can be overridden via environment variables.
    Defaults are provided for production environment.
    """
    
    # Application URLs
    BASE_URL: Final[str] = os.getenv(
        "BASE_URL", 
        "https://testing-box.vercel.app"
    )
    
    # API URL (can be different from BASE_URL)
    API_BASE_URL: Final[str] = os.getenv(
        "API_BASE_URL",
        "https://testing-box.onrender.com/api/v1"
    )
    
    # Timeouts (in milliseconds)
    DEFAULT_TIMEOUT: Final[int] = 30000  # 30 seconds
    NAVIGATION_TIMEOUT: Final[int] = 30000  # 30 seconds
    API_TIMEOUT: Final[int] = 10  # 10 seconds (for requests library)
    
    # Test Execution
    NUM_WORKERS: Final[int] = int(os.getenv("PYTEST_WORKERS", "8"))
    USERS_PER_ROLE: Final[int] = NUM_WORKERS
    
    # Environment Detection
    IS_CI: Final[bool] = os.getenv("CI", "false").lower() == "true"
    IS_LOCAL: Final[bool] = not IS_CI
    
    # Directories
    LOGS_DIR: Final[str] = "logs"
    SCREENSHOTS_DIR: Final[str] = "screenshots"
    VIDEOS_DIR: Final[str] = "videos"
    REPORTS_DIR: Final[str] = "reports"
    AUTH_DIR: Final[str] = ".auth"
    
    # Seed Data
    SEED_DATA_FILE: Final[str] = "seed_data_ids.json"
    SEED_DATA_PREFIX: Final[str] = "SEED_"
    
    # User Credentials
    DEFAULT_PASSWORD: Final[str] = "Admin@123"
    
    @classmethod
    def get_user_email(cls, role: str, number: int) -> str:
        """
        Generate user email based on role and number.
        
        Args:
            role: User role (ADMIN, EDITOR, VIEWER)
            number: User number (1-8)
            
        Returns:
            User email address
            
        Example:
            >>> Settings.get_user_email("ADMIN", 1)
            'admin1@test.com'
        """
        return f"{role.lower()}{number}@test.com"
    
    @classmethod
    def get_auth_file_path(cls, user_email: str) -> str:
        """
        Get auth state file path for a user.
        
        Args:
            user_email: User email address
            
        Returns:
            Path to auth state file
            
        Example:
            >>> Settings.get_auth_file_path("admin1@test.com")
            '.auth/auth_admin1_test_com.json'
        """
        safe_email = user_email.replace("@", "_").replace(".", "_")
        return f"{cls.AUTH_DIR}/auth_{safe_email}.json"


# Export settings instance
settings = Settings()
