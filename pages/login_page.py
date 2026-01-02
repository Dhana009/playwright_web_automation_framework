"""
Login Page Object

This module provides the page object for the login page.
Handles login functionality and related interactions.

Author: Senior SDET
Date: 2026-01-02
"""

from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logger import logger


class LoginPage(BasePage):
    """
    Login page object.
    
    Provides methods for login functionality.
    
    Example:
        >>> login_page = LoginPage(page)
        >>> login_page.login("admin1@test.com", "Admin@123")
    """
    
    # Locators (using data-testid for stability)
    EMAIL_INPUT = '[data-testid="login-email"]'
    PASSWORD_INPUT = '[data-testid="login-password"]'
    SUBMIT_BUTTON = '[data-testid="login-submit"]'
    ERROR_MESSAGE = '[data-testid="login-error"]'
    
    def __init__(self, page: Page):
        """Initialize login page."""
        super().__init__(page)
    
    def navigate_to_login(self) -> None:
        """
        Navigate to login page.
        
        Example:
            >>> login_page.navigate_to_login()
        """
        self.navigate("/login")
        logger.info("Navigated to login page")
    
    def login(self, email: str, password: str) -> None:
        """
        Perform login.
        
        Args:
            email: User email
            password: User password
            
        Example:
            >>> login_page.login("admin1@test.com", "Admin@123")
        """
        logger.info(f"Logging in as {email}")
        
        # Fill credentials
        self.fill_text(self.EMAIL_INPUT, email)
        self.fill_text(self.PASSWORD_INPUT, password)
        
        # Submit
        self.click(self.SUBMIT_BUTTON)
        
        # Wait for navigation to dashboard
        self.wait_for_url("**/dashboard")
        
        logger.info(f"Successfully logged in as {email}")
    
    def get_error_message(self) -> str:
        """
        Get login error message.
        
        Returns:
            Error message text
            
        Example:
            >>> error = login_page.get_error_message()
        """
        if self.is_visible(self.ERROR_MESSAGE):
            return self.get_text(self.ERROR_MESSAGE)
        return ""
    
    def is_error_displayed(self) -> bool:
        """
        Check if error message is displayed.
        
        Returns:
            True if error is visible
            
        Example:
            >>> if login_page.is_error_displayed():
            ...     print("Login failed")
        """
        return self.is_visible(self.ERROR_MESSAGE)
