"""
Item Create/Edit Page Object

This module provides the page object for item creation and editing.
Handles form filling, validation, and submission.

Author: Senior SDET
Date: 2026-01-02
"""

from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logger import logger


class ItemFormPage(BasePage):
    """
    Item create/edit form page object.
    
    Provides methods for item creation and editing.
    
    Example:
        >>> form_page = ItemFormPage(page)
        >>> form_page.fill_item_form(name="Test Item", item_type="PHYSICAL", price=99.99)
        >>> form_page.submit_form()
    """
    
    # Form fields
    NAME_INPUT = '[data-testid="item-name"]'
    DESCRIPTION_INPUT = '[data-testid="item-description"]'
    ITEM_TYPE_DROPDOWN = '[data-testid="item-type"]'
    PRICE_INPUT = '[data-testid="item-price"]'
    QUANTITY_INPUT = '[data-testid="item-quantity"]'
    
    # Conditional fields (PHYSICAL)
    WEIGHT_INPUT = '[data-testid="item-weight"]'
    DIMENSIONS_INPUT = '[data-testid="item-dimensions"]'
    
    # Conditional fields (DIGITAL)
    DOWNLOAD_URL_INPUT = '[data-testid="download-url"]'
    FILE_SIZE_INPUT = '[data-testid="file-size"]'
    
    # Conditional fields (SERVICE)
    DURATION_INPUT = '[data-testid="service-duration"]'
    SERVICE_TYPE_INPUT = '[data-testid="service-type"]'
    
    # File upload
    FILE_UPLOAD_INPUT = '[data-testid="file-upload"]'
    
    # Buttons
    SUBMIT_BUTTON = '[data-testid="submit-button"]'
    CANCEL_BUTTON = '[data-testid="cancel-button"]'
    
    # Validation
    ERROR_MESSAGE = '[data-testid="error-message"]'
    FIELD_ERROR = '[data-testid="field-error"]'
    
    # Toast
    SUCCESS_TOAST = '[data-testid="success-toast"]'
    
    def __init__(self, page: Page):
        """Initialize item form page."""
        super().__init__(page)
    
    def navigate_to_create(self) -> None:
        """
        Navigate to item creation page.
        
        Example:
            >>> form_page.navigate_to_create()
        """
        self.navigate("/items/create")
        logger.info("Navigated to item creation page")
    
    def fill_item_form(
        self,
        name: str,
        item_type: str,
        price: float,
        description: str = None,
        quantity: int = 10,
        **kwargs
    ) -> None:
        """
        Fill item form with data.
        
        Args:
            name: Item name
            item_type: Item type (PHYSICAL, DIGITAL, SERVICE)
            price: Item price
            description: Item description (optional)
            quantity: Item quantity (default: 10)
            **kwargs: Additional type-specific fields
            
        Example:
            >>> form_page.fill_item_form(
            ...     name="Laptop",
            ...     item_type="PHYSICAL",
            ...     price=999.99,
            ...     weight=2.5,
            ...     dimensions="15x10x1"
            ... )
        """
        logger.info(f"Filling item form: {name}")
        
        # Fill common fields
        self.fill_text(self.NAME_INPUT, name)
        
        if description:
            self.fill_text(self.DESCRIPTION_INPUT, description)
        
        self.select_option(self.ITEM_TYPE_DROPDOWN, item_type)
        self.fill_text(self.PRICE_INPUT, str(price))
        self.fill_text(self.QUANTITY_INPUT, str(quantity))
        
        # Fill type-specific fields
        if item_type == "PHYSICAL":
            if "weight" in kwargs:
                self.fill_text(self.WEIGHT_INPUT, str(kwargs["weight"]))
            if "dimensions" in kwargs:
                self.fill_text(self.DIMENSIONS_INPUT, kwargs["dimensions"])
                
        elif item_type == "DIGITAL":
            if "download_url" in kwargs:
                self.fill_text(self.DOWNLOAD_URL_INPUT, kwargs["download_url"])
            if "file_size" in kwargs:
                self.fill_text(self.FILE_SIZE_INPUT, kwargs["file_size"])
                
        elif item_type == "SERVICE":
            if "duration" in kwargs:
                self.fill_text(self.DURATION_INPUT, kwargs["duration"])
            if "service_type" in kwargs:
                self.fill_text(self.SERVICE_TYPE_INPUT, kwargs["service_type"])
    
    def upload_file(self, file_path: str) -> None:
        """
        Upload file attachment.
        
        Args:
            file_path: Path to file
            
        Example:
            >>> form_page.upload_file("test.pdf")
        """
        logger.info(f"Uploading file: {file_path}")
        self.upload_file(self.FILE_UPLOAD_INPUT, file_path)
    
    def submit_form(self) -> None:
        """
        Submit the form.
        
        Example:
            >>> form_page.submit_form()
        """
        logger.info("Submitting form")
        self.click(self.SUBMIT_BUTTON)
    
    def cancel_form(self) -> None:
        """
        Cancel form and go back.
        
        Example:
            >>> form_page.cancel_form()
        """
        logger.info("Canceling form")
        self.click(self.CANCEL_BUTTON)
    
    def is_success_toast_visible(self) -> bool:
        """
        Check if success toast is displayed.
        
        Returns:
            True if success toast is visible
            
        Example:
            >>> if form_page.is_success_toast_visible():
            ...     print("Item created successfully")
        """
        return self.is_visible(self.SUCCESS_TOAST)
    
    def get_error_message(self) -> str:
        """
        Get form error message.
        
        Returns:
            Error message text
            
        Example:
            >>> error = form_page.get_error_message()
        """
        if self.is_visible(self.ERROR_MESSAGE):
            return self.get_text(self.ERROR_MESSAGE)
        return ""
    
    def get_field_error(self, field_name: str) -> str:
        """
        Get field-specific error message.
        
        Args:
            field_name: Field name
            
        Returns:
            Field error message
            
        Example:
            >>> error = form_page.get_field_error("name")
        """
        field_error = f'{self.FIELD_ERROR}[data-field="{field_name}"]'
        if self.is_visible(field_error):
            return self.get_text(field_error)
        return ""
