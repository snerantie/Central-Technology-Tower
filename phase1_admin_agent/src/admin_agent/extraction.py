"""Action-item extraction using Amazon Bedrock.

Sends the transcript to a Bedrock model and asks for a structured JSON list of
actions (description, owner, due date, priority). In mock mode a deterministic
heuristic extractor is used instead, so the pipeline runs with no AWS access.
"""
from __future__ import annotations

import json
import re
from datetime import date, timedelta
from typing import Any

from .config import Settings
from .models import ActionItem, MeetingMetadata

_EXTRACTION_INSTRUCTIONS = """\
You are an assistant that extracts action items from meeting transcripts.
Return ONLY valid JSON matching this schema, with no surrounding prose:

{
  "actions": [
    {
      "description": "string - what needs to be done",
      "owner": "string - person responsible, or 'Unassigned'",
      "due_date": "string - ISO date YYYY-MM-DD, or null if none stated",
      "priority": "Low | Medium | High"
    }
  ]
}

Rules:
- Only include concrete, actionable commitments (not general discussion).
- Resolve relative dates (e.g. 'next Friday') against the meeting date when possible.
- If no owner is stated, use 'Unassigned'.
"""


def _build_prompt(transcript: str, metadata: MeetingMetadata) -> str:
    return (
        f"{_EXTRACTION_INSTRUCTIONS}\n\n"
        f"Meeting title: {metadata.title}\n"
        f"Meeting date: {metadata.meeting_date}\n\n"
        f"Transcript:\n\"\"\"\n{transcript}\n\"\"\""
    )


def _parse_actions_json(raw_text: str, meeting_id: str) -> list[ActionItem]:
    """Pull the JSON object out of a model response and build ActionItems."""
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model response")
    payload: dict[str, Any] = json.loads(match.group(0))

    actions: list[ActionItem] = []
    for item in payload.get("actions", []):
        actions.append(
            ActionItem(
                description=str(item.get("description", "")).strip(),
                owner=str(item.get("owner") or "Unassigned").strip(),
                due_date=(item.get("due_date") or None),
                priority=str(item.get("priority") or "Medium").strip(),
                source_meeting_id=meeting_id,
            )
        )
    return [a for a in actions if a.description]


def extract_actions(
    transcript: str, metadata: MeetingMetadata, settings: Settings
) -> list[ActionItem]:
    """Extract action items from a transcript."""
    if settings.mock_mode:
        return _mock_extract(transcript, metadata)

    import boto3  # lazy import

    client = boto3.client("bedrock-runtime", region_name=settings.aws_region)
    response = client.converse(
        modelId=settings.bedrock_model_id,
        messages=[{"role": "user", "content": [{"text": _build_prompt(transcript, metadata)}]}],
        inferenceConfig={"maxTokens": 2000, "temperature": 0.0},
    )
    text = response["output"]["message"]["content"][0]["text"]
    return _parse_actions_json(text, metadata.meeting_id)


# ---------------------------------------------------------------------------
# Mock extractor -- heuristic, deterministic, no network access.
# ---------------------------------------------------------------------------
_ACTION_CUES = re.compile(
    r"\b(action|todo|to-do|will|to follow up|owns?|owner|assigned to|"
    r"take(?:s)? on|responsible for|by (?:next |end of )?\w+)\b",
    re.IGNORECASE,
)
_OWNER_RE = re.compile(r"\b([A-Z][a-z]+)\s+(?:will|to|owns|takes?|is responsible)\b")
_NEXT_WEEKDAY_RE = re.compile(r"\bby\s+(?:next\s+)?(\w+day)\b", re.IGNORECASE)
_WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
# Capitalised words that look like names to the regex but are not people.
_NON_NAME_OWNERS = {
    "This", "That", "These", "Those", "We", "They", "It", "He", "She",
    "The", "There", "Action", "Let", "Lets", "Also", "Agreed", "Good",
}
# Strip a leading speaker label such as "Sarah:" or "David: Action:".
_SPEAKER_PREFIX_RE = re.compile(r"^(?:[A-Z][a-z]+:\s*)+(?:Action:\s*)?", )


def _resolve_due_date(text: str, base: date) -> str | None:
    if re.search(r"\bend of (the )?week\b", text, re.IGNORECASE):
        return (base + timedelta(days=(4 - base.weekday()) % 7)).isoformat()
    m = _NEXT_WEEKDAY_RE.search(text)
    if m:
        target = m.group(1).lower()
        if target in _WEEKDAYS:
            delta = (_WEEKDAYS.index(target) - base.weekday()) % 7 or 7
            return (base + timedelta(days=delta)).isoformat()
    return None


def _mock_extract(transcript: str, metadata: MeetingMetadata) -> list[ActionItem]:
    try:
        base = date.fromisoformat(metadata.meeting_date)
    except ValueError:
        base = date.today()

    actions: list[ActionItem] = []
    for sentence in re.split(r"(?<=[.!?])\s+|\n", transcript):
        s = sentence.strip()
        if len(s) < 8 or not _ACTION_CUES.search(s):
            continue
        # Drop leading speaker labels ("Sarah:", "David: Action:") for a clean description.
        s = _SPEAKER_PREFIX_RE.sub("", s).strip()
        owner_match = _OWNER_RE.search(s)
        owner = owner_match.group(1) if owner_match else "Unassigned"
        if owner in _NON_NAME_OWNERS:
            owner = "Unassigned"
        priority = "High" if re.search(r"\b(urgent|asap|critical|immediately)\b", s, re.I) else "Medium"
        actions.append(
            ActionItem(
                description=s.rstrip("."),
                owner=owner,
                due_date=_resolve_due_date(s, base),
                priority=priority,
                source_meeting_id=metadata.meeting_id,
            )
        )
    return actions
