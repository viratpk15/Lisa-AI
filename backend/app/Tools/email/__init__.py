"""
Jarvis AIOS — Email Foundation & Intelligence Package
-----------------------------------------------------
Exposes tools for:
- email.sync
- email.verify_sender
- email.classify
- email.summarize
- email.extract_actions
- email.digest
"""

from app.Tools.email.sync_tool import EmailSyncTool
from app.Tools.email.verify_tool import EmailVerifySenderTool
from app.Tools.email.classifier import EmailClassifierTool
from app.Tools.email.summarizer import EmailSummarizerTool
from app.Tools.email.action_extractor import EmailActionExtractorTool
from app.Tools.email.digest import EmailDigestTool

__all__ = [
    "EmailSyncTool",
    "EmailVerifySenderTool",
    "EmailClassifierTool",
    "EmailSummarizerTool",
    "EmailActionExtractorTool",
    "EmailDigestTool",
]
