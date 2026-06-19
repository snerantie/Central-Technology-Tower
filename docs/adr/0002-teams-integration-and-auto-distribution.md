# ADR-0002: Microsoft Teams integration & automated minute distribution

## Status
**Accepted** — 2026-06-19

## Context

The Phase 1 MVP (delivered 19 Jun 2026) processes a meeting transcript provided
manually and stores artifacts in S3 + DynamoDB. To meet the **organisational**
use case for the AI Agent Programme, the agent must:

1. **Trigger automatically** when a Microsoft Teams meeting ends and its
   transcript is published — no manual upload step.
2. **Distribute minutes automatically** — each action's owner receives a
   personalised email containing their action items + a link to the full
   meeting minutes.
3. **Scale across the organisation** so any employee with a Teams meeting
   benefits, not just the original developer.

### Constraints
- AWS-native programme (Bedrock + the deployed CFN stack).
- Teams data resides in Microsoft 365 — integration via Microsoft Graph API
  or Power Platform.
- 5-month delivery window — full Graph integration likely requires Entra ID
  admin consent, which can introduce delay.
- The original developer may not have authority to register an Entra ID app
  for the entire organisation; rollout strategy must accommodate that.

## Decision

Implement Teams ingestion in **two phases**, sharing the same downstream agent
pipeline:

### Phase A — Personal Pilot (within Phase 1 window)

Use **Microsoft Power Automate** to watch the developer's Teams meetings.
When a transcript is created, the flow:
1. Downloads the `.vtt` from Microsoft Graph.
2. Calls an **AWS API Gateway** endpoint (HTTPS POST with the transcript +
   meeting metadata).
3. The API Gateway invokes a Lambda that runs the existing agent pipeline
   (extract → minutes → DynamoDB → S3 → email).

No Entra ID app registration is required because Power Automate runs under
the developer's existing Microsoft 365 credentials.

### Phase B — Org-wide Rollout (Phase 2/3 window)

Once the pilot proves value, register an Entra ID application with delegated
`OnlineMeetings.Read` and `OnlineMeetingTranscript.Read.All` Microsoft Graph
scopes (admin consent required). A **scheduled AWS Lambda** polls the Graph
API every 15 minutes for new transcripts across the organisation and triggers
the same ingestion endpoint.

### Automated Minute Distribution (both phases)

For each meeting processed by the agent:

1. **Look up each action owner's email** —
   - Phase A: pre-populated DynamoDB lookup table (`ctt-user-directory`)
     mapping display name → email.
   - Phase B: Microsoft Graph user lookup by display name (delegated).
2. **Send each owner a personalised email** via **Amazon SES** containing
   their action items plus an attached or linked Markdown copy of the full
   meeting minutes.
3. **For "Unassigned" actions**, route the email to the **meeting organiser**
   as the fallback owner.
4. All outgoing email comes from a **dedicated address** (e.g. `actions@<domain>`)
   not impersonating the user.

## Consequences

### Positive
- Zero manual upload required once Phase A is live.
- Direct, personal action notifications drive adoption.
- Phase B reuses the Phase A ingestion endpoint — no rework for the agent
  pipeline itself.
- Per-owner emails create accountability and surface cross-team dependencies.

### Negative
- Phase B requires Entra ID admin consent — owned by IT/security, may delay
  org-wide rollout into Phase 2/3.
- SES needs to be moved out of sandbox for production volume.
- Owner email lookup is brittle if attendee names don't match Microsoft
  Graph display names (need name-normalisation logic).
- Increased Microsoft 365 ⇄ AWS coupling.

### Neutral
- Power Automate flow lives in the developer's M365 tenant; if they leave the
  organisation, ownership must be transferred. Phase B (Graph polling)
  removes that dependency.

## Alternatives considered

| Alternative | Why rejected |
|-------------|--------------|
| **Manual upload only** (current MVP) | Doesn't meet the "avoid manual work" requirement |
| **Outlook forward-rule for `actions@`** | Already chosen for the *email-action* path (separate from Teams meetings); doesn't capture meeting transcripts |
| **Teams Bot Framework** (bot joins meetings) | Heavy implementation, requires Teams admin policy changes, marginal benefit over Phase B |
| **Microsoft Graph webhooks (push)** instead of 15-min polling | Lower latency (~1 min vs 15 min) but webhook subscription management adds operational overhead — promote to "future enhancement" not v1 |
| **SharePoint workflow** as glue layer | More fragile than Power Automate; deprecation risk |

## Review trigger

Re-evaluate if **any** of:
- Power Automate licensing tier changes block the pilot.
- Microsoft Graph rate limits prevent org-wide polling at 15-min cadence
  (then switch to webhooks).
- Microsoft retires the relevant Graph scopes.
- Microsoft Teams launches native AI features that subsume our agent's value
  (re-scope the programme).
- Email open rates or response rates show the per-owner email is ineffective
  (consider Teams chat notifications instead via Graph).

## Related decisions
- ADR-0001 — Bedrock model selection (Nova 2 Lite).
- *(Future)* ADR-0003 — Action register access patterns for the Phase 2
  Action Tracking Agent (overdue alerts, escalation rules).
- *(Future)* ADR-0004 — User directory & email lookup strategy
  (DynamoDB vs. Graph live lookup).
