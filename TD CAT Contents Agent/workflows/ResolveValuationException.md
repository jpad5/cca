# ResolveValuationException workflow

Build this workflow in the Copilot Studio visual designer. Do not create a local
`workflow.json` file.

## Security prerequisite

Use run-only-user Dataverse and Office 365 Users connections. Verify licensed-adjuster
assignment and authority for the requested resolution code. Never infer or elevate
override authority from conversation.

## Trigger

Use **When an agent calls the flow** with required `caseId` (Text),
`expectedVersion` (Number), `idempotencyKey` (Text), `issueId` (Text),
`resolutionCode` (Text), `reason` (Text), and `changedValues` (Text containing a
compact JSON object).

## Response

Use **Respond to the agent** with **Asynchronous response** set to **Off** for a
synchronous response with all common outputs. Return the resolved issue ID, earliest
rerun state, and invalidated artifact/version IDs only.

## Designer actions

1. Derive correlation/caller values. Validate issue ID, allow-listed resolution code,
   nonempty reason, and the JSON shape/allow-listed fields in changed values.
2. Apply the standard `Command Ledger` replay/reuse check.
3. Get the case and enforce assignment, expected Case Version, and a supported hold
   state: `HeldFileInvalid`, `HeldInventoryIncomplete`, `HeldRulesUnavailable`,
   `HeldQualityException`, or `HeldAdjuster`. Return `Conflict` when stale.
4. Get the open issue, verify it belongs to the case, and verify the caller has any
   additional authority required by its severity/resolution code.
5. Apply only the explicit allowed changed values by creating new immutable versions
   where applicable. Record resolution code, reason, actor, and resolved time.
6. Determine the earliest affected stage from a fixed invalidation matrix. Never let
   the caller select a later stage than the dependency impact permits.
7. Mark dependent evidence, calculation runs, package artifacts, approvals, and
   decision challenges noncurrent/invalid as applicable; consume outstanding
   challenges so they cannot be replayed.
8. Set the case to the earliest rerun state, increment Case Version, and persist a
   checkpoint listing invalidated opaque IDs and dependency reason.
9. Write `Command Ledger` and `Audit Event` rows with changed field names, invalidated
   IDs/hashes, and transition, but not raw sensitive values.
10. Respond `Succeeded` with a summary that names the stage that must rerun. Do not
    imply the exception is cleared until the applicable downstream gates pass again.

## Tool configuration

> Records one explicit authorized resolution for a held valuation issue, invalidates
> all dependent evidence, calculations, packages, approvals, and challenges, and
> returns the earliest stage that must rerun.

## Acceptance tests

1. Unsupported state/code, missing reason, or disallowed changed field makes no write.
2. Wrong assignment/authority is rejected; stale state/version returns `Conflict`.
3. Resolution updates only the target issue and creates immutable changed versions.
4. Every dependent artifact and active challenge is invalidated as required.
5. The case returns to the earliest stage in the fixed invalidation matrix.
6. Exact retries do not repeat invalidation; changed key reuse is rejected.
7. The workflow completes in under 100 seconds and responds synchronously.
