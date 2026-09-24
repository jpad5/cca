# TD CAT Contents Agent

Microsoft Copilot Studio agent for orchestrating the TD CAT Contents Valuation process. The agent targets Microsoft 365 Copilot and uses integrated Microsoft Entra authentication.

## Implemented locally

- Generative orchestration instructions in `settings.mcs.yml`.
- Unrestricted web search disabled; replacement research must use approved workflows.
- Native GHCP Workflow build specification in `workflows/README.md`.
- Portable Copilot Studio Skill packages in `skills/` for task-specific orchestration guidance.
- No authored business topics or topic-based routing.

Copilot Studio owns end-to-end process orchestration. Native GHCP Workflows provide deterministic capabilities, and Dataverse stores the durable case stage and versions. Each workflow enforces its own authorization, state preconditions, concurrency, idempotency, and immutable inputs.

## Current Agent flow status

`OpenValuationCase` is built and saved as a draft in Copilot Studio. The designer
health check reports no problems. Publishing, delegated connection verification,
agent binding, and the acceptance tests in `workflows/OpenValuationCase.md` are
still pending.

## Workflow build required

GHCP Workflows are built in the Copilot Studio visual designer, not by importing an OpenAPI contract and not by hand-authoring workflow files.

1. Create the Dataverse tables and security model listed in `workflows/README.md` inside solution **TD CAT Contents Agent**.
2. In Copilot Studio, select **Workflows** and build each specified workflow.
3. Use **When an agent calls the flow** and synchronous **Respond to the agent**.
4. Test every node and workflow, correct all health-center errors, and publish it.
5. Add each published workflow under **TD CAT Contents Agent > Tools > Workflows**.
6. Upload each `skills/<name>/SKILL.md` from **Build > Skills > Add skill > Upload a skill**.
7. Test skill activation and workflow orchestration in the agent's **Preview** tab.

## Skills to add

| Skill | Activate for | Uses these GHCP Workflows |
| --- | --- | --- |
| `inventory-intake` | Uploading, replacing, validating, parsing, or correcting inventory | `OpenValuationCase`, case setup workflows, `UploadInventorySource`, `ValidateAndParseInventory`, `SubmitInventoryResolution` |
| `valuation-review` | Researching replacements, valuing contents, reviewing calculations, or resolving exceptions | `OpenValuationCase`, `RunApprovedResearch`, `ResolveValuationRules`, `RunDeterministicValuation`, `RunValuationQualityGates`, `ResolveValuationException` |
| `package-review-decision` | Generating or reviewing a package, making a decision, or recording external filing and closure | `OpenValuationCase`, `GenerateValuationPackage`, `PreparePackageDecision`, `SubmitPackageDecision`, `RecordExternalFiling`, `RecordExternalClaimStatus` |

Skills contain reusable task guidance. They don't calculate values, enforce authorization, mutate Dataverse, or replace workflows.

## Workflows to add

| Capability | GHCP Workflows |
| --- | --- |
| Case control | `OpenValuationCase`, `ConfirmMvpEligibility`, `AuthorizeCaseData`, `ConfirmClaimFacts` |
| Inventory Intake | `UploadInventorySource`, `ValidateAndParseInventory`, `SubmitInventoryResolution` |
| Research and valuation | `RunApprovedResearch`, `ResolveValuationRules`, `RunDeterministicValuation`, `RunValuationQualityGates`, `ResolveValuationException` |
| Package generation | `GenerateValuationPackage` |
| Package Review and Decision | `PreparePackageDecision`, `SubmitPackageDecision` |
| External process | `RecordExternalFiling`, `RecordExternalClaimStatus` |

## Workflow tool configuration

Configure workflow tool descriptions with the exact required case stage, inputs, success stage, hold behavior, and invalidation behavior. Copilot Studio uses those descriptions and persisted Dataverse state to select the next workflow.

For `UploadInventorySource`:

- Use a typed file input sourced from the current Microsoft 365 Copilot attachment.
- Send file content directly to the inventory workflow without including it in generated prompts or responses.
- Keep `replaceExisting` explicit; default it to `false`.
- Return only the opaque source version ID, validation outcome, issues, and sanitized metadata.

For `PreparePackageDecision`:

- Display the immutable package ID, version, hash, evidence, calculations, rules, exceptions, workbook, and trace.
- Treat the challenge as hidden workflow state, not user-editable content.

For `SubmitPackageDecision`:

- Present `decision` as fixed choices: `Approve`, `Reject`, or `Hold`.
- Require explicit attestation before invocation.
- Pass the challenge and exact package binding from `PreparePackageDecision`.
- Never populate the decision from free-form conversation.
- Require a reason code and rationale for reject, hold, and override paths.

## Security checks

- Use delegated identity or on-behalf-of authorization.
- Enforce licensed-adjuster role, province authority, and claim assignment server-side.
- Fail closed for unknown data classification or unavailable rule sets.
- Configure the environment DLP policy to allow only the Dataverse, Excel Online, and approved research connectors.
- Keep raw inventory, evidence, and financial details out of general prompt and telemetry logs.
- Reject expired, replayed, mismatched, or stale approval challenges.

## Sync and test sequence

> [!IMPORTANT]
> Create the Dataverse publisher **CAT Contents Assistant** with unique name `catcontentsassistant` and prefix `cca` before packing or importing the solution. The solution and all custom components must use this publisher.

This agent is contained in the unmanaged Power Platform solution `CATContentsAssistant` (friendly name **CAT Contents Assistant**). For this VS Code extension clone, direct `pac copilot push` can report no local changes even when the authoring overlay has changed. The verified workflow is:

```powershell
pac auth select --index <microsoft-profile-index>
pac env select --environment "https://<environment>.crm.dynamics.com/"
pac copilot pack `
  --publisher-prefix cca `
  --project-dir ".\TD CAT Contents Agent" `
  --solution-name CATContentsAssistant `
  --output-path ".\.artifacts\CATContentsAssistant.zip"
pac solution import `
  --environment "https://<environment>.crm.dynamics.com/" `
  --path ".\.artifacts\CATContentsAssistant.zip\CATContentsAssistant.zip"
```

Omit `--publish-changes` so the import updates the draft without publishing the agent to users. Refresh the agent at `copilotstudio.microsoft.com` and use the built-in test pane.

After publishing and adding GHCP Workflows in Copilot Studio, pull the agent before further local edits to obtain their metadata. Do not hand-author generated `workflow.json` files. Publishing the agent itself requires separate approval.

## Remaining implementation

- Dataverse entities, file columns, row security, command ledger, and audit events.
- Publish, bind, and acceptance-test `OpenValuationCase`.
- Build the remaining native GHCP Workflows listed in `workflows/README.md`.
- Upload and Preview validation of the Copilot Studio Skills in `skills/`.
- Approved Canadian source allowlist and immutable rule data.
- Workflow tool publication and agent binding.
- Adversarial, authorization, replay, stale-version, and resume testing.

See [the approved architecture](../docs/TD_CAT_Copilot_Studio_GHCP_Design.md) for the complete state model and acceptance criteria.
