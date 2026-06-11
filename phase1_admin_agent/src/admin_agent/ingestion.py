"""Transcript ingestion.

Supported inputs for the MVP:
  * ``.vtt`` / ``.srt``  -- WebVTT / SubRip caption files (timestamps stripped)
  * ``.txt``             -- plain text transcript or notes
  * ``.docx``            -- Word document (optional, requires python-docx)

Audio/video recordings are handled by :func:`transcribe_recording`, which kicks
off an Amazon Transcribe job. That path requires AWS credentials and an S3
bucket and is intentionally separate from the plain-text fast path.
"""
from __future__ import annotations

import re
import time
from pathlib import Path

from .config import Settings

_TIMESTAMP_RE = re.compile(r"^\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[.,]\d{3}")
_CUE_INDEX_RE = re.compile(r"^\d+$")
_AUDIO_SUFFIXES = {".mp3", ".mp4", ".wav", ".m4a", ".flac", ".ogg", ".webm"}


def _clean_caption_text(raw: str) -> str:
    """Strip WebVTT/SRT headers, cue numbers and timestamp lines."""
    lines: list[str] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped == "WEBVTT" or stripped.startswith("NOTE"):
            continue
        if _TIMESTAMP_RE.match(stripped):
            continue
        if _CUE_INDEX_RE.match(stripped):
            continue
        lines.append(stripped)
    return "\n".join(lines)


def load_transcript(path: str | Path) -> str:
    """Load a transcript file and return clean text.

    Raises:
        FileNotFoundError: if the path does not exist.
        ValueError: if the file type is unsupported.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Transcript not found: {p}")

    suffix = p.suffix.lower()

    if suffix in {".vtt", ".srt"}:
        return _clean_caption_text(p.read_text(encoding="utf-8", errors="replace"))

    if suffix == ".txt":
        return p.read_text(encoding="utf-8", errors="replace").strip()

    if suffix == ".docx":
        try:
            import docx  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise ValueError(
                "Reading .docx requires python-docx. Install it or convert to .txt."
            ) from exc
        document = docx.Document(str(p))
        return "\n".join(par.text for par in document.paragraphs if par.text.strip())

    if suffix in _AUDIO_SUFFIXES:
        raise ValueError(
            f"'{suffix}' is a recording. Use transcribe_recording() to convert it first."
        )

    raise ValueError(f"Unsupported transcript type: {suffix}")


def transcribe_recording(
    s3_uri: str,
    settings: Settings,
    *,
    poll_seconds: int = 15,
    timeout_seconds: int = 3600,
) -> str:
    """Transcribe an audio/video recording stored in S3 via Amazon Transcribe.

    Args:
        s3_uri: Location of the recording, e.g. ``s3://bucket/meeting.mp4``.
        settings: Runtime settings (region, output bucket).
        poll_seconds: Delay between job-status polls.
        timeout_seconds: Maximum time to wait for the job.

    Returns:
        The transcribed text.
    """
    import json
    import urllib.request

    import boto3  # imported lazily so mock/local flows need no AWS SDK

    client = boto3.client("transcribe", region_name=settings.aws_region)
    job_name = f"ctt-admin-{int(time.time())}"

    kwargs: dict = {
        "TranscriptionJobName": job_name,
        "Media": {"MediaFileUri": s3_uri},
        "IdentifyLanguage": True,
    }
    if settings.transcribe_output_bucket:
        kwargs["OutputBucketName"] = settings.transcribe_output_bucket

    client.start_transcription_job(**kwargs)

    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        job = client.get_transcription_job(TranscriptionJobName=job_name)
        status = job["TranscriptionJob"]["TranscriptionJobStatus"]
        if status == "COMPLETED":
            uri = job["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
            with urllib.request.urlopen(uri) as resp:  # noqa: S310
                data = json.loads(resp.read().decode("utf-8"))
            return data["results"]["transcripts"][0]["transcript"]
        if status == "FAILED":
            reason = job["TranscriptionJob"].get("FailureReason", "unknown")
            raise RuntimeError(f"Transcription failed: {reason}")
        time.sleep(poll_seconds)

    raise TimeoutError(f"Transcription job {job_name} did not finish in time")
