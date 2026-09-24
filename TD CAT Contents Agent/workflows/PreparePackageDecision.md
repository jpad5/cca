# PreparePackageDecision workflow

Build this workflow in the Copilot Studio visual designer. Do not create a local
`workflow.json` file.

## Security prerequisite

Use run-only-user Dataverse and Office 365 Users connections. Derive caller identity
and verify licensed-adjuster Assigned Adjuster assignment/authority. Challenge values are workflow
state and must not be user-editable.
This is the mandatory Assignment check.

## Trigger

Use **When an agent calls the flow** with required `caseId` (Text),
`expectedVersion` (Number), `idempotencyKey` (Text), `packageId` (Text),
`packageVersion` (Text), and `packageHash` (Text).

## Response

Use **Respond to the agent** with **Asynchronous response** set to **Off** for a
synchronous response with common outputs plus sanitized `reviewSummary`,
`challengeId`, `challengeExpiresAt`, and immutable package binding. Return opaque
workbook/trace references, not bytes.

## Designer actions

1. Derive correlation/caller values and validate inputs.
2. Apply standard `Command Ledger` replay/reuse checks.
3. Get the case and enforce assignment/authority, state `PackageReady`, and expected
   Case Version. Return `Conflict` without challenge creation if stale.
4. Get the current package and verify its case, ID, version, hash, calculation,
   inventory, evidence, rules, workbook hash, trace hash, and Is Current flag.
5. Invalidate any prior unconsumed challenge for this case/package.
6. Generate a cryptographically unguessable challenge ID with a short expiry. Create
   `Decision Challenge` bound to caller, case version after transition,
   package artifact/version/hash, expiry, and Is Consumed `false`.
7. Set case state `PendingApproval`, increment Case Version, and checkpoint the exact
   package/challenge binding.
8. Build a sanitized review summary from persisted evidence, calculations, rule
   versions, exceptions, and opaque workbook/trace artifacts without recomputation.
9. Write `Command Ledger` and `Audit Event` rows, then respond `Succeeded`. Keep the
   package labeled `UNAPPROVED RECOMMENDATION`.

## Tool configuration

> Revalidates the current PackageReady artifact and creates a short-lived single-use
> decision challenge bound to caller, case version, package version, and package hash.
> It does not approve the package; challenge preparation grants no approval.

## Acceptance tests

1. Any package/binding/hash mismatch returns `Conflict` without a challenge.
2. A challenge is bound to exact caller, case version, package version/hash and expiry.
3. Preparing again invalidates the previous unconsumed challenge.
4. The response includes review data and opaque artifacts, never file bytes.
5. Preparing cannot create an Approval or imply approval.
6. Assignment, authority, and idempotency controls work.
7. The workflow completes in under 100 seconds and responds synchronously.
