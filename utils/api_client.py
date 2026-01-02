"""
API Client

This module provides a reusable API client for interacting with the FlowHub API.
Handles authentication, request retry logic, and error handling.

Author: Senior SDET
Date: 2026-01-02
"""

import time
from typing import Dict, Any, Optional
import requests
from requests.exceptions import RequestException

from config.settings import settings
from utils.logger import logger
from utils.exceptions import APIException, AuthenticationException


class APIClient:
    """
    HTTP client for FlowHub API interactions.
    
    Features:
    - Automatic retry logic (3 attempts)
    - Token-based authentication
    - Comprehensive error handling
    - Request/response logging
    
    Example:
        >>> client = APIClient()
        >>> client.login("admin1@test.com", "Admin@123")
        >>> item = client.create_item({"name": "Test Item", ...})
        >>> client.delete_item(item["id"])
    """
    
    def __init__(self, base_url: str = None, token: str = None):
        """
        Initialize API client.
        
        Args:
            base_url: API base URL (default: from settings)
            token: Authentication token (optional)
        """
        self.base_url = base_url or settings.API_BASE_URL
        self.token = token
        self.session = requests.Session()
        
        if token:
            self._set_auth_header(token)
    
    def _set_auth_header(self, token: str) -> None:
        """Set authorization header with token."""
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        })
    
    def _request(
        self,
        method: str,
        endpoint: str,
        max_retries: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., "/items")
            max_retries: Maximum retry attempts (default: 3)
            **kwargs: Additional arguments for requests
            
        Returns:
            Response JSON data
            
        Raises:
            APIException: If request fails after retries
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.debug(f"API {method} {endpoint} (attempt {attempt}/{max_retries})")
                
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=settings.API_TIMEOUT,
                    **kwargs
                )
                
                # Log response
                logger.debug(f"API Response: {response.status_code}")
                
                # Raise for 4xx/5xx status codes
                response.raise_for_status()
                
                # Return JSON response
                return response.json()
                
            except RequestException as e:
                logger.warning(
                    f"API request failed (attempt {attempt}/{max_retries}): {e}"
                )
                
                # Retry on failure (except last attempt)
                if attempt < max_retries:
                    time.sleep(1)  # Wait 1 second before retry
                    continue
                
                # Final attempt failed - raise exception
                status_code = getattr(e.response, 'status_code', 0) if hasattr(e, 'response') else 0
                message = str(e)
                
                raise APIException(
                    endpoint=endpoint,
                    status_code=status_code,
                    message=message
                )
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Login and get authentication token.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Login response with token
            
        Raises:
            AuthenticationException: If login fails
            
        Example:
            >>> client = APIClient()
            >>> response = client.login("admin1@test.com", "Admin@123")
            >>> print(response["token"])
        """
        try:
            logger.info(f"Logging in as {email}")
            
            response = self._request(
                method="POST",
                endpoint="/auth/login",
                json={"email": email, "password": password}
            )
            
            # Extract and store token
            self.token = response.get("token")
            if not self.token:
                raise AuthenticationException(
                    user_email=email,
                    reason="No token in response"
                )
            
            self._set_auth_header(self.token)
            logger.info(f"Successfully logged in as {email}")
            
            return response
            
        except APIException as e:
            raise AuthenticationException(
                user_email=email,
                reason=f"API error: {e.message}"
            )
    
    def create_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new item.
        
        Args:
            item_data: Item data (name, item_type, price, etc.)
            
        Returns:
            Created item data with ID
            
        Example:
            >>> item = client.create_item({
            ...     "name": "Test Item",
            ...     "item_type": "PHYSICAL",
            ...     "price": 100.00
            ... })
        """
        logger.info(f"Creating item: {item_data.get('name')}")
        return self._request(
            method="POST",
            endpoint="/items",
            json=item_data
        )
    
    def get_item(self, item_id: str) -> Dict[str, Any]:
        """
        Get item by ID.
        
        Args:
            item_id: Item ID
            
        Returns:
            Item data
        """
        logger.debug(f"Getting item: {item_id}")
        return self._request(
            method="GET",
            endpoint=f"/items/{item_id}"
        )
    
    def get_all_items(self) -> Dict[str, Any]:
        """
        Get all items.
        
        Returns:
            List of items with pagination info
        """
        logger.debug("Getting all items")
        return self._request(
            method="GET",
            endpoint="/items"
        )
    
    def update_item(self, item_id: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an item.
        
        Args:
            item_id: Item ID
            item_data: Updated item data
            
        Returns:
            Updated item data
        """
        logger.info(f"Updating item: {item_id}")
        return self._request(
            method="PUT",
            endpoint=f"/items/{item_id}",
            json=item_data
        )
    
    def delete_item(self, item_id: str) -> Dict[str, Any]:
        """
        Delete an item (soft delete).
        
        Args:
            item_id: Item ID
            
        Returns:
            Deletion response
        """
        logger.info(f"Deleting item: {item_id}")
        return self._request(
            method="DELETE",
            endpoint=f"/items/{item_id}"
        )
    
    def validate_token(self) -> bool:
        """
        Validate if current token is valid.
        
        Returns:
            True if token is valid, False otherwise
            
        Example:
            >>> if client.validate_token():
            ...     print("Token is valid")
        """
        if not self.token:
            return False
        
        try:
            # Try to get user info
            self._request(method="GET", endpoint="/auth/me")
            return True
        except APIException:
            return False
