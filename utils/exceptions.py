"""
Custom Exceptions

This module defines custom exceptions for the web automation framework.
Provides clear, specific error handling for different failure scenarios.

Author: Senior SDET
Date: 2026-01-02
"""


class FrameworkException(Exception):
    """Base exception for all framework-specific errors."""
    pass


class PageLoadException(FrameworkException):
    """Raised when a page fails to load within timeout."""
    
    def __init__(self, url: str, timeout: int):
        self.url = url
        self.timeout = timeout
        super().__init__(
            f"Page failed to load: {url} (timeout: {timeout}ms)"
        )


class ElementNotFoundException(FrameworkException):
    """Raised when an element is not found after waiting."""
    
    def __init__(self, locator: str, timeout: int):
        self.locator = locator
        self.timeout = timeout
        super().__init__(
            f"Element not found: {locator} (timeout: {timeout}ms)"
        )


class AuthenticationException(FrameworkException):
    """Raised when authentication fails."""
    
    def __init__(self, user_email: str, reason: str = "Login failed"):
        self.user_email = user_email
        self.reason = reason
        super().__init__(
            f"Authentication failed for {user_email}: {reason}"
        )


class DataCleanupException(FrameworkException):
    """Raised when data cleanup fails."""
    
    def __init__(self, item_id: str, reason: str):
        self.item_id = item_id
        self.reason = reason
        super().__init__(
            f"Failed to cleanup item {item_id}: {reason}"
        )


class APIException(FrameworkException):
    """Raised when API call fails."""
    
    def __init__(self, endpoint: str, status_code: int, message: str):
        self.endpoint = endpoint
        self.status_code = status_code
        self.message = message
        super().__init__(
            f"API call failed: {endpoint} (status: {status_code}) - {message}"
        )


class SeedDataException(FrameworkException):
    """Raised when seed data creation or validation fails."""
    
    def __init__(self, user_email: str, reason: str):
        self.user_email = user_email
        self.reason = reason
        super().__init__(
            f"Seed data error for {user_email}: {reason}"
        )
