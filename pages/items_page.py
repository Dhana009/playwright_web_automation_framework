"""
Items Page Object

This module provides the page object for the items list page.
Handles item listing, search, filter, sort, and pagination.

Author: Senior SDET
Date: 2026-01-02
"""

from typing import List, Optional
from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logger import logger


class ItemsPage(BasePage):
    """
    Items list page object.
    
    Provides methods for item listing and management.
    
    Example:
        >>> items_page = ItemsPage(page)
        >>> items_page.navigate_to_items()
        >>> items_page.search_items("laptop")
    """
    
    # Locators
    CREATE_ITEM_BUTTON = '[data-testid="create-item-button"]'
    SEARCH_INPUT = '[data-testid="search-input"]'
    FILTER_TYPE_DROPDOWN = '[data-testid="filter-type"]'
    FILTER_STATUS_DROPDOWN = '[data-testid="filter-status"]'
    SORT_DROPDOWN = '[data-testid="sort-by"]'
    
    # Item cards
    ITEM_CARD = '[data-testid="item-card"]'
    ITEM_NAME = '[data-testid="item-name"]'
    ITEM_PRICE = '[data-testid="item-price"]'
    ITEM_TYPE = '[data-testid="item-type"]'
    ITEM_STATUS = '[data-testid="item-status"]'
    
    # Actions
    VIEW_DETAILS_BUTTON = '[data-testid="view-details"]'
    EDIT_BUTTON = '[data-testid="edit-item"]'
    DELETE_BUTTON = '[data-testid="delete-item"]'
    
    # Pagination
    PAGINATION_INFO = '[data-testid="pagination-info"]'
    NEXT_PAGE_BUTTON = '[data-testid="next-page"]'
    PREV_PAGE_BUTTON = '[data-testid="prev-page"]'
    PAGE_NUMBER = '[data-testid="page-number"]'
    
    # Empty state
    EMPTY_STATE = '[data-testid="empty-state"]'
    
    # Loading
    LOADING_SPINNER = '[data-testid="loading-spinner"]'
    
    def __init__(self, page: Page):
        """Initialize items page."""
        super().__init__(page)
    
    def navigate_to_items(self) -> None:
        """
        Navigate to items list page.
        
        Example:
            >>> items_page.navigate_to_items()
        """
        self.navigate("/dashboard")
        logger.info("Navigated to items page")
    
    def click_create_item(self) -> None:
        """
        Click create item button.
        
        Example:
            >>> items_page.click_create_item()
        """
        logger.info("Clicking create item button")
        self.click(self.CREATE_ITEM_BUTTON)
        self.wait_for_url("**/items/create")
    
    def search_items(self, search_text: str) -> None:
        """
        Search for items.
        
        Args:
            search_text: Text to search for
            
        Example:
            >>> items_page.search_items("laptop")
        """
        logger.info(f"Searching for: {search_text}")
        self.fill_text(self.SEARCH_INPUT, search_text)
        # Wait for results to load
        self.wait_for_element(self.LOADING_SPINNER, state="hidden", timeout=5000)
    
    def filter_by_type(self, item_type: str) -> None:
        """
        Filter items by type.
        
        Args:
            item_type: Item type (PHYSICAL, DIGITAL, SERVICE)
            
        Example:
            >>> items_page.filter_by_type("PHYSICAL")
        """
        logger.info(f"Filtering by type: {item_type}")
        self.select_option(self.FILTER_TYPE_DROPDOWN, item_type)
        self.wait_for_element(self.LOADING_SPINNER, state="hidden", timeout=5000)
    
    def filter_by_status(self, status: str) -> None:
        """
        Filter items by status.
        
        Args:
            status: Status (ACTIVE, INACTIVE)
            
        Example:
            >>> items_page.filter_by_status("ACTIVE")
        """
        logger.info(f"Filtering by status: {status}")
        self.select_option(self.FILTER_STATUS_DROPDOWN, status)
        self.wait_for_element(self.LOADING_SPINNER, state="hidden", timeout=5000)
    
    def sort_by(self, sort_option: str) -> None:
        """
        Sort items.
        
        Args:
            sort_option: Sort option (name, price, date)
            
        Example:
            >>> items_page.sort_by("price")
        """
        logger.info(f"Sorting by: {sort_option}")
        self.select_option(self.SORT_DROPDOWN, sort_option)
        self.wait_for_element(self.LOADING_SPINNER, state="hidden", timeout=5000)
    
    def get_item_count(self) -> int:
        """
        Get number of items displayed.
        
        Returns:
            Number of items
            
        Example:
            >>> count = items_page.get_item_count()
        """
        items = self.page.locator(self.ITEM_CARD).all()
        return len(items)
    
    def get_item_names(self) -> List[str]:
        """
        Get all item names on current page.
        
        Returns:
            List of item names
            
        Example:
            >>> names = items_page.get_item_names()
        """
        names = []
        items = self.page.locator(self.ITEM_CARD).all()
        
        for item in items:
            name_element = item.locator(self.ITEM_NAME)
            names.append(name_element.text_content() or "")
        
        return names
    
    def click_item_by_name(self, item_name: str) -> None:
        """
        Click on item by name to view details.
        
        Args:
            item_name: Item name
            
        Example:
            >>> items_page.click_item_by_name("Test Item")
        """
        logger.info(f"Clicking item: {item_name}")
        
        # Find item card with this name
        item_card = self.page.locator(self.ITEM_CARD).filter(
            has_text=item_name
        ).first
        
        # Click view details button
        item_card.locator(self.VIEW_DETAILS_BUTTON).click()
        
        # Wait for modal or navigation
        self.page.wait_for_timeout(1000)
    
    def click_edit_item(self, item_name: str) -> None:
        """
        Click edit button for an item.
        
        Args:
            item_name: Item name
            
        Example:
            >>> items_page.click_edit_item("Test Item")
        """
        logger.info(f"Clicking edit for item: {item_name}")
        
        item_card = self.page.locator(self.ITEM_CARD).filter(
            has_text=item_name
        ).first
        
        item_card.locator(self.EDIT_BUTTON).click()
        self.wait_for_url("**/items/*/edit")
    
    def click_delete_item(self, item_name: str) -> None:
        """
        Click delete button for an item.
        
        Args:
            item_name: Item name
            
        Example:
            >>> items_page.click_delete_item("Test Item")
        """
        logger.info(f"Clicking delete for item: {item_name}")
        
        item_card = self.page.locator(self.ITEM_CARD).filter(
            has_text=item_name
        ).first
        
        item_card.locator(self.DELETE_BUTTON).click()
    
    def is_empty_state_visible(self) -> bool:
        """
        Check if empty state is displayed.
        
        Returns:
            True if empty state is visible
            
        Example:
            >>> if items_page.is_empty_state_visible():
            ...     print("No items found")
        """
        return self.is_visible(self.EMPTY_STATE)
    
    def click_next_page(self) -> None:
        """
        Click next page button.
        
        Example:
            >>> items_page.click_next_page()
        """
        logger.info("Clicking next page")
        self.click(self.NEXT_PAGE_BUTTON)
        self.wait_for_element(self.LOADING_SPINNER, state="hidden", timeout=5000)
    
    def click_prev_page(self) -> None:
        """
        Click previous page button.
        
        Example:
            >>> items_page.click_prev_page()
        """
        logger.info("Clicking previous page")
        self.click(self.PREV_PAGE_BUTTON)
        self.wait_for_element(self.LOADING_SPINNER, state="hidden", timeout=5000)
    
    def get_pagination_info(self) -> str:
        """
        Get pagination information text.
        
        Returns:
            Pagination info (e.g., "Showing 1-10 of 50")
            
        Example:
            >>> info = items_page.get_pagination_info()
        """
        return self.get_text(self.PAGINATION_INFO)
