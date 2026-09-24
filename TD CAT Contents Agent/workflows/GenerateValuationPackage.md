# GenerateValuationPackage workflow

Build this workflow in the Copilot Studio visual designer. Do not create a local
`workflow.json` file.

## Security prerequisite

Use run-only-user Dataverse, Office 365 Users, and Excel Online connections permitted
by DLP. Store the approved macro-free template in a governed location; callers cannot
supply or select a template. Enforce Assigned Adjuster assignment before reads/writes.
This is the mandatory Assignment check.

## Trigger

Use **When an agent calls the flow** with required `caseId` (Text),
`expectedVersion` (Number), `idempotencyKey` (Text), `inventoryVersion` (Text),
`evidenceVersion` (Text), `ruleSetVersion` (Text), and `calculationRunId` (Text).

## Response

Use **Respond to the agent** with **Asynchronous response** set to **Off** for a
synchronous response with all common outputs. Return opaque package/workbook/trace
references and immutable version/hash metadata; return no bytes.

## Designer actions

1. Derive correlation/caller values and validate exact version inputs.
2. Apply standard `Command Ledger` replay/reuse checks.
3. Get the case and enforce assignment, state `QualityPassed`, expected Case Version,
   and exact input bindings for inventory, evidence, rule set, and calculation run.
   Return `Conflict` if stale.
4. Load only the approved macro-free template and verify its governed hash/version.
5. Populate fixed named ranges/tables with persisted typed data using Excel Online.
   Do not use AI to create formulas, values, or narrative conclusions.
6. Produce a calculation trace containing input/output versions, hashes, engine/rule
   versions, ordered operations, totals, and quality results.
7. Calculate hashes for the completed workbook and trace. Create one immutable
   `Package Artifact` with a generated package version ID, exact bindings, package
   hash, generator version, files, timestamp, and Is Current `true`.
8. Mark prior package artifacts noncurrent, set case state `PackageReady`, increment
   Case Version, and checkpoint the immutable package binding.
9. Write `Command Ledger` and `Audit Event` rows with template/package hashes and
   bindings, excluding file bytes.
10. Respond `Succeeded` with opaque artifacts and `UNAPPROVED RECOMMENDATION` in the
    display summary.

If generation cannot complete under the timeout, persist an opaque bounded cursor and
retain `QualityPassed`; never expose or mark a partial package current.

## Tool configuration

> Generates the governed valuation workbook and calculation trace for exact current
> input versions after QualityPassed. Stores an immutable package and returns opaque
> references and hash; the package remains an unapproved recommendation.

## Acceptance tests

1. Any stale/mismatched binding returns `Conflict` without a package.
2. Only the approved macro-free template is used and verified.
3. Workbook and trace hashes/versions bind exactly to the calculation inputs.
4. No partial/current duplicate package exists after failure or retry.
5. File bytes are never returned; the summary retains UNAPPROVED RECOMMENDATION.
6. Assignment and idempotency controls work.
7. Every invocation completes in under 100 seconds and responds synchronously.
