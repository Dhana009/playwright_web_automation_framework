"""
Authentication Tests

Tests for login, logout, and session management.

Author: Senior SDET
Date: 2026-01-02
"""

import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage
from config.settings import settings


@pytest.mark.smoke
@pytest.mark.role("ADMIN")
class TestAuthentication:
    """Authentication test suite."""
    
    def test_successful_login(self, page: Page):
        """
        Test successful login with valid credentials.
        
        Steps:
        1. Navigate to login page
        2. Enter valid credentials
        3. Click login button
        4. Verify redirect to dashboard
        """
        login_page = LoginPage(page)
        
        # Navigate to login
        login_page.navigate_to_login()
        
        # Login with valid credentials
        user_email = settings.get_user_email("ADMIN", 1)
        login_page.login(user_email, settings.DEFAULT_PASSWORD)
        
        # Verify redirect to dashboard
        assert "/dashboard" in page.url, "Should redirect to dashboard after login"
    
    def test_login_with_invalid_password(self, page: Page):
        """
        Test login fails with invalid password.
        
        Steps:
        1. Navigate to login page
        2. Enter valid email, invalid password
        3. Click login button
        4. Verify error message displayed
        """
        login_page = LoginPage(page)
        
        # Navigate to login
        login_page.navigate_to_login()
        
        # Fill credentials
        user_email = settings.get_user_email("ADMIN", 1)
        login_page.fill_text(login_page.EMAIL_INPUT, user_email)
        login_page.fill_text(login_page.PASSWORD_INPUT, "WrongPassword123")
        login_page.click(login_page.SUBMIT_BUTTON)
        
        # Verify error message
        assert login_page.is_error_displayed(), "Error message should be displayed"
        error_msg = login_page.get_error_message()
        assert len(error_msg) > 0, "Error message should not be empty"
    
    def test_login_with_empty_credentials(self, page: Page):
        """
        Test login fails with empty credentials.
        
        Steps:
        1. Navigate to login page
        2. Leave fields empty
        3. Click login button
        4. Verify validation errors
        """
        login_page = LoginPage(page)
        
        # Navigate to login
        login_page.navigate_to_login()
        
        # Click submit without filling
        login_page.click(login_page.SUBMIT_BUTTON)
        
        # Verify still on login page
        assert "/login" in page.url, "Should stay on login page with empty credentials"
