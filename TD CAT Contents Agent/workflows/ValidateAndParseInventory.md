# ValidateAndParseInventory workflow

Build this workflow in the Copilot Studio visual designer. Do not create a local
`workflow.json` file.

## Security prerequisite

Use run-only-user Dataverse, Office 365 Users, and approved Excel Online connections.
Derive caller identity and enforce assignment. Never send workbook/CSV bytes or row
content to an AI action.

## Trigger

Use **When an agent calls the flow** with required `caseId` (Text),
`expectedVersion` (Number), `idempotencyKey` (Text), and `sourceVersionId` (Text).
Accept optional `batchCursor` (Text); empty means the first bounded batch.

## Response

Use **Respond to the agent** with **Asynchronous response** set to **Off** for a
synchronous response with the common outputs from
[README.md](README.md). Also return `continuationRequired` and the opaque next cursor
in `authoritativeValues`. Do not return original or normalized row contents.

## Designer actions

1. Initialize correlation/caller values and validate required inputs.
2. Apply the standard `Command Ledger` exact-replay and changed-key rejection check.
3. Get the case and verify assignment, state `InventoryAccepted`, and expected Case
   Version. For continuation calls, also allow `InventoryReview` only when the
   checkpoint identifies this same source and parse operation.
4. Get the immutable source by `sourceVersionId` and verify it belongs to the case,
   classification is permitted, and content hash still matches.
5. Read only the configured worksheet/table or CSV structure with native actions;
   use no AI action for parsing, normalization, validation, or duplicate detection.
   Validate required headers and template version. On structural failure, create a
   typed issue and set `HeldFileInvalid`.
6. Process a configured maximum batch, sized to stay below 100 seconds. For each row,
   preserve compact original row JSON, normalize supported text/numeric fields,
   create a deterministic item version key, and create an `Inventory Item` at version
   `1` with disposition `Pending`.
7. Detect duplicate item keys and missing material fields. Create typed `Case Issue`
   rows linked to affected items; never invent or silently repair values.
8. Persist the next cursor/checkpoint. If rows remain, retain `InventoryAccepted`,
   increment the case version, and return `continuationRequired: true`.
9. When all rows are processed, set state `InventoryReview`, increment the version,
   and return `continuationRequired: false` with issue counts only.
10. Write one `Command Ledger` row and one `Audit Event` per invocation, recording
    source ID, batch boundaries, counts, and hashes but no inventory contents.

An alternate-key collision on an item must reread the existing item and verify an
exact source/hash match; otherwise hold with `ITEM_VERSION_COLLISION`.

## Tool configuration

> Parses one bounded batch from an authorized immutable inventory source using native
> data actions. Preserves original row evidence, creates normalized item versions and
> typed issues, and returns an opaque continuation cursor without exposing contents.

## Acceptance tests

1. Wrong source/case binding, classification, or hash is rejected without parsing.
2. Invalid structure sets HeldFileInvalid and records a typed issue.
3. A bounded batch creates each item at most once and returns a cursor when needed.
4. Missing fields/duplicates create issues without inferred corrections.
5. Final batch sets InventoryReview; no file bytes or row contents are returned.
6. Assignment, conflict, and idempotent replay controls work on every batch.
7. Every invocation completes in under 100 seconds and responds synchronously.
