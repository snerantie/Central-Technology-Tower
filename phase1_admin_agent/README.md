# Phase 1 MVP — Administrative AI Agent

Automates meeting administration: ingest a transcript, extract **action items**
(with owners and due dates), generate **meeting minutes** and a **summary**, and
persist actions to a **central action register**.

This is the data foundation for later phases — the Action Tracking, Reporting and
Knowledge agents all consume the action register produced here.

## Pipeline

```
transcript (.vtt/.srt/.txt/.docx)
        │  ingestion
        ▼
   clean text ──► extraction (Bedrock) ──► action items
        │                                       │
        │  minutes (Bedrock)                    │ repository
        ▼                                       ▼
 minutes.md + summary.txt            action register (SQLite | DynamoDB)
```

## AWS services

| Concern | Service |
|---------|---------|
| Action extraction & summaries | **Amazon Bedrock** (Claude) |
| Recording → text | **Amazon Transcribe** |
| Action register | **Amazon DynamoDB** (local: SQLite) |
| Artifact storage | **Amazon S3** (local: filesystem) |


## Quick start (local, no AWS needed)

The agent runs in **mock mode** with deterministic, heuristic extraction so you
can demo the full pipeline without credentials.

```bash
cd phase1_admin_agent
pip install -r requirements.txt

# Process the bundled sample transcript
python -m admin_agent.cli --mock process samples/sample_meeting.vtt

# Inspect the central action register
python -m admin_agent.cli --mock list
```

Artifacts (`*_minutes.md`, `*_summary.txt`, `*_actions.json`) are written to the
`output/` directory; actions are saved to `action_register.db` (SQLite).

## Running against AWS

Set the environment (see `.env.example`) and disable mock mode:

```bash
export ADMIN_AGENT_MOCK=0
export ACTION_REGISTRY_BACKEND=dynamodb
export ADMIN_AGENT_OUTPUT=s3://my-bucket/meetings
python -m admin_agent.cli process meeting_transcript.txt
```

For recordings, transcribe first via `admin_agent.ingestion.transcribe_recording`
(Amazon Transcribe), then feed the resulting text into the pipeline.

## Configuration

All settings come from environment variables — see [`.env.example`](.env.example).

## Tests

```bash
pip install -r requirements.txt
pytest
```

## Layout

```
phase1_admin_agent/
├── src/admin_agent/
│   ├── config.py       # env-driven settings
│   ├── ingestion.py    # transcript loading + Amazon Transcribe
│   ├── extraction.py   # Bedrock action extraction (+ mock)
│   ├── minutes.py      # minutes & summary generation (+ mock)
│   ├── models.py       # ActionItem / MeetingMetadata / MeetingOutputs
│   ├── repository.py   # SQLite + DynamoDB action register
│   ├── pipeline.py     # end-to-end orchestration
│   └── cli.py          # `process` / `list` commands
├── samples/sample_meeting.vtt
├── tests/test_pipeline.py
├── requirements.txt
├── pyproject.toml
└── .env.example
```
