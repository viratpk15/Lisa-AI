"""
Router Node

Classifies user requests into categories to determine execution path.
Uses lightweight deterministic heuristics - no LLM calls.
"""

import re
import logging
from typing import Literal

from app.LangGraph.state import State
from app.Observability.trace import measure_time, calculate_duration
from app.Observability.manager import observability_manager

logger = logging.getLogger(__name__)


# Keywords that indicate multi-agent team workflows
MULTI_AGENT_PATTERNS = [
    r'\b(delegate to team|multi agent|agent team|multi-agent|team analysis|collaborate|team research)\b',
    r'\b(have researcher and coder|agent collaboration|team pipeline)\b',
]

# Keywords that indicate multi-step workflows
MULTI_STEP_PATTERNS = [
    # Sequential operations
    r'\b(then|after|afterward|afterwards|next|followed by)\b',
    # Comparison operations
    r'\b(compare|contrast|difference|versus|vs)\b',
    # Analysis workflows
    r'\b(analyze.*then|summarize.*then|read.*then|calculate.*then)\b',
    # Report generation
    r'\b(generate.*report|create.*report|write.*report)\b',
    # Multiple actions
    r'\b(and.*then|and.*after|first.*then|step.*step)\b',
    # Batch operations
    r'\b(all|every|each|multiple|several)\b.*\b(files|items|data)\b',
]

# Keywords that indicate single tool usage
SINGLE_TOOL_PATTERNS = [
    # Calculator
    r'\b(calculate|compute|evaluate|solve|what is \d|what\'s \d)\b',
    r'\b(\d+\s*[\+\-\*\/\%]\s*\d+)\b',  # Math expressions
    # File operations
    r'\b(read|show|display|open|load)\b.*\b(file|document|txt|json|csv)\b',
    r'\b(what\'s in|what is in|contents of)\b.*\b(file)\b',
    # Python execution
    r'\b(execute|run|execute)\b.*\b(python|code|script)\b',
    r'\b(print|output|result)\b.*\b(python)\b',
    # DateTime
    r'\b(what time|what date|current time|today|now)\b',
]

# Keywords that indicate conversational requests
CONVERSATION_PATTERNS = [
    # Greetings
    r'\b(hello|hi|hey|good morning|good afternoon|good evening|howdy)\b',
    # Gratitude
    r'\b(thanks|thank you|thx|appreciate)\b',
    # Identity questions
    r'\b(who are you|what are you|your name|tell me about yourself)\b',
    # Explanations
    r'\b(explain|what is|what are|tell me about|describe|define)\b',
    # Jokes/stories
    r'\b(tell me a joke|tell me a story|funny|entertain me)\b',
    # General questions
    r'\b(why|how does|what do you think|can you help|help me)\b',
]

# Keywords that indicate resume requests
RESUME_PATTERNS = [
    r'\b(continue|resume|go on|next|keep going|proceed|carry on)\b',
    r'\b(continue where|resume where|pick up|pickup)\b',
    r'\b(what was|what were|where were|where was)\b',
]


def _match_pattern(text: str, patterns: list[str]) -> bool:
    """Check if text matches any of the given regex patterns.

    Args:
        text: Text to check.
        patterns: List of regex patterns.

    Returns:
        True if any pattern matches, False otherwise.
    """
    text_lower = text.lower()
    for pattern in patterns:
        if re.search(pattern, text_lower):
            return True
    return False


def _count_tool_indicators(message: str) -> int:
    """Count the number of tool indicators in the message.

    Args:
        message: User message to analyze.

    Returns:
        Number of tool indicators found.
    """
    tool_indicators = [
        'calculate', 'compute', 'read', 'write', 'save', 'file',
        'execute', 'run', 'python', 'calculator', 'datetime',
        'open', 'load', 'show', 'display', 'print'
    ]

    message_lower = message.lower()
    count = sum(1 for indicator in tool_indicators if indicator in message_lower)
    return count


def _has_sequential_operators(message: str) -> bool:
    """Check if message contains sequential operators indicating multi-step.

    Args:
        message: User message to analyze.

    Returns:
        True if sequential operators found, False otherwise.
    """
    sequential_ops = [
        ' and then ', ' after ', ' then ', ' followed by ',
        ' next ', ' afterward', ' afterwards',
        ' first ', ' second ', ' finally '
    ]

    message_lower = f' {message.lower()} '
    return any(op in message_lower for op in sequential_ops)


def classify_request(message: str, observation: dict | None = None) -> Literal["conversation", "single_tool", "multi_step", "resume", "multi_agent"]:
    """Classify user request into execution category."""
    # Check for multi-agent team patterns first
    if _match_pattern(message, MULTI_AGENT_PATTERNS):
        logger.debug("Classified as multi_agent: pattern match")
        return "multi_agent"

    # Check for resume requests
    if _match_pattern(message, RESUME_PATTERNS):
        logger.debug("Classified as resume: pattern match")
        return "resume"

    # If there's an observation from previous tool execution,
    # this is likely a continuation of a multi-step workflow
    if observation and observation.get("result") is not None:
        return "multi_step"

    # Check for multi-step indicators
    if _match_pattern(message, MULTI_STEP_PATTERNS):
        logger.debug("Classified as multi_step: pattern match")
        return "multi_step"

    if _has_sequential_operators(message):
        logger.debug("Classified as multi_step: sequential operators")
        return "multi_step"

    # Check for single tool indicators
    if _match_pattern(message, SINGLE_TOOL_PATTERNS):
        logger.debug("Classified as single_tool: pattern match")
        return "single_tool"

    # Count tool indicators
    tool_count = _count_tool_indicators(message)
    if tool_count == 1:
        logger.debug("Classified as single_tool: single indicator")
        return "single_tool"

    # Default to conversation for everything else
    logger.debug("Classified as conversation: default")
    return "conversation"


def router(state: State) -> dict[str, Literal["conversation", "single_tool", "multi_step", "resume"]]:
    """Classify the user request and determine execution path.

    Analyzes the user message and optional observation to classify
    the request as conversation, single_tool, multi_step, or resume.
    Uses deterministic heuristics - no LLM calls.

    Resume requests are detected when user asks to continue, resume,
    go on, next, keep going, etc. If an unfinished plan exists in the
    session (persisted in SQLite), execution resumes directly without
    replanning.

    Args:
        state: The current LangGraph state.

    Returns:
        State update dict with 'request_type' field indicating the category.
    """
    start_time = measure_time()
    message = state["message"]
    observation = state.get("observation")
    session_id = state["session_id"]

    # Check for resume requests first (highest priority)
    if _match_pattern(message, RESUME_PATTERNS):
        # Check if there's a persisted execution state with pending steps
        from app.Memory.manager import memory_manager
        execution_state = memory_manager.load_execution_state(session_id)

        if (
            execution_state
            and execution_state.get("execution_status") in ["executing", "paused"]
            and execution_state.get("pending_steps")
        ):
            logger.info(
                "Resume request detected with persisted execution state (session=%s)",
                session_id,
            )
            # Restore plan from persisted state
            return {
                "request_type": "resume",
                "plan": execution_state.get("current_plan", {}),
            }
        else:
            logger.info(
                "Resume request detected but no active execution state (session=%s)",
                session_id,
            )

    # Use standard classification
    request_type = classify_request(message, observation)

    logger.info(
        "Classified request as '%s' for session %s (message='%s...')",
        request_type,
        session_id,
        message[:50] if len(message) > 50 else message,
    )

    observability_manager.record_duration("router", calculate_duration(start_time))
    return {
        "request_type": request_type,
    }
