# ConfirmMvpEligibility workflow

Build this workflow in the Copilot Studio visual designer. Do not create a local
`workflow.json` file.

## Security prerequisite

Configure Microsoft Dataverse and Office 365 Users as **Provided by run-only user**.
Derive the caller with **Get my profile (V2)**. Never accept caller identity, role,
assignment, case state, or current version from the agent as authoritative.

The licensed-adjuster role requires read/write access to assigned `Valuation Case`
rows and create access to related `Command Ledger` and `Audit Event` rows.

## Trigger

Use **When an agent calls the flow** with these required inputs:

| Name | Type | Description |
| --- | --- | --- |
| `caseId` | Text | Dataverse Valuation Case row ID. |
| `expectedVersion` | Number | Version returned by the previous workflow. |
| `idempotencyKey` | Text | Stable retry key generated once for this command. |
| `isEligible` | Boolean | Adjuster's explicit MVP eligibility decision. |
| `recommendationOnlyAttestation` | Boolean | Adjuster confirms the output is recommendation-only. |
| `eligibilityReason` | Text | Reason supporting the decision. |

Reject empty `caseId`, `idempotencyKey`, or `eligibilityReason` with `NeedsInput`
before mutation.

## Response

Use **Respond to the agent** with **Asynchronous response** set to **Off**. Return
the common outputs defined in [README.md](README.md): `outcome`, `caseId`,
`caseVersion`, `state`, `operationId`, `continuationRequired`, `missingFields`,
`issues`, `artifacts`, `authoritativeValues`, and `displaySummary`. Use compact JSON
text for collection/object outputs and never return raw Dataverse payloads.

## Designer actions

Rename actions as shown so expressions remain stable.

1. Initialize `CorrelationId` with `guid()` and normalize all text inputs with
   `trim()`. Get the caller with `GetCallerProfile`; set `CallerEmail` to lower-case
   Mail with User Principal Name as fallback.
2. Validate required inputs. Return `NeedsInput` with exact field names and no
   mutation when any are missing.
3. List `Command Ledger` rows by `idempotencyKey`, with row count `2`. If one exists:
   - Verify its command is `ConfirmMvpEligibility`, actor is `CallerEmail`, and its
     stored request values match this request.
   - Return its stored result unchanged when they match.
   - Return `Rejected` with `IDEMPOTENCY_KEY_REUSED` when they do not match.
4. Get the `Valuation Case` by `caseId`, selecting Case State, Case Version, Assigned
   Adjuster, and Checkpoint. Return `Rejected` without case details when inaccessible.
5. Verify Assigned Adjuster equals `CallerEmail`. Otherwise return `Rejected` with
   `CASE_ASSIGNMENT_DENIED`.
6. Verify persisted Case State is `Candidate` and Case Version equals
   `expectedVersion`. Otherwise return `Conflict` with the persisted state and
   version and make no writes.
7. Set `NextState` to `EligibilityConfirmed` only when both booleans are true;
   otherwise set it to `StoppedOutsideMvp`.
8. Update the case in a guarded scope: set Case State to `NextState`, Case Version to
   `add(expectedVersion, 1)`, and Checkpoint to `ConfirmMvpEligibility`.
9. Create a `Command Ledger` row related to the case with the idempotency key,
   command, sanitized request values, outcome `Succeeded`, actor, correlation ID,
   compact result JSON, and `utcNow()`.
10. Create an `Audit Event` related to the case with operation
    `ConfirmMvpEligibility`, before/after states and versions, actor, correlation ID,
    event time, and details containing only the two decisions and reason.
11. Respond `Succeeded`. Use `Eligibility confirmed.` when advancing, or
    `Case stopped because it is outside the MVP eligibility boundary.` when stopped.

Configure failure scopes so a stale/concurrent case update returns `Conflict`; a
ledger alternate-key collision rereads and returns the winning stored result. Never
repeat the case mutation after a collision.

## Tool configuration

> Confirms whether a Candidate valuation case is eligible for the MVP and captures
> the recommendation-only attestation. Requires the current case version and an
> explicit reason. Advances to EligibilityConfirmed only when both confirmations are
> true; otherwise stops the case at StoppedOutsideMvp.

Do not allow generative filling of either boolean, the reason, identity, assignment,
state, version, or idempotency key.

## Acceptance tests

1. Missing reason returns `NeedsInput` and creates no rows.
2. Both booleans true advances Candidate to EligibilityConfirmed and increments once.
3. Either boolean false sets StoppedOutsideMvp and records the reason.
4. Wrong assignment returns `Rejected` without case data.
5. Stale state or version returns `Conflict` without mutation.
6. Retrying the same key returns the stored result and does not increment again.
7. Reusing a key with different values returns `Rejected`.
8. The workflow completes in under 100 seconds and responds synchronously.
