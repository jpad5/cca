# UploadInventorySource workflow

Build this workflow in the Copilot Studio visual designer. Do not create a local
`workflow.json` file.

## Security prerequisite

Use run-only-user Dataverse and Office 365 Users connections. Permit only approved
business connectors under the environment DLP policy. Derive caller identity in the
workflow and verify case assignment before accessing the attachment.

## Trigger

Use **When an agent calls the flow** with required `caseId` (Text),
`expectedVersion` (Number), `idempotencyKey` (Text), `inventoryFile` (File input),
`replaceExisting` (Boolean), and `classification` (Text).

## Response

Use **Respond to the agent** with **Asynchronous response** set to **Off** for a
synchronous response with all common outputs from
[README.md](README.md). Return only opaque source IDs and sanitized metadata in
`artifacts` and `authoritativeValues`; there must be no returned bytes or inventory
content.

## Designer actions

1. Initialize a correlation ID and derive normalized caller email.
2. Validate all required inputs before reading file content. Accept only `Approved`
   or `Restricted` classification; fail closed for `Unknown`, `Prohibited`, or any
   unrecognized value.
3. Query `Command Ledger`; replay only an exact matching request by the same caller,
   and reject changed key reuse.
4. Get the case, verify Assigned Adjuster, state `CaseReady`, and exact Case Version.
   Return `Rejected` or `Conflict` without mutation when a gate fails.
5. List current `Inventory Source` rows. If one exists and `replaceExisting` is
   false, return `NeedsInput` with issue `REPLACEMENT_CONFIRMATION_REQUIRED`.
6. Validate the original file name, permitted `.xlsx` or `.csv` extension, MIME type,
   and configured size limit before writing a row. Reject macro-enabled workbooks and
   mismatched extension/MIME combinations.
7. Calculate a SHA-256 content hash with an approved built-in action. Do not use file
   name or size as a hash substitute. Generate `SourceVersionId` with `guid()`.
8. Detect item-photo, data-tag-photo, or receipt-photo content where connector
   metadata permits. Record `PresentExcluded`; never extract or use those images.
9. Create an immutable `Inventory Source` row related to the case with source ID,
   hash, sanitized name, MIME type, size, classification, photo status, file value,
   and Is Immutable `true`.
10. Update the case to `InventoryAccepted`, increment Case Version, and set Checkpoint
    `UploadInventorySource` in a guarded scope.
11. Write `Command Ledger` and `Audit Event` rows without file bytes or item contents.
12. Respond `Succeeded` with the opaque source version ID, hash, sanitized metadata,
    persisted state, and version.

Validation failures set the case to `HeldFileInvalid` only after assignment, state,
and version gates pass; increment once and record a typed `Case Issue`, ledger entry,
and audit event. Connector/transient failures return a retryable issue without
duplicating a source row.

## Tool configuration

> Accepts the current attachment for a CaseReady valuation case, validates its
> classification and file controls, and stores an immutable source version. Requires
> explicit replacement intent and never returns file bytes or inventory contents.

## Acceptance tests

1. Missing file or replacement confirmation returns `NeedsInput` without a source.
2. Invalid classification/type/MIME/size enters HeldFileInvalid with a typed issue.
3. A valid file creates one immutable source and advances to InventoryAccepted.
4. Photos are marked excluded and are not extracted or returned.
5. Wrong assignment is rejected; stale state/version returns `Conflict`.
6. Exact retries replay without duplicate rows; changed key reuse is rejected.
7. The workflow completes in under 100 seconds and responds synchronously.
