# FlowHub Web Automation - Test Cases Specification

**Version:** 1.0  
**Created:** 2026-01-02  
**Framework:** Playwright + Pytest + Python  
**Total Test Cases:** 38 (30 Isolated + 8 E2E)

---

## Test Case Priority Levels

- **P0 (Critical):** Core functionality, blocking issues
- **P1 (High):** Important features, major workflows
- **P2 (Medium):** Secondary features, edge cases

---

## Test Case Format

Each test case includes:
- **Test ID:** Unique identifier
- **Test Name:** Descriptive name
- **Priority:** P0/P1/P2
- **Type:** Isolated/E2E
- **Role:** ADMIN/EDITOR/VIEWER/ALL
- **Preconditions:** Setup requirements
- **Test Steps:** Step-by-step actions with locators
- **Test Data:** Input values
- **Expected Results:** What should happen
- **Assertions:** Validation checks

---

# Test Case Categories

## Understanding Test Types

### ✅ POSITIVE Test Cases (Happy Path)
**Definition:** Valid inputs, expected to succeed  
**Purpose:** Verify core functionality works correctly  
**Examples:** Login with valid credentials, create item with valid data

### ❌ NEGATIVE Test Cases (Invalid Inputs)
**Definition:** Invalid inputs or unauthorized actions, expected to fail gracefully  
**Purpose:** Verify system handles errors correctly  
**Examples:** Login with wrong password, missing required fields, permission denied

### ⚠️ EDGE Test Cases (Boundary Conditions)
**Definition:** Boundary values, unusual scenarios, edge conditions  
**Purpose:** Verify system handles edge cases correctly  
**Examples:** Maximum file size, session timeout, pagination boundaries

---

# ISOLATED TEST CASES (30 Tests)

**Distribution:**
- ✅ Positive: 18 tests
- ❌ Negative: 8 tests
- ⚠️ Edge: 4 tests

---

## Flow 1: Authentication Tests (5 Tests)

### TC-AUTH-001: Login with Valid Credentials (ADMIN) ✅ POSITIVE

**Priority:** P0  
**Type:** Isolated  
**Category:** Positive (Happy Path)  
**Role:** ADMIN

**Preconditions:**
- User `admin1@test.com` exists with password `Admin@123`
- User is on login page `/login`

**Test Steps:**
1. Locate email input: `data-testid="login-email"`
2. Fill email: `admin1@test.com`
3. Locate password input: `data-testid="login-password"`
4. Fill password: `Admin@123`
5. Locate submit button: `data-testid="login-submit"`
6. Click submit button
7. Wait for navigation

**Test Data:**
```json
{
  "email": "admin1@test.com",
  "password": "Admin@123"
}
```

**Expected Results:**
- User redirected to `/dashboard`
- Dashboard page loads successfully
- No error messages displayed

**Assertions:**
- `page.url` contains `/dashboard`
- Success toast appears (optional)
- User menu shows ADMIN role badge

---

### TC-AUTH-002: Login with Invalid Credentials ❌ NEGATIVE

**Priority:** P0  
**Type:** Isolated  
**Category:** Negative (Invalid Input)  
**Role:** ALL

**Preconditions:**
- User is on login page `/login`

**Test Steps:**
1. Locate email input: `data-testid="login-email"`
2. Fill email: `invalid@test.com`
3. Locate password input: `data-testid="login-password"`
4. Fill password: `WrongPassword123`
5. Locate submit button: `data-testid="login-submit"`
6. Click submit button
7. Wait for error message

**Test Data:**
```json
{
  "email": "invalid@test.com",
  "password": "WrongPassword123"
}
```

**Expected Results:**
- User remains on `/login` page
- Error message displayed
- Login button re-enabled

**Assertions:**
- `page.url` contains `/login`
- Error message visible: `data-testid="login-error"`
- Error text contains "Invalid credentials" or similar

---

### TC-AUTH-003: Login with Remember Me Enabled ⚠️ EDGE

**Priority:** P1  
**Type:** Isolated  
**Category:** Edge Case (Optional Feature)  
**Role:** ADMIN

**Preconditions:**
- User `admin2@test.com` exists
- User is on login page `/login`

**Test Steps:**
1. Fill email: `admin2@test.com`
2. Fill password: `Admin@123`
3. Locate Remember Me checkbox: `data-testid="login-remember-me"`
4. Check Remember Me checkbox
5. Verify checkbox is checked: `aria-checked="true"`
6. Click submit button
7. Wait for navigation to `/dashboard`

**Test Data:**
```json
{
  "email": "admin2@test.com",
  "password": "Admin@123",
  "rememberMe": true
}
```

**Expected Results:**
- User redirected to `/dashboard`
- Session persists (refresh token set to 30 days)

**Assertions:**
- Checkbox is checked before submit
- Successful login
- Dashboard loads

---

### TC-AUTH-004: Logout Functionality ✅ POSITIVE

**Priority:** P0  
**Type:** Isolated  
**Category:** Positive (Happy Path)  
**Role:** ADMIN

**Preconditions:**
- User is logged in as `admin1@test.com`
- User is on any authenticated page

**Test Steps:**
1. Locate user menu button: `data-testid="user-menu-button"`
2. Click user menu button
3. Wait for dropdown: `data-testid="user-menu-dropdown"`
4. Locate logout button: `data-testid="menu-logout"`
5. Click logout button
6. Wait for navigation

**Expected Results:**
- User redirected to `/login`
- Session cleared
- Cannot access protected routes

**Assertions:**
- `page.url` contains `/login`
- User menu no longer visible
- Attempting to navigate to `/dashboard` redirects to `/login`

---

### TC-AUTH-005: Login with Empty Fields ❌ NEGATIVE

**Priority:** P1  
**Type:** Isolated  
**Category:** Negative (Missing Input)  
**Role:** ALL

**Preconditions:**
- User is on login page `/login`

**Test Steps:**
1. Leave email field empty
2. Leave password field empty
3. Click submit button: `data-testid="login-submit"`
4. Wait for validation errors

**Expected Results:**
- Form validation prevents submission
- Error messages shown for both fields

**Assertions:**
- Email field shows error
- Password field shows error
- Form not submitted (remains on `/login`)

---

## Flow 2: Item Creation Tests (6 Tests)

### TC-CREATE-001: Create PHYSICAL Item with Valid Data (ADMIN) ✅ POSITIVE

**Priority:** P0  
**Type:** Isolated  
**Category:** Positive (Happy Path)  
**Role:** ADMIN

**Preconditions:**
- User logged in as `admin1@test.com`
- User navigated to `/items/create`

**Test Steps:**
1. Fill name: `data-testid="item-name"` → `Test Physical Item ${uuid}`
2. Fill description: `data-testid="item-description"` → `This is a test physical item description`
3. Select item type: `data-testid="item-type"` → `PHYSICAL`
4. Wait for conditional fields: `data-testid="physical-fields"` visible
5. Fill price: `data-testid="item-price"` → `99.99`
6. Fill category: `data-testid="item-category"` → `Electronics`
7. Fill weight: `data-testid="item-weight"` → `2.5`
8. Fill length: `data-testid="item-dimension-length"` → `30`
9. Fill width: `data-testid="item-dimension-width"` → `20`
10. Fill height: `data-testid="item-dimension-height"` → `10`
11. Click submit: `data-testid="create-item-submit"`
12. Wait for success toast: `data-testid="toast-success"`

**Test Data:**
```json
{
  "name": "Test Physical Item {uuid}",
  "description": "This is a test physical item description",
  "item_type": "PHYSICAL",
  "price": 99.99,
  "category": "Electronics",
  "weight": 2.5,
  "dimensions": {
    "length": 30,
    "width": 20,
    "height": 10
  }
}
```

**Expected Results:**
- Item created successfully
- Success toast appears
- Redirected to `/items` or item details

**Assertions:**
- Success toast visible
- Toast message contains "created successfully"
- Item appears in items list

**Cleanup:**
- Delete created item using item ID

---

### TC-CREATE-002: Create DIGITAL Item with Valid Data (EDITOR) ✅ POSITIVE

**Priority:** P0  
**Type:** Isolated  
**Category:** Positive (Happy Path)  
**Role:** EDITOR

**Preconditions:**
- User logged in as `editor1@test.com`
- User navigated to `/items/create`

**Test Steps:**
1. Fill name: `Test Digital Item ${uuid}`
2. Fill description: `This is a test digital item`
3. Select item type: `DIGITAL`
4. Wait for digital fields: `data-testid="digital-fields"` visible
5. Fill price: `49.99`
6. Fill category: `Software`
7. Fill download URL: `data-testid="item-download-url"` → `https://example.com/download/file.zip`
8. Fill file size: `data-testid="item-file-size"` → `1048576` (1 MB in bytes)
9. Click submit

**Test Data:**
```json
{
  "name": "Test Digital Item {uuid}",
  "description": "This is a test digital item",
  "item_type": "DIGITAL",
  "price": 49.99,
  "category": "Software",
  "download_url": "https://example.com/download/file.zip",
  "file_size": 1048576
}
```

**Expected Results:**
- Item created successfully
- Success toast appears

**Assertions:**
- Success toast visible
- Item created by `editor1@test.com`

**Cleanup:**
- Delete created item

---

### TC-CREATE-003: Create SERVICE Item with Valid Data (ADMIN) ✅ POSITIVE

**Priority:** P0  
**Type:** Isolated  
**Category:** Positive (Happy Path)  
**Role:** ADMIN

**Preconditions:**
- User logged in as `admin1@test.com`
- User navigated to `/items/create`

**Test Steps:**
1. Fill name: `Test Service Item ${uuid}`
2. Fill description: `This is a test service item`
3. Select item type: `SERVICE`
4. Wait for service fields: `data-testid="service-fields"` visible
5. Fill price: `150.00`
6. Fill category: `Consulting`
7. Fill duration: `data-testid="item-duration-hours"` → `8`
8. Click submit

**Test Data:**
```json
{
  "name": "Test Service Item {uuid}",
  "description": "This is a test service item",
  "item_type": "SERVICE",
  "price": 150.00,
  "category": "Consulting",
  "duration_hours": 8
}
```

**Expected Results:**
- Item created successfully
- Success toast appears

**Assertions:**
- Success toast visible
- Service fields were shown correctly

**Cleanup:**
- Delete created item

---

### TC-CREATE-004: Create Item with Invalid Data (Missing Required Fields) ❌ NEGATIVE

**Priority:** P1  
**Type:** Isolated  
**Category:** Negative (Invalid Input)  
**Role:** ADMIN

**Preconditions:**
- User logged in as `admin1@test.com`
- User navigated to `/items/create`

**Test Steps:**
1. Fill name: `Test Item`
2. Leave description empty
3. Leave item type unselected
4. Fill price: `10.00`
5. Click submit
6. Wait for validation errors

**Expected Results:**
- Form validation prevents submission
- Error messages shown for required fields

**Assertions:**
- Description error visible: `data-testid="description-error"`
- Item type error visible: `data-testid="item-type-error"`
- Form not submitted

---

### TC-CREATE-005: Create Item with File Upload (ADMIN) ⚠️ EDGE

**Priority:** P1  
**Type:** Isolated  
**Category:** Edge Case (File Upload Feature)  
**Role:** ADMIN

**Preconditions:**
- User logged in as `admin1@test.com`
- User navigated to `/items/create`
- Valid test file available (e.g., `test-image.jpg`, < 5 MB)

**Test Steps:**
1. Fill all required fields (name, description, type, price, category)
2. Locate file upload: `data-testid="item-file-upload"`
3. Upload file: `test-image.jpg`
4. Wait for file display: `data-testid="selected-file"` visible
5. Verify file name shown
6. Click submit

**Test Data:**
```json
{
  "name": "Test Item with File {uuid}",
  "description": "Item with file attachment",
  "item_type": "PHYSICAL",
  "price": 25.00,
  "category": "Test",
  "file": "test-image.jpg"
}
```

**Expected Results:**
- File uploaded successfully
- File name displayed
- Item created with file attachment

**Assertions:**
- Selected file visible
- Success toast appears
- Item created

**Cleanup:**
- Delete created item

---

### TC-CREATE-006: VIEWER Cannot Create Item (Permission Test) ❌ NEGATIVE

**Priority:** P0  
**Type:** Isolated  
**Category:** Negative (Permission Denied)  
**Role:** VIEWER

**Preconditions:**
- User logged in as `viewer1@test.com`
- User on dashboard or items page

**Test Steps:**
1. Look for "Create Item" button: `data-testid="quick-action-create-item"`
2. Verify button is not visible/rendered
3. Attempt to navigate directly to `/items/create`
4. Verify access denied or redirect

**Expected Results:**
- Create button not visible for VIEWER
- Direct navigation to create page blocked

**Assertions:**
- Create button not in DOM
- Attempting to access `/items/create` shows error or redirects

---

## Flow 3: Item List Tests (6 Tests)

### TC-LIST-001: View Items List (ALL Roles) ✅ POSITIVE

**Priority:** P0  
**Type:** Isolated  
**Category:** Positive (Happy Path)  
**Role:** ALL

**Preconditions:**
- User logged in (any role)
- At least 5 items exist in database
- User navigated to `/items`

**Test Steps:**
1. Wait for items table: `data-testid="items-table"` visible
2. Verify table headers present
3. Count item rows
4. Verify pagination controls visible

**Expected Results:**
- Items table loads successfully
- Items displayed in table rows
- Pagination controls visible

**Assertions:**
- Table visible
- At least 1 item row present
- Columns: Name, Description, Status, Category, Price, Created Date, Actions

---

### TC-LIST-002: Search Items by Name ✅ POSITIVE

**Priority:** P1  
**Type:** Isolated  
**Category:** Positive (Happy Path)  
**Role:** ADMIN

**Preconditions:**
- User logged in as `admin1@test.com`
- Item with name "Laptop" exists
- User on `/items` page

**Test Steps:**
1. Locate search input: `data-testid="item-search"`
2. Fill search: `Laptop`
3. Wait for table update
4. Verify filtered results

**Test Data:**
```json
{
  "searchQuery": "Laptop"
}
```

**Expected Results:**
- Table shows only items matching "Laptop"
- Other items filtered out

**Assertions:**
- Search input contains "Laptop"
- All visible item names contain "Laptop"

---

### TC-LIST-003: Filter Items by Status (Active) ✅ POSITIVE

**Priority:** P1  
**Type:** Isolated  
**Category:** Positive (Happy Path)  
**Role:** ADMIN

**Preconditions:**
- User logged in
- Both active and inactive items exist
- User on `/items` page

**Test Steps:**
1. Locate status filter: `data-testid="filter-status"`
2. Select "Active" from dropdown
3. Wait for table update
4. Verify only active items shown

**Expected Results:**
- Table shows only active items
- Inactive items hidden

**Assertions:**
- All visible items have status badge showing "Active"
- Status filter shows "Active" selected

---

### TC-LIST-004: Sort Items by Price (Ascending) ⚠️ EDGE

**Priority:** P1  
**Type:** Isolated  
**Category:** Edge Case (Sorting Feature)  
**Role:** ADMIN

**Preconditions:**
- User logged in
- Multiple items with different prices exist
- User on `/items` page

**Test Steps:**
1. Locate price column header sort button
2. Click to sort ascending
3. Wait for table update
4. Verify items sorted by price (low to high)

**Expected Results:**
- Items sorted by price ascending
- Sort indicator shows ascending arrow

**Assertions:**
- First item has lowest price
- Last item has highest price
- Prices in ascending order

---

### TC-LIST-005: Pagination - Navigate to Next Page ⚠️ EDGE

**Priority:** P1  
**Type:** Isolated  
**Category:** Edge Case (Pagination Boundary)  
**Role:** ADMIN

**Preconditions:**
- User logged in
- More than 20 items exist (default page size)
- User on `/items` page 1

**Test Steps:**
1. Verify current page is 1
2. Locate next button: `data-testid="pagination-next"`
3. Click next button
4. Wait for page 2 to load
5. Verify URL contains `page=2`

**Expected Results:**
- Page 2 loads
- Different items displayed
- Previous button now enabled

**Assertions:**
- URL contains `page=2`
- Page 2 items different from page 1
- Previous button enabled

---

### TC-LIST-006: Clear All Filters ✅ POSITIVE

**Priority:** P2  
**Type:** Isolated  
**Category:** Positive (Happy Path)  
**Role:** ADMIN

**Preconditions:**
- User logged in
- Filters applied (search + status filter)
- User on `/items` page

**Test Steps:**
1. Apply search filter: `Test`
2. Apply status filter: `Active`
3. Verify filtered results shown
4. Locate clear filters button: `data-testid="clear-filters"`
5. Click clear filters
6. Wait for table reset

**Expected Results:**
- All filters cleared
- Full items list shown
- Search input empty
- Status filter reset to "All"

**Assertions:**
- Search input value is empty
- Status filter shows "All"
- All items visible again

---

## Flow 4: Item Details Tests (4 Tests)

### TC-DETAILS-001: View Item Details in Modal (ADMIN) ✅ POSITIVE

**Priority:** P0  
**Type:** Isolated  
**Category:** Positive (Happy Path)  
**Role:** ADMIN

**Preconditions:**
- User logged in as `admin1@test.com`
- Item with ID `{itemId}` exists
- User on `/items` page

**Test Steps:**
1. Locate view button for item: `data-testid="item-view-{itemId}"`
2. Click view button
3. Wait for modal: `data-testid="item-details-modal"` visible
4. Verify modal title: `data-testid="modal-title"`
5. Verify item name displayed: `data-testid="item-name-{sanitizedId}"`
6. Verify all item fields visible

**Expected Results:**
- Modal opens successfully
- All item details displayed
- Modal overlay visible

**Assertions:**
- Modal visible
- Item name matches expected
- Description, price, category all visible

**Cleanup:**
- Close modal: `data-testid="close-button"`

---

### TC-DETAILS-002: View Item with Iframe Content ⚠️ EDGE

**Priority:** P1  
**Type:** Isolated  
**Category:** Edge Case (Iframe Feature)  
**Role:** ADMIN

**Preconditions:**
- User logged in
- Item with `embed_url` exists
- User on `/items` page

**Test Steps:**
1. Click view button for item with embed URL
2. Wait for modal to open
3. Wait for iframe: `data-testid="item-embed-iframe-{sanitizedId}"` visible
4. Verify iframe src attribute contains embed URL
5. Wait for iframe to load (max 5 seconds)

**Expected Results:**
- Modal opens
- Iframe loads successfully
- Iframe content visible

**Assertions:**
- Iframe element present
- Iframe src matches item's embed_url
- No error state shown

---

### TC-DETAILS-003: Close Item Details Modal ✅ POSITIVE

**Priority:** P1  
**Type:** Isolated  
**Category:** Positive (Happy Path)  
**Role:** ADMIN

**Preconditions:**
- User logged in
- Item details modal is open

**Test Steps:**
1. Locate close button: `data-testid="close-button"`
2. Click close button
3. Wait for modal to close
4. Verify modal not visible

**Expected Results:**
- Modal closes
- Returns to items list
- Modal removed from DOM

**Assertions:**
- Modal not visible
- Items table still visible

---

### TC-DETAILS-004: Item Details Modal Loading State ⚠️ EDGE

**Priority:** P2  
**Type:** Isolated  
**Category:** Edge Case (Loading State)  
**Role:** ADMIN

**Preconditions:**
- User logged in
- User on `/items` page

**Test Steps:**
1. Click view button for an item
2. Immediately check for loading state: `data-testid="loading-state"`
3. Wait for loading to complete
4. Verify item details shown

**Expected Results:**
- Loading state briefly visible
- Then item details load
- No error state

**Assertions:**
- Loading state appears initially
- Loading state disappears when data loads
- Item details visible after load

---

## Flow 5: Item Edit Tests (5 Tests)

### TC-EDIT-001: ADMIN Edit Any Item ✅ POSITIVE

**Priority:** P0  
**Type:** Isolated  
**Category:** Positive (Happy Path)  
**Role:** ADMIN

**Preconditions:**
- User logged in as `admin1@test.com`
- Item created by `editor1@test.com` exists
- User on `/items` page

**Test Steps:**
1. Locate edit button: `data-testid="item-edit-{itemId}"`
2. Click edit button
3. Wait for navigation to `/items/{itemId}/edit`
4. Verify form pre-populated
5. Update name: `data-testid="item-name"` → `Updated Item Name ${uuid}`
6. Update price: `data-testid="item-price"` → `199.99`
7. Click update button: `data-testid="update-item-submit"`
8. Wait for success toast

**Test Data:**
```json
{
  "name": "Updated Item Name {uuid}",
  "price": 199.99
}
```

**Expected Results:**
- ADMIN can edit item created by EDITOR
- Item updated successfully
- Success toast appears

**Assertions:**
- Edit page loads
- Form pre-populated with existing data
- Success toast visible
- Item updated in database

**Cleanup:**
- Restore original item data or delete

---

### TC-EDIT-002: EDITOR Edit Own Item ✅ POSITIVE

**Priority:** P0  
**Type:** Isolated  
**Category:** Positive (Happy Path)  
**Role:** EDITOR

**Preconditions:**
- User logged in as `editor1@test.com`
- Item created by `editor1@test.com` exists
- User on `/items` page

**Test Steps:**
1. Locate edit button for own item
2. Click edit button
3. Navigate to edit page
4. Update description: `Updated by editor`
5. Click update button
6. Wait for success

**Expected Results:**
- EDITOR can edit own item
- Item updated successfully

**Assertions:**
- Edit button visible for own item
- Update successful
- Success toast appears

**Cleanup:**
- Delete test item

---

### TC-EDIT-003: EDITOR Cannot Edit Other's Item ❌ NEGATIVE

**Priority:** P0  
**Type:** Isolated  
**Category:** Negative (Permission Denied)  
**Role:** EDITOR

**Preconditions:**
- User logged in as `editor1@test.com`
- Item created by `admin1@test.com` exists
- User on `/items` page

**Test Steps:**
1. Find item created by admin
2. Verify edit button not visible for that item
3. Attempt direct navigation to `/items/{itemId}/edit`
4. Verify access denied

**Expected Results:**
- Edit button not visible for other's items
- Direct navigation blocked

**Assertions:**
- Edit button not rendered for non-owned items
- 403 error or redirect on direct access

---

### TC-EDIT-004: VIEWER Cannot Edit Any Item ❌ NEGATIVE

**Priority:** P0  
**Type:** Isolated  
**Category:** Negative (Permission Denied)  
**Role:** VIEWER

**Preconditions:**
- User logged in as `viewer1@test.com`
- Items exist in database
- User on `/items` page

**Test Steps:**
1. Verify no edit buttons visible
2. Attempt direct navigation to `/items/{itemId}/edit`
3. Verify access denied

**Expected Results:**
- No edit buttons visible
- Direct access blocked

**Assertions:**
- Edit buttons not in DOM
- 403 error on direct navigation

---

### TC-EDIT-005: Cancel Edit Operation ✅ POSITIVE

**Priority:** P2  
**Type:** Isolated  
**Category:** Positive (Happy Path)  
**Role:** ADMIN

**Preconditions:**
- User logged in
- User on edit page `/items/{itemId}/edit`

**Test Steps:**
1. Make changes to form fields
2. Locate cancel button: `data-testid="cancel-item-edit"`
3. Click cancel button
4. Verify navigation back to `/items`
5. Verify changes not saved

**Expected Results:**
- Redirected to items list
- Changes discarded
- Item unchanged

**Assertions:**
- URL is `/items`
- Item data unchanged in database

---

## Flow 6: Item Delete Tests (4 Tests)

### TC-DELETE-001: ADMIN Delete Any Item ✅ POSITIVE

**Priority:** P0  
**Type:** Isolated  
**Category:** Positive (Happy Path)  
**Role:** ADMIN

**Preconditions:**
- User logged in as `admin1@test.com`
- Item created by `editor1@test.com` exists
- User on `/items` page

**Test Steps:**
1. Locate delete button: `data-testid="item-delete-{itemId}"`
2. Click delete button
3. Wait for confirmation modal: `data-testid="delete-confirmation-modal"`
4. Verify modal message contains item name
5. Locate confirm button: `data-testid="delete-confirm-button"`
6. Click confirm button
7. Wait for success toast
8. Verify item removed from list

**Expected Results:**
- Confirmation modal appears
- Item soft deleted (is_active = false)
- Success toast appears
- Item removed from active list

**Assertions:**
- Confirmation modal visible
- Modal message contains item name
- Success toast appears
- Item not in active items list

---

### TC-DELETE-002: EDITOR Delete Own Item ✅ POSITIVE

**Priority:** P0  
**Type:** Isolated  
**Category:** Positive (Happy Path)  
**Role:** EDITOR

**Preconditions:**
- User logged in as `editor1@test.com`
- Item created by `editor1@test.com` exists
- User on `/items` page

**Test Steps:**
1. Click delete button for own item
2. Confirm deletion in modal
3. Wait for success

**Expected Results:**
- EDITOR can delete own item
- Item soft deleted

**Assertions:**
- Delete successful
- Item removed from list

---

### TC-DELETE-003: EDITOR Cannot Delete Other's Item ❌ NEGATIVE

**Priority:** P0  
**Type:** Isolated  
**Category:** Negative (Permission Denied)  
**Role:** EDITOR

**Preconditions:**
- User logged in as `editor1@test.com`
- Item created by `admin1@test.com` exists
- User on `/items` page

**Test Steps:**
1. Find item created by admin
2. Verify delete button not visible

**Expected Results:**
- Delete button not visible for other's items

**Assertions:**
- Delete button not rendered for non-owned items

---

### TC-DELETE-004: Cancel Delete Operation ✅ POSITIVE

**Priority:** P1  
**Type:** Isolated  
**Category:** Positive (Happy Path)  
**Role:** ADMIN

**Preconditions:**
- User logged in
- User on `/items` page

**Test Steps:**
1. Click delete button for an item
2. Wait for confirmation modal
3. Locate cancel button: `data-testid="delete-cancel-button"`
4. Click cancel button
5. Verify modal closes
6. Verify item still in list

**Expected Results:**
- Modal closes
- Item not deleted
- Item still visible in list

**Assertions:**
- Modal not visible
- Item still in database
- Item still in list

---

# E2E TEST CASES (8 Tests)

---

## E2E-001: ADMIN Complete Item Lifecycle

**Priority:** P0  
**Type:** E2E  
**Role:** ADMIN

**Preconditions:**
- User `admin1@test.com` exists
- User not logged in

**Test Steps:**
1. **Login:**
   - Navigate to `/login`
   - Fill credentials: `admin1@test.com` / `Admin@123`
   - Click submit
   - Verify redirect to `/dashboard`

2. **Navigate to Create:**
   - Click "Create Item" quick action
   - Verify navigation to `/items/create`

3. **Create Item:**
   - Fill all required fields (PHYSICAL item)
   - Submit form
   - Verify success toast
   - Navigate to `/items`

4. **Search for Item:**
   - Use search to find created item
   - Verify item appears in results

5. **View Details:**
   - Click view button
   - Verify modal opens
   - Verify all details correct
   - Close modal

6. **Edit Item:**
   - Click edit button
   - Update name and price
   - Submit update
   - Verify success toast

7. **Verify Update:**
   - View item details again
   - Verify changes applied

8. **Delete Item:**
   - Click delete button
   - Confirm deletion
   - Verify success toast
   - Verify item removed from active list

9. **Logout:**
   - Click logout
   - Verify redirect to `/login`

**Expected Results:**
- Complete workflow executes successfully
- All CRUD operations work
- User can logout

**Assertions:**
- Each step completes successfully
- Data persists correctly
- UI updates reflect backend changes

---

## E2E-002: EDITOR Workflow with Ownership

**Priority:** P0  
**Type:** E2E  
**Role:** EDITOR

**Test Steps:**
1. **Login as EDITOR:**
   - Login: `editor1@test.com`
   - Verify dashboard access

2. **Create Own Item:**
   - Create DIGITAL item
   - Verify success

3. **Edit Own Item:**
   - Edit the created item
   - Verify success

4. **Attempt to Edit Admin's Item:**
   - Find item created by admin
   - Verify edit button not visible

5. **Delete Own Item:**
   - Delete own item
   - Verify success

6. **Attempt to Delete Admin's Item:**
   - Find item created by admin
   - Verify delete button not visible

7. **Logout**

**Expected Results:**
- EDITOR can create, edit, delete own items
- EDITOR cannot edit/delete other's items
- Permission controls work correctly

**Assertions:**
- Own items: all buttons visible
- Other's items: edit/delete buttons hidden
- API returns 403 on unauthorized attempts

---

## E2E-003: VIEWER Read-Only Workflow

**Priority:** P0  
**Type:** E2E  
**Role:** VIEWER

**Test Steps:**
1. **Login as VIEWER:**
   - Login: `viewer1@test.com`
   - Verify dashboard access

2. **View Items List:**
   - Navigate to `/items`
   - Verify can see items
   - Verify no create button

3. **Search and Filter:**
   - Use search
   - Apply filters
   - Verify read access works

4. **View Item Details:**
   - Click view button
   - Verify modal opens
   - Verify all details visible

5. **Verify No Edit Access:**
   - Verify no edit buttons visible
   - Attempt direct navigation to `/items/{id}/edit`
   - Verify access denied

6. **Verify No Delete Access:**
   - Verify no delete buttons visible

7. **Verify No Create Access:**
   - Verify no create button
   - Attempt direct navigation to `/items/create`
   - Verify access denied

8. **Logout**

**Expected Results:**
- VIEWER can view all items
- VIEWER cannot create, edit, or delete
- All write operations blocked

**Assertions:**
- Read operations succeed
- Write operations blocked (403)
- UI hides write action buttons

---

## E2E-004: Multi-Item Type Creation Flow

**Priority:** P1  
**Type:** E2E  
**Role:** ADMIN

**Test Steps:**
1. **Login**
2. **Create PHYSICAL Item:**
   - Navigate to create
   - Select PHYSICAL
   - Fill all physical fields
   - Submit
   - Verify success

3. **Create DIGITAL Item:**
   - Navigate to create
   - Select DIGITAL
   - Fill all digital fields
   - Submit
   - Verify success

4. **Create SERVICE Item:**
   - Navigate to create
   - Select SERVICE
   - Fill all service fields
   - Submit
   - Verify success

5. **Verify All Items in List:**
   - Navigate to items list
   - Verify all 3 items visible
   - Verify correct types displayed

6. **Cleanup:**
   - Delete all 3 items

**Expected Results:**
- All 3 item types create successfully
- Conditional fields work correctly
- All items appear in list

**Assertions:**
- Each item type creates without errors
- Conditional fields show/hide correctly
- All items in database

---

## E2E-005: Search, Filter, Sort Combined

**Priority:** P1  
**Type:** E2E  
**Role:** ADMIN

**Test Steps:**
1. **Login**
2. **Create Test Data:**
   - Create 3 items with different categories
   - Create 2 active, 1 inactive

3. **Apply Search:**
   - Search by name
   - Verify filtered results

4. **Apply Status Filter:**
   - Filter by "Active"
   - Verify only active items shown

5. **Apply Category Filter:**
   - Filter by specific category
   - Verify results match

6. **Apply Sort:**
   - Sort by price ascending
   - Verify sort order

7. **Clear All Filters:**
   - Click clear filters
   - Verify all items shown again

8. **Cleanup:**
   - Delete test items

**Expected Results:**
- All filters work independently
- Filters can be combined
- Clear filters resets all

**Assertions:**
- Each filter produces correct results
- Combined filters work correctly
- Clear filters resets state

---

## E2E-006: Pagination Full Flow

**Priority:** P1  
**Type:** E2E  
**Role:** ADMIN

**Test Steps:**
1. **Login**
2. **Create 25 Test Items:**
   - Loop to create 25 items
   - Verify all created

3. **Verify Pagination:**
   - Navigate to items list
   - Verify page 1 shows 20 items (default)
   - Verify pagination controls visible

4. **Navigate to Page 2:**
   - Click next button
   - Verify page 2 loads
   - Verify different items shown

5. **Navigate Back to Page 1:**
   - Click previous button
   - Verify page 1 loads

6. **Change Page Size:**
   - Select 50 items per page
   - Verify all 25 items now on page 1

7. **Cleanup:**
   - Delete all 25 test items

**Expected Results:**
- Pagination works correctly
- Page size change works
- Navigation between pages works

**Assertions:**
- Correct number of items per page
- Page navigation works
- Page size dropdown works

---

## E2E-007: File Upload and View Flow

**Priority:** P1  
**Type:** E2E  
**Role:** ADMIN

**Test Steps:**
1. **Login**
2. **Create Item with File:**
   - Navigate to create
   - Fill all required fields
   - Upload test file (image.jpg)
   - Verify file selected
   - Submit
   - Verify success

3. **View Item Details:**
   - Open item details modal
   - Verify file attachment shown
   - Verify file can be downloaded/viewed

4. **Edit Item - Replace File:**
   - Edit the item
   - Remove old file
   - Upload new file
   - Submit update
   - Verify success

5. **Verify New File:**
   - View item details
   - Verify new file shown

6. **Cleanup:**
   - Delete item

**Expected Results:**
- File upload works
- File displays in details
- File can be replaced
- File cleanup on delete

**Assertions:**
- File upload successful
- File metadata stored
- File accessible in details

---

## E2E-008: Session and Remember Me Flow

**Priority:** P2  
**Type:** E2E  
**Role:** ADMIN

**Test Steps:**
1. **Login with Remember Me:**
   - Login with Remember Me checked
   - Verify dashboard access

2. **Perform Actions:**
   - Create an item
   - Edit an item
   - View items list

3. **Simulate Browser Refresh:**
   - Refresh page
   - Verify still logged in
   - Verify session persists

4. **Logout and Login Without Remember Me:**
   - Logout
   - Login without Remember Me
   - Verify dashboard access

5. **Simulate Session Timeout:**
   - Wait for token expiration (or mock)
   - Attempt action
   - Verify auto-refresh or re-login prompt

6. **Logout**

**Expected Results:**
- Remember Me extends session
- Session persists across refresh
- Token refresh works
- Logout clears session

**Assertions:**
- Session persists with Remember Me
- Session cleared on logout
- Token refresh mechanism works

---

# Test Execution Summary

## Isolated Tests (30)
- **Auth:** 5 tests
- **Create:** 6 tests
- **List:** 6 tests
- **Details:** 4 tests
- **Edit:** 5 tests
- **Delete:** 4 tests

## E2E Tests (8)
- **Complete workflows:** 3 tests (ADMIN, EDITOR, VIEWER)
- **Feature combinations:** 5 tests

## Total: 38 Test Cases

---

# Test Data Management

## User Pool
```json
{
  "admin": ["admin1@test.com", "admin2@test.com", "admin3@test.com", "admin4@test.com"],
  "editor": ["editor1@test.com", "editor2@test.com", "editor3@test.com", "editor4@test.com"],
  "viewer": ["viewer1@test.com", "viewer2@test.com", "viewer3@test.com", "viewer4@test.com"],
  "password": "Admin@123"
}
```

## Test Item Templates
```json
{
  "physical": {
    "name": "Test Physical {uuid}",
    "description": "Test physical item description",
    "item_type": "PHYSICAL",
    "price": 99.99,
    "category": "Electronics",
    "weight": 2.5,
    "dimensions": {"length": 30, "width": 20, "height": 10}
  },
  "digital": {
    "name": "Test Digital {uuid}",
    "description": "Test digital item description",
    "item_type": "DIGITAL",
    "price": 49.99,
    "category": "Software",
    "download_url": "https://example.com/file.zip",
    "file_size": 1048576
  },
  "service": {
    "name": "Test Service {uuid}",
    "description": "Test service item description",
    "item_type": "SERVICE",
    "price": 150.00,
    "category": "Consulting",
    "duration_hours": 8
  }
}
```

---

**End of Test Cases Document**
