# TD CAT Contents Dataverse Schema

> [!IMPORTANT]
> Before creating the solution or any schema components, create the Dataverse publisher **CAT Contents Assistant** with unique name `catcontentsassistant` and prefix `cca`. Schema prefixes are permanent after component creation; do not use the default publisher or a different prefix.

Create these components inside the unmanaged solution **CAT Contents Assistant** (`CATContentsAssistant`) using the **CAT Contents Assistant** publisher.

All tables are **user or team owned**, have auditing enabled, and use the standard Dataverse GUID primary key. Enable change tracking and optimistic concurrency. Unless specified otherwise, text columns are optional and limited to 200 characters.

> [!IMPORTANT]
> **MVP inventory scope:** Adjusters use PPN SOL spreadsheets without item photos. Do not create photo, receipt-photo, or data-tag-photo columns or extract embedded item images. If a workbook contains item-photo content, record Photo Content Status as `PresentExcluded`; parse only supported text and numeric fields. Template branding images do not count as item photos.

## MVP 2 readiness: inventory files with photos

MVP 2 may ingest item photos, data-tag photos, and receipt photos only after the following capabilities are designed, approved, implemented, and tested. These are future requirements and are **not part of the current schema or deployment**.

- Create a versioned, immutable **Item Evidence** table linked to Valuation Case, Inventory Source, and Inventory Item.
- Store each extracted image in a Dataverse file column or approved evidence repository; retain only an opaque reference in agent context.
- Record evidence type, source sheet/cell or row, file name, MIME type, size, content hash, scan result, classification, extraction status, failure reason, evidence date, retention date, and superseded-version reference.
- Define reliable workbook-image-to-item mapping. Do not associate images by visual proximity alone when merged cells, floating images, hidden rows, or reordered rows make the relationship ambiguous.
- Add bounded extraction with file-count, image-size, workbook-size, and processing-time limits. Reassess the current 128 MB inventory-file limit using representative photo-heavy workbooks.
- Run malware scanning, file-signature validation, metadata stripping where required, and data-classification checks before evidence becomes available for review.
- Apply licensed-adjuster authorization, claim assignment, row ownership, restricted deletion, retention, legal hold, and audit controls to every evidence record and binary.
- Update upload and parsing workflows for partial failures, retries, idempotency, duplicate-image detection, unsupported formats, and explicit human-resolution queues.
- Add approved image-analysis controls before using photos for extraction or valuation. Record model/version, confidence, provenance, and human confirmation; never let image analysis make autonomous coverage or settlement decisions.
- Update package generation to bind evidence versions and hashes to the package reviewed by the adjuster.
- Validate accessibility, privacy, security, performance, storage cost, and accuracy with representative photo workbooks before enabling the capability.

Until these controls are complete, workbooks containing photos remain acceptable only for supported text and numeric ingestion and must use Photo Content Status `PresentExcluded`.

## 1. Valuation Case

**Schema name:** `cca_ValuationCase`<br>
**Primary name:** `cca_CaseName`<br>
**Alternate key:** `cca_ClaimId`

| Column | Schema name | Type | Requirement |
| --- | --- | --- | --- |
| Claim ID | `cca_ClaimId` | Text (100) | Required |
| Policy ID | `cca_PolicyId` | Text (100) | Optional |
| Insured Name | `cca_InsuredName` | Text (300) | Optional |
| Case State | `cca_CaseState` | Choice: Case State | Required; default `Candidate` |
| Case Version | `cca_CaseVersion` | Whole number | Required; default `1` |
| Province | `cca_Province` | Choice: Province | Optional until claim facts confirmed |
| Data Classification | `cca_Classification` | Choice: Data Classification | Optional until authorization |
| Loss Date | `cca_LossDate` | Date only | Optional until claim facts confirmed |
| Loss Type | `cca_LossType` | Text (100) | Optional |
| CAT Code | `cca_CatCode` | Text (50) | Optional |
| Coverage Codes | `cca_CoverageCodes` | Multiline text | Optional |
| Endorsement Codes | `cca_EndorsementCodes` | Multiline text | Optional |
| Contents Limit | `cca_ContentsLimit` | Decimal (2) | Optional |
| Currency | `cca_Currency` | Text (3) | Default `CAD` |
| Checkpoint | `cca_Checkpoint` | Multiline text | Optional |
| Assigned Adjuster | `cca_AssignedAdjuster` | Text (320) | Required |
| Retention Until | `cca_RetentionUntil` | Date only | Optional |
| Legal Hold | `cca_LegalHold` | Yes/No | Default `No` |

## 2. Inventory Source

**Schema name:** `cca_InventorySource`<br>
**Primary name:** `cca_SourceName`<br>
**Alternate key:** `cca_SourceVersionId`

| Column | Schema name | Type | Requirement |
| --- | --- | --- | --- |
| Source Version ID | `cca_SourceVersionId` | Text (100) | Required |
| Valuation Case | `cca_ValuationCaseId` | Lookup to Valuation Case | Required |
| Content Hash | `cca_ContentHash` | Text (128) | Required |
| File Name | `cca_FileName` | Text (260) | Required |
| MIME Type | `cca_MimeType` | Text (100) | Required |
| File Size | `cca_FileSize` | Whole number | Required |
| Data Classification | `cca_Classification` | Choice: Data Classification | Required |
| Template Version | `cca_TemplateVersion` | Text (50) | Optional |
| Source Profile | `cca_SourceProfile` | Text (100) | Optional; identifies the parsed workbook layout |
| Report Date | `cca_ReportDate` | Date and time | Optional |
| Photo Content Status | `cca_PhotoContentStatus` | Choice: Photo Content Status | Required; default `Unknown` |
| Inventory File | `cca_InventoryFile` | File (128 MB maximum) | Required |
| Is Immutable | `cca_IsImmutable` | Yes/No | Required; default `Yes` |

## 3. Inventory Item

**Schema name:** `cca_InventoryItem`<br>
**Primary name:** `cca_ItemName`<br>
**Alternate key:** `cca_ItemVersionKey`

| Column | Schema name | Type | Requirement |
| --- | --- | --- | --- |
| Item Version Key | `cca_ItemVersionKey` | Text (150) | Required |
| Valuation Case | `cca_ValuationCaseId` | Lookup to Valuation Case | Required |
| Inventory Source | `cca_InventorySourceId` | Lookup to Inventory Source | Required |
| Source Row Number | `cca_SourceRowNumber` | Whole number | Required |
| Source Item Reference | `cca_SourceItemReference` | Text (100) | Optional |
| Original Record JSON | `cca_OriginalRecordJson` | Multiline text | Required |
| Room | `cca_Room` | Text (200) | Optional |
| Box or Container | `cca_Container` | Text (200) | Optional |
| Item Location | `cca_Location` | Text (300) | Optional |
| Item Description | `cca_ItemDescription` | Text (500) | Optional |
| Category | `cca_Category` | Text (200) | Optional |
| Brand | `cca_Brand` | Text (200) | Optional |
| Model | `cca_Model` | Text (200) | Optional |
| Serial Number | `cca_SerialNumber` | Text (200) | Optional |
| Supplier or Retailer | `cca_Supplier` | Text (250) | Optional |
| Quantity | `cca_Quantity` | Decimal (4) | Optional |
| Source Item Disposition | `cca_SourceItemDisposition` | Text (100) | Optional; source value retained without changing workflow disposition |
| Condition | `cca_Condition` | Text (200) | Optional |
| Age Years | `cca_AgeYears` | Whole number (0-200) | Optional |
| Age Months | `cca_AgeMonths` | Whole number (0-11) | Optional |
| Declared Cost | `cca_DeclaredCost` | Decimal (2) | Optional; source-entered amount, not an authoritative valuation |
| Declared Cost Basis | `cca_DeclaredCostBasis` | Choice: Declared Cost Basis | Optional |
| Item Notes | `cca_ItemNotes` | Multiline text | Optional |
| Item Version | `cca_ItemVersion` | Whole number | Required; default `1` |
| Disposition | `cca_Disposition` | Choice: Item Disposition | Required; default `Pending` |
| Materially Complete | `cca_MaterialComplete` | Yes/No | Required; default `No` |

## 4. Comparator Evidence

**Schema name:** `cca_ComparatorEvidence`<br>
**Primary name:** `cca_EvidenceName`<br>
**Alternate key:** `cca_EvidenceVersionId`

| Column | Schema name | Type | Requirement |
| --- | --- | --- | --- |
| Evidence Version ID | `cca_EvidenceVersionId` | Text (100) | Required |
| Valuation Case | `cca_ValuationCaseId` | Lookup to Valuation Case | Required |
| Inventory Item | `cca_InventoryItemId` | Lookup to Inventory Item | Required |
| Source URL | `cca_SourceUrl` | URL text (2,000) | Required |
| Source Domain | `cca_SourceDomain` | Text (250) | Required |
| Snapshot Reference | `cca_SnapshotReference` | Text (500) | Optional |
| Content Hash | `cca_ContentHash` | Text (128) | Required |
| Price | `cca_Price` | Decimal (2) | Required |
| Currency | `cca_Currency` | Text (3) | Required; default `CAD` |
| Qualification | `cca_Qualification` | Choice: Evidence Qualification | Required |
| Retrieved At | `cca_RetrievedAt` | Date and time | Required |
| Evidence Text | `cca_EvidenceText` | Multiline text | Optional |
| Is Generic Estimate | `cca_IsGenericEstimate` | Yes/No | Required; default `No` |

## 5. Rule Set Version

**Schema name:** `cca_RuleSetVersion`<br>
**Primary name:** `cca_RuleSetName`<br>
**Alternate key:** `cca_RuleSetVersionIdKey`

| Column | Schema name | Type | Requirement |
| --- | --- | --- | --- |
| Rule Set Version ID | `cca_RuleSetVersionBusinessId` | Text (100) | Required |
| Province | `cca_Province` | Choice: Province | Required |
| Effective Start | `cca_EffectiveStart` | Date only | Required |
| Effective End | `cca_EffectiveEnd` | Date only | Optional |
| Coverage Codes | `cca_CoverageCodes` | Multiline text | Required |
| Endorsement Codes | `cca_EndorsementCodes` | Multiline text | Optional |
| Approval Status | `cca_ApprovalStatus` | Choice: Rule Approval Status | Required; default `Draft` |
| Rule Payload JSON | `cca_RulePayloadJson` | Multiline text | Required |
| Content Hash | `cca_ContentHash` | Text (128) | Required |
| Approved By | `cca_ApprovedBy` | Text (320) | Required when approved |
| Approved At | `cca_ApprovedAt` | Date and time | Required when approved |

## 6. Calculation Run

**Schema name:** `cca_CalculationRun`<br>
**Primary name:** `cca_CalculationName`<br>
**Alternate key:** `cca_CalculationRunIdKey`

| Column | Schema name | Type | Requirement |
| --- | --- | --- | --- |
| Calculation Run ID | `cca_CalculationRunBusinessId` | Text (100) | Required |
| Valuation Case | `cca_ValuationCaseId` | Lookup to Valuation Case | Required |
| Inventory Version | `cca_InventoryVersion` | Text (100) | Required |
| Evidence Version | `cca_EvidenceVersion` | Text (100) | Required |
| Rule Set Version | `cca_RuleSetVersion` | Text (100) | Required |
| Engine Version | `cca_EngineVersion` | Text (100) | Required |
| RCV | `cca_Rcv` | Decimal (2) | Required |
| Depreciation | `cca_Depreciation` | Decimal (2) | Required |
| Tax | `cca_Tax` | Decimal (2) | Required |
| ACV | `cca_Acv` | Decimal (2) | Required |
| Contents Limit | `cca_ContentsLimit` | Decimal (2) | Required |
| Payable Recommendation | `cca_PayableRecommendation` | Decimal (2) | Required |
| Rounding Adjustment | `cca_RoundingAdjustment` | Decimal (2) | Required |
| Reconciliation Passed | `cca_ReconciliationPassed` | Yes/No | Required |
| Input Hash | `cca_InputHash` | Text (128) | Required |
| Calculated At | `cca_CalculatedAt` | Date and time | Required |

## 7. Item Valuation

**Schema name:** `cca_ItemValuation`<br>
**Primary name:** `cca_ItemValuationName`<br>
**Alternate key:** `cca_ItemValuationVersionId`

| Column | Schema name | Type | Requirement |
| --- | --- | --- | --- |
| Item Valuation Version ID | `cca_ItemValuationVersionId` | Text (100) | Required |
| Valuation Case | `cca_ValuationCaseId` | Lookup to Valuation Case | Required |
| Inventory Item | `cca_InventoryItemId` | Lookup to Inventory Item | Required |
| Calculation Run | `cca_CalculationRunId` | Lookup to Calculation Run | Required |
| Replacement Value Each | `cca_ReplacementValueEach` | Decimal (2) | Optional |
| Replacement Value Total | `cca_ReplacementValueTotal` | Decimal (2) | Optional |
| Depreciation Category | `cca_DepreciationCategory` | Text (100) | Optional |
| Depreciation Percent | `cca_DepreciationPercent` | Decimal (4) | Optional |
| Depreciation Amount | `cca_DepreciationAmount` | Decimal (2) | Optional |
| ACV Each | `cca_AcvEach` | Decimal (2) | Optional |
| ACV Total | `cca_AcvTotal` | Decimal (2) | Optional |
| Tax | `cca_Tax` | Decimal (2) | Optional |
| Payable Recommendation | `cca_PayableRecommendation` | Decimal (2) | Optional |
| Input Hash | `cca_InputHash` | Text (128) | Optional |
| Calculated At | `cca_CalculatedAt` | Date and time | Optional |

Source-entered replacement value, depreciation, and ACV cells remain in Original Record JSON for traceability. They do not populate Item Valuation; only the deterministic valuation workflow writes this table.

## 8. Case Issue

**Schema name:** `cca_CaseIssue`<br>
**Primary name:** `cca_IssueName`<br>
**Alternate key:** `cca_IssueKey`

| Column | Schema name | Type | Requirement |
| --- | --- | --- | --- |
| Issue Key | `cca_IssueKey` | Text (150) | Required |
| Valuation Case | `cca_ValuationCaseId` | Lookup to Valuation Case | Required |
| Inventory Item | `cca_InventoryItemId` | Lookup to Inventory Item | Optional |
| Issue Code | `cca_IssueCode` | Text (100) | Required |
| Severity | `cca_Severity` | Choice: Issue Severity | Required |
| Issue Status | `cca_IssueStatus` | Choice: Issue Status | Required; default `Open` |
| Issue Owner Email | `cca_OwnerEmail` | Text (320) | Optional |
| Details | `cca_Details` | Multiline text | Required |
| Resolution Code | `cca_ResolutionCode` | Text (100) | Optional |
| Rationale | `cca_Rationale` | Multiline text | Optional |
| Resolved At | `cca_ResolvedAt` | Date and time | Optional |

## 9. Package Artifact

**Schema name:** `cca_PackageArtifact`<br>
**Primary name:** `cca_PackageName`<br>
**Alternate key:** `cca_PackageVersionId`

| Column | Schema name | Type | Requirement |
| --- | --- | --- | --- |
| Package Version ID | `cca_PackageVersionId` | Text (100) | Required |
| Valuation Case | `cca_ValuationCaseId` | Lookup to Valuation Case | Required |
| Calculation Run | `cca_CalculationRunIdLookup` | Lookup to Calculation Run | Required |
| Inventory Version | `cca_InventoryVersion` | Text (100) | Required |
| Evidence Version | `cca_EvidenceVersion` | Text (100) | Required |
| Rule Set Version | `cca_RuleSetVersion` | Text (100) | Required |
| Package Hash | `cca_PackageHash` | Text (128) | Required |
| Generator Version | `cca_GeneratorVersion` | Text (100) | Required |
| Valuation Workbook | `cca_Workbook` | File (128 MB maximum) | Required |
| Calculation Trace | `cca_CalculationTrace` | File (32 MB maximum) | Required |
| Artifact Created At | `cca_ArtifactCreatedAt` | Date and time | Required |
| Is Current | `cca_IsCurrent` | Yes/No | Required; default `Yes` |

## 10. Decision Challenge

**Schema name:** `cca_DecisionChallenge`<br>
**Primary name:** `cca_ChallengeName`<br>
**Alternate key:** `cca_ChallengeId`

| Column | Schema name | Type | Requirement |
| --- | --- | --- | --- |
| Challenge ID | `cca_ChallengeId` | Text (100) | Required |
| Valuation Case | `cca_ValuationCaseId` | Lookup to Valuation Case | Required |
| Package Artifact | `cca_PackageArtifactId` | Lookup to Package Artifact | Required |
| Package Version ID | `cca_PackageVersionId` | Text (100) | Required |
| Package Hash | `cca_PackageHash` | Text (128) | Required |
| Case Version | `cca_CaseVersion` | Whole number | Required |
| Actor | `cca_Actor` | Text (320) | Required |
| Expires At | `cca_ExpiresAt` | Date and time | Required |
| Consumed At | `cca_ConsumedAt` | Date and time | Optional |
| Is Consumed | `cca_IsConsumed` | Yes/No | Required; default `No` |

## 11. Approval

**Schema name:** `cca_Approval`<br>
**Primary name:** `cca_ApprovalName`<br>
**Alternate key:** `cca_ApprovalIdKey`

| Column | Schema name | Type | Requirement |
| --- | --- | --- | --- |
| Approval ID | `cca_ApprovalBusinessId` | Text (100) | Required |
| Valuation Case | `cca_ValuationCaseId` | Lookup to Valuation Case | Required |
| Package Artifact | `cca_PackageArtifactId` | Lookup to Package Artifact | Required |
| Decision Challenge | `cca_DecisionChallengeId` | Lookup to Decision Challenge | Required |
| Decision | `cca_Decision` | Choice: Decision | Required |
| Attestation | `cca_Attestation` | Yes/No | Required |
| Reason Code | `cca_ReasonCode` | Text (100) | Required for reject, hold, or override |
| Rationale | `cca_Rationale` | Multiline text | Required for reject, hold, or override |
| Package Version ID | `cca_PackageVersionId` | Text (100) | Required |
| Package Hash | `cca_PackageHash` | Text (128) | Required |
| Adjuster Identity | `cca_AdjusterIdentity` | Text (320) | Required |
| Decided At | `cca_DecidedAt` | Date and time | Required |

## 12. Command Ledger

**Schema name:** `cca_CommandLedger`<br>
**Primary name:** `cca_CommandName`<br>
**Alternate key:** `cca_IdempotencyKey`

| Column | Schema name | Type | Requirement |
| --- | --- | --- | --- |
| Idempotency Key | `cca_IdempotencyKey` | Text (200) | Required |
| Valuation Case | `cca_ValuationCaseId` | Lookup to Valuation Case | Required |
| Command | `cca_Command` | Text (150) | Required |
| Request Hash | `cca_RequestHash` | Text (128) | Required |
| Result JSON | `cca_ResultJson` | Multiline text | Required after completion |
| Outcome | `cca_Outcome` | Choice: Workflow Outcome | Required after completion |
| Actor | `cca_Actor` | Text (320) | Required |
| Correlation ID | `cca_CorrelationId` | Text (100) | Required |
| Completed At | `cca_CompletedAt` | Date and time | Required after completion |

## 13. Audit Event

**Schema name:** `cca_AuditEvent`<br>
**Primary name:** `cca_EventName`<br>
**Alternate key:** `cca_AuditEventIdKey`

| Column | Schema name | Type | Requirement |
| --- | --- | --- | --- |
| Audit Event ID | `cca_AuditEventBusinessId` | Text (100) | Required |
| Valuation Case | `cca_ValuationCaseId` | Lookup to Valuation Case | Required |
| Operation | `cca_Operation` | Text (150) | Required |
| Before State | `cca_BeforeState` | Text (100) | Optional |
| After State | `cca_AfterState` | Text (100) | Optional |
| Before Version | `cca_BeforeVersion` | Whole number | Optional |
| After Version | `cca_AfterVersion` | Whole number | Optional |
| Actor | `cca_Actor` | Text (320) | Required |
| Correlation ID | `cca_CorrelationId` | Text (100) | Required |
| Request Hash | `cca_RequestHash` | Text (128) | Optional |
| Event At | `cca_EventAt` | Date and time | Required |
| Details JSON | `cca_DetailsJson` | Multiline text | Optional |

## Relationships

Configure **restrict delete** on every relationship to preserve evidence and audit history. Use parental ownership only where Dataverse access cascading is explicitly approved.

| Parent | Child | Lookup on child | Requirement |
| --- | --- | --- | --- |
| Valuation Case | Inventory Source | `cca_ValuationCaseId` | Required |
| Valuation Case | Inventory Item | `cca_ValuationCaseId` | Required |
| Inventory Source | Inventory Item | `cca_InventorySourceId` | Required |
| Valuation Case | Comparator Evidence | `cca_ValuationCaseId` | Required |
| Inventory Item | Comparator Evidence | `cca_InventoryItemId` | Required |
| Valuation Case | Calculation Run | `cca_ValuationCaseId` | Required |
| Valuation Case | Item Valuation | `cca_ValuationCaseId` | Required |
| Inventory Item | Item Valuation | `cca_InventoryItemId` | Required |
| Calculation Run | Item Valuation | `cca_CalculationRunId` | Required |
| Valuation Case | Case Issue | `cca_ValuationCaseId` | Required |
| Inventory Item | Case Issue | `cca_InventoryItemId` | Optional |
| Valuation Case | Package Artifact | `cca_ValuationCaseId` | Required |
| Calculation Run | Package Artifact | `cca_CalculationRunIdLookup` | Required |
| Valuation Case | Decision Challenge | `cca_ValuationCaseId` | Required |
| Package Artifact | Decision Challenge | `cca_PackageArtifactId` | Required |
| Valuation Case | Approval | `cca_ValuationCaseId` | Required |
| Package Artifact | Approval | `cca_PackageArtifactId` | Required |
| Decision Challenge | Approval | `cca_DecisionChallengeId` | Required |
| Valuation Case | Command Ledger | `cca_ValuationCaseId` | Required |
| Valuation Case | Audit Event | `cca_ValuationCaseId` | Required |

## Choice values

### Case State

`Candidate`, `EligibilityConfirmed`, `AccessAuthorized`, `CaseReady`, `InventoryAccepted`, `InventoryReview`, `InventoryComplete`, `ResearchComplete`, `RulesResolved`, `Calculated`, `QualityPassed`, `PackageReady`, `PendingApproval`, `Approved`, `ExternallyFiled`, `Closed`, `StoppedOutsideMvp`, `StoppedDataProhibited`, `HeldFileInvalid`, `HeldInventoryIncomplete`, `HeldRulesUnavailable`, `HeldQualityException`, `HeldAdjuster`, `OpenExternal`

### Province

`AB`, `BC`, `MB`, `NB`, `NL`, `NS`, `NT`, `NU`, `ON`, `PE`, `QC`, `SK`, `YT`

### Other choices

| Choice | Values |
| --- | --- |
| Data Classification | `Approved`, `Restricted`, `Prohibited`, `Unknown` |
| Photo Content Status | `NotPresent`, `PresentExcluded`, `Unknown` |
| Item Disposition | `Pending`, `Accepted`, `Corrected`, `Duplicate`, `Held`, `Excluded` |
| Declared Cost Basis | `Each`, `Total`, `Unspecified` |
| Evidence Qualification | `Qualified`, `GenericEstimate`, `Rejected`, `NeedsReview` |
| Rule Approval Status | `Draft`, `Approved`, `Retired`, `Rejected` |
| Issue Severity | `Information`, `Warning`, `Error`, `Critical` |
| Issue Status | `Open`, `InReview`, `Resolved`, `Waived`, `Closed` |
| Decision | `Approve`, `Reject`, `Hold` |
| Workflow Outcome | `Succeeded`, `NeedsInput`, `Held`, `Rejected`, `Conflict` |

## Copilot generation order

1. Create all choices.
2. Create Valuation Case and Rule Set Version.
3. Create the remaining tables without lookup columns.
4. Add relationships and lookup columns.
5. Add alternate keys.
6. Enable auditing, change tracking, and optimistic concurrency.
7. Configure row ownership and licensed-adjuster security roles.
8. Publish all customizations and confirm every component belongs to `CATContentsAssistant`.

The machine-readable equivalent is in [schema.json](schema.json).

For natural-language creation in the Power Apps table designer, use [COPILOT_TABLE_GENERATION_PROMPT.md](COPILOT_TABLE_GENERATION_PROMPT.md).

## Dataverse CLI deployment

The deployment script keeps `PacToken` as its default transport. To use the preview Dataverse CLI for authentication and HTTP transport, install `@microsoft/dataverse`, select an authenticated profile, and opt in with `-Transport DataverseCli`:

```powershell
npm install -g @microsoft/dataverse
dataverse auth create --environment https://orgb46f68a9.crm.dynamics.com --name td-cat
dataverse auth list
dataverse auth select --name td-cat
./scripts/Deploy-DataverseSchema.ps1 -Transport DataverseCli -WhatIf
./scripts/Deploy-DataverseSchema.ps1 -Transport DataverseCli
```

The `-WhatIf` invocation performs metadata existence checks but doesn't create or publish components. CLI endpoint, header, naming, and metadata-type mappings are defined in [dataverse-cli-mappings.json](dataverse-cli-mappings.json). The same table model in [schema.json](schema.json) drives both transports.
