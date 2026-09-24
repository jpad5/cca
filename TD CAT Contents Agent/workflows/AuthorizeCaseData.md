# AuthorizeCaseData workflow

Build this workflow in the Copilot Studio visual designer. Do not create a local
`workflow.json` file.

## Security prerequisite

Configure Microsoft Dataverse and Office 365 Users as **Provided by run-only user**.
Derive the caller with **Get my profile (V2)**. The workflow, not the agent, verifies
the caller, case assignment, persisted state, and version.

## Trigger

Use **When an agent calls the flow** with required `caseId` (Text),
`expectedVersion` (Number), `idempotencyKey` (Text), and `classification` (Text).
The only accepted classification labels are `Approved`, `Restricted`, `Prohibited`,
and `Unknown`; match labels case-insensitively after trimming.

## Response

Use synchronous **Respond to the agent** and return every common output from
[README.md](README.md). Return collections and objects as compact JSON text. Never
return raw Dataverse rows.

## Designer actions

1. Initialize `CorrelationId` with `guid()`. Resolve `CallerEmail` from Mail with User
   Principal Name fallback and normalize the classification.
2. Return `NeedsInput` for an empty case ID, idempotency key, or classification.
3. Query `Command Ledger` by idempotency key. Return the stored result only when the
   command, caller, and sanitized request match; otherwise reject with
   `IDEMPOTENCY_KEY_REUSED`.
4. Get the case by ID and verify assignment. An inaccessible or unassigned case
   returns `Rejected` without exposing case data.
5. Require persisted state `EligibilityConfirmed` and the exact expected Case
   Version. Return `Conflict` with authoritative state/version when stale.
6. Set `NextState` to `AccessAuthorized` only for `Approved` or `Restricted`.
   Set it to `StoppedDataProhibited` for `Prohibited`, `Unknown`, or any unrecognized
   value. Fail closed; do not silently map an unknown label.
7. Update Data Classification, Case State, Case Version `+ 1`, and Checkpoint
   `AuthorizeCaseData` in a guarded scope.
8. Write a related `Command Ledger` result and append an `Audit Event` containing
   only the normalized classification and state transition.
9. Respond `Succeeded` with persisted classification, state, and version in
   `authoritativeValues`. Summarize whether access was authorized or stopped.

On a concurrent update return `Conflict`. On a ledger alternate-key collision,
reread and return the winning result; never repeat the mutation.

## Tool configuration

> Records the explicit data classification for an EligibilityConfirmed case. It
> authorizes only Approved or Restricted data and fails closed to
> StoppedDataProhibited for Prohibited, Unknown, or invalid values.

Do not let the model infer classification or populate caller/security values.

## Acceptance tests

1. Missing classification returns `NeedsInput` without writes.
2. Approved and Restricted advance to AccessAuthorized.
3. Prohibited, Unknown, and invalid labels set StoppedDataProhibited.
4. Wrong assignment is rejected without case details.
5. Wrong state/version returns `Conflict` without mutation.
6. A matching retry returns the stored result; a changed retry is rejected.
7. The workflow completes in under 100 seconds and responds synchronously.
