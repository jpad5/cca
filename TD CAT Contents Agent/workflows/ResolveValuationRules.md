# ResolveValuationRules workflow

Build this workflow in the Copilot Studio visual designer. Do not create a local
`workflow.json` file.

## Security prerequisite

Use run-only-user Dataverse and Office 365 Users connections. Only designated rule
administrators may create/approve immutable Rule Set Version rows; this workflow has
read-only access to rule content.

## Trigger

Use **When an agent calls the flow** with required `caseId` (Text),
`expectedVersion` (Number), and `idempotencyKey` (Text).

## Response

Use **Respond to the agent** with **Asynchronous response** set to **Off** for a
synchronous response containing all common outputs. Return only the selected rule-set
version ID/hash and matching facts, never the full rule payload.

## Designer actions

1. Derive correlation/caller values and validate required inputs.
2. Apply the standard `Command Ledger` replay/reuse check.
3. Get the case and enforce assignment, state `ResearchComplete`, and expected Case
   Version. Read persisted province, loss date, coverage codes, and endorsements.
   Return `Conflict` without mutation when state or version is stale.
4. Query `Rule Set Version` for Approval Status `Approved`, matching province,
   effective dates where Effective Start is on/before the loss date and Effective End
   is empty or on/after it, and applicable coverage/endorsement codes. Use governed
   structured matching with no inference or substring matching by an AI action.
5. Require exactly one approved match. Verify its content hash and immutable status.
6. For exactly one match, store its version ID/hash in the case checkpoint, set state
   `RulesResolved`, and increment Case Version.
7. For zero or multiple matches, create a typed `Case Issue`, set state
   `HeldRulesUnavailable`, and increment once. Never select a nearest or newer rule.
8. Write the ledger result and append an audit event with matching facts, count, and
   selected version/hash when applicable.
9. Return `Succeeded` for one match or `Held` otherwise, with a sanitized summary.

## Tool configuration

> Resolves the one immutable approved rule set applicable to a ResearchComplete case
> by province, loss date, coverage, and endorsements. Holds the case when no single
> approved match exists and never infers or substitutes rules.

## Acceptance tests

1. One exact approved match advances to RulesResolved with its ID and hash.
2. Zero or multiple matches enter HeldRulesUnavailable with a typed issue.
3. Draft, retired, rejected, out-of-date, or hash-invalid rules are never selected.
4. Assignment/state/version failures produce no rule binding.
5. Exact retries replay and changed key reuse is rejected.
6. The workflow completes in under 100 seconds and responds synchronously.
