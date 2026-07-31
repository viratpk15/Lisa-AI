"""
Window Manager

Manages sliding window for conversation history, ensuring only the most
recent messages are retained while preserving complete Human/AI pairs.
"""

from typing import TYPE_CHECKING

from langchain_core.messages import BaseMessage

if TYPE_CHECKING:
    from langchain_core.chat_history import BaseChatMessageHistory


class WindowManager:
    """Manages sliding window for conversation history.

    Ensures conversation history never exceeds the configured window size
    by removing the oldest messages while preserving complete Human/AI pairs.

    The window always operates on complete pairs to maintain conversation
    coherence. If a window size of 10 is configured, up to 10 messages
    (5 Human/AI pairs) are retained.

    Attributes:
        window_size: Maximum number of messages to retain (must be even).
    """

    def __init__(self, window_size: int = 10):
        """Initialize window manager.

        Args:
            window_size: Maximum number of messages to keep.
                Must be even to preserve Human/AI pairs.
                Defaults to 10 (5 pairs).

        Raises:
            ValueError: If window_size is not a positive even number.
        """
        if window_size <= 0:
            raise ValueError(
                f"Window size must be positive. Got: {window_size}"
            )

        if window_size % 2 != 0:
            raise ValueError(
                f"Window size must be even to preserve Human/AI pairs. "
                f"Got: {window_size}"
            )

        self.window_size = window_size

    def apply_window(self, messages: list[BaseMessage]) -> list[BaseMessage]:
        """Apply sliding window to message list.

        Removes the oldest messages to ensure the total count does not
        exceed the configured window size. Only complete Human/AI pairs
        are removed - a partial pair is never split.

        Args:
            messages: Complete list of messages in chronological order
                (oldest first, newest last).

        Returns:
            Windowed message list containing only the most recent messages,
            never exceeding self.window_size messages.
        """
        if len(messages) <= self.window_size:
            # No windowing needed
            return messages

        # Calculate how many messages to remove
        excess = len(messages) - self.window_size

        # Remove messages in pairs to preserve Human/AI pairs
        # Each pair is 2 messages, so remove in multiples of 2
        messages_to_remove = (excess // 2) * 2

        # Return only the most recent messages
        return messages[messages_to_remove:]

    def get_windowed_history(
        self, history: "BaseChatMessageHistory"
    ) -> list[BaseMessage]:
        """Get windowed messages from a chat history.

        Convenience method that retrieves messages from a chat history
        and applies the window.

        Args:
            history: Chat message history to window.

        Returns:
            Windowed list of messages.
        """
        messages = history.messages
        return self.apply_window(messages)


# Default window size: 10 messages (5 Human/AI pairs)
MAX_WINDOW_SIZE: int = 10
