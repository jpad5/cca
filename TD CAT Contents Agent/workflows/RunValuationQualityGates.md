# RunValuationQualityGates workflow

Build this workflow in the Copilot Studio visual designer. Do not create a local
`workflow.json` file.

## Security prerequisite

Use run-only-user Dataverse and Office 365 Users connections. Quality checks must use
persisted typed values and deterministic expressions, not AI judgment or arithmetic.

## Trigger

Use **When an agent calls the flow** with required `caseId` (Text),
`expectedVersion` (Number), `idempotencyKey` (Text), and `calculationRunId` (Text).

## Response

Use **Respond to the agent** with **Asynchronous response** set to **Off** for a
synchronous response with every common output. Return gate codes/counts and the exact
calculation binding, not raw item-level financial records.

## Designer actions

1. Derive correlation/caller values and validate inputs.
2. Apply the standard `Command Ledger` exact-replay and changed-key rejection check.
3. Get the case and enforce assignment, state `Calculated`, and expected Case Version.
   Return `Conflict` without writes for a stale state or version.
4. Get the Calculation Run and verify it belongs to the case and matches the current
   inventory, evidence, rule, input hash, and engine bindings.
5. Reconcile item valuation totals to case RCV, depreciation, tax, ACV, payable, and
   rounding within configured decimal tolerances.
6. Evaluate typed gates for nonnegative values, contents limit, currency, evidence
   qualification, specialty/high-value flags, rule coverage, rounding, duplicate or
   missing item outputs, and version consistency.
7. Create one typed `Case Issue` per failed gate, with no duplicate open issue keys.
8. When all gates pass, set Calculation Run Reconciliation Passed `true`, case state
   `QualityPassed`, Case Version `+ 1`, and checkpoint to the calculation run.
9. When any material gate fails, set Reconciliation Passed `false`, case state
   `HeldQualityException`, increment once, and return outcome `Held`.
10. Write `Command Ledger` and `Audit Event` rows containing gate IDs, counts, input
    bindings, and transition, without duplicating sensitive item details.

## Tool configuration

> Runs deterministic quality gates against the current Calculation Run, including
> reconciliation, limits, evidence, specialty flags, nonnegative values, rounding,
> and version consistency. Advances to QualityPassed or holds with typed issues.

## Acceptance tests

1. A stale or mismatched calculation binding returns `Conflict` without mutation.
2. Exact reconciled valid totals advance to QualityPassed.
3. Each failed material gate creates one typed issue and enters HeldQualityException.
4. No AI action judges or calculates a gate.
5. Exact retries do not duplicate issues or increment the case again.
6. Assignment and changed-key reuse fail closed.
7. The workflow completes in under 100 seconds and responds synchronously.
