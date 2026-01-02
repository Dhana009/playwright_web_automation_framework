"""
Simple test using working API code

This test uses the EXACT same code that worked in test_api_direct.py
"""

import pytest
from playwright.sync_api import Page
import requests

from config.settings import settings


def test_create_item_simple(authenticated_page: Page, test_context):
    """Test using the working API code directly."""
    print("\n=== Simple API Test ===")
    print(f"User: {test_context.user_email}")
    print(f"Token: {test_context.auth_token[:50]}...")
    
    # FIRST: Validate token works
    print("\nValidating token...")
    validate_response = requests.get(
        f"{settings.API_BASE_URL}/items",
        headers={'Authorization': f'Bearer {test_context.auth_token}'}
    )
    print(f"Token validation status: {validate_response.status_code}")
    if validate_response.status_code != 200:
        print(f"Token validation failed: {validate_response.text}")
        pytest.fail("Token is invalid!")
    
    # Use the EXACT code that worked in test_api_direct.py
    data = {
        'name': 'Test Laptop Simple',
        'description': 'A high-performance laptop for testing purposes with all required features',
        'item_type': 'PHYSICAL',
        'price': '999.99',
        'category': 'Electronics',
        'weight': '2.5',
        'length': '35',
        'width': '25',
        'height': '2'
    }
    
    print(f"\nSending data: {data}")
    
    response = requests.post(
        f"{settings.API_BASE_URL}/items",
        headers={'Authorization': f'Bearer {test_context.auth_token}'},
        data=data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    
    # Cleanup
    result = response.json()
    item_id = result.get('item_id')
    if item_id:
        requests.delete(
            f"{settings.API_BASE_URL}/items/{item_id}",
            headers={'Authorization': f'Bearer {test_context.auth_token}'}
        )
        print(f"Deleted item: {item_id}")
