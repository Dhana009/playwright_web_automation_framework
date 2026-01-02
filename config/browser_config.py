"""
Browser Configuration

This module provides browser-specific configuration for Playwright.
Supports headless/headed mode, viewport settings, and browser selection.

Author: Senior SDET
Date: 2026-01-02
"""

import os
from typing import Dict, Any, Final


class BrowserConfig:
    """
    Browser configuration for Playwright.
    
    All settings can be overridden via environment variables.
    """
    
    # Browser Settings
    HEADLESS: Final[bool] = os.getenv("HEADLESS", "true").lower() == "true"
    BROWSER_TYPE: Final[str] = os.getenv("BROWSER", "chromium")
    SLOW_MO: Final[int] = int(os.getenv("SLOW_MO", "0"))  # Milliseconds
    
    # Viewport Configurations
    VIEWPORT: Final[Dict[str, Dict[str, int]]] = {
        "desktop": {"width": 1920, "height": 1080},
        "mobile": {"width": 375, "height": 667},
        "tablet": {"width": 768, "height": 1024}
    }
    
    DEVICE: Final[str] = os.getenv("DEVICE", "desktop")
    
    # Video Recording (CI/CD only)
    RECORD_VIDEO: Final[bool] = os.getenv("CI", "false").lower() == "true"
    VIDEO_SIZE: Final[Dict[str, int]] = {"width": 1920, "height": 1080}
    
    @classmethod
    def get_launch_options(cls) -> Dict[str, Any]:
        """
        Get browser launch options for Playwright.
        
        Returns:
            Dictionary of launch options
            
        Example:
            >>> BrowserConfig.get_launch_options()
            {'headless': True, 'slow_mo': 0}
        """
        return {
            "headless": cls.HEADLESS,
            "slow_mo": cls.SLOW_MO,
        }
    
    @classmethod
    def get_context_options(cls, video_dir: str = None) -> Dict[str, Any]:
        """
        Get browser context options for Playwright.
        
        Args:
            video_dir: Directory to save videos (optional)
            
        Returns:
            Dictionary of context options
            
        Example:
            >>> BrowserConfig.get_context_options()
            {'viewport': {'width': 1920, 'height': 1080}}
        """
        options = {
            "viewport": cls.VIEWPORT[cls.DEVICE],
        }
        
        # Add video recording for CI/CD
        if cls.RECORD_VIDEO and video_dir:
            options["record_video_dir"] = video_dir
            options["record_video_size"] = cls.VIDEO_SIZE
        
        return options


# Export config instance
browser_config = BrowserConfig()
