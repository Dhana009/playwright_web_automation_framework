# FlowHub Web Automation Framework - Quick Reference

**Target:** https://testing-box.vercel.app  
**Stack:** Playwright + Pytest + Python  
**Purpose:** Production-grade web automation with parallel execution

---

## Problems We're Solving

1. **Slow Tests** → Parallel execution (8x faster)
2. **Flaky Tests** → Smart retry + auto-wait
3. **Maintenance Hell** → Page Object Model
4. **Data Conflicts** → User pool + seed data strategy
5. **Hard to Debug** → Screenshots + logs + Allure reports

---

## Core Architecture (20 Decisions)

### **Execution**
- **8 parallel workers** → Full CPU utilization
- **24 user accounts** → 8 ADMIN, 8 EDITOR, 8 VIEWER
- **Smart auth** → Validate tokens, reuse if valid, re-login if expired
- **New context per test** → Complete isolation

### **Test Data**
- **72 seed items** → Persistent baseline data (API-created)
- **Transient data** → Per-test, auto-cleanup
- **Worker mapping** → Worker 0 = admin1/editor1/viewer1

### **Test Design**
- **80% isolated** → Fast, parallel-safe feature tests
- **20% E2E** → Complete user workflows
- **Test Context Pattern** → Centralized user/role/token/seed mapping

### **Reliability**
- **3-layer retry** → Playwright auto-wait + pytest reruns (2x) + custom wrappers
- **Semantic locators** → role > label > testid > CSS
- **Page Object Model** → UI changes in one place

### **Reporting & CI/CD**
- **Allure reports** → Screenshots, timeline, retry info
- **GitHub Actions** → Parallel matrix (Chromium, Firefox, WebKit)
- **Screenshots** → All failures
- **Logs** → Last 5 local, 30 days CI

---

## Test Coverage (38 Tests)

**6 Flows:**
1. Auth (login, logout, session)
2. Create (3 item types, validation, permissions)
3. List (search, filter, sort, pagination)
4. Details (modal, iframe, loading states)
5. Edit (permissions, ownership)
6. Delete (soft delete, confirmation, permissions)

**Role Testing:**
- ADMIN: Full access
- EDITOR: Create/edit/delete own items
- VIEWER: Read-only

---

## Key Patterns

**Test Independence:**
```
Create data → Use → Cleanup (no shared state)
```

**Smart Auth:**
```
Check cached token → Validate → Reuse ✅ or Re-login
```

**Seed Data:**
```
Local: Reuse if exists (idempotent)
CI/CD: Fresh every run
```

**Lazy Loading:**
```
Smoke tests (5 tests) → 1-2 logins, 3-6 seed items
Full suite (38 tests) → 24 logins, 72 seed items
Only creates what's needed
```

**Worker Mapping:**
```
Test @role("ADMIN") + Worker 0 → admin1@test.com
Test @role("EDITOR") + Worker 2 → editor3@test.com
```

---

## Execution Flow

**Setup (Once):**
1. Validate/create 24 auth states
2. Create/validate 72 seed items (API)

**Per Test:**
1. Get test context (user, role, token, seed data)
2. Load auth state (no login UI)
3. Run test with seed data
4. Cleanup transient data
5. Screenshot on failure

**Results:**
- Parallel execution: ~5 minutes (vs 20+ sequential)
- Allure report with screenshots
- Logs for debugging

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| Framework | Pytest |
| Automation | Playwright |
| Parallel | pytest-xdist (8 workers) |
| Retry | pytest-rerunfailures (2x) |
| Randomization | pytest-random-order |
| Timeout | pytest-timeout (60s) |
| API Client | requests |
| Reporting | Allure |
| CI/CD | GitHub Actions (parallel matrix) |

---

## Success Metrics

- ✅ Test execution: < 5 minutes
- ✅ Test stability: > 95% pass rate
- ✅ Coverage: All 6 flows + 3 roles
- ✅ Parallel speedup: 8x faster

---

**Industry Standard:** Follows patterns from Google, Netflix, Uber, Microsoft
