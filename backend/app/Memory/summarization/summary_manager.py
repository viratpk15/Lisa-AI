"""
Summary Manager

Manages conversation summarization, automatically generating summaries
of older messages when conversations exceed configured thresholds.
"""

from typing import TYPE_CHECKING

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage

if TYPE_CHECKING:
    from app.LLM.client import llm


class SummaryManager:
    """Manages conversation summarization.

    Automatically summarizes older conversation history when the message
    count exceeds the configured threshold. Summaries preserve important
    facts, tasks, goals, preferences, and decisions from older messages.

    The summary is stored as a SystemMessage and injected before recent
    messages, maintaining chronological order while reducing token usage.

    Attributes:
        threshold: Number of messages that triggers summarization.
        keep_recent: Number of recent messages to preserve without summarization.
    """

    def __init__(
        self,
        llm: "llm",
        threshold: int = 20,
        keep_recent: int = 10,
    ):
        """Initialize summary manager.

        Args:
            llm: LLM instance for generating summaries.
            threshold: Total message count that triggers summarization.
                Defaults to 20 messages.
            keep_recent: Number of recent messages to keep untouched.
                Must be even to preserve Human/AI pairs. Defaults to 10.

        Raises:
            ValueError: If keep_recent is not a positive even number.
        """
        if keep_recent <= 0:
            raise ValueError(
                f"keep_recent must be positive. Got: {keep_recent}"
            )

        if keep_recent % 2 != 0:
            raise ValueError(
                f"keep_recent must be even to preserve Human/AI pairs. "
                f"Got: {keep_recent}"
            )

        self._llm = llm
        self.threshold = threshold
        self.keep_recent = keep_recent

    def should_summarize(self, message_count: int) -> bool:
        """Check if summarization should be triggered.

        Args:
            message_count: Current total message count.

        Returns:
            True if summarization should occur, False otherwise.
        """
        return message_count >= self.threshold

    def summarize(self, messages: list[BaseMessage]) -> str:
        """Generate a summary of older messages.

        Uses the LLM to create a concise summary that preserves important
        facts, tasks, goals, preferences, and decisions from the conversation.

        Args:
            messages: List of older messages to summarize (chronological order).

        Returns:
            Summary text string.
        """
        if not messages:
            return ""

        # Build summarization prompt
        prompt = self._build_summarization_prompt(messages)

        # Generate summary using LLM
        try:
            response = self._llm.invoke([HumanMessage(content=prompt)])
            summary_text = response.content.strip()
        except Exception:
            # Fallback: create a basic summary if LLM fails
            summary_text = self._create_fallback_summary(messages)

        return summary_text

    def _build_summarization_prompt(self, messages: list[BaseMessage]) -> str:
        """Build prompt for LLM summarization.

        Args:
            messages: Messages to summarize.

        Returns:
            Formatted prompt string.
        """
        # Format messages for the prompt
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                formatted_messages.append(f"User: {msg.content}")
            elif isinstance(msg, AIMessage):
                formatted_messages.append(f"Assistant: {msg.content}")
            else:
                formatted_messages.append(f"{msg.type}: {msg.content}")

        conversation_text = "\n\n".join(formatted_messages)

        prompt = f"""Summarize the following conversation history. Preserve:
- Important facts and information shared by the user
- Tasks and goals mentioned
- User preferences and decisions
- Key conclusions and outcomes

Write a concise summary (2-3 sentences) that captures the essential context.

Conversation:
{conversation_text}

Summary:"""

        return prompt

    def _create_fallback_summary(self, messages: list[BaseMessage]) -> str:
        """Create a basic fallback summary if LLM fails.

        Args:
            messages: Messages to summarize.

        Returns:
            Basic summary string.
        """
        human_count = sum(1 for m in messages if isinstance(m, HumanMessage))
        ai_count = sum(1 for m in messages if isinstance(m, AIMessage))

        return (
            f"Previous conversation with {human_count} user messages "
            f"and {ai_count} assistant responses."
        )

    def get_messages_to_summarize(self, messages: list[BaseMessage]) -> list[BaseMessage]:
        """Extract older messages that should be summarized.

        Args:
            messages: Complete message list (chronological order).

        Returns:
            List of older messages to summarize (excluding recent messages).
        """
        if len(messages) < self.keep_recent:
            return []

        # Return all messages except the most recent ones
        return messages[:-self.keep_recent]

    def get_recent_messages(self, messages: list[BaseMessage]) -> list[BaseMessage]:
        """Extract recent messages to preserve.

        Args:
            messages: Complete message list (chronological order).

        Returns:
            List of recent messages to keep untouched.
        """
        if len(messages) < self.keep_recent:
            return messages

        return messages[-self.keep_recent:]

    def build_summarized_message_list(
        self, summary: str, recent_messages: list[BaseMessage]
    ) -> list[BaseMessage]:
        """Build final message list with summary injected.

        Args:
            summary: Summary text string.
            recent_messages: Recent messages to preserve.

        Returns:
            Complete message list with summary as SystemMessage followed by recent messages.
        """
        if not summary:
            return recent_messages

        summary_message = SystemMessage(
            content=f"Conversation Summary: {summary}"
        )

        return [summary_message] + recent_messages
