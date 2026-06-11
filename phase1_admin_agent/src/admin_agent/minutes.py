"""Generate meeting minutes and a summary from a transcript.

Uses Amazon Bedrock for high-quality narrative output. In mock mode, builds a
structured Markdown document deterministically from the transcript and the
already-extracted action items.
"""
from __future__ import annotations

import textwrap

from .config import Settings
from .models import ActionItem, MeetingMetadata

_SUMMARY_INSTRUCTIONS = """\
Summarise the following meeting transcript in 4-6 concise sentences. Focus on
decisions made, key discussion points and outcomes. Return plain text only.
"""


def _render_actions_table(actions: list[ActionItem]) -> str:
    if not actions:
        return "_No action items were identified._"
    rows = [
        "| # | Action | Owner | Due | Priority |",
        "|---|--------|-------|-----|----------|",
    ]
    for i, a in enumerate(actions, 1):
        due = a.due_date or "-"
        rows.append(f"| {i} | {a.description} | {a.owner} | {due} | {a.priority} |")
    return "\n".join(rows)


def _render_minutes(
    metadata: MeetingMetadata, summary: str, actions: list[ActionItem]
) -> str:
    attendees = ", ".join(metadata.attendees) if metadata.attendees else "Not recorded"
    return textwrap.dedent(
        f"""\
        # Meeting Minutes - {metadata.title}

        - **Date:** {metadata.meeting_date}
        - **Meeting ID:** {metadata.meeting_id}
        - **Attendees:** {attendees}

        ## Summary

        {summary}

        ## Action Items

        {_render_actions_table(actions)}
        """
    )


def generate_summary(transcript: str, settings: Settings) -> str:
    """Produce a short narrative summary of the meeting."""
    if settings.mock_mode:
        return _mock_summary(transcript)

    import boto3  # lazy import

    client = boto3.client("bedrock-runtime", region_name=settings.aws_region)
    response = client.converse(
        modelId=settings.bedrock_model_id,
        messages=[
            {
                "role": "user",
                "content": [{"text": f"{_SUMMARY_INSTRUCTIONS}\n\nTranscript:\n{transcript}"}],
            }
        ],
        inferenceConfig={"maxTokens": 500, "temperature": 0.2},
    )
    return response["output"]["message"]["content"][0]["text"].strip()


def generate_minutes(
    transcript: str,
    metadata: MeetingMetadata,
    actions: list[ActionItem],
    settings: Settings,
) -> tuple[str, str]:
    """Return ``(summary, minutes_markdown)`` for the meeting."""
    summary = generate_summary(transcript, settings)
    minutes = _render_minutes(metadata, summary, actions)
    return summary, minutes


def _mock_summary(transcript: str) -> str:
    """Deterministic summary: first few substantive sentences, capped."""
    sentences = [s.strip() for s in transcript.replace("\n", " ").split(".") if len(s.strip()) > 15]
    head = ". ".join(sentences[:4])
    if head and not head.endswith("."):
        head += "."
    return head or "Meeting transcript processed; no substantive content detected."
