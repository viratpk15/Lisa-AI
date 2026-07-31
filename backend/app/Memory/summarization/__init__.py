"""
Conversation Summarization

Provides automatic summarization of older conversation history when
conversations exceed configured thresholds. Summaries are stored as
SystemMessage and injected before recent messages.
"""

from app.Memory.summarization.summary_manager import SummaryManager

__all__ = ["SummaryManager"]
