"""
Pytest Configuration and Fixtures

This module provides pytest fixtures for the web automation framework.
Implements lazy loading, test context pattern, and seed data management.

Author: Senior SDET
Date: 2026-01-02
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Set
from dataclasses import dataclass
from datetime import datetime, timedelta

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright
from dotenv import load_dotenv

# Auto-load environment based on --env argument or ENV variable
# Usage: pytest --env=staging  OR  $env:ENV="staging"; pytest
env_name = os.getenv("ENV", "local")  # Default to local

# Load corresponding .env file
env_file_map = {
    "local": ".env.local",
    "staging": ".env.staging",
    "production": ".env"
}

env_file = env_file_map.get(env_name, ".env.local")
if Path(env_file).exists():
    load_dotenv(env_file)
    print(f"✅ Loaded {env_name} environment from {env_file}")
else:
    print(f"⚠️  Environment file {env_file} not found, using defaults")

from config.settings import settings
from config.browser_config import browser_config
from utils.logger import logger, Logger
from utils.api_client import APIClient
from utils.exceptions import AuthenticationException, SeedDataException
from data.test_data import test_data


# ============================================================================
# Pytest Configuration Hooks
# ============================================================================

def pytest_addoption(parser):
    """
    Add custom command line options.
    
    Usage:
        pytest --env=staging
        pytest --env=production
        pytest --env=local (default)
    """
    parser.addoption(
        "--env",
        action="store",
        default="local",
        help="Environment to run tests against: local, staging, production"
    )


def pytest_configure(config):
    """
    Configure pytest based on command line options.
    
    Sets ENV environment variable based on --env argument.
    """
    env = config.getoption("--env")
    os.environ["ENV"] = env
    print(f"🎯 Running tests against: {env} environment")


# ============================================================================
# Test Context Pattern
# ============================================================================

@dataclass
class TestContext:
    """
    Test execution context (Industry Standard Pattern).
    
    Encapsulates all test state in one object:
    - User information
    - Authentication token
    - Seed data for this user
    - Worker information
    
    Used by: Google, Netflix, Uber, Spotify
    """
    user_email: str
    user_role: str
    auth_token: str
    seed_items: Dict[str, Any]
    worker_id: str
    
    def get_seed_item(self, item_type: str) -> Dict[str, Any]:
        """
        Get seed item by type.
        
        Args:
            item_type: Item type (physical, digital, service)
            
        Returns:
            Seed item data
        """
        return self.seed_items.get(item_type.lower(), {})


# ============================================================================
# Session-Scoped Fixtures (Run Once)
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    """Setup logging and cleanup old logs."""
    logger.info("=" * 80)
    logger.info("TEST SESSION STARTED")
    logger.info("=" * 80)
    
    # Cleanup old logs (keep last 5)
    Logger.cleanup_old_logs(keep_count=5)
    
    yield
    
    logger.info("=" * 80)
    logger.info("TEST SESSION COMPLETED")
    logger.info("=" * 80)


@pytest.fixture(scope="session")
def playwright_browser(playwright: Playwright) -> Browser:
    """
    Launch browser with configuration.
    
    Returns:
        Playwright browser instance
    """
    logger.info(f"Launching browser: {browser_config.BROWSER_TYPE}")
    logger.info(f"Headless mode: {browser_config.HEADLESS}")
    
    # Launch browser
    browser_type = getattr(playwright, browser_config.BROWSER_TYPE)
    browser = browser_type.launch(**browser_config.get_launch_options())
    
    yield browser
    
    logger.info("Closing browser")
    browser.close()


def get_worker_id() -> str:
    """
    Get current worker ID for parallel execution.
    
    Returns:
        Worker ID (e.g., "gw0", "gw1", or "master")
    """
    return os.getenv("PYTEST_XDIST_WORKER", "master")


def extract_worker_number(worker_id: str) -> int:
    """
    Extract worker number from worker ID.
    
    Args:
        worker_id: Worker ID (e.g., "gw0", "gw1", "master")
        
    Returns:
        Worker number (0-7 for parallel, 0 for master)
        
    Example:
        >>> extract_worker_number("gw0")
        0
        >>> extract_worker_number("gw7")
        7
        >>> extract_worker_number("master")
        0
    """
    if worker_id == "master" or not worker_id.startswith("gw"):
        return 0
    return int(worker_id.replace("gw", ""))


def get_user_for_worker(role: str, worker_id: str) -> str:
    """
    Map worker to user based on role and worker ID.
    
    Args:
        role: User role (ADMIN, EDITOR, VIEWER)
        worker_id: Worker ID
        
    Returns:
        User email
        
    Example:
        >>> get_user_for_worker("ADMIN", "gw0")
        'admin1@test.com'
        >>> get_user_for_worker("ADMIN", "gw7")
        'admin8@test.com'
    """
    worker_num = extract_worker_number(worker_id)
    user_num = (worker_num % 8) + 1  # Map to 1-8
    return settings.get_user_email(role, user_num)


def determine_needed_users(test_items) -> Set[str]:
    """
    Determine which users are needed by selected tests (Lazy Loading).
    
    Args:
        test_items: List of pytest test items
        
    Returns:
        Set of user emails needed
        
    This is the key to lazy loading - only login users that tests need.
    For parallel execution, determines users based on worker count.
    """
    needed_users = set()
    roles_needed = set()
    
    # Determine which roles are needed
    for item in test_items:
        role_marker = item.get_closest_marker("role")
        role = role_marker.args[0] if role_marker else "ADMIN"
        roles_needed.add(role)
    
    # Get number of workers
    num_workers = settings.NUM_WORKERS
    
    # For each role needed, add users for all workers
    for role in roles_needed:
        for worker_num in range(num_workers):
            worker_id = f"gw{worker_num}"
            user_email = get_user_for_worker(role, worker_id)
            needed_users.add(user_email)
    
    logger.info(f"Determined {len(needed_users)} users needed for {len(roles_needed)} roles across {num_workers} workers")
    return needed_users


@pytest.fixture(scope="session")
def auth_states(request, playwright_browser: Browser) -> Dict[str, Dict[str, Any]]:
    """
    Create authentication states for needed users (Lazy Loading).
    
    Only logs in users that are needed by selected tests.
    Implements smart token validation with automatic refresh.
    
    Returns:
        Dictionary mapping user email to auth state
    """
    logger.info("Setting up authentication states")
    
    # Determine which users are needed (lazy loading)
    needed_users = determine_needed_users(request.session.items)
    logger.info(f"Need to authenticate {len(needed_users)} users")
    
    auth_states_dict = {}
    
    for user_email in needed_users:
        auth_state = get_valid_auth_state(user_email, playwright_browser)
        auth_states_dict[user_email] = auth_state
    
    logger.info(f"Successfully authenticated {len(auth_states_dict)} users")
    return auth_states_dict


def get_valid_auth_state(user_email: str, browser: Browser) -> Dict[str, Any]:
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
        if validate_token(auth_state.get("token")):
            logger.info(f"✅ Reusing valid token for {user_email}")
            return auth_state
        else:
            logger.warning(f"⚠️ Token invalid for {user_email}, re-logging in")
    
    # Login and save new auth state
    logger.info(f"🔐 Logging in as {user_email}")
    return login_and_save_state(user_email, browser)


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


def login_and_save_state(user_email: str, browser: Browser) -> Dict[str, Any]:
    """
    Login via UI and save auth state.
    
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
        # Login via UI
        login_page = LoginPage(page)
        login_page.navigate_to_login()
        login_page.login(user_email, settings.DEFAULT_PASSWORD)
        
        # Save auth state
        auth_state = context.storage_state()
        
        # Extract token from localStorage (if available)
        token = page.evaluate("() => localStorage.getItem('token')")
        auth_state["token"] = token
        auth_state["user_email"] = user_email
        auth_state["expires_at"] = (datetime.now() + timedelta(days=7)).isoformat()
        
        # Save to file
        auth_file = Path(settings.get_auth_file_path(user_email))
        auth_file.parent.mkdir(exist_ok=True)
        
        with open(auth_file, 'w') as f:
            json.dump(auth_state, f, indent=2)
        
        logger.info(f"✅ Successfully logged in and saved auth state for {user_email}")
        
        return auth_state
        
    except Exception as e:
        raise AuthenticationException(user_email=user_email, reason=str(e))
    finally:
        context.close()


@pytest.fixture(scope="session")
def seed_data(auth_states: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Create seed data for authenticated users (Lazy Loading).
    
    Only creates seed data for users that logged in.
    Depends on auth_states fixture.
    
    Args:
        auth_states: Dictionary of auth states
        
    Returns:
        Dictionary mapping user email to seed items
    """
    logger.info("Setting up seed data")
    logger.info(f"Creating seed data for {len(auth_states)} users")
    
    seed_items_dict = {}
    
    for user_email, auth_state in auth_states.items():
        seed_items = create_seed_items_for_user(user_email, auth_state["token"])
        seed_items_dict[user_email] = seed_items
    
    logger.info(f"Successfully created seed data for {len(seed_items_dict)} users")
    
    # Save seed data IDs for reuse (local only)
    if settings.IS_LOCAL:
        test_data.save_seed_data_ids(seed_items_dict)
    
    return seed_items_dict


def check_existing_seed_items(user_email: str, token: str) -> Dict[str, Any]:
    """
    Check if seed items already exist for user.
    
    Args:
        user_email: User email
        token: Auth token
        
    Returns:
        Dictionary with existing seed items (if found)
    """
    client = APIClient(token=token)
    seed_items = {}
    
    try:
        # Get all items
        response = client.get_all_items()
        all_items = response.get("items", [])
        
        # Get user info for seed item names
        user = test_data.get_user_by_email(user_email)
        role = user["role"].lower()
        number = user["number"]
        
        # Check for each seed item type
        for item_type in ["PHYSICAL", "DIGITAL", "SERVICE"]:
            expected_name = test_data.generate_seed_item_name(role, number, item_type)
            
            # Find item with this name
            for item in all_items:
                if item.get("name") == expected_name:
                    seed_items[item_type.lower()] = item
                    logger.debug(f"Found existing seed item: {expected_name}")
                    break
        
        return seed_items
        
    except Exception as e:
        logger.warning(f"Failed to check existing seed items: {e}")
        return {}


def create_seed_items_for_user(user_email: str, token: str) -> Dict[str, Any]:
    """
    Create 3 seed items for a user (idempotent for local).
    
    Args:
        user_email: User email
        token: Auth token
        
    Returns:
        Dictionary with physical, digital, service seed items
    """
    # Check if seed items already exist (local only)
    if settings.IS_LOCAL:
        existing_seeds = check_existing_seed_items(user_email, token)
        if len(existing_seeds) >= 3:
            logger.info(f"✅ Reusing {len(existing_seeds)} existing seed items for {user_email}")
            return existing_seeds
        elif len(existing_seeds) > 0:
            logger.info(f"Found {len(existing_seeds)} seed items, creating missing ones")
    
    # Create fresh seed items
    logger.info(f"Creating seed items for {user_email}")
    
    client = APIClient(token=token)
    seed_items = {}
    
    # Get user info
    user = test_data.get_user_by_email(user_email)
    role = user["role"].lower()
    number = user["number"]
    
    # Create 3 seed items (one of each type)
    for item_type in ["PHYSICAL", "DIGITAL", "SERVICE"]:
        # Skip if already exists (from partial creation)
        if settings.IS_LOCAL and item_type.lower() in existing_seeds:
            seed_items[item_type.lower()] = existing_seeds[item_type.lower()]
            continue
        
        name = test_data.generate_seed_item_name(role, number, item_type)
        item_data = test_data.generate_item_data(name=name, item_type=item_type)
        
        try:
            created_item = client.create_item(item_data)
            seed_items[item_type.lower()] = created_item
            logger.info(f"Created seed item: {name}")
        except Exception as e:
            raise SeedDataException(user_email=user_email, reason=str(e))
    
    return seed_items


# ============================================================================
# Function-Scoped Fixtures (Run Per Test)
# ============================================================================

@pytest.fixture
def browser_context(playwright_browser: Browser) -> BrowserContext:
    """
    Create new browser context per test (isolation).
    
    Returns:
        Playwright browser context
    """
    video_dir = settings.VIDEOS_DIR if settings.IS_CI else None
    context = playwright_browser.new_context(
        **browser_config.get_context_options(video_dir=video_dir)
    )
    
    yield context
    
    context.close()


@pytest.fixture
def page(browser_context: BrowserContext) -> Page:
    """
    Create new page per test.
    
    Returns:
        Playwright page instance
    """
    page = browser_context.new_page()
    
    yield page
    
    page.close()


@pytest.fixture
def authenticated_page(
    page: Page,
    request,
    auth_states: Dict[str, Dict[str, Any]]
) -> Page:
    """
    Get authenticated page with loaded auth state.
    
    Args:
        page: Playwright page
        request: Pytest request
        auth_states: Auth states dictionary
        
    Returns:
        Authenticated page
    """
    # Get role from test marker
    role_marker = request.node.get_closest_marker("role")
    role = role_marker.args[0] if role_marker else "ADMIN"
    
    # Get worker ID and map to user
    worker_id = get_worker_id()
    user_email = get_user_for_worker(role, worker_id)
    
    # Load auth state
    auth_state = auth_states.get(user_email)
    if not auth_state:
        raise AuthenticationException(
            user_email=user_email,
            reason="Auth state not found"
        )
    
    # Set storage state (cookies, localStorage)
    page.context.add_cookies(auth_state.get("cookies", []))
    
    logger.info(f"Loaded auth state for {user_email}")
    
    return page


@pytest.fixture
def test_context(
    request,
    auth_states: Dict[str, Dict[str, Any]],
    seed_data: Dict[str, Dict[str, Any]]
) -> TestContext:
    """
    Create test context with user, role, token, and seed data.
    
    Industry Standard Pattern (Google, Netflix, Uber).
    
    Args:
        request: Pytest request
        auth_states: Auth states dictionary
        seed_data: Seed data dictionary
        
    Returns:
        TestContext instance
    """
    # Get role from test marker
    role_marker = request.node.get_closest_marker("role")
    role = role_marker.args[0] if role_marker else "ADMIN"
    
    # Get worker ID and map to user
    worker_id = get_worker_id()
    user_email = get_user_for_worker(role, worker_id)
    
    # Get auth state and seed data
    auth_state = auth_states.get(user_email, {})
    user_seed_data = seed_data.get(user_email, {})
    
    # Create context
    context = TestContext(
        user_email=user_email,
        user_role=role,
        auth_token=auth_state.get("token", ""),
        seed_items=user_seed_data,
        worker_id=worker_id
    )
    
    logger.debug(f"Created test context for {user_email}")
    
    return context


# ============================================================================
# Pytest Hooks
# ============================================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Capture screenshot on test failure.
    
    Industry Standard: Screenshot all failures.
    """
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call" and report.failed:
        # Get page fixture if available
        if "page" in item.funcargs:
            page = item.funcargs["page"]
            
            # Take screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_name = f"{item.name}_{timestamp}.png"
            screenshot_path = f"{settings.SCREENSHOTS_DIR}/{screenshot_name}"
            
            try:
                page.screenshot(path=screenshot_path, full_page=True)
                logger.info(f"Screenshot saved: {screenshot_path}")
            except Exception as e:
                logger.error(f"Failed to capture screenshot: {e}")
