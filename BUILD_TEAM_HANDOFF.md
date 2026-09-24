# CCA Build Team Handoff

## Purpose

This package contains the current implementation source and design guidance for **CCA | CAT Contents Assistant**. Build from these files rather than from older generated solution archives.

## Required publisher

> [!IMPORTANT]
> Before creating the solution or any custom component, create the Dataverse publisher **CAT Contents Assistant** with unique name `catcontentsassistant` and prefix `cca`. Schema prefixes cannot be changed after component creation.

## Current MVP baseline

- Publisher prefix: `cca`
- Dataverse tables: 13
- Non-lookup custom columns: 158
- Alternate keys: 13
- Many-to-one relationships: 20
- Inventory scope: text and numeric fields from supported PPN SOL workbooks
- Photo scope: item, data-tag, and receipt photos are excluded and recorded as `PresentExcluded`
- Decision authority: licensed adjuster; the agent operates in recommendation-only mode

MVP 2 photo-ingestion requirements are documented but not implemented.

## Current implementation status

The `OpenValuationCase` Agent flow has been built in the Copilot Studio visual
designer and passes health validation as a saved draft. It has not been published.
Delegated connection verification, agent binding, and acceptance testing remain
pending. The local workflow file is the build specification; Copilot Studio owns
the generated flow definition.

## Source of truth

| Area | File or folder |
| --- | --- |
| Machine-readable Dataverse model | `dataverse/schema.json` |
| Dataverse build guide | `dataverse/README.md` |
| Power Apps Copilot prompts | `dataverse/COPILOT_TABLE_GENERATION_PROMPT.md` |
| Deployment script | `scripts/Deploy-DataverseSchema.ps1` |
| Agent source | `TD CAT Contents Agent/` |
| Architecture and implementation | `docs/TD_CAT_Agent_Implementation_Design.md` |
| Workflow design | `docs/TD_CAT_Copilot_Studio_GHCP_Design.md` |
| Inventory workbook findings | `docs/PPN_SOL_Inventory_Schema_Review.md` |
| Business schema guide | `docs/TD_CAT_Dataverse_Schema_Business_Guide.md` |

## Recommended build order

1. Create the `CAT Contents Assistant` publisher with prefix `cca`.
2. Create the unmanaged solution `CATContentsAssistant` using that publisher.
3. Review `dataverse/README.md` and deploy or create the Dataverse schema.
4. Verify exactly 13 tables, 158 non-lookup columns, 13 alternate keys, and 20 relationships.
5. Configure auditing, change tracking, optimistic concurrency, ownership, security roles, restrict-delete relationships, retention, and legal-hold controls.
6. Build and publish the synchronous workflows described under `TD CAT Contents Agent/workflows/`.
7. Import or synchronize the agent source and its three Skills.
8. Bind only published workflow tools, then test authorization, state transitions, idempotency, calculation reproducibility, package approval, and resume behavior.
9. Confirm photo content remains excluded from MVP processing.
10. Complete security, privacy, accessibility, operational, and business acceptance gates before publishing to users.

## Packaging exclusions

This handoff intentionally excludes:

- `.artifacts/` solution archives and inspection output because they predate current schema refinements.
- Customer sample workbooks and extracted images because they may contain sensitive claim information.
- Generated Markdown conversions stored beside the customer workbooks.
- Credentials, environment-specific tokens, and authentication profiles.

## Validation completed

The schema parses successfully and has been checked for unique tables and columns, valid key references, valid relationship references, required inventory fields, three Item Valuation relationships, prefix `cca`, and absence of photo-content columns. Documentation and agent configuration report no editor diagnostics.
