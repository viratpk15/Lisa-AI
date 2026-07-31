"""
Jarvis AIOS — Multi-Agent Execution Metrics
------------------------------------------

Lightweight in-memory metrics tracker for multi-agent task execution metrics.
"""

from typing import Dict, Any


class ExecutionMetricsTracker:
    """Internal metrics tracker for multi-agent execution metrics."""

    def __init__(self) -> None:
        self.total_tasks: int = 0
        self.completed_tasks: int = 0
        self.failed_tasks: int = 0
        self.total_duration_ms: float = 0.0
        self.total_retries: int = 0

    def record_task(self, success: bool, duration_ms: float, retries: int = 0) -> None:
        """Record task execution metrics."""
        self.total_tasks += 1
        if success:
            self.completed_tasks += 1
        else:
            self.failed_tasks += 1
        self.total_duration_ms += duration_ms
        self.total_retries += retries

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics."""
        avg_dur = (self.total_duration_ms / self.total_tasks) if self.total_tasks > 0 else 0.0
        return {
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "average_duration_ms": round(avg_dur, 2),
            "retry_count": self.total_retries,
        }

    def reset(self) -> None:
        """Reset internal metrics counters."""
        self.total_tasks = 0
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.total_duration_ms = 0.0
        self.total_retries = 0


_metrics_instance: ExecutionMetricsTracker | None = None


def get_execution_metrics() -> ExecutionMetricsTracker:
    """Get the global execution metrics tracker singleton."""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = ExecutionMetricsTracker()
    return _metrics_instance
