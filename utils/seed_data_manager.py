"""
Seed Data Manager

Handles seed data creation and management for tests.

Author: Senior SDET
Date: 2026-01-02
"""

from typing import Dict, Any

from config.settings import settings
from utils.logger import logger
from utils.api_client import APIClient
from utils.exceptions import SeedDataException
from data.test_data import test_data


class SeedDataManager:
    """
    Manages seed data creation and lifecycle.
    
    Industry Standard Pattern (Google, Netflix, Uber).
    """
    
    @staticmethod
    def check_existing_seed_items(
        user_email: str,
        token: str
    ) -> Dict[str, Any]:
        """
        Check if seed items already exist for user.
        
        Args:
            user_email: User email
            token: Auth token
            
        Returns:
            Dictionary with existing seed items (if found)
        """
        client = APIClient(token=token)
        seed_items = {}
        
        try:
            # Get user info for seed item names
            user = test_data.get_user_by_email(user_email)
            role = user["role"].lower()
            number = user["number"]
            
            # Search specifically for this user's seed items
            # This avoids pagination issues and is much more efficient
            search_term = f"SEED_"  # Or more specific if API supports it
            
            response = client.get_all_items(limit=100, search=search_term)
            # API can return items in 'data' or 'items' depending on query
            all_items = response.get("data", response.get("items", []))
            
            # Check for each seed item type
            for item_type in ["PHYSICAL", "DIGITAL", "SERVICE"]:
                expected_name = test_data.generate_seed_item_name(
                    role, number, item_type
                )
                
                # Find item with this name
                for item in all_items:
                    if item.get("name") == expected_name:
                        seed_items[item_type.lower()] = item
                        logger.debug(f"Found existing seed item: {expected_name}")
                        break
            
            return seed_items
            
        except Exception as e:
            logger.warning(f"Failed to check existing seed items: {e}")
            return {}
    
    @staticmethod
    def create_seed_items_for_user(
        user_email: str,
        token: str
    ) -> Dict[str, Any]:
        """
        Create or reuse seed items for a user (OPTION B: Per-test, just-in-time).
        
        Strategy by Role:
        - ADMIN: Create once in admin1, all admins share (no filter on data)
        - EDITOR: Create specifically for each editor (filtered by created_by)
        - VIEWER: No creation needed (read-only, no create permissions)
        
        Args:
            user_email: User email
            token: Auth token
            
        Returns:
            Dictionary with seed items (empty dict for viewers)
        """
        client = APIClient(token=token)
        seed_items = {}
        
        # Get user info
        user = test_data.get_user_by_email(user_email)
        role = user["role"].lower()
        number = user["number"]
        
        logger.info(f"Initializing seed data for {user_email} ({role})")
        
        # ========================================================================
        # STEP 1: SKIP VIEWERS - They have no create permissions and can see all data
        # ========================================================================
        if role == "viewer":
            logger.info(f"[VIEWER] No seed data creation needed for {user_email}")
            logger.info(f"[VIEWER] Will view existing items (admin + editor data)")
            return {}
        
        # ========================================================================
        # STEP 2: ADMIN STRATEGY - Create once (in admin1), all admins share
        # ========================================================================
        if role == "admin":
            # Only admin1 creates the shared items
            if "admin1" in user_email:
                logger.info(f"[ADMIN1] Creating shared seed items")
                SeedDataManager._create_admin_base_items(client, seed_items)
            else:
                # Other admins (admin2, admin3, etc) don't create - just verify items exist
                logger.info(f"[ADMIN{number}] Reusing items created by admin1")
                # They can see all items anyway since ADMIN has no filter
        
        # ========================================================================
        # STEP 3: EDITOR STRATEGY - Create specifically for this editor
        # ========================================================================
        if role == "editor":
            logger.info(f"[EDITOR{number}] Creating editor-specific seed items")
            SeedDataManager._create_editor_items(client, user_email, seed_items)
        
        logger.info(f"Seed data ready for {user_email}: {len(seed_items)} items")
        return seed_items
    
    @staticmethod
    def _create_admin_base_items(client, seed_items_dict):
        """
        Create base seed items for ADMIN (called only by admin1).
        These are shared across ALL admins since ADMIN has no filter.
        """
        for item_type in ["PHYSICAL", "DIGITAL", "SERVICE"]:
            key = item_type.lower()
            name = f"SEED_{item_type}_admin1"
            item_data = test_data.generate_item_data(name=name, item_type=item_type)
            SeedDataManager._create_safe(client, item_data, seed_items_dict, key)
    
    @staticmethod
    def _create_editor_items(client, user_email, seed_items_dict):
        """
        Create editor-specific seed items.
        Items are marked with created_by=editor_id so only this editor sees them.
        """
        user = test_data.get_user_by_email(user_email)
        number = user["number"]
        
        for item_type in ["PHYSICAL", "DIGITAL", "SERVICE"]:
            key = item_type.lower()
            name = f"SEED_{item_type}_editor{number}"
            item_data = test_data.generate_item_data(name=name, item_type=item_type)
            SeedDataManager._create_safe(client, item_data, seed_items_dict, key)

    @staticmethod
    def _create_safe(client, item_data, seed_items_dict, key):
        """Helper to create item handling 409s (conflict = already exists) and rate limits."""
        import time
        try:
            time.sleep(0.05)  # Rate limit protection
            response = client.create_item(item_data)
            created = response.get('data', response)
            seed_items_dict[key] = created
            logger.info(f"Created: {item_data['name']}")
        except Exception as e:
            # Handle 409 Conflict: Item already exists
            if "409" in str(e) or "Conflict" in str(e):
                logger.debug(f"Item exists (409): {item_data['name']}, fetching existing...")
                try:
                    # Determine search status based on item state
                    status_param = "inactive" if item_data.get("is_active") is False else "active"
                    res = client.get_all_items(search=item_data['name'], status=status_param)
                    items = res.get("data", res.get("items", []))
                    
                    # Find the exact item by name
                    existing = next((i for i in items if i["name"] == item_data['name']), None)
                    if existing:
                        seed_items_dict[key] = existing
                        logger.info(f"Reused existing: {item_data['name']}")
                    else:
                        logger.warning(f"Could not find existing item: {item_data['name']}")
                except Exception as fetch_error:
                    logger.warning(f"Failed to fetch existing item {item_data['name']}: {fetch_error}")
            else:
                # Other errors - log and skip
                logger.warning(f"Failed to create {item_data['name']}: {str(e)[:100]}")


