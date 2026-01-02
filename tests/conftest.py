"""
Pytest Configuration and Fixtures

This module provides pytest fixtures for the web automation framework.
Implements lazy loading, test context pattern, and seed data management.

Author: Senior SDET
Date: 2026-01-02
"""

import os
from pathlib import Path

# CRITICAL: Load environment FIRST before any other imports
# This ensures settings.py gets the correct values
env_name = os.getenv("ENV", "local")

env_file_map = {
    "local": ".env.local",
    "staging": ".env.staging",
    "production": ".env"
}

env_file = env_file_map.get(env_name, ".env.local")
if Path(env_file).exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)
    print(f"Loaded {env_name} environment from {env_file}")
else:
    print(f"WARNING: Environment file {env_file} not found, using defaults")

# NOW import everything else (settings will have correct values)
from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright

from config.settings import settings
from config.browser_config import browser_config
from utils.logger import logger, Logger
from utils.auth_manager import AuthManager
from utils.seed_data_manager import SeedDataManager
from utils.worker_mapper import WorkerMapper
from utils.exceptions import AuthenticationException


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
    print(f"Running tests against: {env} environment")


# ============================================================================
# Test Context Pattern
# ============================================================================

@dataclass
class TestContext:
    """
    Test execution context (Industry Standard Pattern).
    
    Encapsulates all test state in one object.
    Used by: Google, Netflix, Uber, Spotify
    """
    user_email: str
    user_role: str
    auth_token: str
    seed_items: Dict[str, Any]
    worker_id: str
    
    def get_seed_item(self, item_type: str) -> Dict[str, Any]:
        """Get seed item by type."""
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
    """Launch browser with configuration."""
    logger.info(f"Launching browser: {browser_config.BROWSER_TYPE}")
    logger.info(f"Headless mode: {browser_config.HEADLESS}")
    
    # Launch browser
    browser_type = getattr(playwright, browser_config.BROWSER_TYPE)
    browser = browser_type.launch(**browser_config.get_launch_options())
    
    yield browser
    
    logger.info("Closing browser")
    browser.close()


@pytest.fixture(scope="session")
def auth_states(request, playwright_browser: Browser) -> Dict[str, Dict[str, Any]]:
    """
    Create authentication states for needed users (Lazy Loading).
    
    Uses AuthManager to handle all auth logic.
    """
    return AuthManager.setup_auth_states(
        request.session.items,
        playwright_browser
    )


# ============================================================================
# Function-Scoped Fixtures (Run Per Test)
# ============================================================================

@pytest.fixture
def browser_context(playwright_browser: Browser) -> BrowserContext:
    """Create new browser context per test (isolation)."""
    video_dir = settings.VIDEOS_DIR if settings.IS_CI else None
    context = playwright_browser.new_context(
        **browser_config.get_context_options(video_dir=video_dir)
    )
    
    yield context
    
    context.close()


@pytest.fixture
def page(browser_context: BrowserContext) -> Page:
    """Create new page per test."""
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
    """
    # Get role from test marker
    role_marker = request.node.get_closest_marker("role")
    role = role_marker.args[0] if role_marker else "ADMIN"
    
    # Get worker ID and map to user
    worker_id = WorkerMapper.get_worker_id()
    user_email = WorkerMapper.get_user_for_worker(role, worker_id)
    
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
    auth_states: Dict[str, Dict[str, Any]]
) -> TestContext:
    """
    Create test context with user, role, token, and JUST-IN-TIME seed data.
    
    OPTION B: Function-scoped (per-test) seed data setup.
    - Only creates seed data for the user running THIS test
    - Checks if data exists first (idempotent)
    - Creates only what's missing
    
    Industry Standard Pattern (Google, Netflix, Uber).
    """
    # Get role from test marker
    role_marker = request.node.get_closest_marker("role")
    role = role_marker.args[0] if role_marker else "ADMIN"
    
    # Get worker ID and map to user
    worker_id = WorkerMapper.get_worker_id()
    user_email = WorkerMapper.get_user_for_worker(role, worker_id)
    
    # Get auth state
    auth_state = auth_states.get(user_email, {})
    if not auth_state:
        raise AuthenticationException(
            user_email=user_email,
            reason="Auth state not found"
        )
    
    # SETUP SEED DATA: Just-in-time for THIS test's user
    logger.info(f"Setting up seed data for {user_email} (per-test)")
    token = auth_state.get("token", "")
    seed_items = SeedDataManager.create_seed_items_for_user(user_email, token)
    
    # Create context
    context = TestContext(
        user_email=user_email,
        user_role=role,
        auth_token=token,
        seed_items=seed_items,
        worker_id=worker_id
    )
    
    logger.info(f"Test context ready for {user_email} with {len(seed_items)} seed items")
    
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
