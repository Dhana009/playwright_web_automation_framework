"""
Simple API Test Script

Test the API directly without Playwright to verify it works.

Usage:
    python test_api_direct.py
"""

import requests

# Configuration
API_URL = "http://localhost:3000/api/v1"
EMAIL = "admin1@test.com"  #  Fixed
PASSWORD = "Admin@123"

def test_login():
    """Test login and get token."""
    print("\n=== Step 1: Testing Login ===")
    
    response = requests.post(
        f"{API_URL}/auth/login",
        json={
            "email": EMAIL,
            "password": PASSWORD
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        token = response.json().get("token")
        print(f"\n Login successful!")
        print(f"Token: {token[:50]}...")
        return token
    else:
        print(f"\n Login failed!")
        return None


def test_create_physical_item(token):
    """Test creating a PHYSICAL item."""
    print("\n=== Step 2: Testing Create PHYSICAL Item ===")
    
    # Prepare form data (exactly as curl -F does)
    data = {
        'name': 'Test Laptop',
        'description': 'A high-performance laptop for testing purposes with all required features',
        'item_type': 'PHYSICAL',
        'price': '999.99',
        'category': 'Electronics',
        'weight': '2.5',
        'length': '35',
        'width': '25',
        'height': '2'
    }
    
    print(f"Sending data: {data}")
    
    response = requests.post(
        f"{API_URL}/items",
        headers={'Authorization': f'Bearer {token}'},
        data=data  #  multipart/form-data
    )
    
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        result = response.json()
        print(f"\n Item created successfully!")
        print(f"Item ID: {result.get('item_id')}")
        return result.get('item_id')
    else:
        print(f"\n Item creation failed!")
        try:
            error = response.json()
            print(f"Error: {error}")
        except:
            print(f"Raw response: {response.text}")
        return None


def test_get_items(token):
    """Test getting all items."""
    print("\n=== Step 3: Testing Get Items ===")
    
    response = requests.get(
        f"{API_URL}/items",
        headers={'Authorization': f'Bearer {token}'}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        items = result.get('data', [])
        print(f"\n Got {len(items)} items")
        return items
    else:
        print(f"\n Failed to get items")
        return []


def test_delete_item(token, item_id):
    """Test deleting an item."""
    print(f"\n=== Step 4: Testing Delete Item {item_id} ===")
    
    response = requests.delete(
        f"{API_URL}/items/{item_id}",
        headers={'Authorization': f'Bearer {token}'}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"\n Item deleted successfully!")
    else:
        print(f"\n Failed to delete item")


if __name__ == "__main__":
    print("=" * 60)
    print("API Direct Test Script")
    print("=" * 60)
    
    # Step 1: Login
    token = test_login()
    
    if not token:
        print("\n Cannot proceed without token. Check if backend is running.")
        exit(1)
    
    # Step 2: Create item
    item_id = test_create_physical_item(token)
    
    if not item_id:
        print("\n Item creation failed. Check error message above.")
        exit(1)
    
    # Step 3: Get items
    items = test_get_items(token)
    
    # Step 4: Delete item
    if item_id:
        test_delete_item(token, item_id)
    
    print("\n" + "=" * 60)
    print(" All tests completed!")
    print("=" * 60)
