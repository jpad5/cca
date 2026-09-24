# Copilot prompt for Dataverse table generation

> [!IMPORTANT]
> First create the Dataverse publisher **CAT Contents Assistant** with unique name `catcontentsassistant` and prefix `cca`. Create or configure the solution to use this publisher before generating any tables. Do not proceed under the default publisher because schema prefixes cannot be changed after component creation.
>
> **MVP inventory scope:** Do not generate columns or tables for item photos, data-tag photos, or receipt photos. Photo content is excluded from extraction and valuation. Workbooks containing item photos may contribute supported text and numeric fields only and must be marked `PresentExcluded` in Photo Content Status.

Use these prompts in Power Apps at **Tables > Create with Copilot**. Create one table at a time in the listed order. Review the proposed schema before selecting **Create**.

## Common instruction

Paste this paragraph before each table prompt:

> Create this exact Dataverse table with prefix `cca`. Keep every specified name and column; add nothing. Use user/team ownership. Enable auditing, change tracking, notes, and optimistic concurrency. Primary name: required text, max 200. Text=single-line; multiline=multiline; date/time=user-local. Keep decimal precision and choice order. No lookups or sample rows.

## 1. Valuation Case

> Table: Valuation Case; plural: Valuation Cases; schema: `cca_valuationcase`. Description: Durable orchestration state for a CAT contents valuation case. Primary name: Case Name (`cca_casename`).
>
> Columns: Claim ID (`cca_claimid`), required text max 100; Policy ID (`cca_policyid`), text max 100; Insured Name (`cca_insuredname`), text max 300; Case State (`cca_casestate`), required choice: Candidate, EligibilityConfirmed, AccessAuthorized, CaseReady, InventoryAccepted, InventoryReview, InventoryComplete, ResearchComplete, RulesResolved, Calculated, QualityPassed, PackageReady, PendingApproval, Approved, ExternallyFiled, Closed, StoppedOutsideMvp, StoppedDataProhibited, HeldFileInvalid, HeldInventoryIncomplete, HeldRulesUnavailable, HeldQualityException, HeldAdjuster, OpenExternal; Case Version (`cca_caseversion`), required whole number min 1; Province (`cca_province`), choice: AB, BC, MB, NB, NL, NS, NT, NU, ON, PE, QC, SK, YT; Data Classification (`cca_classification`), choice: Approved, Restricted, Prohibited, Unknown; Loss Date (`cca_lossdate`), date/time; Loss Type (`cca_losstype`), text max 100; CAT Code (`cca_catcode`), text max 50; Coverage Codes (`cca_coveragecodes`), multiline; Endorsement Codes (`cca_endorsementcodes`), multiline; Contents Limit (`cca_contentslimit`), decimal precision 2; Currency (`cca_currency`), text max 3; Checkpoint (`cca_checkpoint`), multiline; Assigned Adjuster (`cca_assignedadjuster`), text max 320; Retention Until (`cca_retentionuntil`), date/time; Legal Hold (`cca_legalhold`), yes/no default No.
> Create alternate key Claim ID Key (`cca_claimidkey`) using Claim ID.

## 2. Rule Set Version

> Table display name: Rule Set Version. Plural name: Rule Set Versions. Schema name: `cca_rulesetversion`. Description: Effective-dated immutable valuation rule set. Primary name: Rule Set Name, schema name `cca_rulesetname`.
>
> Add these columns: Rule Set Version ID (`cca_rulesetversionbusinessid`), required text maximum 100; Province (`cca_province`), choice with AB, BC, MB, NB, NL, NS, NT, NU, ON, PE, QC, SK, YT; Effective Start (`cca_effectivestart`), date and time; Effective End (`cca_effectiveend`), date and time; Coverage Codes (`cca_coveragecodes`), multiline text; Endorsement Codes (`cca_endorsementcodes`), multiline text; Approval Status (`cca_approvalstatus`), choice with Draft, Approved, Retired, Rejected; Rule Payload JSON (`cca_rulepayloadjson`), multiline text; Content Hash (`cca_contenthash`), text maximum 128; Approved By (`cca_approvedby`), text maximum 320; Approved At (`cca_approvedat`), date and time.
>
> Create alternate key Rule Set Version ID Key (`cca_rulesetversionidkey`) using Rule Set Version ID.

## 3. Inventory Source

> Table display name: Inventory Source. Plural name: Inventory Sources. Schema name: `cca_inventorysource`. Description: Immutable source file and validation metadata for an inventory version. Primary name: Source Name, schema name `cca_sourcename`.
>
> Add these columns: Source Version ID (`cca_sourceversionid`), required text maximum 100; Content Hash (`cca_contenthash`), required text maximum 128; File Name (`cca_filename`), text maximum 260; MIME Type (`cca_mimetype`), text maximum 100; File Size (`cca_filesize`), whole number minimum 0; Data Classification (`cca_classification`), choice with Approved, Restricted, Prohibited, Unknown; Template Version (`cca_templateversion`), text maximum 50; Source Profile (`cca_sourceprofile`), text maximum 100; Report Date (`cca_reportdate`), date and time; Photo Content Status (`cca_photocontentstatus`), choice with NotPresent, PresentExcluded, Unknown; Inventory File (`cca_inventoryfile`), file maximum 131072 KB; Is Immutable (`cca_isimmutable`), yes/no default No.
>
> Create alternate key Source Version ID Key (`cca_sourceversionidkey`) using Source Version ID.

## 4. Inventory Item

> Table display name: Inventory Item. Plural name: Inventory Items. Schema name: `cca_inventoryitem`. Description: Versioned normalized inventory row with original source data retained. Primary name: Item Name, schema name `cca_itemname`.
>
> Add these columns: Item Version Key (`cca_itemversionkey`), required text maximum 150; Source Row Number (`cca_sourcerownumber`), whole number minimum 1; Source Item Reference (`cca_sourceitemreference`), text maximum 100; Original Record JSON (`cca_originalrecordjson`), multiline text; Room (`cca_room`), text maximum 200; Box or Container (`cca_container`), text maximum 200; Item Location (`cca_location`), text maximum 300; Item Description (`cca_itemdescription`), text maximum 500; Category (`cca_category`), text maximum 200; Brand (`cca_brand`), text maximum 200; Model (`cca_model`), text maximum 200; Serial Number (`cca_serialnumber`), text maximum 200; Supplier or Retailer (`cca_supplier`), text maximum 250; Quantity (`cca_quantity`), decimal precision 4; Source Item Disposition (`cca_sourceitemdisposition`), text maximum 100; Condition (`cca_condition`), text maximum 200; Age Years (`cca_ageyears`), whole number minimum 0 maximum 200; Age Months (`cca_agemonths`), whole number minimum 0 maximum 11; Declared Cost (`cca_declaredcost`), decimal precision 2; Declared Cost Basis (`cca_declaredcostbasis`), choice with Each, Total, Unspecified; Item Notes (`cca_itemnotes`), multiline text; Item Version (`cca_itemversion`), required whole number minimum 1; Disposition (`cca_disposition`), choice with Pending, Accepted, Corrected, Duplicate, Held, Excluded; Materially Complete (`cca_materialcomplete`), yes/no default No.
>
> Create alternate key Item Version Key (`cca_itemversionkeykey`) using the Item Version Key column.

## 5. Comparator Evidence

> Table display name: Comparator Evidence. Plural name: Comparator Evidence. Schema name: `cca_comparatorevidence`. Description: Immutable approved-source replacement evidence for an inventory item. Primary name: Evidence Name, schema name `cca_evidencename`.
>
> Add these columns: Evidence Version ID (`cca_evidenceversionid`), required text maximum 100; Source URL (`cca_sourceurl`), text maximum 2000; Source Domain (`cca_sourcedomain`), text maximum 250; Snapshot Reference (`cca_snapshotreference`), text maximum 500; Content Hash (`cca_contenthash`), text maximum 128; Price (`cca_price`), decimal precision 2; Currency (`cca_currency`), text maximum 3; Qualification (`cca_qualification`), choice with Qualified, GenericEstimate, Rejected, NeedsReview; Retrieved At (`cca_retrievedat`), date and time; Evidence Text (`cca_evidencetext`), multiline text; Is Generic Estimate (`cca_isgenericestimate`), yes/no default No.
>
> Create alternate key Evidence Version ID Key (`cca_evidenceversionidkey`) using Evidence Version ID.

## 6. Calculation Run

> Table display name: Calculation Run. Plural name: Calculation Runs. Schema name: `cca_calculationrun`. Description: Deterministic valuation output bound to immutable input versions. Primary name: Calculation Name, schema name `cca_calculationname`.
>
> Add these columns: Calculation Run ID (`cca_calculationrunbusinessid`), required text maximum 100; Inventory Version (`cca_inventoryversion`), text maximum 100; Evidence Version (`cca_evidenceversion`), text maximum 100; Rule Set Version (`cca_rulesetversion`), text maximum 100; Engine Version (`cca_engineversion`), text maximum 100; RCV (`cca_rcv`), decimal precision 2; Depreciation (`cca_depreciation`), decimal precision 2; Tax (`cca_tax`), decimal precision 2; ACV (`cca_acv`), decimal precision 2; Contents Limit (`cca_contentslimit`), decimal precision 2; Payable Recommendation (`cca_payablerecommendation`), decimal precision 2; Rounding Adjustment (`cca_roundingadjustment`), decimal precision 2; Reconciliation Passed (`cca_reconciliationpassed`), yes/no default No; Input Hash (`cca_inputhash`), text maximum 128; Calculated At (`cca_calculatedat`), date and time.
>
> Create alternate key Calculation Run ID Key (`cca_calculationrunidkey`) using Calculation Run ID.

## 7. Item Valuation

> Table display name: Item Valuation. Plural name: Item Valuations. Schema name: `cca_itemvaluation`. Description: Versioned deterministic valuation output for one normalized inventory item. Primary name: Item Valuation Name, schema name `cca_itemvaluationname`.
>
> Add these columns: Item Valuation Version ID (`cca_itemvaluationversionid`), required text maximum 100; Replacement Value Each (`cca_replacementvalueeach`), decimal precision 2; Replacement Value Total (`cca_replacementvaluetotal`), decimal precision 2; Depreciation Category (`cca_depreciationcategory`), text maximum 100; Depreciation Percent (`cca_depreciationpercent`), decimal precision 4; Depreciation Amount (`cca_depreciationamount`), decimal precision 2; ACV Each (`cca_acveach`), decimal precision 2; ACV Total (`cca_acvtotal`), decimal precision 2; Tax (`cca_tax`), decimal precision 2; Payable Recommendation (`cca_payablerecommendation`), decimal precision 2; Input Hash (`cca_inputhash`), text maximum 128; Calculated At (`cca_calculatedat`), date and time.
>
> Create alternate key Item Valuation Version ID Key (`cca_itemvaluationversionidkey`) using Item Valuation Version ID.

## 8. Case Issue

> Table display name: Case Issue. Plural name: Case Issues. Schema name: `cca_caseissue`. Description: Typed validation, quality, and business issue requiring resolution. Primary name: Issue Name, schema name `cca_issuename`.
>
> Add these columns: Issue Key (`cca_issuekey`), required text maximum 150; Issue Code (`cca_issuecode`), required text maximum 100; Severity (`cca_severity`), choice with Information, Warning, Error, Critical; Issue Status (`cca_issuestatus`), choice with Open, InReview, Resolved, Waived, Closed; Issue Owner Email (`cca_owneremail`), text maximum 320; Details (`cca_details`), multiline text; Resolution Code (`cca_resolutioncode`), text maximum 100; Rationale (`cca_rationale`), multiline text; Resolved At (`cca_resolvedat`), date and time.
>
> Create alternate key Issue Key (`cca_issuekeykey`) using the Issue Key column.

## 9. Package Artifact

> Table display name: Package Artifact. Plural name: Package Artifacts. Schema name: `cca_packageartifact`. Description: Immutable workbook and trace package bound to valuation inputs. Primary name: Package Name, schema name `cca_packagename`.
>
> Add these columns: Package Version ID (`cca_packageversionid`), required text maximum 100; Inventory Version (`cca_inventoryversion`), text maximum 100; Evidence Version (`cca_evidenceversion`), text maximum 100; Rule Set Version (`cca_rulesetversion`), text maximum 100; Package Hash (`cca_packagehash`), required text maximum 128; Generator Version (`cca_generatorversion`), text maximum 100; Valuation Workbook (`cca_workbook`), file maximum 131072 KB; Calculation Trace (`cca_calculationtrace`), file maximum 32768 KB; Artifact Created At (`cca_artifactcreatedat`), date and time; Is Current (`cca_iscurrent`), yes/no default No.
>
> Create alternate key Package Version ID Key (`cca_packageversionidkey`) using Package Version ID.

## 10. Decision Challenge

> Table display name: Decision Challenge. Plural name: Decision Challenges. Schema name: `cca_decisionchallenge`. Description: Short-lived single-use approval challenge bound to actor and package. Primary name: Challenge Name, schema name `cca_challengename`.
>
> Add these columns: Challenge ID (`cca_challengeid`), required text maximum 100; Package Version ID (`cca_packageversionid`), text maximum 100; Package Hash (`cca_packagehash`), text maximum 128; Case Version (`cca_caseversion`), whole number minimum 1; Actor (`cca_actor`), text maximum 320; Expires At (`cca_expiresat`), date and time; Consumed At (`cca_consumedat`), date and time; Is Consumed (`cca_isconsumed`), yes/no default No.
>
> Create alternate key Challenge ID Key (`cca_challengeidkey`) using Challenge ID.

## 11. Approval

> Table display name: Approval. Plural name: Approvals. Schema name: `cca_approval`. Description: Immutable licensed-adjuster package decision record. Primary name: Approval Name, schema name `cca_approvalname`.
>
> Add these columns: Approval ID (`cca_approvalbusinessid`), required text maximum 100; Decision (`cca_decision`), required choice with Approve, Reject, Hold; Attestation (`cca_attestation`), yes/no default No; Reason Code (`cca_reasoncode`), text maximum 100; Rationale (`cca_rationale`), multiline text; Package Version ID (`cca_packageversionid`), text maximum 100; Package Hash (`cca_packagehash`), text maximum 128; Adjuster Identity (`cca_adjusteridentity`), text maximum 320; Decided At (`cca_decidedat`), date and time.
>
> Create alternate key Approval ID Key (`cca_approvalidkey`) using Approval ID.

## 12. Command Ledger

> Table display name: Command Ledger. Plural name: Command Ledger Entries. Schema name: `cca_commandledger`. Description: Idempotency ledger for workflow mutations and replay-safe responses. Primary name: Command Name, schema name `cca_commandname`.
>
> Add these columns: Idempotency Key (`cca_idempotencykey`), required text maximum 200; Command (`cca_command`), required text maximum 150; Request Hash (`cca_requesthash`), text maximum 128; Result JSON (`cca_resultjson`), multiline text; Outcome (`cca_outcome`), choice with Succeeded, NeedsInput, Held, Rejected, Conflict; Actor (`cca_actor`), text maximum 320; Correlation ID (`cca_correlationid`), text maximum 100; Completed At (`cca_completedat`), date and time.
>
> Create alternate key Idempotency Key (`cca_idempotencykeykey`) using Idempotency Key.

## 13. Audit Event

> Table display name: Audit Event. Plural name: Audit Events. Schema name: `cca_auditevent`. Description: Append-only material workflow operation and state transition record. Primary name: Event Name, schema name `cca_eventname`.
>
> Add these columns: Audit Event ID (`cca_auditeventbusinessid`), required text maximum 100; Operation (`cca_operation`), required text maximum 150; Before State (`cca_beforestate`), text maximum 100; After State (`cca_afterstate`), text maximum 100; Before Version (`cca_beforeversion`), whole number minimum 0; After Version (`cca_afterversion`), whole number minimum 0; Actor (`cca_actor`), text maximum 320; Correlation ID (`cca_correlationid`), text maximum 100; Request Hash (`cca_requesthash`), text maximum 128; Event At (`cca_eventat`), date and time; Details JSON (`cca_detailsjson`), multiline text.
>
> Create alternate key Audit Event ID Key (`cca_auditeventidkey`) using Audit Event ID.

## Relationship creation

> [!IMPORTANT]
> Do not use the Copilot data-workspace prompt for these relationships after the tables have been created. Power Apps does not support creating a relationship between two existing tables in that workspace. The error "Please reenter the query and ensure the relevant table names are also specified" can occur even when both table names are present.
>
> Create each relationship manually in Power Apps: open the child table, select **Relationships** > **New relationship** > **Many-to-one**, and select the related parent table. Then open the generated lookup column and relationship to apply the display name, schema name, requiredness, and behavior specified below. Save and publish after each relationship. For every relationship, use **Referential, Restrict Delete** with no cascading assign, share, unshare, merge, or reparent.

### Inventory Source

> Create a relationship between Inventory Source (`cca_inventorysource`) and Valuation Case (`cca_valuationcase`). Use a Many-to-one relationship with Inventory Source as the child table and Valuation Case as the parent table. Lookup display name: Valuation Case. Lookup schema name: `cca_valuationcaseid`. Requiredness: Business Required. Relationship schema name: `cca_valuationcase_inventorysource`.

### Inventory Item

> Create a relationship between Inventory Item (`cca_inventoryitem`) and Valuation Case (`cca_valuationcase`). Use a Many-to-one relationship with Inventory Item as the child table and Valuation Case as the parent table. Lookup display name: Valuation Case. Lookup schema name: `cca_valuationcaseid`. Requiredness: Business Required. Relationship schema name: `cca_valuationcase_inventoryitem`.
>
> Create a relationship between Inventory Item (`cca_inventoryitem`) and Inventory Source (`cca_inventorysource`). Use a Many-to-one relationship with Inventory Item as the child table and Inventory Source as the parent table. Lookup display name: Inventory Source. Lookup schema name: `cca_inventorysourceid`. Requiredness: Business Required. Relationship schema name: `cca_inventorysource_inventoryitem`.

### Comparator Evidence

> Create a relationship between Comparator Evidence (`cca_comparatorevidence`) and Valuation Case (`cca_valuationcase`). Use a Many-to-one relationship with Comparator Evidence as the child table and Valuation Case as the parent table. Lookup display name: Valuation Case. Lookup schema name: `cca_valuationcaseid`. Requiredness: Business Required. Relationship schema name: `cca_valuationcase_comparatorevidence`.
>
> Create a relationship between Comparator Evidence (`cca_comparatorevidence`) and Inventory Item (`cca_inventoryitem`). Use a Many-to-one relationship with Comparator Evidence as the child table and Inventory Item as the parent table. Lookup display name: Inventory Item. Lookup schema name: `cca_inventoryitemid`. Requiredness: Business Required. Relationship schema name: `cca_inventoryitem_comparatorevidence`.

### Calculation Run

> Create a relationship between Calculation Run (`cca_calculationrun`) and Valuation Case (`cca_valuationcase`). Use a Many-to-one relationship with Calculation Run as the child table and Valuation Case as the parent table. Lookup display name: Valuation Case. Lookup schema name: `cca_valuationcaseid`. Requiredness: Business Required. Relationship schema name: `cca_valuationcase_calculationrun`.

### Item Valuation

> Create a relationship between Item Valuation (`cca_itemvaluation`) and Valuation Case (`cca_valuationcase`). Use a Many-to-one relationship with Item Valuation as the child table and Valuation Case as the parent table. Lookup display name: Valuation Case. Lookup schema name: `cca_valuationcaseid`. Requiredness: Business Required. Relationship schema name: `cca_valuationcase_itemvaluation`.
>
> Create a relationship between Item Valuation (`cca_itemvaluation`) and Inventory Item (`cca_inventoryitem`). Use a Many-to-one relationship with Item Valuation as the child table and Inventory Item as the parent table. Lookup display name: Inventory Item. Lookup schema name: `cca_inventoryitemid`. Requiredness: Business Required. Relationship schema name: `cca_inventoryitem_itemvaluation`.
>
> Create a relationship between Item Valuation (`cca_itemvaluation`) and Calculation Run (`cca_calculationrun`). Use a Many-to-one relationship with Item Valuation as the child table and Calculation Run as the parent table. Lookup display name: Calculation Run. Lookup schema name: `cca_calculationrunid`. Requiredness: Business Required. Relationship schema name: `cca_calculationrun_itemvaluation`.

### Case Issue

> Create a relationship between Case Issue (`cca_caseissue`) and Valuation Case (`cca_valuationcase`). Use a Many-to-one relationship with Case Issue as the child table and Valuation Case as the parent table. Lookup display name: Valuation Case. Lookup schema name: `cca_valuationcaseid`. Requiredness: Business Required. Relationship schema name: `cca_valuationcase_caseissue`.
>
> Create a relationship between Case Issue (`cca_caseissue`) and Inventory Item (`cca_inventoryitem`). Use a Many-to-one relationship with Case Issue as the child table and Inventory Item as the parent table. Lookup display name: Inventory Item. Lookup schema name: `cca_inventoryitemid`. Requiredness: Optional. Relationship schema name: `cca_inventoryitem_caseissue`.

### Package Artifact

> Create a relationship between Package Artifact (`cca_packageartifact`) and Valuation Case (`cca_valuationcase`). Use a Many-to-one relationship with Package Artifact as the child table and Valuation Case as the parent table. Lookup display name: Valuation Case. Lookup schema name: `cca_valuationcaseid`. Requiredness: Business Required. Relationship schema name: `cca_valuationcase_packageartifact`.
>
> Create a relationship between Package Artifact (`cca_packageartifact`) and Calculation Run (`cca_calculationrun`). Use a Many-to-one relationship with Package Artifact as the child table and Calculation Run as the parent table. Lookup display name: Calculation Run. Lookup schema name: `cca_calculationrunidlookup`. Requiredness: Business Required. Relationship schema name: `cca_calculationrun_packageartifact`.

### Decision Challenge

> Create a relationship between Decision Challenge (`cca_decisionchallenge`) and Valuation Case (`cca_valuationcase`). Use a Many-to-one relationship with Decision Challenge as the child table and Valuation Case as the parent table. Lookup display name: Valuation Case. Lookup schema name: `cca_valuationcaseid`. Requiredness: Business Required. Relationship schema name: `cca_valuationcase_decisionchallenge`.
>
> Create a relationship between Decision Challenge (`cca_decisionchallenge`) and Package Artifact (`cca_packageartifact`). Use a Many-to-one relationship with Decision Challenge as the child table and Package Artifact as the parent table. Lookup display name: Package Artifact. Lookup schema name: `cca_packageartifactid`. Requiredness: Business Required. Relationship schema name: `cca_packageartifact_decisionchallenge`.

### Approval

> Create a relationship between Approval (`cca_approval`) and Valuation Case (`cca_valuationcase`). Use a Many-to-one relationship with Approval as the child table and Valuation Case as the parent table. Lookup display name: Valuation Case. Lookup schema name: `cca_valuationcaseid`. Requiredness: Business Required. Relationship schema name: `cca_valuationcase_approval`.
>
> Create a relationship between Approval (`cca_approval`) and Package Artifact (`cca_packageartifact`). Use a Many-to-one relationship with Approval as the child table and Package Artifact as the parent table. Lookup display name: Package Artifact. Lookup schema name: `cca_packageartifactid`. Requiredness: Business Required. Relationship schema name: `cca_packageartifact_approval`.
>
> Create a relationship between Approval (`cca_approval`) and Decision Challenge (`cca_decisionchallenge`). Use a Many-to-one relationship with Approval as the child table and Decision Challenge as the parent table. Lookup display name: Decision Challenge. Lookup schema name: `cca_decisionchallengeid`. Requiredness: Business Required. Relationship schema name: `cca_decisionchallenge_approval`. Do not use `cca_approvalid`; it is Approval's primary key.

### Command Ledger

> Create a relationship between Command Ledger (`cca_commandledger`) and Valuation Case (`cca_valuationcase`). Use a Many-to-one relationship with Command Ledger as the child table and Valuation Case as the parent table. Lookup display name: Valuation Case. Lookup schema name: `cca_valuationcaseid`. Requiredness: Business Required. Relationship schema name: `cca_valuationcase_commandledger`.

### Audit Event

> Create a relationship between Audit Event (`cca_auditevent`) and Valuation Case (`cca_valuationcase`). Use a Many-to-one relationship with Audit Event as the child table and Valuation Case as the parent table. Lookup display name: Valuation Case. Lookup schema name: `cca_valuationcaseid`. Requiredness: Business Required. Relationship schema name: `cca_valuationcase_auditevent`.

## Verification prompt

> Review the generated Dataverse model without changing it. Confirm that it contains exactly 13 custom tables with prefix `cca`, 158 non-lookup custom columns, 13 alternate keys, and 20 many-to-one relationships. Confirm there are no item-photo, data-tag-photo, or receipt-photo columns. List every missing, renamed, duplicated, or incorrectly typed component. Pay special attention to required columns, choice value order, decimal precision, file size limits, lookup requiredness, and schema names. Do not create sample data.

Copilot can ignore or reinterpret advanced settings. Verify schema names, alternate keys, relationship behavior, auditing, change tracking, notes, and optimistic concurrency in the table designer before using the model.
