
import pytest
from playwright.sync_api import Page, expect
from config.settings import settings
import re

@pytest.mark.role("ADMIN")
class TestItemList:
    """
    Flow 3: Item List Tests (TC-LIST-001 to TC-LIST-006)
    Uses Extended Seed Data (20+ items) created for Admin.
    Verified against Backend Specs:
    - Default Limit: 20
    - Status: active/inactive
    - Sort: price, createdAt
    - Price Type: Number
    """

    def test_view_items_list(self, authenticated_page: Page, test_context):
        """TC-LIST-001: View Items List & Default Pagination"""
        print("\n=== TC-LIST-001: View Items List ===")
        page = authenticated_page
        page.goto(f"{settings.BASE_URL}/items")
        
        # 1. Wait for Table
        table = page.locator('[data-testid="items-table"]')
        expect(table).to_be_visible()
        
        # 2. Verify Default Count (Limit 20)
        rows = page.locator('tbody tr')
        expect(rows).to_have_count(20)
        
        # 3. Pagination Controls
        expect(page.locator('button:has-text("Next")')).to_be_visible()

    def test_sort_items(self, authenticated_page: Page):
        """TC-LIST-004: Sort Items (Price)"""
        print("\n=== TC-LIST-004: Sort Items ===")
        page = authenticated_page
        
        # 1. Sort ASC
        page.goto(f"{settings.BASE_URL}/items?sort_by=price&sort_order=asc")
        # Wait for first row to be bound implies load
        page.wait_for_selector('tbody tr', state='visible')
        
        val_asc = page.locator('tbody tr').first.locator('td:nth-child(4)').text_content()
        print(f"Sort ASC First Price: {val_asc}")
        
        # Clean string: "$ 1.00" -> 1.00
        # Backend returns Number, frontend might format with $ and ,
        price_asc = float(str(val_asc).replace("$", "").replace(",", "").strip())
        assert price_asc <= 2.00, f"Expected low price <= 2.00, got {price_asc}"
        
        # 2. Sort DESC
        page.goto(f"{settings.BASE_URL}/items?sort_by=price&sort_order=desc")
        page.wait_for_selector('tbody tr', state='visible')
        
        val_desc = page.locator('tbody tr').first.locator('td:nth-child(4)').text_content()
        print(f"Sort DESC First Price: {val_desc}")
        
        price_desc = float(str(val_desc).replace("$", "").replace(",", "").strip())
        # We know items up to $999.99 exist. Seed was 999.00.
        assert price_desc >= 999.00, f"Expected high price >= 999.00, got {price_desc}"

    def test_search_items(self, authenticated_page: Page, test_context):
        """TC-LIST-002: Search Items"""
        print("\n=== TC-LIST-002: Search Items ===")
        page = authenticated_page
        # Go to clean state
        page.goto(f"{settings.BASE_URL}/items")

        # 1. Search for unique term "Zebra" (matches SEED_Unique_Zebra...)
        search_input = page.locator('[data-testid="item-search"]')
        search_input.fill("Zebra")
        search_input.press("Enter")
        
        # 2. Verify URL contains search param
        expect(page).to_have_url(re.compile(r".*search=Zebra.*"))
        
        # 3. Should find exactly 1 item
        rows = page.locator('tbody tr')
        expect(rows).to_have_count(1)
        expect(rows.first).to_contain_text("Zebra")

    def test_filter_by_status(self, authenticated_page: Page, test_context):
        """TC-LIST-003: Filter Items by Status"""
        print("\n=== TC-LIST-003: Filter Status ===")
        page = authenticated_page
        
        # 1. Filter Inactive
        # Direct URL navigation as selectors might vary, but verified active/inactive are valid
        page.goto(f"{settings.BASE_URL}/items?status=inactive")
        
        # 2. Verify Inactive Item appears
        rows = page.locator('tbody tr')
        # We created exactly 1 inactive item per admin
        expect(rows).to_have_count(1)
        expect(rows.first).to_contain_text("Inactive")
        
        # 3. Filter Active
        page.goto(f"{settings.BASE_URL}/items?status=active")
        # Should NOT see inactive item
        # Wait for table reload
        page.wait_for_selector('tbody tr', state='visible')
        expect(page.locator('body')).not_to_contain_text("SEED_Inactive")

    def test_pagination(self, authenticated_page: Page):
        """TC-LIST-005: Pagination"""
        print("\n=== TC-LIST-005: Pagination ===")
        page = authenticated_page
        page.goto(f"{settings.BASE_URL}/items")
        
        # 1. Check Page 1 (Limit 20)
        expect(page.locator('tbody tr')).to_have_count(20)
        
        # 2. Click Next
        next_btn = page.locator('button:has-text("Next")')
        expect(next_btn).to_be_enabled()
        next_btn.click()
        
        # 3. Verify Page 2 URL
        # We explicitly wait for the URL to change to page=2
        expect(page).to_have_url(re.compile(r".*page=2.*"))
        
        # 4. Check Page 2 has items (we created enough seed data)
        # Wait for table to load rows
        page.wait_for_selector('tbody tr', state='visible')
        expect(page.locator('tbody tr')).not_to_have_count(0)
