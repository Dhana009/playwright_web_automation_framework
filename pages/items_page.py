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
    SEARCH_INPUT = '[data-testid="item-search"]'
    FILTER_STATUS_DROPDOWN = '[data-testid="filter-status"]'
    SORT_DROPDOWN = '[data-testid="sort-by"]'
    PAGE_SIZE_DROPDOWN = '[data-testid="page-size"]'
    CLEAR_FILTERS_BUTTON = '[data-testid="clear-filters"]'
    
    # Table
    ITEMS_TABLE = '[data-testid="items-table"]'
    TABLE_ROWS = 'tbody tr'
    PRICE_HEADER = "th:has-text('Price')"
    
    # Pagination
    PAGINATION_LIMIT = '[data-testid="pagination-limit"]'  # Page size dropdown
    PAGINATION_PAGE_BUTTON = '[data-testid="pagination-page-{page_num}"]'  # Page number button
    PAGINATION_NEXT = '[data-testid="pagination-next"]'  # Next button
    PAGINATION_PREV = '[data-testid="pagination-prev"]'  # Previous button
    
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
        self.navigate("/items")
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
        Search for items by name.
        
        Args:
            search_text: Text to search for
            
        Example:
            >>> items_page.search_items("SEED_")
        """
        logger.info(f"Searching for: {search_text}")
        if self.is_visible(self.SEARCH_INPUT):
            self.fill_text(self.SEARCH_INPUT, search_text)
            self.page.wait_for_timeout(1000)
        else:
            logger.warning("Search input not found")
    
    def set_page_size(self, size: str) -> None:
        """
        Set number of items per page.
        
        Args:
            size: Page size (10, 20, 50, 100)
            
        Example:
            >>> items_page.set_page_size("10")
        """
        logger.info(f"Setting page size to: {size}")
        if self.is_visible(self.PAGINATION_LIMIT):
            self.select_option(self.PAGINATION_LIMIT, size)
            self.page.wait_for_timeout(1000)
        else:
            logger.warning("Pagination limit dropdown not found")
    
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
    
    def sort_by_price(self) -> None:
        """
        Click price header to sort by price.
        
        Example:
            >>> items_page.sort_by_price()
        """
        logger.info("Sorting by price")
        price_header = self.page.locator(self.PRICE_HEADER)
        if price_header.count() > 0:
            price_header.click()
            self.page.wait_for_timeout(1000)
        else:
            logger.warning("Price column not found")
    
    def get_item_count(self) -> int:
        """
        Get number of items displayed in table.
        
        Returns:
            Number of items
            
        Example:
            >>> count = items_page.get_item_count()
        """
        return self.page.locator(self.TABLE_ROWS).count()
    
    def clear_filters(self) -> None:
        """
        Click clear filters button.
        
        Example:
            >>> items_page.clear_filters()
        """
        logger.info("Clearing filters")
        if self.is_visible(self.CLEAR_FILTERS_BUTTON):
            self.click(self.CLEAR_FILTERS_BUTTON)
            self.page.wait_for_timeout(1000)
        else:
            logger.warning("Clear filters button not found")
    
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
    
    def go_to_page(self, page_num: int) -> None:
        """
        Click page number button to navigate to specific page.
        
        Args:
            page_num: Page number to go to
            
        Example:
            >>> items_page.go_to_page(2)
        """
        logger.info(f"Going to page {page_num}")
        selector = self.PAGINATION_PAGE_BUTTON.format(page_num=page_num)
        if self.is_visible(selector):
            self.click(selector)
            self.page.wait_for_timeout(2000)
        else:
            logger.warning(f"Page {page_num} button not found or not visible")
    
    def click_next_page(self) -> None:
        """
        Click next page button.
        
        Example:
            >>> items_page.click_next_page()
        """
        logger.info("Clicking next page")
        if self.is_visible(self.PAGINATION_NEXT) and self.page.locator(self.PAGINATION_NEXT).is_enabled():
            self.click(self.PAGINATION_NEXT)
            self.page.wait_for_timeout(2000)
        else:
            logger.warning("Next page button not available or disabled")
    
    def click_prev_page(self) -> None:
        """
        Click previous page button.
        
        Example:
            >>> items_page.click_prev_page()
        """
        logger.info("Clicking previous page")
        if self.is_visible(self.PAGINATION_PREV) and self.page.locator(self.PAGINATION_PREV).is_enabled():
            self.click(self.PAGINATION_PREV)
            self.page.wait_for_timeout(2000)
        else:
            logger.warning("Previous page button not available or disabled")
    
    def get_pagination_info(self) -> str:
        """
        Get pagination information text.
        
        Returns:
            Pagination info (e.g., "Showing 1-10 of 50")
            
        Example:
            >>> info = items_page.get_pagination_info()
        """
        return self.get_text(self.PAGINATION_INFO)
