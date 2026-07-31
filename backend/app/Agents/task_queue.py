"""
Jarvis AIOS — Multi-Agent Task Queue
------------------------------------

In-memory FIFO Task Queue preserving task ordering for Supervisor task assignment
and Worker Dispatcher execution.
"""

from collections import deque
from typing import List, Optional
from app.Agents.task_model import AgentTask, TaskStatus


class TaskQueue:
    """In-memory ordered Task Queue for Multi-Agent execution."""

    def __init__(self) -> None:
        self._queue: deque[AgentTask] = deque()

    def enqueue(self, task: AgentTask) -> None:
        """Add task to the queue."""
        self._queue.append(task)

    def dequeue(self) -> Optional[AgentTask]:
        """Remove and return the next task from the queue."""
        if not self._queue:
            return None
        task = self._queue.popleft()
        task.status = TaskStatus.RUNNING
        return task

    def peek(self) -> Optional[AgentTask]:
        """Return the next task without removing it."""
        return self._queue[0] if self._queue else None

    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._queue) == 0

    def size(self) -> int:
        """Get number of pending tasks."""
        return len(self._queue)

    def list_tasks(self) -> List[AgentTask]:
        """List all pending tasks in order."""
        return list(self._queue)

    def clear(self) -> None:
        """Clear all tasks in the queue."""
        self._queue.clear()
