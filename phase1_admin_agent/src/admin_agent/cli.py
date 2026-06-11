"""Command-line entry point for the Administrative AI Agent.

Examples
--------
Run locally with no AWS access (heuristic mock mode)::

    ADMIN_AGENT_MOCK=1 python -m admin_agent.cli process samples/sample_meeting.vtt

Run against AWS (Bedrock + DynamoDB)::

    ACTION_REGISTRY_BACKEND=dynamodb \\
    python -m admin_agent.cli process s3-or-local-transcript.txt
"""
from __future__ import annotations

import argparse
import sys

from .config import load_settings
from .pipeline import process_meeting
from .repository import build_registry


def _cmd_process(args: argparse.Namespace) -> int:
    settings = load_settings()
    if args.mock:
        settings.mock_mode = True

    outputs, written = process_meeting(
        args.transcript,
        title=args.title,
        meeting_date=args.date,
        attendees=args.attendees.split(",") if args.attendees else None,
        settings=settings,
    )

    print(f"\nProcessed: {outputs.metadata.title} ({outputs.metadata.meeting_id})")
    print(f"Mode:      {'MOCK (no AWS)' if settings.mock_mode else 'AWS Bedrock'}")
    print(f"Actions:   {len(outputs.actions)} extracted and saved to register")
    print("\nArtifacts:")
    for name, loc in written.items():
        print(f"  - {name}: {loc}")

    if outputs.actions:
        print("\nAction register preview:")
        for a in outputs.actions:
            due = a.due_date or "no due date"
            print(f"  [{a.priority:<6}] {a.owner:<12} {due:<12} {a.description}")
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    settings = load_settings()
    if args.mock:
        settings.mock_mode = True
    registry = build_registry(settings)
    rows = registry.list_actions(status=args.status)
    if not rows:
        print("No actions in the register.")
        return 0
    print(f"{'OWNER':<14}{'DUE':<13}{'STATUS':<12}{'PRIORITY':<10}DESCRIPTION")
    print("-" * 80)
    for r in rows:
        print(
            f"{(r.get('owner') or '-'):<14}{(r.get('due_date') or '-'):<13}"
            f"{(r.get('status') or '-'):<12}{(r.get('priority') or '-'):<10}"
            f"{r.get('description', '')}"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="admin-agent", description=__doc__)
    parser.add_argument("--mock", action="store_true", help="Force mock mode (no AWS calls)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_proc = sub.add_parser("process", help="Process a transcript end-to-end")
    p_proc.add_argument("transcript", help="Path to a .vtt/.srt/.txt/.docx transcript")
    p_proc.add_argument("--title", help="Meeting title")
    p_proc.add_argument("--date", help="Meeting date (YYYY-MM-DD)")
    p_proc.add_argument("--attendees", help="Comma-separated attendee names")
    p_proc.set_defaults(func=_cmd_process)

    p_list = sub.add_parser("list", help="List actions in the register")
    p_list.add_argument("--status", help="Filter by status (Open/In Progress/Closed)")
    p_list.set_defaults(func=_cmd_list)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
