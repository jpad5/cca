# TD CAT Contents Agent Dataverse Schema: Business Guide

## Purpose

The TD CAT Contents Agent uses Dataverse as the trusted record of each contents valuation case. Dataverse stores the case's progress, source inventory, item-level details, supporting price evidence, valuation results, review decisions, and audit history.

The schema is designed to help a licensed adjuster understand what happened, review the evidence behind a recommendation, and make the final decision. The agent supports that work but does not settle, pay, deny, or close a claim autonomously.

## How the data fits together

The **Valuation Case** is the central record. Almost every other record belongs to a valuation case and documents one part of its journey:

1. The case is opened and the claim facts, authority, and data classification are confirmed.
2. An inventory file is stored as an **Inventory Source** and converted into individual **Inventory Items**.
3. Approved replacement-price research is retained as **Comparator Evidence** for each item.
4. An approved **Rule Set Version** is selected for the claim's province, coverage, endorsements, and loss date.
5. A **Calculation Run** applies those inputs and produces reproducible valuation totals.
6. **Item Valuations** retain the deterministic replacement value, depreciation, and ACV for each item.
7. Any missing information, exception, or quality concern is tracked as a **Case Issue**.
8. A reviewable workbook and calculation trace are stored as a **Package Artifact**.
9. A short-lived **Decision Challenge** confirms exactly who is deciding on which package.
10. The adjuster's decision is retained as an immutable **Approval** record.
11. The **Command Ledger** prevents duplicate processing, while **Audit Events** preserve the history of material actions and state changes.

## Table roles

### 1. Valuation Case

**Business purpose:** The master record for one contents valuation case. It provides the current, authoritative view of where the case is in the process.

**What it contains:** Claim and policy identifiers, insured name, current case state, province, loss date and type, CAT code, data classification, coverage and endorsement codes, contents limit, currency, assigned adjuster, retention date, legal-hold status, and a workflow checkpoint.

**When it is used:** Created when valuation work begins and updated as the case moves through eligibility, inventory review, research, calculation, quality review, approval, and external filing.

**Why it matters:** It is the common reference point for the whole process. The case version supports controlled updates so that an older action cannot accidentally overwrite newer work.

**Connected records:** Inventory sources, inventory items, comparator evidence, calculation runs, case issues, package artifacts, decision challenges, approvals, command-ledger entries, and audit events.

### 2. Inventory Source

**Business purpose:** Preserves each uploaded inventory file as an original, versioned source record.

**What it contains:** The file itself, file name, type and size, content hash, data classification, template version, source profile, report date, photo-content status, and a unique source version identifier.

**When it is used:** Created whenever an inventory is accepted. A corrected or replacement file creates a new source version instead of changing the earlier record.

**Why it matters:** It proves which file was used for a valuation and protects the original submission from silent alteration. The content hash can confirm that the file has not changed.

**Connected records:** Belongs to one valuation case and is the source for one or more inventory-item records.

### 3. Inventory Item

**Business purpose:** Represents one normalized line item from an inventory, such as a television, sofa, or appliance.

**What it contains:** Original row data, source reference and row number, room, container and location, description, category, brand, model, serial number, supplier or retailer, quantity, source disposition, condition, age, declared cost, notes, item version, workflow disposition, and whether the item is materially complete.

**When it is used:** Created when an accepted inventory is parsed. A corrected item is retained as a new version so the history remains visible.

**Why it matters:** Item-level records allow incomplete, duplicate, excluded, or corrected items to be managed individually. Keeping the original row alongside normalized fields makes the transformation traceable.

**Connected records:** Belongs to a valuation case and inventory source. It may have comparator evidence and case issues attached to it.

### 4. Comparator Evidence

**Business purpose:** Records the approved-source evidence used to support an item's replacement value.

**What it contains:** Source website and domain, snapshot reference, evidence text, price, currency, retrieval time, content hash, qualification result, and whether the amount is a generic estimate.

**When it is used:** Created during approved product research. Evidence that needs review or is rejected is still identified clearly rather than being treated as qualified support.

**Why it matters:** An adjuster can see where a proposed replacement price came from, when it was retrieved, and whether it met the evidence rules. Versioning and hashing help make research reproducible.

**Connected records:** Belongs to one valuation case and one inventory item.

### 5. Rule Set Version

**Business purpose:** Stores a governed, effective-dated version of the valuation rules.

**What it contains:** Province, effective dates, applicable coverage and endorsement codes, approval status, the rule definition, content hash, and approval details.

**When it is used:** An approved rule version is selected before valuation based on the case facts and loss date. Draft, retired, or rejected versions are not treated as approved valuation authority.

**Why it matters:** Rules can change over time. This table identifies the exact approved rules used so a valuation can be explained and reproduced later.

**Connected records:** The selected rule-set version is recorded on calculation runs and package artifacts through its version identifier.

### 6. Calculation Run

**Business purpose:** Stores the result of one deterministic valuation calculation using fixed, versioned inputs.

**What it contains:** Inventory, evidence, rule-set, and calculation-engine versions; replacement cost value (RCV); depreciation; tax; actual cash value (ACV); contents limit; payable recommendation; rounding adjustment; reconciliation result; input hash; and calculation time.

**When it is used:** Created when the inventory, evidence, and applicable rules are ready for calculation. A recalculation produces a new run rather than replacing the previous result.

**Why it matters:** It separates financial calculation from conversational AI. The result can be tested, reconciled, and reproduced from the same inputs and engine version.

**Connected records:** Belongs to one valuation case and can be the basis for one or more package artifacts.

### 7. Item Valuation

**Business purpose:** Preserves the deterministic financial result for one inventory item.

**What it contains:** Replacement value per item and total, depreciation category, percentage and amount, ACV per item and total, tax, payable recommendation, input hash, and calculation time.

**When it is used:** Created by the approved calculation workflow for every valued item. A recalculation creates a new version rather than overwriting the previous result.

**Why it matters:** Adjusters commonly review valuation results at item level. Keeping these outputs separate from source-entered spreadsheet amounts prevents unverified values from becoming authoritative calculations.

**Connected records:** Belongs to one valuation case, inventory item, and calculation run.

### 8. Case Issue

**Business purpose:** Tracks a specific validation, quality, or business concern that requires attention.

**What it contains:** Issue code, severity, status, owner, details, resolution, rationale, and resolution time. An issue can optionally point to a specific inventory item.

**When it is used:** Created when the process finds missing information, invalid source data, low-confidence evidence, a quality exception, or another condition that should not be handled silently.

**Why it matters:** It provides a visible work queue and resolution history. This supports clear ownership and prevents exceptions from being lost in chat history or informal notes.

**Connected records:** Always belongs to a valuation case and may also belong to an individual inventory item.

### 9. Package Artifact

**Business purpose:** Stores the review package presented to the adjuster.

**What it contains:** The valuation workbook, calculation trace, package hash, generator version, related input versions, creation time, and an indicator showing whether it is the current package.

**When it is used:** Created after the calculation and quality gates pass. If inputs change, a new package version is generated and the earlier package remains available as history.

**Why it matters:** It binds the review material to the exact inventory, evidence, rules, and calculation used. The package hash helps prove that the reviewed document is the same one that was approved.

**Connected records:** Belongs to one valuation case and one calculation run. Decision challenges and approvals refer to the package being reviewed.

### 10. Decision Challenge

**Business purpose:** Creates a short-lived, single-use control for an adjuster's package decision.

**What it contains:** Challenge identifier, package version and hash, case version, intended actor, expiry time, consumption time, and whether it has already been used.

**When it is used:** Created immediately before the agent asks an adjuster to approve, reject, or hold a package. It expires after a limited period and cannot be reused.

**Why it matters:** It prevents a free-form or stale chat response from authorizing a decision. The control confirms the actor, case version, and exact package under review.

**Connected records:** Belongs to one valuation case and one package artifact. A completed challenge is referenced by the resulting approval record.

### 11. Approval

**Business purpose:** Preserves the licensed adjuster's formal decision on a valuation package.

**What it contains:** Decision to approve, reject, or hold; attestation; reason and rationale where required; package version and hash; adjuster identity; and decision time.

**When it is used:** Created after a valid decision challenge is completed. It is an immutable decision record rather than a field that is repeatedly overwritten.

**Why it matters:** It provides evidence that a named adjuster reviewed a specific package and made an explicit decision. The record does not mean that the claim has been paid or externally closed.

**Connected records:** Belongs to one valuation case and links to the package artifact and decision challenge used for the decision.

### 12. Command Ledger

**Business purpose:** Prevents the same workflow request from being processed more than once and preserves the response returned for that request.

**What it contains:** A unique retry key, command name, request hash, outcome, stored result, actor, correlation identifier, and completion time.

**When it is used:** Written for workflow actions that change case data. If the same valid request is retried, the prior result can be returned without repeating the business action.

**Why it matters:** Cloud and agent interactions can be retried because of time-outs or connection issues. This table helps prevent duplicate uploads, calculations, packages, or decisions.

**Connected records:** Each entry belongs to one valuation case.

### 13. Audit Event

**Business purpose:** Provides an append-only history of material operations and case-state changes.

**What it contains:** Operation performed, before and after states, before and after case versions, actor, time, correlation identifier, request hash, and supporting details.

**When it is used:** Added whenever a material workflow action or state transition occurs. Existing events are retained rather than rewritten.

**Why it matters:** It allows reviewers to reconstruct who did what, when it happened, and how the case progressed. It supports operational review, compliance, troubleshooting, and investigation.

**Connected records:** Each event belongs to one valuation case.

## Business controls built into the schema

- **One authoritative case record:** The Valuation Case shows the current stage and assigned adjuster.
- **Versioned inputs and outputs:** Source files, items, evidence, rules, calculations, and packages can be traced to the versions used at the time.
- **No-photo MVP:** Item, data-tag, and receipt photos are not extracted, stored as item evidence, or used in valuation. A source status records when photo content was present but excluded.
- **Human accountability:** Package decisions are bound to a licensed adjuster and an exact package.
- **Exception visibility:** Issues are recorded, owned, and resolved explicitly.
- **Replay protection:** The Command Ledger reduces the risk of duplicate processing during retries.
- **End-to-end traceability:** Audit Events preserve the material history without relying on conversation history.
- **History preservation:** Relationships use restricted deletion so source evidence, decisions, and audit records are not casually removed with a parent record.

## Plain-language glossary

| Term | Meaning |
| --- | --- |
| ACV | Actual cash value: replacement cost less applicable depreciation. |
| RCV | Replacement cost value: the estimated cost to replace an item before depreciation. |
| Content hash | A digital fingerprint used to detect whether a file or data payload has changed. |
| Deterministic calculation | A calculation that produces the same result when run with the same inputs and engine version. |
| Immutable record | A record retained as historical evidence instead of being overwritten. Corrections create a new version. |
| Case version | A sequence number used to prevent an older action from overwriting newer case data. |
| Correlation identifier | A reference used to connect related workflow and audit activity during support or investigation. |
| Package hash | A digital fingerprint that binds an adjuster's decision to the exact package reviewed. |
