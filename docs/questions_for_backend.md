# Questions for Backend Team (Flow 3: Item List)

We are implementing tests for **TC-LIST-001** to **TC-LIST-005** and encountering ambiguities regarding API filtering and sorting. Please provide the exact expected behavior for the following:

## 1. Filter Parameters
*   **Search**: What is the query parameter name? (`q`, `search`, `query`?)
    *   *Observation:* `search=...` seemed to work initially but return 0 results in recent probe.
    *   *Question:* What fields does it search against? (Name, Description, Category?)
*   **Status**: Is the parameter `status`?
    *   *Question:* What are the valid case-sensitive values? (`active`/`inactive` or `ACTIVE`/`INACTIVE`)?
    *   *Question:* Does `status=all` exist or do we omit the parameter for all?

## 2. Sorting Behavior
*   **Sort Keys**: What are the valid `sort_by` fields?
    *   *Specific Question:* For "Created Date", is the key `created_at`, `createdAt`, `creation_date`?
    *   *Specific Question:* For "Price", is the key `price`?
*   **Data Type**:
    *   Does the API return Price as a **Number** (10.5) or **String** ("10.50")?
    *   Does the API return `created_at` as ISO string?

## 3. Pagination Limits
*   **Max Limit**: We received `422 Unprocessable Entity` when sending `limit=1000`.
    *   *Question:* What is the maximum allowed `limit`? (e.g., 100?)
    *   *Question:* What is the default `limit` if unspecified?

## 4. Seed Data State
*   **Persistence**: We are seeding items like `SEED_Low_Price_admin1`.
    *   *Question:* Are "Active" items guaranteed to stay active unless manually changed, or is there an auto-expiry?

## 5. Error Handling
*   **422 vs 400**:
    *   *Question:* Should invalid filter parameters (e.g. `status=invalid`) return 400 (Bad Request) or just ignore the filter?
