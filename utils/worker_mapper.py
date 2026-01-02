"""
Worker Mapping Utilities

Handles mapping of pytest-xdist workers to users for parallel execution.

Author: Senior SDET
Date: 2026-01-02
"""

import os
from typing import Set

from config.settings import settings
from utils.logger import logger


class WorkerMapper:
    """
    Maps pytest workers to users for parallel execution.
    
    Industry Standard Pattern (Google, Netflix, Uber).
    """
    
    @staticmethod
    def get_worker_id() -> str:
        """
        Get current worker ID for parallel execution.
        
        Returns:
            Worker ID (e.g., "gw0", "gw1", or "master")
            
        Example:
            >>> WorkerMapper.get_worker_id()
            'gw0'
        """
        return os.getenv("PYTEST_XDIST_WORKER", "master")
    
    @staticmethod
    def extract_worker_number(worker_id: str) -> int:
        """
        Extract worker number from worker ID.
        
        Args:
            worker_id: Worker ID (e.g., "gw0", "gw1", "master")
            
        Returns:
            Worker number (0-7 for parallel, 0 for master)
            
        Example:
            >>> WorkerMapper.extract_worker_number("gw0")
            0
            >>> WorkerMapper.extract_worker_number("gw7")
            7
            >>> WorkerMapper.extract_worker_number("master")
            0
        """
        if worker_id == "master" or not worker_id.startswith("gw"):
            return 0
        return int(worker_id.replace("gw", ""))
    
    @staticmethod
    def get_user_for_worker(role: str, worker_id: str) -> str:
        """
        Map worker to user based on role and worker ID.
        
        Args:
            role: User role (ADMIN, EDITOR, VIEWER)
            worker_id: Worker ID
            
        Returns:
            User email
            
        Example:
            >>> WorkerMapper.get_user_for_worker("ADMIN", "gw0")
            'admin1@test.com'
            >>> WorkerMapper.get_user_for_worker("ADMIN", "gw7")
            'admin8@test.com'
        """
        worker_num = WorkerMapper.extract_worker_number(worker_id)
        user_num = (worker_num % 8) + 1  # Map to 1-8
        return settings.get_user_email(role, user_num)
    
    @staticmethod
    def determine_needed_users(test_items) -> Set[str]:
        """
        Determine which users are needed by selected tests (Lazy Loading).
        
        Args:
            test_items: List of pytest test items
            
        Returns:
            Set of user emails needed
            
        This is the key to lazy loading - only login users that tests need.
        For parallel execution, determines users based on worker count.
        """
        needed_users = set()
        roles_needed = set()
        
        # Determine which roles are needed
        for item in test_items:
            role_marker = item.get_closest_marker("role")
            role = role_marker.args[0] if role_marker else "ADMIN"
            roles_needed.add(role)
        
        # Get number of workers
        num_workers = settings.NUM_WORKERS
        
        # For each role needed, add users for all workers
        for role in roles_needed:
            for worker_num in range(num_workers):
                worker_id = f"gw{worker_num}"
                user_email = WorkerMapper.get_user_for_worker(role, worker_id)
                needed_users.add(user_email)
        
        logger.info(
            f"Determined {len(needed_users)} users needed for "
            f"{len(roles_needed)} roles across {num_workers} workers"
        )
        return needed_users
