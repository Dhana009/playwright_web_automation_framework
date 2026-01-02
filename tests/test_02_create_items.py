"""
Test 2: Item Creation (Following Architecture)

Using authenticated_page and test_context fixtures as designed.

Author: Senior SDET
Date: 2026-01-02
"""

import pytest
from playwright.sync_api import Page
import uuid

from config.settings import settings
from utils.api_client import APIClient
from utils.file_generator import file_generator
import os


@pytest.mark.role("ADMIN")
class TestItemCreationAdmin:
    """Item creation tests for ADMIN role."""
    
    def test_create_physical_item(self, authenticated_page: Page, test_context):
        """
        TC-CREATE-001: Create PHYSICAL Item with Valid Data (ADMIN)
        
        Uses fixtures:
        - authenticated_page: Already logged in as admin1@test.com
        - test_context: Has user info and auth token
        """
        print("\n=== TC-CREATE-001: Create PHYSICAL Item (ADMIN) ===")
        print(f"User: {test_context.user_email}")
        print(f"Worker: {test_context.worker_id}")
        
        page = authenticated_page
        
        # Navigate to create page
        print("1. Navigating to /items/create...")
        page.goto(f"{settings.BASE_URL}/items/create")
        page.wait_for_load_state("networkidle")
        
        # Fill form
        print("2. Filling form...")
        item_name = f"Test Physical Item {uuid.uuid4().hex[:8]}"
        
        page.fill('[data-testid="item-name"]', item_name)
        page.fill('[data-testid="item-description"]', "This is a test physical item description")
        page.select_option('[data-testid="item-type"]', "PHYSICAL")
        
        page.wait_for_selector('[data-testid="physical-fields"]', state="visible", timeout=5000)
        
        page.fill('[data-testid="item-price"]', "99.99")
        page.fill('[data-testid="item-category"]', "Electronics")
        page.fill('[data-testid="item-weight"]', "2.5")
        page.fill('[data-testid="item-dimension-length"]', "30")
        page.fill('[data-testid="item-dimension-width"]', "20")
        page.fill('[data-testid="item-dimension-height"]', "10")
        
        print("    All fields filled")
        
        # Submit
        print("3. Submitting form...")
        page.click('[data-testid="create-item-submit"]')
        
        # Verify
        print("4. Verifying success...")
        page.wait_for_selector('[data-testid="toast-success"]', state="visible", timeout=10000)
        print("    Item created successfully")
        
        # Cleanup using test_context token
        print("5. Cleaning up...")
        api_client = APIClient(token=test_context.auth_token)
        response = api_client.get_all_items()
        items = response.get("items", [])
        
        for item in items:
            if item.get("name") == item_name:
                api_client.delete_item(item.get("_id"))
                print(f"    Deleted item")
                break
        
        print("\n Test PASSED: TC-CREATE-001\n")
    
    def test_create_service_item(self, authenticated_page: Page, test_context):
        """
        TC-CREATE-003: Create SERVICE Item with Valid Data (ADMIN)
        """
        print("\n=== TC-CREATE-003: Create SERVICE Item (ADMIN) ===")
        print(f"User: {test_context.user_email}")
        
        page = authenticated_page
        
        # Navigate
        page.goto(f"{settings.BASE_URL}/items/create")
        page.wait_for_load_state("networkidle")
        
        # Fill form
        item_name = f"Test Service Item {uuid.uuid4().hex[:8]}"
        
        page.fill('[data-testid="item-name"]', item_name)
        page.fill('[data-testid="item-description"]', "This is a test service item")
        page.select_option('[data-testid="item-type"]', "SERVICE")
        
        page.wait_for_selector('[data-testid="service-fields"]', state="visible", timeout=5000)
        
        page.fill('[data-testid="item-price"]', "150.00")
        page.fill('[data-testid="item-category"]', "Consulting")
        page.fill('[data-testid="item-duration-hours"]', "8")
        
        # Submit
        page.click('[data-testid="create-item-submit"]')
        
        # Verify
        page.wait_for_selector('[data-testid="toast-success"]', state="visible", timeout=10000)
        print("    Item created successfully")
        
        # Cleanup
        api_client = APIClient(token=test_context.auth_token)
        response = api_client.get_all_items()
        items = response.get("items", [])
        
        for item in items:
            if item.get("name") == item_name:
                api_client.delete_item(item.get("_id"))
                break
        
        print("\n Test PASSED: TC-CREATE-003\n")

    def test_create_item_invalid_data(self, authenticated_page: Page, test_context):
        """
        TC-CREATE-004: Create Item with Invalid Data (Missing Required Fields).
        """
        print("\n=== TC-CREATE-004: Invalid Data (ADMIN) ===")
        page = authenticated_page
        
        page.goto(f"{settings.BASE_URL}/items/create")
        page.wait_for_load_state("networkidle")
        
        # Fill only some fields
        page.fill('[data-testid="item-name"]', "Test Item Invalid")
        page.fill('[data-testid="item-price"]', "10.00")
        
        # Leave description empty
        # Leave type unselected
        
        print("    Submitting valid form...")
        page.click('[data-testid="create-item-submit"]')
        
        # Wait verification
        # Expectation: validation errors, no navigation
        page.wait_for_timeout(1000)
        assert "/items/create" in page.url
        
        # Check for error elements if defined
        # WEB_TEST_CASES says: data-testid="description-error" and "item-type-error"
        # We check generic invalid state or specific error
        
        is_invalid = page.evaluate("document.querySelector('input:invalid, select:invalid, textarea:invalid') !== null")
        # Or check for error message texts if locators exist
        # We assume HTML5 validation or framework validation prevents it
        
        print(f"    Validation active: {is_invalid}")
        assert is_invalid or page.is_visible('[data-testid="description-error"]'), "Validation should prevent submission"
        print("\n Test PASSED: TC-CREATE-004\n")

    def test_create_item_with_file(self, authenticated_page: Page, test_context):
        """
        TC-CREATE-005: Create Item with File Upload (ADMIN).
        """
        print("\n=== TC-CREATE-005: File Upload (ADMIN) ===")
        page = authenticated_page
        
        # Generate dummy file
        file_name = "test_image.jpg"
        file_path = os.path.abspath(f"d:/frameworks_hybrid/resume/data/{file_name}")
        file_generator.generate_test_image(file_path, size=(100, 100))
        
        try:
            page.goto(f"{settings.BASE_URL}/items/create")
            
            # Fill required
            item_name = f"Test File Item {uuid.uuid4().hex[:8]}"
            page.fill('[data-testid="item-name"]', item_name)
            page.fill('[data-testid="item-description"]', "Item with file")
            page.select_option('[data-testid="item-type"]', "PHYSICAL")
            
            # Wait for fields
            page.wait_for_selector('[data-testid="physical-fields"]', state="visible")
            page.fill('[data-testid="item-price"]', "25.00")
            page.fill('[data-testid="item-category"]', "Test")
            page.fill('[data-testid="item-weight"]', "1.0")
            page.fill('[data-testid="item-dimension-length"]', "10")
            page.fill('[data-testid="item-dimension-width"]', "10")
            page.fill('[data-testid="item-dimension-height"]', "10")
            
            # Upload file
            print(f"    Uploading {file_name}...")
            # Locator from spec: data-testid="item-file-upload"
            # If input is hidden, we might need to set input files on the input element
            
            # Handling generic file upload
            upload_input = page.locator('input[type="file"]')
            if upload_input.count() > 0:
                upload_input.set_input_files(file_path)
            else:
                 # Fallback to testid if it points to input or wrapper
                 page.set_input_files('[data-testid="item-file-upload"]', file_path)
            
            # Verify file selection (optional check)
            
            page.click('[data-testid="create-item-submit"]')
            
            # Verify success
            page.wait_for_selector('[data-testid="toast-success"]', state="visible", timeout=10000)
            print("    Item created with file")
            
            # Cleanup item
            api_client = APIClient(token=test_context.auth_token)
            response = api_client.get_all_items()
            items = response.get("items", [])
            for item in items:
                if item.get("name") == item_name:
                    api_client.delete_item(item.get("_id"))
                    break
                    
        finally:
            # Cleanup file
            if os.path.exists(file_path):
                os.remove(file_path)
                print("    Temp file cleaned up")
        
        print("\n Test PASSED: TC-CREATE-005\n")


@pytest.mark.role("EDITOR")
class TestItemCreationEditor:
    """Item creation tests for EDITOR role."""
    
    def test_create_digital_item(self, authenticated_page: Page, test_context):
        """
        TC-CREATE-002: Create DIGITAL Item with Valid Data (EDITOR)
        """
        print("\n=== TC-CREATE-002: Create DIGITAL Item (EDITOR) ===")
        print(f"User: {test_context.user_email}")
        
        page = authenticated_page
        
        # Navigate
        page.goto(f"{settings.BASE_URL}/items/create")
        page.wait_for_load_state("networkidle")
        
        # Fill form
        item_name = f"Test Digital Item {uuid.uuid4().hex[:8]}"
        
        page.fill('[data-testid="item-name"]', item_name)
        page.fill('[data-testid="item-description"]', "This is a test digital item")
        page.select_option('[data-testid="item-type"]', "DIGITAL")
        
        page.wait_for_selector('[data-testid="digital-fields"]', state="visible", timeout=5000)
        
        page.fill('[data-testid="item-price"]', "49.99")
        page.fill('[data-testid="item-category"]', "Software")
        page.fill('[data-testid="item-download-url"]', "https://example.com/download/file.zip")
        page.fill('[data-testid="item-file-size"]', "1048576")
        
        # Submit
        page.click('[data-testid="create-item-submit"]')
        
        # Verify
        page.wait_for_selector('[data-testid="toast-success"]', state="visible", timeout=10000)
        print("    Item created successfully")
        
        # Cleanup
        api_client = APIClient(token=test_context.auth_token)
        response = api_client.get_all_items()
        items = response.get("items", [])
        
        for item in items:
            if item.get("name") == item_name:
                api_client.delete_item(item.get("_id"))
                break
        
        print("\n Test PASSED: TC-CREATE-002\n")


@pytest.mark.role("VIEWER")
class TestItemCreationViewer:
    """Item creation permission tests for VIEWER role."""
    
    def test_viewer_cannot_create_item(self, authenticated_page: Page, test_context):
        """
        TC-CREATE-006: VIEWER Cannot Create Item (Permission Test).
        
        Refined Requirement:
        - Viewer CAN access the link /items/create
        - Viewer CAN enter data
        - Error "Access denied..." appears ONLY after clicking Create
        """
        print("\n=== TC-CREATE-006: Viewer Permission (VIEWER) ===")
        page = authenticated_page
        
        # 1. Navigate
        print("1. Navigating to /items/create...")
        page.goto(f"{settings.BASE_URL}/items/create")
        page.wait_for_load_state("networkidle")
        
        # 2. Fill Form (Valid Data)
        print("2. Filling form with valid data...")
        item_name = f"Viewer Attempt {uuid.uuid4().hex[:8]}"
        
        page.fill('[data-testid="item-name"]', item_name)
        page.fill('[data-testid="item-description"]', "Viewer trying to create item")
        page.select_option('[data-testid="item-type"]', "PHYSICAL")
        
        page.wait_for_selector('[data-testid="physical-fields"]', state="visible", timeout=5000)
        
        page.fill('[data-testid="item-price"]', "10.00")
        page.fill('[data-testid="item-category"]', "Test")
        page.fill('[data-testid="item-weight"]', "1.0")
        page.fill('[data-testid="item-dimension-length"]', "10")
        page.fill('[data-testid="item-dimension-width"]', "10")
        page.fill('[data-testid="item-dimension-height"]', "10")
        
        # 3. Submit
        print("3. Submitting form...")
        page.click('[data-testid="create-item-submit"]')
        
        # 4. Verify Error Message
        expected_error = "Access denied. Requires one of the following roles: ADMIN, EDITOR"
        print(f"4. Checking for error: '{expected_error}'")
        
        # Wait for toast failure or error message on page
        # We look for the text anywhere on the page appearing after submit
        try:
            # Assuming it appears in a toast or error container
            # Using text-locator for exact match or contains
            error_locator = page.locator(f"text={expected_error}")
            error_locator.wait_for(state="visible", timeout=5000)
            print("    Error message displayed successfully")
        except Exception as e:
            # Fallback check content if it's not a discrete element or timed out
            content = page.content()
            if expected_error in content:
                print("    Error text found in page content")
            else:
                print(f"    Error not found. Current URL: {page.url}")
                raise e
        
        # Verify NO success toast
        assert not page.is_visible('[data-testid="toast-success"]'), "Success toast should NOT appear"
        
        print("\n Test PASSED: TC-CREATE-006\n")
