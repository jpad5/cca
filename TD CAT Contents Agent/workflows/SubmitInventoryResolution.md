# SubmitInventoryResolution workflow

Build this workflow in the Copilot Studio visual designer. Do not create a local
`workflow.json` file.

## Security prerequisite

Use run-only-user Dataverse and Office 365 Users connections. Derive caller identity,
verify assignment, and authorize access to both the case and target item.

## Trigger

Use **When an agent calls the flow** with required `caseId` (Text),
`expectedVersion` (Number), `idempotencyKey` (Text), `itemId` (Text), `itemVersion`
(Number), `resolution` (Text), `correctedValues` (Text containing compact JSON), and
`reason` (Text). Allow only `Correct`, `Accept`, `Duplicate`, `Exclude`, or `Hold`.

## Response

Use **Respond to the agent** with **Asynchronous response** set to **Off** for a
synchronous response and return every common output from
[README.md](README.md). Return sanitized item/issue identifiers and counts, never raw
original row JSON.

## Designer actions

1. Initialize correlation/caller values. Validate required fields, fixed resolution,
   reason, and JSON object shape before mutation.
2. Apply the standard `Command Ledger` replay/reuse check.
3. Get the case and enforce assignment, expected Case Version, and state
   `InventoryReview` or `HeldInventoryIncomplete`.
4. Get the item and verify it belongs to this case and its Item Version equals
   `itemVersion`. A stale item returns `Conflict` without writes.
5. Apply one explicit resolution per invocation. For `Correct`, allow-list supported
   fields and validate types/ranges. Create a new
   immutable item version with corrected values and disposition `Corrected`; retain
   the prior version. Reject unknown fields.
6. For `Accept`, `Duplicate`, or `Exclude`, create a new version with the selected
   disposition. For `Hold`, create a new version with `Held` and set case state
   `HeldInventoryIncomplete`.
7. Resolve or update only issues addressed by this explicit resolution and record the
   reason. Do not close unrelated issues.
8. Requery open material inventory issues. If none remain, set `InventoryComplete`;
   otherwise use `InventoryReview`, except an explicit hold remains
   `HeldInventoryIncomplete`.
9. Increment Case Version once, set Checkpoint `SubmitInventoryResolution`, write the
   ledger result, and append an audit event with changed field names but no sensitive
   before/after values.
10. Respond with persisted state/version, new item version, remaining issues count,
    and a sanitized summary.

## Tool configuration

> Applies one explicit, versioned inventory correction or disposition to an item in
> InventoryReview or HeldInventoryIncomplete. It never infers corrections and sets
> InventoryComplete only when no material inventory issues remain.

## Acceptance tests

1. Invalid resolution/JSON/field/value returns `NeedsInput` without writes.
2. Stale case or item version returns `Conflict`.
3. A correction creates a new item version and retains the original.
4. Duplicate/exclude/accept resolves only the addressed issue; hold enters the hold.
5. The final material resolution advances to InventoryComplete.
6. Exact retries do not create another item version.
7. The workflow completes in under 100 seconds and responds synchronously.
