"""
Base Page Object

This module provides the base page object class with common methods.
All page objects inherit from this base class.

Author: Senior SDET
Date: 2026-01-02
"""

from typing import Optional
from playwright.sync_api import Page, Locator, expect

from config.settings import settings
from utils.logger import logger
from utils.exceptions import PageLoadException, ElementNotFoundException


class BasePage:
    """
    Base page object with common methods.
    
    All page objects should inherit from this class.
    Provides reusable methods for common page interactions.
    
    Example:
        >>> class LoginPage(BasePage):
        ...     def login(self, email, password):
        ...         self.fill_text(self.email_input, email)
    """
    
    def __init__(self, page: Page):
        """
        Initialize base page.
        
        Args:
            page: Playwright page instance
        """
        self.page = page
        self.base_url = settings.BASE_URL
        
        # Set default timeouts
        self.page.set_default_timeout(settings.DEFAULT_TIMEOUT)
        self.page.set_default_navigation_timeout(settings.NAVIGATION_TIMEOUT)
    
    def navigate(self, path: str = "") -> None:
        """
        Navigate to a URL.
        
        Args:
            path: URL path (appended to base_url)
            
        Example:
            >>> page.navigate("/login")
        """
        url = f"{self.base_url}{path}"
        logger.info(f"Navigating to: {url}")
        
        try:
            self.page.goto(url, wait_until="domcontentloaded")
        except Exception as e:
            raise PageLoadException(url=url, timeout=settings.NAVIGATION_TIMEOUT)
    
    def wait_for_url(self, url_pattern: str, timeout: int = None) -> None:
        """
        Wait for URL to match pattern.
        
        Args:
            url_pattern: URL pattern to match (supports wildcards)
            timeout: Custom timeout in milliseconds
            
        Example:
            >>> page.wait_for_url("**/dashboard")
        """
        timeout = timeout or settings.NAVIGATION_TIMEOUT
        logger.debug(f"Waiting for URL: {url_pattern}")
        self.page.wait_for_url(url_pattern, timeout=timeout)
    
    def get_element(self, locator: str) -> Locator:
        """
        Get element by locator.
        
        Args:
            locator: Element locator (CSS, role, testid, etc.)
            
        Returns:
            Playwright Locator
            
        Example:
            >>> element = page.get_element('[data-testid="login-button"]')
        """
        return self.page.locator(locator)
    
    def click(self, locator: str, timeout: int = None) -> None:
        """
        Click an element.
        
        Args:
            locator: Element locator
            timeout: Custom timeout in milliseconds
            
        Example:
            >>> page.click('[data-testid="submit-button"]')
        """
        timeout = timeout or settings.DEFAULT_TIMEOUT
        logger.debug(f"Clicking: {locator}")
        
        try:
            element = self.get_element(locator)
            element.click(timeout=timeout)
        except Exception as e:
            raise ElementNotFoundException(locator=locator, timeout=timeout)
    
    def fill_text(self, locator: str, text: str, timeout: int = None) -> None:
        """
        Fill text into an input field.
        
        Args:
            locator: Element locator
            text: Text to fill
            timeout: Custom timeout in milliseconds
            
        Example:
            >>> page.fill_text('[data-testid="email"]', "test@example.com")
        """
        timeout = timeout or settings.DEFAULT_TIMEOUT
        logger.debug(f"Filling text in {locator}: {text}")
        
        try:
            element = self.get_element(locator)
            element.fill(text, timeout=timeout)
        except Exception as e:
            raise ElementNotFoundException(locator=locator, timeout=timeout)
    
    def get_text(self, locator: str, timeout: int = None) -> str:
        """
        Get text content of an element.
        
        Args:
            locator: Element locator
            timeout: Custom timeout in milliseconds
            
        Returns:
            Element text content
            
        Example:
            >>> text = page.get_text('[data-testid="message"]')
        """
        timeout = timeout or settings.DEFAULT_TIMEOUT
        
        try:
            element = self.get_element(locator)
            return element.text_content(timeout=timeout) or ""
        except Exception as e:
            raise ElementNotFoundException(locator=locator, timeout=timeout)
    
    def is_visible(self, locator: str, timeout: int = 5000) -> bool:
        """
        Check if element is visible.
        
        Args:
            locator: Element locator
            timeout: Custom timeout in milliseconds (default: 5s)
            
        Returns:
            True if visible, False otherwise
            
        Example:
            >>> if page.is_visible('[data-testid="error"]'):
            ...     print("Error displayed")
        """
        try:
            element = self.get_element(locator)
            element.wait_for(state="visible", timeout=timeout)
            return True
        except:
            return False
    
    def wait_for_element(
        self,
        locator: str,
        state: str = "visible",
        timeout: int = None
    ) -> None:
        """
        Wait for element to reach a specific state.
        
        Args:
            locator: Element locator
            state: Element state (visible, hidden, attached, detached)
            timeout: Custom timeout in milliseconds
            
        Example:
            >>> page.wait_for_element('[data-testid="modal"]', state="visible")
        """
        timeout = timeout or settings.DEFAULT_TIMEOUT
        logger.debug(f"Waiting for {locator} to be {state}")
        
        try:
            element = self.get_element(locator)
            element.wait_for(state=state, timeout=timeout)
        except Exception as e:
            raise ElementNotFoundException(locator=locator, timeout=timeout)
    
    def select_option(self, locator: str, value: str, timeout: int = None) -> None:
        """
        Select option from dropdown.
        
        Args:
            locator: Dropdown locator
            value: Option value to select
            timeout: Custom timeout in milliseconds
            
        Example:
            >>> page.select_option('[data-testid="item-type"]', "PHYSICAL")
        """
        timeout = timeout or settings.DEFAULT_TIMEOUT
        logger.debug(f"Selecting option {value} in {locator}")
        
        try:
            element = self.get_element(locator)
            element.select_option(value, timeout=timeout)
        except Exception as e:
            raise ElementNotFoundException(locator=locator, timeout=timeout)
    
    def upload_file(self, locator: str, file_path: str, timeout: int = None) -> None:
        """
        Upload file to input element.
        
        Args:
            locator: File input locator
            file_path: Path to file
            timeout: Custom timeout in milliseconds
            
        Example:
            >>> page.upload_file('[data-testid="file-upload"]', "test.pdf")
        """
        timeout = timeout or settings.DEFAULT_TIMEOUT
        logger.debug(f"Uploading file {file_path} to {locator}")
        
        try:
            element = self.get_element(locator)
            element.set_input_files(file_path, timeout=timeout)
        except Exception as e:
            raise ElementNotFoundException(locator=locator, timeout=timeout)
    
    def take_screenshot(self, name: str) -> str:
        """
        Take screenshot of current page.
        
        Args:
            name: Screenshot name (without extension)
            
        Returns:
            Path to screenshot file
            
        Example:
            >>> path = page.take_screenshot("login_page")
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = f"{settings.SCREENSHOTS_DIR}/{filename}"
        
        logger.info(f"Taking screenshot: {filepath}")
        self.page.screenshot(path=filepath, full_page=True)
        
        return filepath
    
    def get_current_url(self) -> str:
        """
        Get current page URL.
        
        Returns:
            Current URL
            
        Example:
            >>> url = page.get_current_url()
        """
        return self.page.url
    
    def reload(self) -> None:
        """
        Reload current page.
        
        Example:
            >>> page.reload()
        """
        logger.debug("Reloading page")
        self.page.reload(wait_until="domcontentloaded")
