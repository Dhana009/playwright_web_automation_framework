"""
Complete API Test Suite

Test all CRUD operations for items to understand exact API behavior.

Author: Senior SDET
Date: 2026-01-02
"""

import requests

# Configuration
API_URL = "http://localhost:3000/api/v1"
EMAIL = "admin1@test.com"
PASSWORD = "Admin@123"


def get_token():
    """Get authentication token."""
    response = requests.post(
        f"{API_URL}/auth/login",
        json={"email": EMAIL, "password": PASSWORD}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["token"]


def test_create_physical_item(token):
    """Test creating PHYSICAL item."""
    print("\n=== TEST 1: Create PHYSICAL Item ===")
    
    data = {
        'name': 'Test Physical Item',
        'description': 'A test physical item with all required fields for validation',
        'item_type': 'PHYSICAL',
        'price': '99.99',
        'category': 'Electronics',
        'weight': '2.5',
        'length': '35',
        'width': '25',
        'height': '2'
    }
    
    response = requests.post(
        f"{API_URL}/items",
        headers={'Authorization': f'Bearer {token}'},
        data=data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    
    result = response.json()
    item_id = result.get('item_id')
    print(f"Created item ID: {item_id}")
    
    return item_id


def test_create_digital_item(token):
    """Test creating DIGITAL item."""
    print("\n=== TEST 2: Create DIGITAL Item ===")
    
    data = {
        'name': 'Test Digital Item',
        'description': 'A test digital item with download URL and file size',
        'item_type': 'DIGITAL',
        'price': '49.99',
        'category': 'Software',
        'download_url': 'https://example.com/download/file.zip',
        'file_size': '1048576'
    }
    
    response = requests.post(
        f"{API_URL}/items",
        headers={'Authorization': f'Bearer {token}'},
        data=data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 201
    return response.json().get('item_id')


def test_create_service_item(token):
    """Test creating SERVICE item."""
    print("\n=== TEST 3: Create SERVICE Item ===")
    
    data = {
        'name': 'Test Service Item',
        'description': 'A test service item with duration in hours',
        'item_type': 'SERVICE',
        'price': '150.00',
        'category': 'Consulting',
        'duration_hours': '8'
    }
    
    response = requests.post(
        f"{API_URL}/items",
        headers={'Authorization': f'Bearer {token}'},
        data=data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 201
    return response.json().get('item_id')


def test_get_all_items(token):
    """Test getting all items."""
    print("\n=== TEST 4: Get All Items ===")
    
    response = requests.get(
        f"{API_URL}/items",
        headers={'Authorization': f'Bearer {token}'}
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Total items: {len(result.get('data', []))}")
    
    assert response.status_code == 200
    return result.get('data', [])


def test_get_single_item(token, item_id):
    """Test getting single item."""
    print(f"\n=== TEST 5: Get Single Item {item_id} ===")
    
    response = requests.get(
        f"{API_URL}/items/{item_id}",
        headers={'Authorization': f'Bearer {token}'}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    return response.json().get('data')


def test_update_item(token, item_id):
    """Test updating item."""
    print(f"\n=== TEST 6: Update Item {item_id} ===")
    
    # First get current version
    get_response = requests.get(
        f"{API_URL}/items/{item_id}",
        headers={'Authorization': f'Bearer {token}'}
    )
    current_item = get_response.json().get('data')
    version = current_item.get('version', 1)
    
    print(f"Current version: {version}")
    
    # Update with version
    data = {
        'version': str(version),
        'name': 'Updated Item Name',
        'description': 'Updated description for the item with all required fields',
        'price': '199.99'
    }
    
    response = requests.put(
        f"{API_URL}/items/{item_id}",
        headers={'Authorization': f'Bearer {token}'},
        data=data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200


def test_delete_item(token, item_id):
    """Test deleting item."""
    print(f"\n=== TEST 7: Delete Item {item_id} ===")
    
    response = requests.delete(
        f"{API_URL}/items/{item_id}",
        headers={'Authorization': f'Bearer {token}'}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200


if __name__ == "__main__":
    print("=" * 60)
    print("COMPLETE API TEST SUITE")
    print("=" * 60)
    
    # Get token
    print("\n=== Getting Token ===")
    token = get_token()
    print(f"Token: {token[:50]}...")
    
    # Test CREATE operations
    physical_id = test_create_physical_item(token)
    digital_id = test_create_digital_item(token)
    service_id = test_create_service_item(token)
    
    # Test READ operations
    all_items = test_get_all_items(token)
    item_details = test_get_single_item(token, physical_id)
    
    # Test UPDATE operation
    test_update_item(token, physical_id)
    
    # Test DELETE operations
    test_delete_item(token, physical_id)
    test_delete_item(token, digital_id)
    test_delete_item(token, service_id)
    
    print("\n" + "=" * 60)
    print("ALL API TESTS PASSED!")
    print("=" * 60)
