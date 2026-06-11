"""End-to-end tests for the Administrative AI Agent (mock mode, no AWS)."""
from __future__ import annotations

from pathlib import Path

import pytest

from admin_agent.config import Settings
from admin_agent.ingestion import load_transcript
from admin_agent.pipeline import process_meeting
from admin_agent.repository import SqliteActionRegistry

SAMPLE = Path(__file__).resolve().parents[1] / "samples" / "sample_meeting.vtt"


def _mock_settings(tmp_path: Path) -> Settings:
    return Settings(
        mock_mode=True,
        registry_backend="sqlite",
        sqlite_path=str(tmp_path / "test.db"),
        output_location=str(tmp_path / "out"),
    )


def test_load_transcript_strips_vtt_metadata() -> None:
    text = load_transcript(SAMPLE)
    assert "WEBVTT" not in text
    assert "-->" not in text
    assert "Bedrock" in text


def test_pipeline_extracts_actions_and_writes_artifacts(tmp_path: Path) -> None:
    settings = _mock_settings(tmp_path)
    outputs, written = process_meeting(str(SAMPLE), settings=settings)

    # Actions were extracted
    assert len(outputs.actions) >= 3
    owners = {a.owner for a in outputs.actions}
    assert {"David", "Sarah", "Marcus"} & owners

    # At least one due date resolved, and an urgent item flagged High
    assert any(a.due_date for a in outputs.actions)
    assert any(a.priority == "High" for a in outputs.actions)

    # Artifacts written
    for name in ("minutes.md", "summary.txt", "actions.json"):
        assert any(name in key for key in written), f"missing {name}"
    assert all(Path(p).exists() for p in written.values())


def test_actions_persisted_to_register(tmp_path: Path) -> None:
    settings = _mock_settings(tmp_path)
    process_meeting(str(SAMPLE), settings=settings)

    registry = SqliteActionRegistry(settings.sqlite_path)
    stored = registry.list_actions()
    assert len(stored) >= 3
    assert all(row["action_id"].startswith("ACT-") for row in stored)


def test_unsupported_file_type_raises(tmp_path: Path) -> None:
    bad = tmp_path / "recording.mp4"
    bad.write_bytes(b"\x00")
    with pytest.raises(ValueError):
        load_transcript(bad)
