"""
Authentication Manager

Handles authentication state management, token validation, and login.

Author: Senior SDET
Date: 2026-01-02
"""

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timedelta

from playwright.sync_api import Browser

from config.settings import settings
from utils.logger import logger
from utils.api_client import APIClient
from utils.exceptions import AuthenticationException


class AuthManager:
    """
    Manages authentication states for users.
    
    Industry Standard Pattern (Google, Netflix, Uber).
    """
    
    @staticmethod
    def setup_auth_states(
        test_items,
        browser: Browser
    ) -> Dict[str, Dict[str, Any]]:
        """
        Create authentication states for needed users (Lazy Loading).
        
        Args:
            test_items: Pytest test items
            browser: Playwright browser instance
            
        Returns:
            Dictionary mapping user email to auth state
        """
        from utils.worker_mapper import WorkerMapper
        
        logger.info("Setting up authentication states")
        
        # Determine which users are needed (lazy loading)
        needed_users = WorkerMapper.determine_needed_users(test_items)
        logger.info(f"Need to authenticate {len(needed_users)} users")
        
        auth_states_dict = {}
        
        for user_email in needed_users:
            auth_state = AuthManager.get_valid_auth_state(user_email, browser)
            auth_states_dict[user_email] = auth_state
        
        logger.info(f"Successfully authenticated {len(auth_states_dict)} users")
        return auth_states_dict
    
    @staticmethod
    def get_valid_auth_state(
        user_email: str,
        browser: Browser
    ) -> Dict[str, Any]:
        """
        Get valid auth state for user (with token validation).
        
        Smart validation:
        1. Check if auth file exists
        2. Validate token with API
        3. Reuse if valid, re-login if expired
        
        Args:
            user_email: User email
            browser: Playwright browser instance
            
        Returns:
            Auth state with token
        """
        auth_file = Path(settings.get_auth_file_path(user_email))
        
        # Check if auth file exists
        if auth_file.exists() and settings.IS_LOCAL:
            logger.info(f"Found existing auth state for {user_email}")
            
            with open(auth_file, 'r') as f:
                auth_state = json.load(f)
            
            # Validate token with API
            if AuthManager.validate_token(auth_state.get("token")):
                logger.info(f"Reusing valid token for {user_email}")
                return auth_state
            else:
                logger.warning(f"Token invalid for {user_email}, re-logging in")
        
        # Login and save new auth state
        logger.info(f"Logging in as {user_email}")
        return AuthManager.login_and_save_state(user_email, browser)
    
    @staticmethod
    def validate_token(token: str) -> bool:
        """
        Validate if token is valid by making API call.
        
        Args:
            token: Authentication token
            
        Returns:
            True if valid, False otherwise
        """
        if not token:
            return False
        
        try:
            client = APIClient(token=token)
            return client.validate_token()
        except:
            return False
    
    @staticmethod
    def login_and_save_state(
        user_email: str,
        browser: Browser
    ) -> Dict[str, Any]:
        """
        Login and save auth state.
        
        Uses BOTH UI login (for browser state) AND API login (for token).
        
        Args:
            user_email: User email
            browser: Playwright browser instance
            
        Returns:
            Auth state with token
        """
        from pages.login_page import LoginPage
        
        # Create new context and page
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # Step 1: Login via UI (for browser cookies/session)
            login_page = LoginPage(page)
            login_page.navigate_to_login()
            login_page.login(user_email, settings.DEFAULT_PASSWORD)
            
            # Save browser auth state (cookies, localStorage, etc.)
            auth_state = context.storage_state()
            
            # Step 2: Login via API to get token (more reliable)
            logger.info(f"Getting token via API login for {user_email}")
            api_client = APIClient()
            api_response = api_client.login(user_email, settings.DEFAULT_PASSWORD)
            
            # Extract token from API response
            token = api_response.get("token")
            if not token:
                logger.warning(f"No token in API response for {user_email}")
                # Fallback: try localStorage
                token = page.evaluate("() => localStorage.getItem('token')")
            
            auth_state["token"] = token
            auth_state["user_email"] = user_email
            auth_state["expires_at"] = (
                datetime.now() + timedelta(days=7)
            ).isoformat()
            
            # Save to file
            auth_file = Path(settings.get_auth_file_path(user_email))
            auth_file.parent.mkdir(exist_ok=True)
            
            with open(auth_file, 'w') as f:
                json.dump(auth_state, f, indent=2)
            
            logger.info(
                f"Successfully logged in and saved auth state for {user_email}"
            )
            
            return auth_state
            
        except Exception as e:
            raise AuthenticationException(user_email=user_email, reason=str(e))
        finally:
            context.close()
