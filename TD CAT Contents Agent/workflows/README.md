# GHCP Workflow Build Specification

Build these capabilities in **Copilot Studio > Workflows** using the GitHub Copilot harness. They are native GHCP Workflows, not Power Automate Agent Flows, custom APIs, or authored business topics.

Every workflow used by the agent must:

- Start with **When an agent calls the flow**.
- End with **Respond to the agent**.
- Have **Asynchronous response** set to **Off**.
- Complete in less than 100 seconds.
- Be published before it is added under **TD CAT Contents Agent > Tools > Workflows**.
- Use the authenticated caller and Dataverse connector actions.
- Return `outcome`, `caseId`, `caseVersion`, `state`, `missingFields`, `issues`, `artifacts`, and `displaySummary`.
- Check the expected case state and row version before mutation.
- Return `Conflict` without mutation when the stage or version is stale.

## Shared conventions

All mutating workflows accept `caseId`, `expectedVersion`, and `idempotencyKey`. Generate correlation and audit identifiers inside the workflow. Store completed idempotency keys in `Command Ledger`; when a key already exists, return its stored result.

Use these fixed outcome values:

- `Succeeded`
- `NeedsInput`
- `Held`
- `Rejected`
- `Conflict`

Use these persisted case states:

`Candidate`, `EligibilityConfirmed`, `AccessAuthorized`, `CaseReady`, `InventoryAccepted`, `InventoryReview`, `InventoryComplete`, `ResearchComplete`, `RulesResolved`, `Calculated`, `QualityPassed`, `PackageReady`, `PendingApproval`, `Approved`, `ExternallyFiled`, `Closed`, `StoppedOutsideMvp`, `StoppedDataProhibited`, `HeldFileInvalid`, `HeldInventoryIncomplete`, `HeldRulesUnavailable`, `HeldQualityException`, `HeldAdjuster`, `OpenExternal`.

## Workflow catalog

### 1. Open or resume valuation case

**Tool name:** `OpenValuationCase`

**Inputs:** `claimId` (text, required)

**Steps:**

1. Read the current caller identity.
2. Find the assigned `Valuation Case` by claim ID.
3. If found, verify assignment and return its current state and version.
4. If absent, verify licensed-adjuster access and create the case in `Candidate` state.
5. Write an `Audit Event`.

**Outputs:** Common response plus `isNewCase`.

### 2. Confirm eligibility

**Tool name:** `ConfirmMvpEligibility`

**Required state:** `Candidate`

**Inputs:** Common mutation inputs, `isEligible` (boolean), `recommendationOnlyAttestation` (boolean), `eligibilityReason` (text)

**Steps:** Validate assignment and row version. If either boolean is false, set `StoppedOutsideMvp`; otherwise set `EligibilityConfirmed`. Write command and audit records.

### 3. Authorize case data

**Tool name:** `AuthorizeCaseData`

**Required state:** `EligibilityConfirmed`

**Inputs:** Common mutation inputs, `classification` (choice)

**Steps:** Allow only approved classification values. Missing, unknown, or prohibited values set `StoppedDataProhibited`; approved values set `AccessAuthorized`.

### 4. Confirm claim facts

**Tool name:** `ConfirmClaimFacts`

**Required state:** `AccessAuthorized`

**Inputs:** Common mutation inputs, `province`, `lossDate`, `coverageCodes`, `endorsementCodes`, `contentsLimit`, `currency`

**Steps:** Validate required fields and Canadian jurisdiction. Return `NeedsInput` without mutation when fields are missing. Persist confirmed facts and set `CaseReady`.

### 5. Upload inventory source

**Tool name:** `UploadInventorySource`

**Required state:** `CaseReady`

**Inputs:** Common mutation inputs, `inventoryFile` (file), `replaceExisting` (boolean), `classification` (choice)

**Steps:**

1. Verify assignment and permitted classification.
2. Validate filename, extension, MIME type, configured size limit, and replacement intent.
3. Calculate or obtain a content hash using an available built-in data operation.
4. Create an immutable `Inventory Source` row and Dataverse file value.
5. Set `InventoryAccepted`; otherwise set `HeldFileInvalid` with an issue.

Do not return file bytes or inventory contents to the agent.

### 6. Parse and validate inventory

**Tool name:** `ValidateAndParseInventory`

**Required state:** `InventoryAccepted`

**Inputs:** Common mutation inputs, `sourceVersionId`

**Steps:** Read the approved workbook or CSV with native Excel/CSV and data operations, preserve original row JSON, create normalized `Inventory Item` rows, detect missing material fields and duplicate keys, then set `InventoryReview`. Keep the workflow below 100 seconds by processing a bounded batch and return `continuationRequired` when more rows remain.

### 7. Resolve inventory issues

**Tool name:** `SubmitInventoryResolution`

**Required state:** `InventoryReview` or `HeldInventoryIncomplete`

**Inputs:** Common mutation inputs, `itemId`, `itemVersion`, `resolution` (choice), `correctedValues` (object), `reason`

**Steps:** Apply one versioned correction, duplicate decision, or hold. Recheck unresolved material issues. Set `InventoryComplete` only when none remain; otherwise retain `InventoryReview`.

### 8. Research approved replacement sources

**Tool name:** `RunApprovedResearch`

**Required state:** `InventoryComplete`

**Inputs:** Common mutation inputs, `inventoryVersion`, `batchCursor`

**Steps:** Use only approved native connector or AI actions configured in the workflow. Restrict sources to the approved Canadian allowlist table. Store source, retrieval time, evidence text, price, currency, qualification code, and snapshot reference. Use bounded batches and return a cursor when necessary. Set `ResearchComplete` only when all items have qualified evidence or an explicitly flagged generic estimate.

### 9. Resolve valuation rules

**Tool name:** `ResolveValuationRules`

**Required state:** `ResearchComplete`

**Inputs:** Common mutation inputs

**Steps:** Query immutable approved `Rule Set Version` rows by province, loss date, coverage, and endorsements. Set `RulesResolved` with the exact version and hash, or `HeldRulesUnavailable` when no single approved match exists.

### 10. Run deterministic valuation

**Tool name:** `RunDeterministicValuation`

**Required state:** `RulesResolved`

**Inputs:** Common mutation inputs, `inventoryVersion`, `evidenceVersion`, `ruleSetVersion`

**Steps:** Use workflow expressions and decimal variables only. Calculate RCV, depreciation, taxes, ACV, limits, payable recommendation, and rounding from persisted typed values. Store item and case totals with input versions. Never use an AI action for arithmetic. Set `Calculated`.

### 11. Run quality gates

**Tool name:** `RunValuationQualityGates`

**Required state:** `Calculated`

**Inputs:** Common mutation inputs, `calculationRunId`

**Steps:** Reconcile item and case totals; check limits, evidence, specialty/high-value flags, nonnegative values, rounding, and version consistency. Set `QualityPassed` or `HeldQualityException` and create typed issues.

### 12. Resolve valuation exception

**Tool name:** `ResolveValuationException`

**Required state:** A supported hold state

**Inputs:** Common mutation inputs, `issueId`, `resolutionCode`, `reason`, `changedValues`

**Steps:** Record the licensed adjuster's decision. Invalidate dependent evidence, calculations, packages, approvals, and challenges. Set the earliest stage that must rerun.

### 13. Generate valuation package

**Tool name:** `GenerateValuationPackage`

**Required state:** `QualityPassed`

**Inputs:** Common mutation inputs, exact inventory, evidence, rules, and calculation version IDs

**Steps:** Populate an approved macro-free Excel template using Excel Online actions, create a calculation trace file, record hashes and versions in `Package Artifact`, and set `PackageReady`. Return opaque artifact references only.

### 14. Prepare package decision

**Tool name:** `PreparePackageDecision`

**Required state:** `PackageReady`

**Inputs:** Common mutation inputs, `packageId`, `packageVersion`, `packageHash`

**Steps:** Revalidate package bindings, create a short-lived single-use `Decision Challenge` bound to caller, case version, package version, and hash, then set `PendingApproval`.

**Outputs:** Common response plus review summary, challenge ID, expiry, and immutable package binding.

### 15. Submit package decision

**Tool name:** `SubmitPackageDecision`

**Required state:** `PendingApproval`

**Inputs:** Common mutation inputs, `challengeId`, immutable package binding, `decision` (single choice: `Approve`, `Reject`, `Hold`), `attestation` (boolean), `reasonCode`, `rationale`

**Steps:** Reject free-text or missing decisions. Validate caller, assignment, authority, challenge expiry, one-time use, case version, and package hash. Mark the challenge consumed. Set `Approved`, `HeldAdjuster`, or the configured correction state and write the immutable approval record.

### 16. Record external filing

**Tool name:** `RecordExternalFiling`

**Required state:** `Approved`

**Inputs:** Common mutation inputs, `externalReference`, `filedAt`, `evidenceReference`

**Steps:** Record the adjuster's manual filing evidence and set `ExternallyFiled`. This workflow does not write to the claims system.

### 17. Record external claim status

**Tool name:** `RecordExternalClaimStatus`

**Required state:** `ExternallyFiled` or `OpenExternal`

**Inputs:** Common mutation inputs, `externalStatus` (choice), `confirmedAt`, `evidenceReference`

**Steps:** Set `OpenExternal` for open or held claims. Set `Closed` only for closed or completed status with evidence. Write closure audit and retention metadata.

## Dataverse tables

Create these tables in the **TD CAT Contents Agent** solution before building workflows. Use the complete column, key, choice, and relationship blueprint in [`../../dataverse/README.md`](../../dataverse/README.md).

- `Valuation Case`
- `Inventory Source`
- `Inventory Item`
- `Comparator Evidence`
- `Rule Set Version`
- `Calculation Run`
- `Case Issue`
- `Package Artifact`
- `Decision Challenge`
- `Approval`
- `Command Ledger`
- `Audit Event`

Use row ownership, licensed-adjuster security roles, province/assignment checks, alternate keys for idempotency, optimistic concurrency, file columns for artifacts, and choice columns for states and decisions.

## Build and test order

1. Build the Dataverse tables and security model in the same solution.
2. Create workflows 1-4 and test case setup and authorization.
3. Create workflows 5-7 and test file intake plus correction loops.
4. Create workflows 8-12 and test research, calculation, gates, and invalidation.
5. Create workflows 13-17 and test packaging, explicit approval, filing, and closure.
6. Publish each error-free workflow.
7. Add each workflow to **TD CAT Contents Agent > Tools > Workflows**.
8. Give every tool a precise stage-oriented description.
9. Upload the three `skills/<name>/SKILL.md` files under **Build > Skills**.
10. Test individual nodes, full workflows, Skill activation, then the agent's **Preview** chat.

## Platform constraints

- Workflow authoring is performed in the Copilot Studio visual designer; do not hand-author `workflow.json` files.
- Only published synchronous workflows with both required agent trigger/response nodes appear as tools.
- A workflow must respond within 100 seconds. Split or batch long inventory and research operations.
- Test runs from the workflow designer and embedded agent test chat don't consume workflow capacity.

References:

- [Workflows overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/workflows-experience/flows-overview)
- [Add a workflow as an agent tool](https://learn.microsoft.com/en-us/microsoft-copilot-studio/workflows-experience/flow-agent)
- [Workflow designer and testing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/workflows-experience/flow-designer)
- [Skills overview for agents](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-overview)
- [Add an existing skill to an agent](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-add-existing)
