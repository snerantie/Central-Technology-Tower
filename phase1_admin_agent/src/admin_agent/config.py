"""Configuration for the Administrative AI Agent.

All settings are read from environment variables so the same code runs locally
(mock mode) and on AWS without changes. See ``.env.example`` for the full list.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


def _env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class Settings:
    """Runtime configuration, populated from the environment."""

    # --- Operating mode -------------------------------------------------
    # When True, no AWS calls are made; deterministic local stand-ins are used.
    # Lets the pipeline be demoed/tested without credentials.
    mock_mode: bool = field(default_factory=lambda: _env_bool("ADMIN_AGENT_MOCK", False))

    # --- AWS / Bedrock --------------------------------------------------
    # Default to Amazon Nova 2 Lite via the eu cross-region inference profile.
    # Nova 2 Lite (released late 2025) is multimodal, has a 1M-token context
    # window, supports extended thinking, and is the cost-effective choice
    # for the AI Agent Programme. As of late 2025, AWS retired the Bedrock
    # model-access opt-in flow -- access is enabled by default per IAM only.
    # Override with BEDROCK_MODEL_ID for a different model (Nova Pro, Mistral,
    # Llama, Claude, etc.). All share the Bedrock Converse API.
    aws_region: str = field(default_factory=lambda: os.getenv("AWS_REGION", "eu-west-1"))
    bedrock_model_id: str = field(
        default_factory=lambda: os.getenv(
            "BEDROCK_MODEL_ID", "eu.amazon.nova-2-lite-v1:0"
        )
    )

    # --- Storage --------------------------------------------------------
    # Action register backend: "sqlite" (local) or "dynamodb" (AWS).
    registry_backend: str = field(
        default_factory=lambda: os.getenv("ACTION_REGISTRY_BACKEND", "sqlite")
    )
    sqlite_path: str = field(
        default_factory=lambda: os.getenv("ACTION_REGISTRY_SQLITE_PATH", "action_register.db")
    )
    dynamodb_table: str = field(
        default_factory=lambda: os.getenv("ACTION_REGISTRY_TABLE", "ctt-action-register")
    )

    # Where generated minutes/summaries are written. If it looks like an S3
    # URI (s3://bucket/prefix) they are uploaded; otherwise a local directory.
    output_location: str = field(
        default_factory=lambda: os.getenv("ADMIN_AGENT_OUTPUT", "output")
    )

    # --- Amazon Transcribe (for audio/video recordings) ----------------
    transcribe_output_bucket: str = field(
        default_factory=lambda: os.getenv("TRANSCRIBE_OUTPUT_BUCKET", "")
    )

    @property
    def output_is_s3(self) -> bool:
        return self.output_location.startswith("s3://")


def load_settings() -> Settings:
    """Build a :class:`Settings` instance from the current environment."""
    return Settings()
