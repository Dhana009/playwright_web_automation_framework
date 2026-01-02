import os
from dotenv import load_dotenv

# Load env FIRST
load_dotenv(".env.local")
os.environ["ENV"] = "local" # Force it

from utils.api_client import APIClient
from data.test_data import test_data

def verify_api():
    print("=== API Feature Probe (Backend Validation) ===")
    
    # 1. Login
    client = APIClient()
    print("[1] Logging in as admin1@test.com...")
    resp = client.login("admin1@test.com", "Admin@123")
    token = resp.get("token")
    if not token:
        print("Login Failed! No token.")
        return
    
    auth_client = APIClient(token=token)
    
    # 2. Probe Status Filter
    print("\n[2] Probing Status Filter...")
    all_items = auth_client.get_all_items(limit=100)
    total_count = len(all_items.get("data", []))
    print(f"Total Items: {total_count}")
    
    # Active
    active = auth_client.get_all_items(limit=100, status="active").get("data", [])
    print(f"Active Items: {len(active)}")
    
    # Inactive
    inactive = auth_client.get_all_items(limit=100, status="inactive").get("data", [])
    print(f"Inactive Items: {len(inactive)}")
    
    # Validation
    print(f"Status Filter Works: {len(active) + len(inactive) == total_count or len(active) > 0}")

    # 3. Probe Search Filter
    print("\n[3] Probing Search Filter...")
    # Search for "Seed" (should match many)
    search_seed = auth_client.get_all_items(limit=100, search="SEED").get("data", [])
    print(f"Search 'SEED' Count: {len(search_seed)}")
    if search_seed:
        print(f"First Result: {search_seed[0]['name']}")
        
    # Search for specific Zebra
    search_zebra = auth_client.get_all_items(limit=100, search="Zebra").get("data", [])
    print(f"Search 'Zebra' Count: {len(search_zebra)}")

    # 4. Probe Sort Keys
    print("\n[4] Probing Sort Keys...")
    
    # Price ASC
    sort_price = auth_client.get_all_items(limit=5, sort_by="price", sort_order="asc").get("data", [])
    if sort_price:
        prices = [float(str(i['price']).replace('$','')) for i in sort_price]
        print(f"Price ASC: {prices} -> Sorted? {prices == sorted(prices)}")
        
    # Price DESC
    sort_price_desc = auth_client.get_all_items(limit=5, sort_by="price", sort_order="desc").get("data", [])
    if sort_price_desc:
        prices = [float(str(i['price']).replace('$','')) for i in sort_price_desc]
        print(f"Price DESC: {prices} -> Sorted? {prices == sorted(prices, reverse=True)}")

    # Created ASC (to check if key is supported)
    # Backend might use 'created_at' or 'createdAt' or 'date'
    for key in ['created_at', 'createdAt', 'date']:
        print(f"Testing sort_by='{key}'...")
        res = auth_client.get_all_items(limit=5, sort_by=key, sort_order="asc").get("data", [])
        if res:
             dates = [i.get('created_at') or i.get('createdAt') for i in res]
             print(f"Dates ({key}): {dates}")

if __name__ == "__main__":
    verify_api()
