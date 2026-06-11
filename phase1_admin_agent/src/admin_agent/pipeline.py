"""End-to-end orchestration for the Administrative AI Agent.

    transcript file -> clean text -> extract actions -> minutes & summary
                     -> persist actions -> write artifacts
"""
from __future__ import annotations

import json
from pathlib import Path

from .config import Settings, load_settings
from .extraction import extract_actions
from .ingestion import load_transcript
from .minutes import generate_minutes
from .models import MeetingMetadata, MeetingOutputs
from .repository import build_registry


def _write_outputs(outputs: MeetingOutputs, settings: Settings) -> dict[str, str]:
    """Write minutes (.md), summary (.txt) and actions (.json). Local or S3."""
    mid = outputs.metadata.meeting_id
    files = {
        f"{mid}_minutes.md": outputs.minutes_markdown,
        f"{mid}_summary.txt": outputs.summary,
        f"{mid}_actions.json": json.dumps(
            [a.to_dict() for a in outputs.actions], indent=2
        ),
    }

    if settings.output_is_s3:
        import boto3  # lazy import

        _, _, rest = settings.output_location.partition("s3://")
        bucket, _, prefix = rest.partition("/")
        s3 = boto3.client("s3", region_name=settings.aws_region)
        written = {}
        for name, body in files.items():
            key = f"{prefix.rstrip('/')}/{name}" if prefix else name
            s3.put_object(Bucket=bucket, Key=key, Body=body.encode("utf-8"))
            written[name] = f"s3://{bucket}/{key}"
        return written

    out_dir = Path(settings.output_location)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = {}
    for name, body in files.items():
        path = out_dir / name
        path.write_text(body, encoding="utf-8")
        written[name] = str(path)
    return written



def process_meeting(
    transcript_path: str,
    *,
    title: str | None = None,
    meeting_date: str | None = None,
    attendees: list[str] | None = None,
    settings: Settings | None = None,
) -> tuple[MeetingOutputs, dict[str, str]]:
    """Run the full pipeline for a single transcript file.

    Returns the produced :class:`MeetingOutputs` and a map of artifact name ->
    location (local path or S3 URI).
    """
    settings = settings or load_settings()

    transcript = load_transcript(transcript_path)

    metadata = MeetingMetadata(
        title=title or Path(transcript_path).stem.replace("_", " ").title(),
        source_file=str(transcript_path),
    )
    if meeting_date:
        metadata.meeting_date = meeting_date
    if attendees:
        metadata.attendees = attendees

    actions = extract_actions(transcript, metadata, settings)
    summary, minutes_md = generate_minutes(transcript, metadata, actions, settings)

    outputs = MeetingOutputs(
        metadata=metadata,
        summary=summary,
        minutes_markdown=minutes_md,
        actions=actions,
    )

    registry = build_registry(settings)
    registry.save_actions(actions)

    written = _write_outputs(outputs, settings)
    return outputs, written
