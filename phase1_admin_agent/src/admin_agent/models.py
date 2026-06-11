"""Domain models shared across the pipeline.

These data structures are the contract that later phases (Action Tracking,
Reporting, Knowledge) consume, so keep them stable and well-defined.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timezone
from typing import Any, Optional


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ActionItem:
    """A single action extracted from a meeting."""

    description: str
    owner: str = "Unassigned"
    due_date: Optional[str] = None          # ISO date string (YYYY-MM-DD) or None
    status: str = "Open"                     # Open | In Progress | Closed
    priority: str = "Medium"                 # Low | Medium | High
    source_meeting_id: str = ""
    action_id: str = field(default_factory=lambda: f"ACT-{uuid.uuid4().hex[:8]}")
    created_at: str = field(default_factory=_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MeetingMetadata:
    """Descriptive information about the meeting being processed."""

    title: str = "Untitled Meeting"
    meeting_date: str = field(default_factory=lambda: date.today().isoformat())
    attendees: list[str] = field(default_factory=list)
    source_file: str = ""
    meeting_id: str = field(default_factory=lambda: f"MTG-{uuid.uuid4().hex[:8]}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MeetingOutputs:
    """The complete set of artifacts produced for one meeting."""

    metadata: MeetingMetadata
    summary: str
    minutes_markdown: str
    actions: list[ActionItem] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "metadata": self.metadata.to_dict(),
            "summary": self.summary,
            "minutes_markdown": self.minutes_markdown,
            "actions": [a.to_dict() for a in self.actions],
        }
