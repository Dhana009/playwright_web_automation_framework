"""
Test API Client with Seed Data

Verify APIClient.create_item() works with seed data.
"""

from utils.api_client import APIClient
from data.test_data import TestDataHelper

# Login
client = APIClient()
response = client.login("admin1@test.com", "Admin@123")
token = response["token"]
print(f"Token: {token[:50]}...")

# Create client with token
client_with_token = APIClient(token=token)

# Generate seed item data
item_data = TestDataHelper.generate_item_data(
    name="SEED_Physical_admin1_test",
    item_type="PHYSICAL",
    price=99.99
)

print(f"\nGenerated item data:")
for key, value in item_data.items():
    print(f"  {key}: {value} ({type(value).__name__})")

# Create item using API client
print(f"\nCreating item via API client...")
try:
    response = client_with_token.create_item(item_data)
    print(f"\nSUCCESS!")
    print(f"Response: {response}")
    
    # Extract item ID
    item_id = response.get('item_id') or response.get('data', {}).get('_id')
    print(f"Item ID: {item_id}")
    
    # Cleanup
    if item_id:
        client_with_token.delete_item(item_id)
        print(f"Deleted item: {item_id}")
        
except Exception as e:
    print(f"\nFAILED: {e}")
