# Central Technology Tower — Enterprise AI Agent Programme

A phased programme to automate meeting administration, action tracking, governance
intelligence, reporting and enterprise knowledge — culminating in a **Central Control
Tower** that orchestrates all agents. Built on **Amazon Web Services (AWS)**.

## Delivery Roadmap (12 months)

| Phase | Module | Timeline | Core AWS Services |
|-------|--------|----------|-------------------|
| 1 | Administrative AI Agent (MVP) | M1–M2 | Transcribe, Bedrock, S3, DynamoDB, Lambda |
| 2 | Action Tracking Agent | M3 | EventBridge, SES/SNS, DynamoDB, Lambda |
| 3 | Governance & Forum Agent | M4–M5 | Bedrock, Bedrock Knowledge Bases, S3, Lambda |
| 4 | Reporting & Analytics Agent | M6–M7 | QuickSight, Glue, Athena, S3 |
| 5 | Enterprise Knowledge Agent | M8–M9 | Bedrock Knowledge Bases, OpenSearch Serverless, Bedrock (RAG) |
| 6 | Central Control Tower (Orchestration) | M10–M12 | Bedrock Agents, Step Functions, API Gateway, Cognito |

**Key milestones:** MVP live (M2) · Governance insights (M5) · Knowledge Q&A (M9) · Control Tower (M12)

Cross-cutting from M1: Security & IAM, cost governance, data privacy/PII, CI/CD, human-in-the-loop review.

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
