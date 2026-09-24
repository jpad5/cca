# RecordExternalClaimStatus workflow

Build this workflow in the Copilot Studio visual designer. Do not create a local
`workflow.json` file.

## Security prerequisite

Use run-only-user Dataverse and Office 365 Users connections. Record only status and
evidence supplied by the Assigned Adjuster. This is the mandatory Assignment check.
There is no claims-system write; do not query or update a claims system.

## Trigger

Use **When an agent calls the flow** with required `caseId` (Text),
`expectedVersion` (Number), `idempotencyKey` (Text), `externalStatus` (Text fixed
choice), `confirmedAt` (Text ISO 8601), and `evidenceReference` (Text). Configure
explicit mappings for open/held and closed/completed labels; reject unknown labels.

## Response

Use **Respond to the agent** with **Asynchronous response** set to **Off** for a
synchronous response with all common outputs and sanitized external status evidence.

## Designer actions

1. Derive correlation/caller values and validate fixed status, time, and evidence.
2. Apply standard `Command Ledger` replay/reuse checks.
3. Get the case and enforce assignment, expected Case Version, and state
   `ExternallyFiled` or `OpenExternal`. Return `Conflict` if stale.
4. Verify the current Approval, package, and filing checkpoint remain bound and valid.
5. Apply the open-held mapping: map open or held external status to `OpenExternal`.
   Apply the closed-completed mapping: map closed or completed to
   `Closed` only when evidence reference is present and validated. Never infer closure.
6. For Closed, calculate retention metadata from governed policy while respecting
   Legal Hold; do not shorten an existing retention date.
7. Persist the status evidence/checkpoint, increment Case Version, and append closure
   metadata when applicable.
8. Write `Command Ledger` and `Audit Event` rows. The closure audit includes external
   status, confirmation time, evidence reference, retention date, and legal-hold flag.
9. Respond `Succeeded` with the recorded state. Do not claim the agent closed, denied,
   paid, or otherwise changed the external claim.

## Tool configuration

> Records adjuster-confirmed external claim status after filing. Keeps open/held
> claims at OpenExternal and closes only on explicit closed/completed status with
> evidence, while recording retention and legal-hold metadata.

## Acceptance tests

1. Unknown/missing status or evidence returns `NeedsInput` without mutation.
2. Open/held maps to OpenExternal; closed/completed with evidence maps to Closed.
3. Closure without evidence is refused and never inferred.
4. Retention metadata honors governed policy and Legal Hold.
5. Stale state/version returns `Conflict`; wrong assignment is rejected.
6. Exact retries replay without duplicate closure audit events.
7. The workflow completes in under 100 seconds and responds synchronously.
