"""The central action register.

Two interchangeable backends implement :class:`ActionRegistry`:

  * :class:`SqliteActionRegistry`   -- local, zero-setup, great for the MVP/demo.
  * :class:`DynamoDBActionRegistry` -- AWS-native, the target for production.

Both expose the same small interface so later phases (e.g. the Action Tracking
Agent) can read/write actions without caring where they live.
"""
from __future__ import annotations

import json
import sqlite3
from abc import ABC, abstractmethod

from .config import Settings
from .models import ActionItem


class ActionRegistry(ABC):
    """Storage contract for action items."""

    @abstractmethod
    def save_actions(self, actions: list[ActionItem]) -> int:
        """Persist actions; return the number written."""

    @abstractmethod
    def list_actions(self, status: str | None = None) -> list[dict]:
        """Return stored actions, optionally filtered by status."""



class SqliteActionRegistry(ActionRegistry):
    """Local SQLite-backed register. Schema mirrors the DynamoDB item shape."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS actions (
                    action_id         TEXT PRIMARY KEY,
                    description       TEXT NOT NULL,
                    owner             TEXT,
                    due_date          TEXT,
                    status            TEXT,
                    priority          TEXT,
                    source_meeting_id TEXT,
                    created_at        TEXT
                )
                """
            )

    def save_actions(self, actions: list[ActionItem]) -> int:
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO actions
                (action_id, description, owner, due_date, status, priority,
                 source_meeting_id, created_at)
                VALUES (:action_id, :description, :owner, :due_date, :status,
                        :priority, :source_meeting_id, :created_at)
                """,
                [a.to_dict() for a in actions],
            )
        return len(actions)

    def list_actions(self, status: str | None = None) -> list[dict]:
        query = "SELECT * FROM actions"
        params: tuple = ()
        if status:
            query += " WHERE status = ?"
            params = (status,)
        query += " ORDER BY COALESCE(due_date, '9999-12-31'), priority"
        with self._connect() as conn:
            return [dict(row) for row in conn.execute(query, params).fetchall()]



class DynamoDBActionRegistry(ActionRegistry):
    """DynamoDB-backed register for AWS deployments.

    Expects a table whose partition key is ``action_id`` (String). A
    ``status``/``due_date`` GSI is recommended for the Action Tracking Agent.
    """

    def __init__(self, table_name: str, region: str) -> None:
        import boto3  # lazy import

        self.table = boto3.resource("dynamodb", region_name=region).Table(table_name)

    def save_actions(self, actions: list[ActionItem]) -> int:
        with self.table.batch_writer() as batch:
            for action in actions:
                # DynamoDB GSI keys can't be NULL: drop None attributes so items
                # without a due_date are simply absent from the status-due-index
                # (still stored in the main table) instead of being rejected.
                item = {k: v for k, v in action.to_dict().items() if v is not None}
                batch.put_item(Item=item)
        return len(actions)

    def list_actions(self, status: str | None = None) -> list[dict]:
        from boto3.dynamodb.conditions import Attr

        kwargs: dict = {}
        if status:
            kwargs["FilterExpression"] = Attr("status").eq(status)
        items: list[dict] = []
        response = self.table.scan(**kwargs)
        items.extend(response.get("Items", []))
        while "LastEvaluatedKey" in response:
            kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]
            response = self.table.scan(**kwargs)
            items.extend(response.get("Items", []))
        return items


def build_registry(settings: Settings) -> ActionRegistry:
    """Factory: choose a registry backend from settings."""
    backend = settings.registry_backend.lower()
    if backend == "dynamodb":
        return DynamoDBActionRegistry(settings.dynamodb_table, settings.aws_region)
    if backend == "sqlite":
        return SqliteActionRegistry(settings.sqlite_path)
    raise ValueError(f"Unknown ACTION_REGISTRY_BACKEND: {settings.registry_backend!r}")
