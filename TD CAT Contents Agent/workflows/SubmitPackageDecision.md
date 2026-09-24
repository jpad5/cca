# SubmitPackageDecision workflow

Build this workflow in the Copilot Studio visual designer. Do not create a local
`workflow.json` file.

## Security prerequisite

Use run-only-user Dataverse and Office 365 Users connections. Verify licensed-adjuster
Assigned Adjuster assignment and decision authority. Never derive a decision or attestation from free
text; both must arrive through fixed workflow inputs.
This is the mandatory Assignment check.

## Trigger

Use **When an agent calls the flow** with required `caseId` (Text),
`expectedVersion` (Number), `idempotencyKey` (Text), `challengeId` (Text),
`packageId` (Text), `packageVersion` (Text), `packageHash` (Text), `decision` (fixed decision
choice: `Approve`, `Reject`, or `Hold`), `attestation` (Boolean), `reasonCode`
(Text), and `rationale` (Text).

## Response

Use **Respond to the agent** with **Asynchronous response** set to **Off** for a
synchronous response with all common outputs and immutable approval ID/package
binding when recorded.

## Designer actions

1. Derive correlation/caller values. Reject missing/free-form decision values and
   require attestation `true`. Require reason code and rationale for Reject/Hold.
2. Apply standard `Command Ledger` replay/reuse checks.
3. Get the case and enforce assignment/authority, state `PendingApproval`, and exact
   expected Case Version. Return `Conflict` if stale.
4. Get the challenge and package. Verify case, caller, expiry, unexpired time, Is Consumed
   `false`, challenge ID, case version, package artifact/version/hash, and current
   package bindings. Reject replay or mismatch without disclosing protected details.
5. Atomically mark the challenge consumed before recording the decision; configure
   concurrency so only one invocation can succeed.
6. Create one immutable `Approval` bound to the case, package, and challenge with
   decision, attestation, reason, rationale, caller, and `utcNow()`.
7. For Approve, set state `Approved`. For Hold, set `HeldAdjuster`. For Reject, set
   the configured correction state from a fixed reason-code mapping and invalidate
   dependent package/challenges as required. Increment Case Version once.
8. Write `Command Ledger` and `Audit Event` rows with exact immutable binding and
   decision. Do not log challenge secrets beyond its opaque ID.
9. Respond with persisted decision/state. Claim approval only when state is Approved.

## Tool configuration

> Records one explicit Approve, Reject, or Hold decision for the exact package bound
> to a valid single-use challenge. Requires explicit attestation and rejects expired,
> replayed, transferred, mismatched, or stale challenges.

## Acceptance tests

1. Missing/invalid decision or false attestation creates no approval.
2. Expired, consumed, wrong-caller, stale, or mismatched challenge is rejected.
3. Concurrent submissions create at most one Approval and consume once.
4. Approve sets Approved; Hold sets HeldAdjuster; Reject uses fixed correction mapping.
5. A decision cannot transfer to a regenerated package.
6. Exact retries replay; changed key reuse is rejected.
7. The workflow completes in under 100 seconds and responds synchronously.
