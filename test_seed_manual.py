"""
Manual Seed Data Creation Test

Create seed data manually to verify the exact issue.
"""

import requests
from data.test_data import TestDataHelper

API_URL = "http://localhost:3000/api/v1"

# Login
response = requests.post(
    f"{API_URL}/auth/login",
    json={"email": "admin1@test.com", "password": "Admin@123"}
)
token = response.json()["token"]
print(f"Token: {token[:50]}...")

# Generate seed item data using TestDataHelper
item_data = TestDataHelper.generate_item_data(
    name="SEED_Physical_admin1",
    item_type="PHYSICAL",
    price=99.99
)

print(f"\nGenerated item data:")
for key, value in item_data.items():
    print(f"  {key}: {value}")

# Try to create it
print(f"\nCreating item...")
response = requests.post(
    f"{API_URL}/items",
    headers={'Authorization': f'Bearer {token}'},
    data=item_data  # Send as form data
)

print(f"\nStatus: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 201:
    print("\nSUCCESS!")
else:
    print("\nFAILED!")
