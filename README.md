# CCA | CAT Contents Assistant

Customer-facing implementation artifacts and build guidance for the CAT Contents Assistant MVP.

## Start here

- [Build team handoff](BUILD_TEAM_HANDOFF.md)
- [Dataverse build guide](dataverse/README.md)
- [Business schema guide](docs/TD_CAT_Dataverse_Schema_Business_Guide.md)
- [Agent implementation design](docs/TD_CAT_Agent_Implementation_Design.md)
- [Copilot Studio design](docs/TD_CAT_Copilot_Studio_GHCP_Design.md)
- [Agent source and deployment guidance](TD%20CAT%20Contents%20Agent/README.md)
- [Workflow catalog](TD%20CAT%20Contents%20Agent/workflows/README.md)
- [OpenValuationCase build specification](TD%20CAT%20Contents%20Agent/workflows/OpenValuationCase.md)
- [Process diagram](TD_CAT_Contents_BPMN_Flow.svg)

## Current status

The Dataverse schema and agent source are included. The `OpenValuationCase` Agent flow has been built in Copilot Studio and passes designer health validation as a draft. Publishing, agent binding, delegated connection verification, and acceptance testing remain pending.

## Package boundaries

This repository intentionally excludes customer claim workbooks, extracted images, credentials, environment-specific tokens, Dataverse backups, generated solution archives, and local inspection output.
