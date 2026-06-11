"""Administrative AI Agent (Phase 1 MVP).

Automates meeting administration: ingest a transcript, extract action items
(owners + due dates), generate minutes and a summary, and persist actions to a
central action register.

Pipeline:
    transcript -> extraction -> minutes/summary -> action register
"""

__version__ = "0.1.0"
