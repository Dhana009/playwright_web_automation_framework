# Web Automation vs API Automation - Testing Scope & Strategy

**Purpose:** Clarify what we test in Web Automation vs API Automation  
**Date:** 2026-01-02

---

## Core Distinction

### **API Testing = Tests the LOGIC**
- Backend validation rules
- Business logic correctness
- Data integrity
- Boundary conditions
- Deep functional testing

### **Web Testing = Tests the UI BEHAVIOR**
- UI reflects API responses correctly
- User can complete workflows
- Error messages display
- UI elements work as expected
- User experience validation

---

## Test Design Techniques - Where They Apply

| Technique | API Testing (Primary) | Web Testing (Secondary) |
|-----------|----------------------|------------------------|
| **Boundary Value Analysis (BVA)** | ✅ Test all boundary values | ⚠️ Verify UI shows errors for invalid boundaries |
| **Equivalence Partitioning (EP)** | ✅ Test all partitions (valid/invalid) | ⚠️ Verify UI handles each partition correctly |
| **Decision Tables** | ✅ Test all rule combinations | ⚠️ Verify UI reflects business rules |
| **State Transition Testing** | ✅ Test all state changes | ⚠️ Verify UI shows correct states |

---

## Practical Example: Price Field Testing

### **API Tests (Detailed Functional Testing)**

**Boundary Value Analysis:**
```
Field: Price (min: 0.01, max: 999999.99)

Test Cases:
✅ price = 0.00 → 400 Bad Request (below min)
✅ price = 0.01 → 200 OK (min boundary)
✅ price = 0.02 → 200 OK (just above min)
✅ price = 100.00 → 200 OK (mid value)
✅ price = 999999.98 → 200 OK (just below max)
✅ price = 999999.99 → 200 OK (max boundary)
✅ price = 1000000.00 → 400 Bad Request (above max)
✅ price = -10.00 → 400 Bad Request (negative)
✅ price = 99.999 → 400 Bad Request (3 decimals, invalid precision)
```

**Equivalence Partitioning:**
```
Valid Partition: 0.01 to 999999.99
✅ Test: 50.00 → 200 OK

Invalid Partition 1: < 0.01
✅ Test: 0.00 → 400
✅ Test: -5.00 → 400

Invalid Partition 2: > 999999.99
✅ Test: 1000000.00 → 400

Invalid Partition 3: Wrong format
✅ Test: "abc" → 400
✅ Test: null → 400
```

### **Web Tests (UI Behavior Validation)**

**What We Test:**
```
✅ UI shows error message when price = 0.00
✅ UI accepts valid price (99.99)
✅ UI shows error for negative price
✅ Form doesn't submit when validation fails
✅ Success toast appears when item created
```

**We DON'T test all boundaries in Web:**
- We test 1-2 representative cases
- We verify UI correctly displays API errors
- We verify user can complete the workflow

---

## Web Test Case Categories

### **Positive Test Cases**
**Definition:** Valid inputs, expected to succeed

**Examples:**
- Login with valid credentials
- Create item with all required fields filled correctly
- Search for existing item
- Edit item with valid data

**What We Verify:**
- Success messages/toasts appear
- User redirected to correct page
- Data displays correctly in UI

---

### **Negative Test Cases**
**Definition:** Invalid inputs, expected to fail gracefully

**Examples:**
- Login with wrong password
- Create item with missing required fields
- VIEWER attempts to create item (permission denied)
- EDITOR attempts to delete admin's item

**What We Verify:**
- Error messages display in UI
- Form doesn't submit
- User stays on same page
- Appropriate error toast appears

---

### **Edge Cases**
**Definition:** Boundary conditions, unusual scenarios

**Examples:**
- Login with Remember Me checked
- Create item with maximum length name (100 chars)
- Upload file at size limit (5 MB)
- Pagination with exactly 20 items (page boundary)
- Session timeout during action

**What We Verify:**
- UI handles edge conditions correctly
- No crashes or unexpected behavior
- Appropriate feedback to user

---

## Web Test Cases - Categorized

### **Positive Cases (Happy Path)**
1. TC-AUTH-001: Login with valid credentials ✅ **POSITIVE**
2. TC-CREATE-001: Create PHYSICAL item with valid data ✅ **POSITIVE**
3. TC-CREATE-002: Create DIGITAL item with valid data ✅ **POSITIVE**
4. TC-CREATE-003: Create SERVICE item with valid data ✅ **POSITIVE**
5. TC-LIST-001: View items list ✅ **POSITIVE**
6. TC-LIST-002: Search items by name ✅ **POSITIVE**
7. TC-DETAILS-001: View item details in modal ✅ **POSITIVE**
8. TC-EDIT-001: ADMIN edit any item ✅ **POSITIVE**
9. TC-EDIT-002: EDITOR edit own item ✅ **POSITIVE**
10. TC-DELETE-001: ADMIN delete any item ✅ **POSITIVE**

### **Negative Cases (Invalid Inputs/Permissions)**
1. TC-AUTH-002: Login with invalid credentials ❌ **NEGATIVE**
2. TC-AUTH-005: Login with empty fields ❌ **NEGATIVE**
3. TC-CREATE-004: Create item with missing required fields ❌ **NEGATIVE**
4. TC-CREATE-006: VIEWER cannot create item ❌ **NEGATIVE** (Permission)
5. TC-EDIT-003: EDITOR cannot edit other's item ❌ **NEGATIVE** (Permission)
6. TC-EDIT-004: VIEWER cannot edit any item ❌ **NEGATIVE** (Permission)
7. TC-DELETE-003: EDITOR cannot delete other's item ❌ **NEGATIVE** (Permission)

### **Edge Cases (Boundaries/Unusual Scenarios)**
1. TC-AUTH-003: Login with Remember Me enabled ⚠️ **EDGE CASE**
2. TC-CREATE-005: Create item with file upload (max size) ⚠️ **EDGE CASE**
3. TC-LIST-004: Sort items by price ⚠️ **EDGE CASE**
4. TC-LIST-005: Pagination - navigate to next page ⚠️ **EDGE CASE**
5. TC-DETAILS-002: View item with iframe content ⚠️ **EDGE CASE**
6. TC-DETAILS-004: Item details modal loading state ⚠️ **EDGE CASE**
7. E2E-008: Session and Remember Me flow ⚠️ **EDGE CASE**

---

## Why This Matters for Your Interview

**Interviewer might ask:**
> "How do you decide what to test in Web automation vs API automation?"

**Your Answer:**
> "In API automation, I focus on deep functional testing using techniques like Boundary Value Analysis and Equivalence Partitioning to validate business logic, data integrity, and all edge cases. 
>
> In Web automation, I focus on UI behavior - verifying that the UI correctly displays errors from the API, success messages appear, user workflows complete successfully, and UI elements work as expected. 
>
> For example, for a price field with range 0.01-999999.99, in API testing I'd test all boundaries (0.00, 0.01, 0.02, max-1, max, max+1), but in Web testing I'd verify the UI shows the error message when I enter 0.00 and accepts 99.99. The deep validation testing happens at the API layer."

---

## Summary

**API Testing:**
- ✅ All boundary values
- ✅ All equivalence partitions
- ✅ All business rule combinations
- ✅ Deep functional validation
- ✅ 100+ test cases for comprehensive coverage

**Web Testing:**
- ✅ Representative positive cases (happy path)
- ✅ Representative negative cases (UI shows errors)
- ✅ Key edge cases (boundaries, unusual scenarios)
- ✅ End-to-end user workflows
- ✅ 30-40 test cases for UI behavior coverage

**Both are essential. API tests the logic. Web tests the user experience.**

---

**End of Document**
