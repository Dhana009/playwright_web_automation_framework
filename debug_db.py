import requests
import json

API_URL = "http://localhost:3000/api/v1"

# Login
# Note: admin1@test.com is the user we are using in tests
resp = requests.post(f"{API_URL}/auth/login", 
    json={"email":"admin1@test.com","password":"Admin@123"})
token = resp.json()['token']

print("=" * 60)
print("DATABASE INSPECTION")
print("=" * 60)

# Get all items (limit 200 to be safe)
response = requests.get(
    f"{API_URL}/items?limit=200",
    headers={"Authorization": f"Bearer {token}"}
)

print(f"Response Status: {response.status_code}")
try:
    all_items = response.json()
    print("Response Keys:", all_items.keys())
    # Handle both structures
    items_list = all_items.get('data', all_items.get('items', []))
    print(f"\n✅ TOTAL ITEMS: {len(items_list)}")
except Exception as e:
    print(f"Failed to parse response: {e}")
    print(response.text)
    exit(1)

# Find SEED items
seed_items = [i for i in items_list if 'SEED_' in i['name']]
print(f"📦 SEED ITEMS: {len(seed_items)}")

for item in seed_items:
    print(f"\n  Name: {item['name']}")
    print(f"  Category: {item['category']}")
    print(f"  Active: {item['is_active']}")
    print(f"  ID: {item['_id']}")
    print(f"  Created By: {item['created_by']}")

# Try to create one
print("\n" + "=" * 60)
print("ATTEMPTING TO CREATE SEED ITEM")
print("=" * 60)

data = {
    'name': 'SEED_Physical_admin1',
    'description': 'Seed item for testing with required description length',
    'item_type': 'PHYSICAL',
    'price': '999.99',
    'category': 'Electronics',
    'weight': '2.5',
    'length': '35',
    'width': '25',
    'height': '2'
}

resp = requests.post(
    f"{API_URL}/items",
    headers={"Authorization": f"Bearer {token}"},
    data=data
)

print(f"\nStatus: {resp.status_code}")
try:
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
except:
    print(f"Response Text: {resp.text}")

if resp.status_code == 409:
    print("\n⚠️ 409 CONFLICT DETECTED!")
    # Check which item is blocking
    blocking = [i for i in items_list 
                if i['name'].lower() == data['name'].lower()]
    if blocking:
        print(f"Blocking item: {blocking[0]['_id']}")
        print(f"Created by: {blocking[0]['created_by']}")
        
        # Try to delete blocking item
        print(f"\nAttempting to delete blocking item {blocking[0]['_id']}...")
        del_resp = requests.delete(
            f"{API_URL}/items/{blocking[0]['_id']}",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"Delete Status: {del_resp.status_code}")
