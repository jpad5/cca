---
name: package-review-decision
description: "Guide an authorized adjuster through valuation package generation, evidence review, explicit approve-reject-hold decision, and external filing status. Use when an adjuster asks to generate, review, approve, reject, hold, file, or close a valuation package."
---

# Package Review And Decision

Use this skill for package generation, human review, explicit decision capture, and external-process recording.

## Procedure

1. Invoke `OpenValuationCase` and verify the persisted state.
2. Invoke `GenerateValuationPackage` only from `QualityPassed` using the exact workflow-returned version IDs.
3. Invoke `PreparePackageDecision` only for the current package version and hash.
4. Present the returned evidence, calculations, rule versions, exceptions, workbook, trace, package version, and package hash without alteration.
5. Ask the adjuster to choose exactly one fixed option: `Approve`, `Reject`, or `Hold`.
6. Require the explicit attestation and any reason code or rationale required by the workflow.
7. Invoke `SubmitPackageDecision` once using the unmodified challenge ID and immutable package binding returned by `PreparePackageDecision`.
8. Present the recorded outcome. Do not claim approval unless the workflow returns `Approved`.
9. After approval, use `RecordExternalFiling` and `RecordExternalClaimStatus` only to record evidence supplied by the adjuster about work completed outside the agent.

## Constraints

- Never treat conversational phrases such as "looks good" or "approved" as a decision.
- Never expose, edit, reuse, or transfer the decision challenge.
- Never approve a regenerated or version-mismatched package.
- Never file to, update, close, deny, or pay a claim in an external claims system.
- On an expired, replayed, stale, or mismatched challenge, invoke `OpenValuationCase` and prepare a new decision only if the persisted state permits it.