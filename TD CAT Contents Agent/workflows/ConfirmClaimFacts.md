# ConfirmClaimFacts workflow

Build this workflow in the Copilot Studio visual designer. Do not create a local
`workflow.json` file.

## Security prerequisite

Use run-only-user Dataverse and Office 365 Users connections. Derive caller identity
inside the workflow and enforce assignment before reading or changing claim facts.

## Trigger

Use **When an agent calls the flow** with these inputs:

| Name | Type | Required |
| --- | --- | --- |
| `caseId` | Text | Yes |
| `expectedVersion` | Number | Yes |
| `idempotencyKey` | Text | Yes |
| `province` | Text | Yes |
| `lossDate` | Text | Yes; ISO 8601 date/time |
| `coverageCodes` | Text | Yes; compact JSON array |
| `endorsementCodes` | Text | Yes; compact JSON array, `[]` allowed |
| `contentsLimit` | Number | Yes; zero or greater |
| `currency` | Text | Yes; must be `CAD` |

## Response

Use synchronous **Respond to the agent** and return every common output from
[README.md](README.md), using compact JSON text for collections and objects.

## Designer actions

1. Initialize a correlation ID, derive normalized caller email, and trim/uppercase
   province and currency.
2. Build `MissingFields` for empty province, loss date, coverage codes, contents
   limit, or currency. Return `NeedsInput` without writing a ledger, audit, or case
   row when the array is non-empty.
3. Validate province against `AB, BC, MB, NB, NL, NS, NT, NU, ON, PE, QC, SK, YT`;
   validate the loss date with a guarded conversion; validate both code fields as
   JSON arrays; require a nonnegative contents limit and currency `CAD`. Return
   `NeedsInput` with field-specific issues when invalid.
4. Query `Command Ledger` by idempotency key. Replay only an exact matching command,
   caller, and sanitized request; reject changed reuse.
5. Get the case and verify the assigned adjuster. Require state `AccessAuthorized`
   and exact expected Case Version; otherwise return `Rejected` or `Conflict`
   without mutation as applicable.
6. Update Province, Loss Date, Coverage Codes, Endorsement Codes, Contents Limit,
   Currency, Case State `CaseReady`, Case Version `+ 1`, and Checkpoint
   `ConfirmClaimFacts` in a guarded scope.
7. Write the related `Command Ledger` row and append an `Audit Event`. Do not include
   insured identity or raw claim narrative in either record.
8. Respond `Succeeded` with the persisted facts in `authoritativeValues` and summary
   `Claim facts confirmed; the case is ready for inventory intake.`

On a concurrent write return `Conflict`. On an idempotency-key collision, reread the
winning result and do not repeat the case update.

## Tool configuration

> Validates and records the required Canadian claim facts for an AccessAuthorized
> case. Returns exact missing or invalid fields without mutation and advances a valid
> case to CaseReady.

Do not infer claim facts, dates, limits, currency, caller identity, or versions.

## Acceptance tests

1. Every missing required fact is returned in `missingFields` with no writes.
2. Invalid province/date/JSON, negative limit, or non-CAD currency is rejected as
   `NeedsInput` without mutation.
3. Valid Canadian facts persist exactly and advance to CaseReady once.
4. Wrong assignment is rejected; stale state/version returns `Conflict`.
5. Exact retries replay and changed key reuse is rejected.
6. The workflow completes in under 100 seconds and responds synchronously.
