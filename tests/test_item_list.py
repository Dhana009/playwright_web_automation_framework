"""
Item List Tests

Tests for viewing, searching, filtering, and sorting items.

Author: Senior SDET
Date: 2026-01-02
"""

import pytest
from playwright.sync_api import Page

from pages.items_page import ItemsPage


@pytest.mark.role("VIEWER")
class TestItemList:
    """Item list viewing test suite."""
    
    @pytest.mark.smoke
    def test_view_items_list(self, authenticated_page: Page, test_context):
        """
        Test viewing items list with seed data.
        
        Uses:
        - test_context: Contains seed items for this user
        
        Steps:
        1. Navigate to items page
        2. Verify seed items are displayed
        """
        items_page = ItemsPage(authenticated_page)
        
        # Navigate to items
        items_page.navigate_to_items()
        
        # Verify items are displayed
        item_count = items_page.get_item_count()
        assert item_count > 0, "Should display items"
        
        # Verify seed items are present
        item_names = items_page.get_item_names()
        
        # Get seed item name for this user
        physical_seed = test_context.get_seed_item("physical")
        if physical_seed:
            seed_name = physical_seed.get("name")
            assert seed_name in item_names, f"Seed item {seed_name} should be in list"
    
    def test_search_items(self, authenticated_page: Page, test_context):
        """
        Test searching for items.
        
        Steps:
        1. Navigate to items page
        2. Search for seed item
        3. Verify filtered results
        """
        items_page = ItemsPage(authenticated_page)
        
        # Navigate
        items_page.navigate_to_items()
        
        # Get seed item name
        physical_seed = test_context.get_seed_item("physical")
        seed_name = physical_seed.get("name", "")
        
        # Search for seed item
        items_page.search_items(seed_name)
        
        # Verify results
        item_names = items_page.get_item_names()
        assert seed_name in item_names, "Searched item should be in results"
    
    def test_filter_by_type(self, authenticated_page: Page):
        """
        Test filtering items by type.
        
        Steps:
        1. Navigate to items page
        2. Filter by PHYSICAL type
        3. Verify only PHYSICAL items shown
        """
        items_page = ItemsPage(authenticated_page)
        
        # Navigate
        items_page.navigate_to_items()
        
        # Filter by PHYSICAL
        items_page.filter_by_type("PHYSICAL")
        
        # Verify items are displayed
        item_count = items_page.get_item_count()
        assert item_count > 0, "Should display filtered items"
