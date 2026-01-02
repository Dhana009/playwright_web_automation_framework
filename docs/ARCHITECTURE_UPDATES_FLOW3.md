# Architecture Updates for Flow 3 (List/Search/Filter/Sort/Paginate)

## What Changed

Updated **Decision 19: Test Data Management Strategy** in ARCHITECTURE.md to support per-test, just-in-time data setup.

## Key Points (IMPORTANT)

### ❌ What Did NOT Change
- Auth strategy (still 24 users - admin1-8, editor1-8, viewer1-8)
- User pool structure (one representative per role, but any user can run test)
- Token lifecycle
- Worker assignment strategy

### ✅ What DID Change
**Removed:** Session-level baseline seed data creation  
**Added:** Per-test, account-specific, lazy-loading data setup (JIT)

## The Concept

### Before (Old Way)
```
Session Start:
├─ Create 72 seed items (3 per user, 24 users)
├─ All tests share these items
└─ Problem: ❌ Tests dependent on each other
           ❌ Wasted data if test doesn't run
```

### Now (New Way - Pure Lazy Loading)
```
Session Start:
├─ Just authenticate users
├─ NO data creation

Before Each Test:
├─ Check: Does this user have data for THIS test?
│  ├─ NO → Create test-specific data for this user
│  └─ YES → Reuse it
└─ Run test with user's account-specific data

Result: ✅ Each test completely independent
        ✅ Only needed data created
        ✅ Can run in ANY order
        ✅ Any user (admin1, admin2, admin3) can run it
```

## Critical Understanding

**IMPORTANT: Not about admin1, admin2, admin3...**

```
❌ WRONG: "Only admin1 runs Flow 3 tests"

✅ CORRECT: "ANY admin (admin1, admin2, ... admin8) can run Flow 3
            Before they run, make sure THAT admin has the data"
```

**Example:**
```
Scenario 1: admin1 runs TC-LIST-001
├─ Check: Does admin1 have view list data?
├─ NO → Create it for admin1
└─ Run test

Scenario 2: admin3 runs same TC-LIST-001 (different run)
├─ Check: Does admin3 have view list data?
├─ NO → Create it for admin3 (separate from admin1's)
└─ Run test

Both work independently!
```

## Implementation Details

### Lazy Loading Pattern
```python
@pytest.fixture(scope="function")
def test_context(request, seed_data, auth_states):
    # Get whatever user this test is assigned to
    user_email = get_user_for_test(request)
    token = auth_states[user_email]["token"]
    test_name = request.node.name
    
    # Before running test: Ensure THIS user has THIS test's data
    test_data = ensure_test_specific_data(user_email, token, test_name)
    
    # If data didn't exist, it was created above
    # If data existed, it was reused
    # Either way, test has what it needs
    
    yield TestContext(user_email, seed_data[user_email], test_data)
```

### Flow 3 Data Examples

**TC-LIST-001 (View Items):**
```
User: Whatever admin gets assigned (admin1, admin2, admin3, etc.)
Data: 5 basic items
Check: "Does this user have 5 view items?"
Setup: Create if missing
```

**TC-LIST-002 (Search Items):**
```
User: Whatever admin gets assigned next
Data: 1 unique searchable item (e.g., "Laptop")
Check: "Does this user have a searchable item?"
Setup: Create if missing
```

**TC-LIST-005 (Pagination):**
```
User: Whatever admin gets assigned
Data: 21 items (for pagination across pages)
Check: "Does this user have 21 pagination items?"
Setup: Create if missing (THIS is the important one for pagination!)
```

## Pure Lazy Loading (JIT) Data System

### One-Tier: Test-Specific Data Only
- **When:** Created per-test, only when needed
- **Quantity:** Exactly what that test needs (5, 21, 3, etc.)
- **Purpose:** All operations (Create, Edit, Delete, List, Search, Filter, Sort, Paginate)
- **Lifecycle:** Reused within user session if test runs again

**No baseline data!** Only create what's actually needed.

## Summary

✅ **Architecture mostly unchanged** - Still 24 users, same auth, same structure
✅ **Removed baseline data** - No session-level seed creation
✅ **Added per-test JIT setup** - Create data only when test needs it
✅ **True independence** - Each test completely isolated with its own data
✅ **Flexible assignment** - Any admin (admin1, admin2, admin3, etc.) can run any test
✅ **Just-in-time** - Create exactly what's needed, nothing more
✅ **Efficient** - No wasted data, no unnecessary creation

**The KEY principle:** 
```
Before running a test, check if that user (whoever it is) 
has the data that test needs. 
If not, create it. 
Reuse if it exists.
That's it!
```

**No baseline seed data needed!**
