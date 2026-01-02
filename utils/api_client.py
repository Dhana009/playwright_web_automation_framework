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
            "Authorization": f"Bearer {token}"
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
        Create a new item using multipart/form-data.
        
        Args:
            item_data: Item data with flat fields:
                - name, description, item_type, price, category
                - PHYSICAL: weight, length, width, height
                - DIGITAL: download_url, file_size
                - SERVICE: duration_hours
                - Optional: tags (comma-separated string)
            
        Returns:
            Created item data with ID
            
        Example:
            >>> item = client.create_item({
            ...     "name": "Test Laptop",
            ...     "description": "Test description...",
            ...     "item_type": "PHYSICAL",
            ...     "price": 999.99,
            ...     "category": "Electronics",
            ...     "weight": 2.5,
            ...     "length": 35,
            ...     "width": 25,
            ...     "height": 2
            ... })
        """
        logger.info(f"Creating item: {item_data.get('name')}")
        
        # Prepare form data (convert all values to strings for multipart)
        form_data = {}
        for key, value in item_data.items():
            if value is not None:
                form_data[key] = str(value)
        
        # Make request with form data
        # 'requests' will automatically set Content-Type to application/x-www-form-urlencoded
        url = f"{self.base_url}/items"
        
        for attempt in range(1, 4):  # 3 retries
            try:
                response = self.session.post(
                    url,
                    data=form_data,
                    timeout=settings.API_TIMEOUT
                )
                
                logger.debug(f"API Response: {response.status_code}")
                response.raise_for_status()
                
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if hasattr(e, 'response') else 0
                
                # Don't retry on 409 Conflict - let caller handle it
                if status_code == 409:
                    logger.debug(f"Item conflict (409): {e}")
                    raise
                
                # Retry on other errors
                logger.warning(f"Create item failed (attempt {attempt}/3): {e}")
                
                if attempt < 3:
                    time.sleep(1)
                    continue
                
                raise APIException(
                    endpoint="/items",
                    status_code=status_code,
                    message=str(e)
                )
            except requests.exceptions.RequestException as e:
                logger.warning(f"Create item failed (attempt {attempt}/3): {e}")
                
                if attempt < 3:
                    time.sleep(1)
                    continue
                
                raise APIException(
                    endpoint="/items",
                    status_code=0,
                    message=str(e)
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
    
    def get_all_items(
        self,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        page: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get all items with filtering and pagination.
        
        Args:
            limit: Pagination limit
            search: Search query
            status: Filter by status (active, inactive, all)
            sort_by: Field to sort by (name, category, price, createdAt)
            sort_order: Sort order (asc, desc)
            page: Page number
            
        Returns:
            List of items response
        """
        params = {"limit": limit}
        if search:
            params["search"] = search
        if status:
            params["status"] = status
        if sort_by:
            params["sort_by"] = sort_by
        if sort_order:
            params["sort_order"] = sort_order
        if page:
            params["page"] = page
            
        return self._request(
            method="GET",
            endpoint="/items",
            params=params
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
        
        Since there's no /auth/me endpoint, we validate by making
        an authenticated API call to GET /items.
        
        Returns:
            True if token is valid, False otherwise
            
        Example:
            >>> if client.validate_token():
            ...     print("Token is valid")
        """
        if not self.token:
            return False
        
        try:
            # Try to get items (any authenticated endpoint works)
            self._request(method="GET", endpoint="/items")
            return True
        except APIException:
            return False
