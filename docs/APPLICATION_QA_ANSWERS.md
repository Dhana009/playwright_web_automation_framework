# Application QA Answers (Backend Specs for Flow 3)

Source of Truth provided by Backend Team on 2026-01-02.

## 1. Filter Parameters
*   **Search Param**: `search` (case-sensitive key).
*   **Search Scope**: Matches `name` OR `description` (case-insensitive values).
*   **Status Param**: `status` (exact key).
*   **Status Values**: `active` or `inactive` (LOWERCASE only).
*   **All Status**: Omit the `status` parameter entirely. `status=all` is INVALID.

## 2. Sorting
*   **Key Param**: `sort_by`
*   **Order Param**: `sort_order` (`asc` or `desc`)
*   **Valid Keys**: `name`, `category`, `price`, `createdAt` (NOT `created_at`).
*   **Default**: `createdAt` DESC.

## 3. Data Types
*   **Price**: Returned as `Number` (e.g. `999.99`). Test assertions must handle formatting if UI adds `$`.
*   **Dates**: ISO 8601 String (e.g. `2024-01-15T...`).

## 4. Limits
*   **Max Limit**: 100.
*   **Default Limit**: 20.
*   **Error**: `limit > 100` returns `422 Unprocessable Entity`.

## 5. Persistence
*   **Seed Data**: Persists indefinitely. No auto-expiry.
*   **Strategy**: Use searching or create unique items with timestamps.
