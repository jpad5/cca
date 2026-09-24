# RunDeterministicValuation workflow

Build this workflow in the Copilot Studio visual designer. Do not create a local
`workflow.json` file.

## Security prerequisite

Use run-only-user Dataverse and Office 365 Users connections. No AI or generative
action may perform arithmetic, choose a rule, alter evidence, or round a value.

## Trigger

Use **When an agent calls the flow** with required `caseId` (Text),
`expectedVersion` (Number), `idempotencyKey` (Text), `inventoryVersion` (Text),
`evidenceVersion` (Text), and `ruleSetVersion` (Text). Exactly three version inputs
bind the calculation: inventory, evidence, and rule set.

## Response

Use **Respond to the agent** with **Asynchronous response** set to **Off** for a
synchronous response containing all common outputs. Return the calculation run ID,
input versions/hash, currency, and persisted totals as authoritative values.

## Designer actions

1. Derive correlation/caller values and validate every version ID.
2. Apply the standard `Command Ledger` replay/reuse check.
3. Get the case and verify assignment, state `RulesResolved`, and expected Case
   Version. Verify all three input versions equal the case's persisted bindings.
4. Recompute/verify an input hash over ordered immutable item, evidence, rule, limit,
   and currency values. Reject incomplete, stale, negative, or mixed-currency inputs.
5. Initialize Decimal variables only. Use no AI arithmetic. For each bounded item,
   use workflow expressions
   to calculate replacement value, depreciation, tax, ACV, limit effects, payable
   recommendation, and configured rounding in the rule-defined order.
6. Create immutable `Item Valuation` rows bound to item and calculation run, including
   input hash and calculated time. Do not update prior valuation rows.
7. Sum persisted item outputs, apply case-level limits/rounding, and create one
   immutable `Calculation Run` with exact inventory/evidence/rule versions, engine
   version, totals, input hash, and timestamp.
8. Re-read the run, set case state `Calculated`, increment Case Version, and set the
   checkpoint to the calculation run/version bindings.
9. Write the `Command Ledger` and `Audit Event` records using persisted totals and
   version IDs.
10. Respond `Succeeded` with summary `Deterministic valuation calculated; results are
    an unapproved recommendation pending quality review and adjuster decision.`

If a bounded implementation cannot finish safely within one invocation, persist an
opaque cursor and retain `RulesResolved`; never publish partial case totals.

## Tool configuration

> Calculates the valuation deterministically from exact immutable inventory,
> evidence, and rule versions. Uses decimal workflow expressions only, stores item and
> case outputs, and labels results as an unapproved recommendation.

## Acceptance tests

1. Any mismatched/missing input version or hash returns `Conflict` without outputs.
2. Same inputs and engine version produce identical item/case totals and hashes.
3. RCV, depreciation, tax, ACV, limits, payable, and rounding follow rule order.
4. No AI action participates in arithmetic or rule selection.
5. One calculation run and immutable item valuations are created per successful key.
6. Assignment, state/version, and idempotency controls work.
7. Every invocation completes in under 100 seconds and responds synchronously.
