"""
Test Full Architecture with Seed Data

Verify that seed data creation and test_context work correctly.
"""

import pytest
from playwright.sync_api import Page


@pytest.mark.role("ADMIN")
def test_seed_data_available(authenticated_page: Page, test_context):
    """
    Test that seed data is created and available in test_context.
    
    This verifies the full architecture is working:
    - Auth states created
    - Seed data created for ADMIN/EDITOR users
    - Test context populated
    
    Note: VIEWER users don't get seed data (no create permissions)
    """
    print(f"\n=== Testing Full Architecture ===")
    print(f"User: {test_context.user_email}")
    print(f"Role: {test_context.user_role}")
    print(f"Worker: {test_context.worker_id}")
    print(f"Token: {test_context.auth_token[:50]}...")
    
    # Check seed items
    print(f"\nSeed items: {list(test_context.seed_items.keys())}")
    
    # ADMIN and EDITOR should have seed items
    if test_context.user_role in ["ADMIN", "EDITOR"]:
        # Verify we have all 3 seed items
        assert 'physical' in test_context.seed_items, "Should have physical seed item"
        assert 'digital' in test_context.seed_items, "Should have digital seed item"
        assert 'service' in test_context.seed_items, "Should have service seed item"
        
        # Print seed item details
        for item_type, item in test_context.seed_items.items():
            print(f"\n{item_type.upper()} seed item:")
            print(f"  Name: {item.get('name')}")
            print(f"  ID: {item.get('_id')}")
    else:
        # VIEWER users don't have seed data
        print("\nVIEWER user - no seed data (expected)")
        assert len(test_context.seed_items) == 0, "VIEWER should not have seed items"
    
    print("\nFull architecture working correctly!")
