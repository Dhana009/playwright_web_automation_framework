"""
Test Data Helpers

This module provides helper functions for test data generation and management.
Includes item data templates and seed data utilities.

Author: Senior SDET
Date: 2026-01-02
"""

import json
import uuid
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from config.settings import settings
from utils.logger import logger


class TestDataHelper:
    """Helper class for test data management."""
    
    @staticmethod
    def generate_item_data(
        name: str,
        item_type: str = "PHYSICAL",
        price: float = 100.00,
        is_active: bool = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate item data payload.
        
        Args:
            name: Item name
            item_type: Item type
            price: Item price
            is_active: Optional active status (true/false)
            **kwargs: Additional fields
            
        Returns:
            Item data dictionary
        """
        # Base required fields
        base_data = {
            "name": name,
            "description": f"Test item description for {name} with sufficient length for validation",
            "item_type": item_type,
            "price": price,
            "category": "TestCategory"
        }
        
        if is_active is not None:
            base_data["is_active"] = is_active
        
        # Add type-specific required fields (FLAT structure)
        if item_type == "PHYSICAL":
            base_data.update({
                "weight": 2.5,
                "length": 35,  #  Flat fields, not nested!
                "width": 25,
                "height": 2
            })
        elif item_type == "DIGITAL":
            base_data.update({
                "download_url": "https://example.com/download/file.zip",
                "file_size": 1048576  # 1 MB in bytes
            })
        elif item_type == "SERVICE":
            base_data.update({
                "duration_hours": 8
            })
        
        # Merge with any additional fields
        base_data.update(kwargs)
        
        return base_data
    
    @staticmethod
    def generate_seed_item_name(role: str, number: int, item_type: str) -> str:
        """
        Generate seed item name.
        
        Args:
            role: User role (admin, editor, viewer)
            number: User number (1-8)
            item_type: Item type (PHYSICAL, DIGITAL, SERVICE)
            
        Returns:
            Seed item name
            
        Example:
            >>> name = TestDataHelper.generate_seed_item_name("admin", 1, "PHYSICAL")
            >>> print(name)
            'SEED_Physical_admin1'
        """
        item_type_formatted = item_type.capitalize()
        return f"{settings.SEED_DATA_PREFIX}{item_type_formatted}_{role}{number}"
    
    @staticmethod
    def generate_transient_item_name(item_type: str) -> str:
        """
        Generate transient item name with UUID.
        
        Args:
            item_type: Item type
            
        Returns:
            Transient item name
            
        Example:
            >>> name = TestDataHelper.generate_transient_item_name("PHYSICAL")
            >>> print(name)
            'Transient_PHYSICAL_abc123...'
        """
        unique_id = str(uuid.uuid4())[:8]
        return f"Transient_{item_type}_{unique_id}"
    
    @staticmethod
    def load_users() -> Dict[str, List[Dict[str, Any]]]:
        """
        Load user data from JSON file.
        
        Returns:
            User data dictionary
            
        Example:
            >>> users = TestDataHelper.load_users()
            >>> admin_users = users["admin"]
        """
        users_file = Path("data/users.json")
        
        if not users_file.exists():
            raise FileNotFoundError(f"Users file not found: {users_file}")
        
        with open(users_file, 'r') as f:
            data = json.load(f)
        
        return data["users"]
    
    @staticmethod
    def get_user_by_email(email: str) -> Dict[str, Any]:
        """
        Get user data by email.
        
        Args:
            email: User email
            
        Returns:
            User data
            
        Example:
            >>> user = TestDataHelper.get_user_by_email("admin1@test.com")
            >>> print(user["role"])
            'ADMIN'
        """
        users = TestDataHelper.load_users()
        
        for role, user_list in users.items():
            for user in user_list:
                if user["email"] == email:
                    return user
        
        raise ValueError(f"User not found: {email}")
    
    @staticmethod
    def save_seed_data_ids(seed_data: Dict[str, Any]) -> None:
        """
        Save seed data IDs to file for reuse.
        
        Args:
            seed_data: Seed data dictionary
            
        Example:
            >>> TestDataHelper.save_seed_data_ids(seed_items)
        """
        seed_file = Path(settings.SEED_DATA_FILE)
        
        with open(seed_file, 'w') as f:
            json.dump(seed_data, f, indent=2)
        
        logger.info(f"Seed data IDs saved to {seed_file}")
    
    @staticmethod
    def load_seed_data_ids() -> Dict[str, Any]:
        """
        Load seed data IDs from file.
        
        Returns:
            Seed data dictionary
            
        Example:
            >>> seed_data = TestDataHelper.load_seed_data_ids()
        """
        seed_file = Path(settings.SEED_DATA_FILE)
        
        if not seed_file.exists():
            logger.warning(f"Seed data file not found: {seed_file}")
            return {}
        
        with open(seed_file, 'r') as f:
            data = json.load(f)
        
        logger.info(f"Loaded seed data IDs from {seed_file}")
        return data


# Export helper instance
test_data = TestDataHelper()
