"""
Cleanup Seed Data

Delete all items starting with SEED_ to ensure a clean state.
"""

import requests

API_URL = "http://localhost:3000/api/v1"
EMAIL = "admin1@test.com"
PASSWORD = "Admin@123"

def get_token():
    response = requests.post(f"{API_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD})
    return response.json()["token"]

def cleanup():
    print("Cleaning up seed data...")
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_URL}/items", headers=headers)
    items = response.json().get('data', [])
    
    count = 0
    for item in items:
        if item['name'].startswith("SEED_"):
            print(f"Deleting {item['name']}...")
            requests.delete(f"{API_URL}/items/{item['_id']}", headers=headers)
            count += 1
            
    print(f"Deleted {count} seed items.")

if __name__ == "__main__":
    cleanup()
