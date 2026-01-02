"""
Item Details Page Object

This module provides the page object for item details modal/page.
Handles viewing item details in modal or iframe.

Author: Senior SDET
Date: 2026-01-02
"""

from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logger import logger


class ItemDetailsPage(BasePage):
    """
    Item details modal/page object.
    
    Provides methods for viewing item details.
    
    Example:
        >>> details_page = ItemDetailsPage(page)
        >>> name = details_page.get_item_name()
        >>> details_page.close_modal()
    """
    
    # Modal
    MODAL = '[data-testid="item-details-modal"]'
    MODAL_CLOSE_BUTTON = '[data-testid="modal-close"]'
    
    # Item details
    ITEM_NAME = '[data-testid="detail-item-name"]'
    ITEM_DESCRIPTION = '[data-testid="detail-item-description"]'
    ITEM_TYPE = '[data-testid="detail-item-type"]'
    ITEM_PRICE = '[data-testid="detail-item-price"]'
    ITEM_QUANTITY = '[data-testid="detail-item-quantity"]'
    ITEM_STATUS = '[data-testid="detail-item-status"]'
    
    # Type-specific fields
    WEIGHT = '[data-testid="detail-weight"]'
    DIMENSIONS = '[data-testid="detail-dimensions"]'
    DOWNLOAD_URL = '[data-testid="detail-download-url"]'
    FILE_SIZE = '[data-testid="detail-file-size"]'
    DURATION = '[data-testid="detail-duration"]'
    SERVICE_TYPE = '[data-testid="detail-service-type"]'
    
    # Actions
    EDIT_BUTTON = '[data-testid="detail-edit-button"]'
    DELETE_BUTTON = '[data-testid="detail-delete-button"]'
    
    # Iframe
    IFRAME = '[data-testid="item-details-iframe"]'
    
    # Loading
    LOADING_SPINNER = '[data-testid="loading-spinner"]'
    
    def __init__(self, page: Page):
        """Initialize item details page."""
        super().__init__(page)
    
    def wait_for_modal(self) -> None:
        """
        Wait for details modal to appear.
        
        Example:
            >>> details_page.wait_for_modal()
        """
        logger.info("Waiting for item details modal")
        self.wait_for_element(self.MODAL, state="visible")
        self.wait_for_element(self.LOADING_SPINNER, state="hidden", timeout=5000)
    
    def close_modal(self) -> None:
        """
        Close details modal.
        
        Example:
            >>> details_page.close_modal()
        """
        logger.info("Closing item details modal")
        self.click(self.MODAL_CLOSE_BUTTON)
        self.wait_for_element(self.MODAL, state="hidden")
    
    def get_item_name(self) -> str:
        """
        Get item name from details.
        
        Returns:
            Item name
            
        Example:
            >>> name = details_page.get_item_name()
        """
        return self.get_text(self.ITEM_NAME)
    
    def get_item_description(self) -> str:
        """
        Get item description.
        
        Returns:
            Item description
        """
        return self.get_text(self.ITEM_DESCRIPTION)
    
    def get_item_type(self) -> str:
        """
        Get item type.
        
        Returns:
            Item type
        """
        return self.get_text(self.ITEM_TYPE)
    
    def get_item_price(self) -> str:
        """
        Get item price.
        
        Returns:
            Item price
        """
        return self.get_text(self.ITEM_PRICE)
    
    def get_item_status(self) -> str:
        """
        Get item status.
        
        Returns:
            Item status (ACTIVE/INACTIVE)
        """
        return self.get_text(self.ITEM_STATUS)
    
    def click_edit(self) -> None:
        """
        Click edit button in details modal.
        
        Example:
            >>> details_page.click_edit()
        """
        logger.info("Clicking edit button")
        self.click(self.EDIT_BUTTON)
        self.wait_for_url("**/items/*/edit")
    
    def click_delete(self) -> None:
        """
        Click delete button in details modal.
        
        Example:
            >>> details_page.click_delete()
        """
        logger.info("Clicking delete button")
        self.click(self.DELETE_BUTTON)
    
    def switch_to_iframe(self) -> None:
        """
        Switch context to iframe (if details shown in iframe).
        
        Example:
            >>> details_page.switch_to_iframe()
        """
        logger.info("Switching to iframe")
        iframe_element = self.page.frame_locator(self.IFRAME)
        # Future: Handle iframe context if needed
    
    def is_modal_visible(self) -> bool:
        """
        Check if modal is visible.
        
        Returns:
            True if modal is visible
            
        Example:
            >>> if details_page.is_modal_visible():
            ...     print("Modal is open")
        """
        return self.is_visible(self.MODAL)
