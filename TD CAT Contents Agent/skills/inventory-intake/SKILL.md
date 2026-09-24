---
name: inventory-intake
description: "Guide licensed adjusters through CAT contents inventory upload, validation, parsing, and item correction. Use when an adjuster wants to upload, replace, validate, review, or correct an inventory file."
---

# Inventory Intake

Use this skill only for inventory intake and correction work on an authorized valuation case.

## Procedure

1. Invoke `OpenValuationCase` before handling inventory.
2. If the case has not reached `CaseReady`, use the required eligibility, authorization, and claim-fact workflows first.
3. Ask for an inventory attachment only when the case is `CaseReady`.
4. Confirm replacement intent when an inventory source already exists. Never infer `replaceExisting: true`.
5. Send the attachment only to `UploadInventorySource`. Never quote, summarize, transform, or place raw file bytes in model context.
6. If the workflow reports item-photo, data-tag-photo, or receipt-photo content, present it as excluded from MVP and continue only with supported text and numeric fields.
7. Present the workflow's sanitized validation result and recorded issues.
8. Invoke `ValidateAndParseInventory` in bounded batches until `continuationRequired` is false or the case enters a hold.
9. For each issue requiring human input, ask only for the fields and choices returned by the workflow.
10. Submit one explicit correction or disposition at a time with `SubmitInventoryResolution`.
11. Stop when the workflow reports `InventoryComplete`, a hold, a conflict, or an authorization failure.

## Constraints

- Treat workflow state, versions, issue codes, and parsed values as authoritative.
- Never bypass file classification, type, size, hash, template, or assignment checks.
- Never extract, describe, classify, store, or reason over item photos, data-tag photos, or receipt photos in MVP. Ignore template branding images.
- Never invent inventory values or silently fix source data.
- On `Conflict`, invoke `OpenValuationCase` and resume from the returned state.
- On a hold, explain the recorded issue without suggesting that processing succeeded.