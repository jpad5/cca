---
name: valuation-review
description: "Run and explain the controlled CAT contents research, rule resolution, deterministic valuation, quality review, and exception cycle. Use when an adjuster asks to research replacements, calculate a valuation, review results, or resolve valuation issues."
---

# Valuation Review

Use this skill to coordinate the valuation workflow sequence after inventory is complete.

## Procedure

1. Invoke `OpenValuationCase` and use its persisted state and versions.
2. Invoke the next required workflow in this order: `RunApprovedResearch`, `ResolveValuationRules`, `RunDeterministicValuation`, `RunValuationQualityGates`.
3. Continue bounded research batches only when `continuationRequired` is true, preserving the returned cursor and case version.
4. Ask the adjuster for input only when the workflow returns `NeedsInput` or a recorded issue requiring human resolution.
5. Use `ResolveValuationException` for an explicit licensed-adjuster resolution, then resume from the state it returns.
6. Present evidence, rule versions, financial values, and quality results exactly as returned.
7. Keep the `UNAPPROVED RECOMMENDATION` label visible until `SubmitPackageDecision` succeeds with `Approve`.

## Constraints

- Never use unrestricted web search or unapproved sources.
- Never perform or modify RCV, depreciation, tax, ACV, limits, payable recommendations, or rounding in language-model reasoning.
- Never infer rules, evidence, prices, issue resolutions, or override authority.
- Never advance from a held, rejected, stale, or conflicting result.
- On `Conflict`, invoke `OpenValuationCase` before selecting another workflow.