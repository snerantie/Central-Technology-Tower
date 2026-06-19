# Central Technology Tower — Enterprise AI Agent Programme

A phased programme to automate meeting administration, action tracking, governance
intelligence, reporting and enterprise knowledge — culminating in a **Central Control
Tower** that orchestrates all agents. Built on **Amazon Web Services (AWS)**.

## Delivery Roadmap (5 months)

> Compressed to a 5-month delivery window — phases run in parallel to hit the deadline.

| Phase | Module | Timeline | Core AWS Services |
|-------|--------|----------|-------------------|
| 1 | Administrative AI Agent (MVP) | M1 | Transcribe, Bedrock, S3, DynamoDB, Lambda |
| 2 | Action Tracking Agent | M2 | EventBridge, SES/SNS, DynamoDB, Lambda |
| 3 | Governance & Forum Agent | M2–M3 | Bedrock, Bedrock Knowledge Bases, S3, Lambda |
| 4 | Reporting & Analytics Agent | M3–M4 | QuickSight, Glue, Athena, S3 |
| 5 | Enterprise Knowledge Agent | M4 | Bedrock Knowledge Bases, OpenSearch Serverless, Bedrock (RAG) |
| 6 | Central Control Tower (Orchestration) | M4–M5 | Bedrock Agents, Step Functions, API Gateway, Cognito |

**Key milestones:** MVP live (M1) · Governance insights (M3) · Knowledge Q&A (M4) · Control Tower (M5)

Cross-cutting from M1: Security & IAM, cost governance, data privacy/PII, CI/CD, human-in-the-loop review.

## Phase 1 MVP — Administrative AI Agent

The runnable Phase 1 implementation lives in [`phase1_admin_agent/`](phase1_admin_agent/).
It ingests a meeting transcript, extracts action items (owners + due dates), generates
minutes and a summary, and writes actions to a central register. Runs locally in mock
mode (no AWS) or against Amazon Bedrock + DynamoDB. See its README for usage.

## Architecture Decisions

Significant architectural decisions are captured as **ADRs** under [`docs/adr/`](docs/adr/):

- [ADR-0001 — Use Amazon Nova Lite as default Bedrock LLM](docs/adr/0001-bedrock-model-selection.md)
- [ADR-0002 — Microsoft Teams integration & automated minute distribution](docs/adr/0002-teams-integration-and-auto-distribution.md)

## Planning Artifacts

| File | Description |
|------|-------------|
| `AI_Agent_Programme_Roadmap.pptx` | Stakeholder deck: title, Gantt roadmap, AWS service mapping |
| `AI_Agent_Programme_Plan.xlsx` | Workbook: Roadmap (Gantt), Phase Plan, Detailed Tasks |
| `build_pptx.py` | Script that regenerates the PowerPoint deck |
| `build_xlsx.py` | Script that regenerates the Excel workbook |

### Regenerating the artifacts

```bash
pip install python-pptx openpyxl
python3 build_pptx.py
python3 build_xlsx.py
```
