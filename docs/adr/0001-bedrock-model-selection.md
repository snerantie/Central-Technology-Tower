# ADR-0001: Use Amazon Nova Lite as default Bedrock LLM

## Status
**Accepted** — 2026-06-19

## Context

The Central Technology Tower AI Agent Programme requires a Large Language
Model (LLM) across all six phases:

- **Phase 1 — Admin Agent (MVP):** extract action items, owners, due dates
  from meeting transcripts; generate minutes & summaries.
- **Phase 2 — Action Tracking:** detect overdue actions, draft reminder text.
- **Phase 3 — Governance:** detect themes/risks across SteerCo, CIO, Cyber,
  Risk, Audit forum outputs.
- **Phase 4 — Reporting:** consolidate trends and generate executive packs.
- **Phase 5 — Knowledge Agent:** Q&A over organisational memory.
- **Phase 6 — Control Tower:** orchestration logic across agents.

### Constraints
- Programme runs on AWS only — Bedrock is the primary LLM access point.
- 5-month delivery window: kickoff **17 Jun 2026** → go-live **16 Nov 2026**.
- Cost must remain manageable as usage scales across managers and meetings.
- Avoid mid-programme model migrations — architectural stability matters.
- Models must currently be supported by AWS (avoid retirement risk).

### What pushed this decision

During initial Phase 1 development we hit problems with Anthropic Claude:

1. **Model retirement velocity:** Both `anthropic.claude-3-5-sonnet-20240620-v1:0`
   and `eu.anthropic.claude-3-7-sonnet-20250219-v1:0` returned
   `ResourceNotFoundException` stating *"This model version has reached the
   end of its life"* during MVP development — two forced model migrations
   within the first few hours of using Bedrock.
2. **Onboarding friction:** Even when the model id was current, Anthropic
   models required submitting a *"use case details"* form per AWS account
   before allowing unrestricted Converse API calls, with a ~15 minute wait.
3. **Cost at scale:** Claude Sonnet 4 list price (~$3 per 1M input tokens)
   becomes a meaningful operational cost when the agent fans out across
   multiple managers, each running multiple meetings per day.

## Decision

**Default `BEDROCK_MODEL_ID` to `eu.amazon.nova-lite-v1:0`** (Amazon Nova
Lite, EU cross-region inference profile) for the entire programme.

Per-phase guidance — override `BEDROCK_MODEL_ID` env var when needed (no code
change required, since the agent uses the Bedrock Converse API, which is
shared by Nova / Claude / Mistral / Llama):

| Phase | Recommended model | Rationale |
|-------|-------------------|-----------|
| 1 — Admin Agent | Nova Lite | Extraction + structured JSON, simple summary |
| 2 — Action Tracking | Nova Lite | Short reminder text, status checks |
| 3 — Governance | Nova Lite (→ Nova Pro if quality lacking) | Theme/risk detection |
| 4 — Reporting | **Nova Pro** | Richer prose quality matters for executives |
| 5 — Knowledge Q&A | **Nova Pro** | Conversational tone for managers |
| 6 — Control Tower | Nova Lite | Routing logic only |

## Consequences

### Positive
- ~50× cheaper input tokens vs Claude Sonnet 4 (~$0.06 vs ~$3 per 1M).
- AWS-native: no vendor-specific use-case forms, single billing / IAM /
  CloudTrail integration.
- Same Converse API as alternatives — zero-cost code-level migration if a
  better model emerges.
- Lower latency than Sonnet (faster perceived agent response).
- 300K-token context window — handles long meeting transcripts in one call.
- AWS-supported, less aggressive retirement cadence than third-party Bedrock
  models historically.

### Negative
- Slightly less polished prose than Claude Sonnet for narrative output.
  Mitigated by upgrading specific phases (4, 5) to Nova Pro.
- Weaker on multi-step reasoning than dedicated reasoning models — not
  relevant for our task profile.
- Deeper coupling to the AWS ecosystem. Acceptable given the AWS-only
  programme constraint.

### Neutral
- Nova family will continue to evolve (Nova Premier, etc.). Cross-region
  inference profiles partially abstract version drift, but explicit version
  pins via `BEDROCK_MODEL_ID` remain recommended for reproducibility.

## Alternatives considered

| Alternative | Why rejected |
|-------------|--------------|
| **Anthropic Claude Sonnet 4** (initial default) | ~50× cost; use-case-form gate; Anthropic versions retiring fast on Bedrock |
| **Anthropic Claude Haiku** | Still ~4× more expensive than Nova Lite; same use-case-form requirement; no quality advantage for our tasks |
| **Mistral Small / Meta Llama 3.3 70B** | More expensive than Nova Lite, no measurable quality advantage for extraction/summary |
| **DeepSeek-R1** | Reasoning model — overkill, higher latency and cost, optimised for problems we don't have |
| **Qwen / Alibaba** | Not natively on Bedrock; would require SageMaker JumpStart or external API, adding ops complexity inconsistent with the AWS-only constraint |

## Review trigger

Re-evaluate this decision if **any** of the following occur:

- Phase 4 or 5 stakeholders report Nova Pro narrative quality is insufficient
  for executive-facing outputs.
- Nova Lite reaches end-of-life on Bedrock.
- Monthly Bedrock spend exceeds the programme operating budget threshold.
- A Bedrock-hosted model offers clearly superior price/performance and
  satisfies the AWS-native constraint.

## Related decisions

- *(Future)* ADR-0002 — Action register storage backend (DynamoDB selected —
  see `phase1_admin_agent/aws/cloudformation.yaml`).
- *(Future)* ADR-0003 — Meeting transcript ingestion pathway (manual upload +
  Outlook forwarding via Amazon SES inbound for the email path).
