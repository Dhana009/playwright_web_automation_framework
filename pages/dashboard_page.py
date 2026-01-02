"""
Dashboard Page Object

Handles dashboard interactions including user menu and logout.
"""

from playwright.sync_api import Page
from pages.base_page import BasePage
from utils.logger import logger

class DashboardPage(BasePage):
    """Dashboard page object."""
    
    # Locators
    USER_MENU_BUTTON = '[data-testid="user-menu-button"]'
    USER_MENU_DROPDOWN = '[data-testid="user-menu-dropdown"]'
    LOGOUT_BUTTON = '[data-testid="menu-logout"]'
    
    def __init__(self, page: Page):
        super().__init__(page)
        
    def logout(self) -> None:
        """
        Perform logout action.
        clicks user menu then logout button.
        """
        logger.info("Performing logout")
        self.click(self.USER_MENU_BUTTON)
        self.wait_for_element(self.USER_MENU_DROPDOWN, state="visible")
        self.click(self.LOGOUT_BUTTON)
        self.wait_for_url("**/login")
        logger.info("Logged out successfully")

    def is_on_dashboard(self) -> bool:
        """Check if currently on dashboard."""
        return "/dashboard" in self.get_current_url()
