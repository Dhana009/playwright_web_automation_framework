"""
Item Creation Tests

Tests for creating items with different types and validation.

Author: Senior SDET
Date: 2026-01-02
"""

import pytest
from playwright.sync_api import Page

from pages.items_page import ItemsPage
from pages.item_form_page import ItemFormPage
from data.test_data import test_data
from utils.api_client import APIClient


@pytest.mark.role("ADMIN")
class TestItemCreation:
    """Item creation test suite."""
    
    @pytest.mark.smoke
    def test_create_physical_item(self, authenticated_page: Page, test_context):
        """
        Test creating a PHYSICAL item.
        
        Uses:
        - authenticated_page: Pre-authenticated page
        - test_context: User context with auth token
        
        Steps:
        1. Navigate to items page
        2. Click create item
        3. Fill form with PHYSICAL item data
        4. Submit form
        5. Verify item created
        6. Cleanup: Delete item via API
        """
        items_page = ItemsPage(authenticated_page)
        form_page = ItemFormPage(authenticated_page)
        
        # Generate transient item data
        item_name = test_data.generate_transient_item_name("PHYSICAL")
        
        # Navigate and create
        items_page.navigate_to_items()
        items_page.click_create_item()
        
        # Fill form
        form_page.fill_item_form(
            name=item_name,
            item_type="PHYSICAL",
            price=99.99,
            description="Test physical item",
            weight=2.5,
            dimensions="10x10x10"
        )
        
        # Submit
        form_page.submit_form()
        
        # Verify success
        assert form_page.is_success_toast_visible(), "Success toast should be displayed"
        
        # Verify redirect to items list
        assert "/dashboard" in authenticated_page.url, "Should redirect to dashboard"
        
        # Cleanup: Delete via API
        client = APIClient(token=test_context.auth_token)
        response = client.get_all_items()
        items = response.get("items", [])
        
        # Find and delete the created item
        for item in items:
            if item.get("name") == item_name:
                client.delete_item(item["id"])
                break
    
    def test_create_digital_item(self, authenticated_page: Page, test_context):
        """
        Test creating a DIGITAL item.
        
        Steps:
        1. Navigate to create page
        2. Fill form with DIGITAL item data
        3. Submit form
        4. Verify item created
        5. Cleanup
        """
        form_page = ItemFormPage(authenticated_page)
        
        # Generate item data
        item_name = test_data.generate_transient_item_name("DIGITAL")
        
        # Navigate
        form_page.navigate_to_create()
        
        # Fill form
        form_page.fill_item_form(
            name=item_name,
            item_type="DIGITAL",
            price=49.99,
            description="Test digital item",
            download_url="https://example.com/download",
            file_size="100MB"
        )
        
        # Submit
        form_page.submit_form()
        
        # Verify success
        assert form_page.is_success_toast_visible(), "Success toast should be displayed"
        
        # Cleanup
        client = APIClient(token=test_context.auth_token)
        response = client.get_all_items()
        items = response.get("items", [])
        
        for item in items:
            if item.get("name") == item_name:
                client.delete_item(item["id"])
                break
    
    def test_create_item_with_missing_required_fields(self, authenticated_page: Page):
        """
        Test validation when required fields are missing.
        
        Steps:
        1. Navigate to create page
        2. Leave required fields empty
        3. Submit form
        4. Verify validation errors
        """
        form_page = ItemFormPage(authenticated_page)
        
        # Navigate
        form_page.navigate_to_create()
        
        # Submit without filling required fields
        form_page.submit_form()
        
        # Verify still on create page (validation failed)
        assert "/items/create" in authenticated_page.url, "Should stay on create page"
        
        # Verify error message
        error = form_page.get_error_message()
        assert len(error) > 0 or form_page.is_visible(form_page.FIELD_ERROR), \
            "Validation error should be displayed"
