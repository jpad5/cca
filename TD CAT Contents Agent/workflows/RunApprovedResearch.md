# RunApprovedResearch workflow

Build this workflow in the Copilot Studio visual designer. Do not create a local
`workflow.json` file.

## Security prerequisite

Use run-only-user Dataverse, Office 365 Users, and only research connectors approved
in the environment DLP policy. Maintain the Canadian source allowlist as governed
data; never accept a source URL or domain supplied by the agent.

## Trigger

Use **When an agent calls the flow** with required `caseId` (Text),
`expectedVersion` (Number), `idempotencyKey` (Text), `inventoryVersion` (Text), and
optional `batchCursor` (Text).

## Response

Use **Respond to the agent** with **Asynchronous response** set to **Off** for a
synchronous response containing every common output from [README.md](README.md).
Return the next opaque cursor and evidence version in `authoritativeValues`; do not
return unrestricted page content or connector payloads.

## Designer actions

1. Derive correlation ID and caller email; validate required inputs.
2. Apply exact-match `Command Ledger` replay and changed-key rejection.
3. Get the case and verify Assigned Adjuster, state `InventoryComplete`, expected
   Case Version, and exact persisted inventory version. Return `Conflict` without
   mutation for a stale state, case version, or inventory version.
4. Select the next bounded batch of accepted/corrected items using the opaque cursor.
5. For each item, query only enabled Canadian allowlist sources through approved
   native connector or configured AI actions. Never use unrestricted web search.
6. Validate source domain against the current allowlist after redirects. Required
   evidence fields are source, retrieval time, evidence text, price, currency,
   qualification code, snapshot reference, and content hash. Persist them with the
   Evidence Version ID and item/case relationships in one immutable
   `Comparator Evidence` row per qualified result.
7. Permit `GenericEstimate` only when explicitly flagged and no qualified comparator
   is available under configured policy. Record source attempts and a typed issue.
8. If items remain, persist the cursor/checkpoint, retain `InventoryComplete`,
   increment Case Version, and return `continuationRequired: true`.
9. When every item has qualified evidence or an explicit generic estimate, set
   `ResearchComplete`, increment the version, and return `continuationRequired: false`.
10. Write the ledger result and audit event with batch boundaries, allowlist version,
    evidence IDs, and hashes, excluding full page content.

Transient source failures return a retryable issue and cursor without looping past
the workflow timeout. Exhausted/non-retryable failures return `Held` and preserve the
last safe checkpoint.

## Tool configuration

> Researches one bounded inventory batch using only governed Canadian sources. Stores
> immutable evidence and returns an opaque cursor until all items have qualified
> evidence or an explicitly flagged generic estimate.

## Acceptance tests

1. A non-allowlisted or redirected domain is rejected and never stored as evidence.
2. Each evidence row has source, time, text, price, currency, qualification, and hash.
3. Batches resume from the cursor without duplicate evidence.
4. ResearchComplete is set only when every eligible item meets evidence policy.
5. Wrong assignment/version/state/inventory binding fails without research writes.
6. Exact retries replay; changed key reuse is rejected.
7. Every invocation completes in under 100 seconds and responds synchronously.
