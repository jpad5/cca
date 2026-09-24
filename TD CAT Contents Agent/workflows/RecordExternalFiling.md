# RecordExternalFiling workflow

Build this workflow in the Copilot Studio visual designer. Do not create a local
`workflow.json` file.

## Security prerequisite

Use run-only-user Dataverse and Office 365 Users connections. This workflow records
evidence only; enforce Assigned Adjuster assignment. There is no claims-system write:
it must not connect to or write into an external claims system.
This is the mandatory Assignment check.

## Trigger

Use **When an agent calls the flow** with required `caseId` (Text),
`expectedVersion` (Number), `idempotencyKey` (Text), `externalReference` (Text),
`filedAt` (Text ISO 8601), and `evidenceReference` (Text).

## Response

Use **Respond to the agent** with **Asynchronous response** set to **Off** for a
synchronous response with all common outputs and sanitized filing references.

## Designer actions

1. Derive correlation/caller values; validate nonempty references and filed-at date.
2. Apply standard `Command Ledger` replay/reuse checks.
3. Get the case and enforce assignment, state `Approved`, and expected Case Version.
   Return `Conflict` without writes when stale.
4. Verify the current immutable Approval and package binding remain valid.
5. Persist the external reference, filing time, and evidence reference in the case
   checkpoint or governed filing record. Do not call an external claims API.
6. Set state `ExternallyFiled`, increment Case Version, and write `Command Ledger`
   and `Audit Event` rows with filing metadata but no external document content.
7. Respond `Succeeded` and state clearly that external filing evidence was recorded,
   not that the agent filed or paid the claim.

## Tool configuration

> Records adjuster-supplied evidence that an Approved valuation was manually filed in
> an external process. It never writes to the claims system or represents payment.

## Acceptance tests

1. Missing/invalid filing evidence returns `NeedsInput` without mutation.
2. Only an Approved case with a valid current approval can advance.
3. No external claims-system connector or write is invoked.
4. Stale state/version returns `Conflict`; wrong assignment is rejected.
5. Exact retries replay without duplicate filing history.
6. The workflow completes in under 100 seconds and responds synchronously.
