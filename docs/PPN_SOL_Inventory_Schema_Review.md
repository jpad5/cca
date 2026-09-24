# PPN SOL Inventory Schema Review

## Scope

This review compares the two adjuster inventory examples supplied for schema refinement:

- `PPN SOL List - no photos.xlsx`
- `PPN SOL List - with photos.xlsx`

The MVP accepts inventory text and numeric data. Item photos, data-tag photos, and receipt photos are explicitly out of scope.

## Workbook observations

### No-photo workbook

The workbook contains claim header fields for insured name, date of loss, claim number, and policy number. Its item grid contains:

| Source field | MVP treatment |
| --- | --- |
| Ref | Normalize to Source Item Reference. |
| Room | Normalize to Room. |
| Description | Normalize to Item Description. |
| Brand | Normalize to Brand. |
| Model | Normalize to Model. |
| Supplier | Normalize to Supplier or Retailer. |
| Qty | Normalize to Quantity. |
| Age Years / Months | Normalize to separate bounded whole-number fields. |
| Original Cost | Normalize to Declared Cost with an explicit cost basis when known. |
| Notes | Normalize to Item Notes. |

The converter found two embedded images even though this is the no-photo variant. These appear to be template assets rather than item evidence. The workflow must identify photo content from mapped item-photo fields, not from the mere presence of any embedded image.

### Photo workbook

The detailed workbook adds header fields for report date, claim ID, claim date, insured name, loss type, and CAT code. Its item grid adds:

| Source field | MVP treatment |
| --- | --- |
| Box | Normalize to Box or Container. |
| Location | Normalize to Item Location. |
| Disposition | Preserve as Source Item Disposition; do not overwrite workflow disposition. |
| Condition | Normalize to Condition. |
| Model Number | Normalize to Model. |
| Serial Number | Normalize to Serial Number. |
| Retailer | Normalize to Supplier or Retailer. |
| Purchase Price | Normalize to Declared Cost and cost basis. |
| Replacement Source | Preserve in Original Record JSON; approved research remains authoritative. |
| Replacement Value | Preserve source value in Original Record JSON; deterministic workflow writes Item Valuation. |
| Depreciation | Preserve source value in Original Record JSON; deterministic workflow writes Item Valuation. |
| Actual Cash Value | Preserve source value in Original Record JSON; deterministic workflow writes Item Valuation. |
| Notes | Normalize to Item Notes. |
| Item Photo / Data Tag Photo / Receipt Photo | Exclude from MVP extraction, storage, and valuation. |

The workbook contains 199 embedded images. Their presence confirms the need for a clear exclusion control but does not justify photo entities or photo columns in the MVP schema.

## Schema decisions

### Valuation Case

Added Policy ID, Insured Name, Loss Type, and CAT Code. Existing Claim ID and Loss Date fields already cover the remaining case-level values.

### Inventory Source

Added Source Profile, Report Date, and Photo Content Status. Photo Content Status uses `NotPresent`, `PresentExcluded`, or `Unknown`; it records scope handling without retaining item-photo content.

### Inventory Item

Added source reference, room, container, location, serial number, supplier or retailer, source disposition, condition, age, declared cost and basis, and notes. Original Record JSON remains necessary because source templates vary and may contain untrusted or unmapped values.

Workflow Disposition remains separate from Source Item Disposition. This prevents labels such as `Unaffected`, `Return`, or `Non-Restorable` from being mistaken for the agent's processing state.

### Item Valuation

Added a versioned Item Valuation table for replacement value, depreciation, ACV, tax, and payable recommendation at item level. Only the deterministic valuation workflow writes these values. Source-entered financial values do not become authoritative by being present in an uploaded workbook.

## MVP parsing rules

1. Accept supported workbook text and numeric fields through the upload workflow only.
2. Retain the original source file and original row JSON for auditability.
3. Ignore template branding images.
4. Mark workbooks with mapped item-photo content as `PresentExcluded`.
5. Do not extract, describe, classify, store, or use item photos, data-tag photos, or receipt photos.
6. Do not trust source-entered replacement value, depreciation, or ACV as calculated output.
7. Create explicit issues for missing or ambiguous fields instead of silently inferring values.

## MVP 2 requirements for photo ingestion

MVP 2 is not implemented by this schema revision. Before photo-enabled inventory processing is introduced:

1. Add an immutable Item Evidence entity with case, source, and item relationships plus evidence versioning and supersession.
2. Store extracted binaries in controlled file storage and expose only opaque references to the agent.
3. Capture evidence type, workbook location, hash, MIME type, size, scan and classification results, extraction status, retention, and legal-hold metadata.
4. Define deterministic image-to-row mapping and route ambiguous associations to adjuster review.
5. Introduce extraction limits, duplicate detection, idempotent retries, partial-failure handling, and human work queues.
6. Reassess workbook and evidence storage limits with the 199-image sample and other representative files.
7. Apply malware, privacy, authorization, auditing, restricted-delete, and retention controls to images independently of the workbook.
8. Approve and validate any image-analysis model before it can derive item attributes. Preserve model version, confidence, and provenance, and require human confirmation for material results.
9. Bind the exact evidence versions and hashes into calculation traces and adjuster review packages.
10. Complete security, privacy, accessibility, performance, cost, and accuracy testing before release.

Until these requirements are met, Photo Content Status remains `PresentExcluded`, and photos must not influence normalization, research, valuation, or approval.
