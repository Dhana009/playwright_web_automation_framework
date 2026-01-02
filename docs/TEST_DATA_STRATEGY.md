# Test Data Management Strategy

**Purpose:** Define how test data is created, managed, and cleaned up across all test cases  
**Date:** 2026-01-02

---

## The Problem

**CRUD operations require different data states:**

| Operation | Data Requirement | Problem |
|-----------|------------------|---------|
| **CREATE** | Clean slate | Easy - create new, delete after |
| **READ** | Existing data | ❌ Need pre-existing data to read |
| **UPDATE** | Existing data | ❌ Need pre-existing data to update |
| **DELETE** | Existing data | ❌ Need pre-existing data to delete |

**If every test creates → uses → deletes, READ/UPDATE/DELETE tests have nothing to work with.**

---

## The Solution: Two-Tier Data Strategy

### **Tier 1: Seed Data (Persistent)**
**Purpose:** Pre-existing data that persists across test runs  
**Lifecycle:** Created once at suite start, never deleted  
**Used For:** READ, UPDATE, DELETE tests

### **Tier 2: Transient Data (Temporary)**
**Purpose:** Test-specific data created and deleted per test  
**Lifecycle:** Created in test setup, deleted in test cleanup  
**Used For:** CREATE tests, isolated operations

---

## Seed Data Specification

### **What Seed Data We Need**

**Per User Account (12 accounts total):**

Each user needs **3 seed items** (one of each type):
- 1 PHYSICAL item
- 1 DIGITAL item  
- 1 SERVICE item

**Total Seed Items:** 12 users × 3 items = **36 seed items**

---

### **Seed Data Structure**

```json
{
  "admin1@test.com": {
    "items": [
      {
        "name": "SEED_Physical_Admin1",
        "description": "Seed physical item for admin1 - DO NOT DELETE",
        "item_type": "PHYSICAL",
        "price": 100.00,
        "category": "Seed_Electronics",
        "weight": 1.5,
        "dimensions": {"length": 20, "width": 15, "height": 10},
        "is_seed": true
      },
      {
        "name": "SEED_Digital_Admin1",
        "description": "Seed digital item for admin1 - DO NOT DELETE",
        "item_type": "DIGITAL",
        "price": 50.00,
        "category": "Seed_Software",
        "download_url": "https://example.com/seed/admin1.zip",
        "file_size": 1048576,
        "is_seed": true
      },
      {
        "name": "SEED_Service_Admin1",
        "description": "Seed service item for admin1 - DO NOT DELETE",
        "item_type": "SERVICE",
        "price": 200.00,
        "category": "Seed_Consulting",
        "duration_hours": 10,
        "is_seed": true
      }
    ]
  },
  // ... repeat for all 12 users
}
```

**Key Points:**
- ✅ Names prefixed with `SEED_` for easy identification
- ✅ Description includes "DO NOT DELETE"
- ✅ `is_seed: true` flag (if backend supports custom fields)
- ✅ Each user has own seed data (ownership isolation)

---

## Test Data Usage Patterns

### **Pattern 1: CREATE Tests**
**Data Strategy:** Transient (create → use → delete)

```python
def test_create_item(authenticated_page):
    # Setup: None needed (clean slate)
    
    # Action: Create new item
    item_name = f"Test_Item_{uuid.uuid4()}"
    create_item(item_name, ...)
    
    # Assert: Item created
    assert item_exists(item_name)
    
    # Cleanup: Delete created item
    delete_item(item_name)
```

**Why:** CREATE tests verify creation logic, don't need existing data

---

### **Pattern 2: READ Tests (List, Search, Filter, Details)**
**Data Strategy:** Use seed data (no cleanup)

```python
def test_view_item_details(authenticated_page, seed_items):
    # Setup: Use seed data
    seed_item = seed_items["admin1"]["physical"]
    
    # Action: View item details
    open_item_details(seed_item["id"])
    
    # Assert: Details displayed correctly
    assert item_name_visible(seed_item["name"])
    
    # Cleanup: None (seed data persists)
```

**Why:** READ tests verify display logic, need existing data

---

### **Pattern 3: UPDATE Tests**
**Data Strategy:** Hybrid (use seed, restore after)

```python
def test_edit_item(authenticated_page, seed_items):
    # Setup: Get seed item + save original state
    seed_item = seed_items["admin1"]["physical"]
    original_name = seed_item["name"]
    original_price = seed_item["price"]
    
    # Action: Update item
    new_name = f"{original_name}_EDITED"
    update_item(seed_item["id"], name=new_name, price=999.99)
    
    # Assert: Update successful
    assert item_name_equals(seed_item["id"], new_name)
    
    # Cleanup: Restore original state
    update_item(seed_item["id"], name=original_name, price=original_price)
```

**Why:** UPDATE tests verify edit logic, need existing data, must restore to not affect other tests

---

### **Pattern 4: DELETE Tests**
**Data Strategy:** Create transient item to delete

```python
def test_delete_item(authenticated_page):
    # Setup: Create item specifically for deletion
    item_name = f"ToDelete_{uuid.uuid4()}"
    item_id = create_item(item_name, ...)
    
    # Action: Delete item
    delete_item(item_id)
    
    # Assert: Item deleted (soft delete)
    assert item_not_in_active_list(item_id)
    
    # Cleanup: None needed (already deleted)
```

**Why:** DELETE tests verify deletion logic, can't delete seed data, create transient item instead

---

## Seed Data Management

### **Setup Phase (Session-Scoped Fixture)**

```python
@pytest.fixture(scope="session")
def seed_data(setup_auth_states):
    """Create seed data once for entire test suite"""
    
    seed_items = {}
    
    # For each user in pool
    for role in ["admin", "editor", "viewer"]:
        for i in range(1, 5):
            user_email = f"{role}{i}@test.com"
            
            # Login as user
            auth_state = f"auth_{role}{i}.json"
            
            # Create 3 seed items
            items = []
            
            # Physical item
            physical = create_item_api(
                name=f"SEED_Physical_{role}{i}",
                description=f"Seed physical item for {user_email} - DO NOT DELETE",
                item_type="PHYSICAL",
                price=100.00,
                category="Seed_Electronics",
                weight=1.5,
                dimensions={"length": 20, "width": 15, "height": 10}
            )
            items.append(physical)
            
            # Digital item
            digital = create_item_api(
                name=f"SEED_Digital_{role}{i}",
                description=f"Seed digital item for {user_email} - DO NOT DELETE",
                item_type="DIGITAL",
                price=50.00,
                category="Seed_Software",
                download_url="https://example.com/seed/file.zip",
                file_size=1048576
            )
            items.append(digital)
            
            # Service item
            service = create_item_api(
                name=f"SEED_Service_{role}{i}",
                description=f"Seed service item for {user_email} - DO NOT DELETE",
                item_type="SERVICE",
                price=200.00,
                category="Seed_Consulting",
                duration_hours=10
            )
            items.append(service)
            
            seed_items[user_email] = {
                "physical": physical,
                "digital": digital,
                "service": service
            }
    
    # Save seed data IDs to file for reference
    with open("seed_data_ids.json", "w") as f:
        json.dump(seed_items, f, indent=2)
    
    yield seed_items
    
    # Cleanup: DO NOT DELETE SEED DATA
    # Seed data persists for next test run
```

---

### **Cleanup Phase (Session-Scoped Teardown)**

```python
@pytest.fixture(scope="session", autouse=True)
def cleanup_transient_data():
    """Cleanup only transient test data, preserve seed data"""
    
    yield  # Tests run
    
    # After all tests complete
    print("Cleaning up transient test data...")
    
    # Delete all items NOT prefixed with "SEED_"
    all_items = get_all_items_api()
    
    for item in all_items:
        if not item["name"].startswith("SEED_"):
            delete_item_api(item["id"])
            print(f"Deleted transient item: {item['name']}")
    
    print("Cleanup complete. Seed data preserved.")
```

---

## Test Case Data Requirements

### **Tests Using Seed Data**

| Test Case | Seed Data Needed | Restore After? |
|-----------|------------------|----------------|
| TC-LIST-001: View items list | ✅ All seed items | No |
| TC-LIST-002: Search items | ✅ Seed items | No |
| TC-LIST-003: Filter items | ✅ Seed items | No |
| TC-LIST-004: Sort items | ✅ Seed items | No |
| TC-LIST-005: Pagination | ✅ Seed items | No |
| TC-DETAILS-001: View details | ✅ 1 seed item | No |
| TC-DETAILS-002: View iframe | ✅ 1 seed item with embed_url | No |
| TC-EDIT-001: Admin edit any | ✅ 1 seed item | **Yes** |
| TC-EDIT-002: Editor edit own | ✅ 1 seed item | **Yes** |

### **Tests Creating Transient Data**

| Test Case | Creates Data? | Deletes After? |
|-----------|---------------|----------------|
| TC-CREATE-001: Create physical | ✅ Yes | ✅ Yes |
| TC-CREATE-002: Create digital | ✅ Yes | ✅ Yes |
| TC-CREATE-003: Create service | ✅ Yes | ✅ Yes |
| TC-CREATE-005: Create with file | ✅ Yes | ✅ Yes |
| TC-DELETE-001: Admin delete | ✅ Yes (to delete) | ✅ Yes (via delete action) |
| TC-DELETE-002: Editor delete own | ✅ Yes (to delete) | ✅ Yes (via delete action) |

---

## Fixture Implementation

### **Seed Data Fixture**

```python
@pytest.fixture
def seed_items(seed_data, worker_id):
    """Provide seed data for current worker's user"""
    
    # Determine which user this worker is using
    worker_num = int(worker_id.replace("gw", "")) if worker_id != "master" else 0
    
    # Map worker to user (assuming admin role for this example)
    user_email = f"admin{worker_num + 1}@test.com"
    
    return seed_data[user_email]
```

### **Transient Item Fixture**

```python
@pytest.fixture
def create_transient_item(authenticated_page):
    """Create a transient item that will be auto-deleted"""
    
    created_items = []
    
    def _create(item_type="PHYSICAL", **kwargs):
        item_name = f"Transient_{item_type}_{uuid.uuid4()}"
        item_id = create_item_via_ui(
            page=authenticated_page,
            name=item_name,
            item_type=item_type,
            **kwargs
        )
        created_items.append(item_id)
        return item_id
    
    yield _create
    
    # Cleanup: Delete all created items
    for item_id in created_items:
        delete_item_api(item_id)
```

---

## Data Isolation Strategy

### **Per-User Seed Data**

**Why:** Parallel execution requires data isolation

**How:**
- Each user has own seed items
- Worker 0 (admin1) uses admin1's seed items
- Worker 1 (admin2) uses admin2's seed items
- No conflicts between workers

**Example:**
```
Worker 0 (admin1@test.com):
  - SEED_Physical_admin1
  - SEED_Digital_admin1
  - SEED_Service_admin1

Worker 1 (admin2@test.com):
  - SEED_Physical_admin2
  - SEED_Digital_admin2
  - SEED_Service_admin2
```

---

## Naming Conventions

### **Seed Data Naming**
```
SEED_{ItemType}_{UserRole}{Number}

Examples:
- SEED_Physical_admin1
- SEED_Digital_editor2
- SEED_Service_viewer3
```

### **Transient Data Naming**
```
Transient_{ItemType}_{UUID}

Examples:
- Transient_PHYSICAL_a1b2c3d4
- Transient_DIGITAL_e5f6g7h8
```

### **Test-Specific Naming**
```
Test_{Purpose}_{UUID}

Examples:
- Test_Create_a1b2c3d4
- Test_FileUpload_e5f6g7h8
- ToDelete_f9g0h1i2
```

---

## Summary

### **Data Strategy**

| Data Type | Purpose | Lifecycle | Used By |
|-----------|---------|-----------|---------|
| **Seed Data** | Pre-existing items for READ/UPDATE tests | Persistent (never deleted) | READ, UPDATE tests |
| **Transient Data** | Test-specific items | Created → Used → Deleted | CREATE, DELETE tests |

### **Key Rules**

1. ✅ **Seed data is sacred** - Never delete items prefixed with `SEED_`
2. ✅ **Each user has own seed data** - Parallel execution safe
3. ✅ **UPDATE tests must restore** - Return seed data to original state
4. ✅ **DELETE tests create transient items** - Don't delete seed data
5. ✅ **Cleanup only transient data** - Preserve seed data for next run

---

**End of Document**
