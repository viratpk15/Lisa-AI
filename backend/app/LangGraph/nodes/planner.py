"""
Planner Node

Generates structured plans for achieving user goals. Plans consist of
ordered steps that may involve tool execution or conversational responses.
The planner analyzes the current context and produces a validated Plan object.
"""

import json
import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError

from app.LLM.client import llm
from app.Models.plan import Plan
from app.LangGraph.state import State
from app.Observability.trace import measure_time, calculate_duration
from app.Observability.manager import observability_manager
from app.LangGraph.guardrails.validator import NON_REPLAN_OUTCOMES
from app.LangGraph.validation.validator import validate_plan
from app.LangGraph.guardrails.validator import OUTCOME_INVALID_PLAN

logger = logging.getLogger(__name__)

# Maximum number of steps in a plan
MAX_PLAN_STEPS = 10

# Number of validation retries permitted before a plan is rejected.
MAX_VALIDATION_RETRIES: int = 1

def _build_planner_prompt() -> str:
    """Dynamically construct planner system prompt from registered tools in ToolRegistry."""
    from app.Tools.registry import registry
    registered_tools = registry.discover()
    tool_lines = []
    for meta in registered_tools:
        appr = " (Requires Approval)" if meta.requires_approval else ""
        tool_lines.append(f"- {meta.name}: {meta.description} [Category: {meta.category}]{appr}")
    tools_str = "\n".join(tool_lines) if tool_lines else "- None registered"

    return f"""You are a planning assistant for Jarvis AIOS.

Your job is to create a structured plan to achieve the user's goal.

Available tools:
{tools_str}

Rules:

1. Analyze the user's request and context (summary, memories, conversation).

2. Create a plan with ordered steps to achieve the goal.

3. Each step must have:
   - A clear description
   - A tool name (if tool execution is needed) or empty string (if conversational)
   - Status "pending"

4. If no tool is needed, create a single-step conversational plan.

5. If multiple tools are needed, create multiple ordered steps.

6. Maximum 10 steps per plan.

7. Return ONLY valid JSON in this exact format:

{{
    "goal": "High-level goal description",
    "steps": [
        {{
            "id": 1,
            "description": "Step description",
            "tool": "tool_name_or_empty_string",
            "status": "pending"
        }}
    ]
}}

Never explain.
Never use markdown formatting.
Return JSON only.
"""

PLANNER_PROMPT = _build_planner_prompt()


def _build_plan_from_llm(raw_content: str) -> dict[str, Any]:
    """Parse and validate LLM response into a plan dict.

    The LLM response is first parsed as JSON, then validated against
    the Plan Pydantic model. Invalid plans are rejected and replaced
    with a safe default plan.

    Args:
        raw_content: The raw string content from the LLM response.

    Returns:
        A validated plan dict with 'goal' and 'steps' keys.
    """
    # Step 1: Try to parse as JSON
    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError:
        logger.warning("Planner returned invalid JSON, using default plan")
        return _create_default_plan(raw_content)

    # Step 2: Reject non-dict values
    if not isinstance(parsed, dict):
        logger.warning("Planner returned non-dict JSON, using default plan")
        return _create_default_plan(raw_content)

    # Step 3: Validate against Plan model
    try:
        plan = Plan(**parsed)
        return plan.model_dump()
    except ValidationError as e:
        logger.warning("Planner returned invalid plan: %s", str(e))
        return _create_default_plan(raw_content)


def _create_default_plan(fallback_content: str) -> dict[str, Any]:
    """Create a default conversational plan.

    Used when the LLM returns an invalid or unparseable plan.

    Args:
        fallback_content: Fallback content to use as description.

    Returns:
        A valid plan dict with a single conversational step.
    """
    return {
        "goal": "Respond to user",
        "steps": [
            {
                "id": 1,
                "description": fallback_content[:200] if fallback_content else "Provide response",
                "tool": "",
                "status": "pending",
            }
        ],
    }


def _validate_and_retry(
    state: State,
    plan_dict: dict[str, Any],
    is_replanning: bool,
) -> dict[str, Any]:
    """Validate a generated plan and retry once on failure.

    After the planner produces a plan, it is validated deterministically. If
    the plan is invalid, the planner retries exactly once by regenerating the
    plan from the LLM with the validation errors included as feedback. If the
    retried plan is still invalid, the plan is replaced with an empty plan and
    the termination outcome is set to INVALID_PLAN so the executor never
    receives an invalid plan.

    Args:
        state: The current LangGraph state.
        plan_dict: The initially generated plan dict.
        is_replanning: Whether this invocation was a replanning event.

    Returns:
        A state update dict containing the (possibly retried) plan and routing.
    """
    result = validate_plan(plan_dict)
    if result.valid:
        return {"plan": plan_dict}

    logger.warning(
        "Plan validation failed (attempt 1): %s",
        result.reason,
    )

    # Retry once with validation feedback included in the prompt.
    retry_messages = [
        SystemMessage(content=PLANNER_PROMPT),
        HumanMessage(
            content=(
                f"User request: {state['message']}\n\n"
                "Your previous plan was rejected for these reasons:\n"
                f"{result.reason}\n\n"
                "Generate a corrected plan that satisfies every rule."
            )
        ),
    ]
    try:
        llm_start = measure_time()
        retry_response = llm.invoke(retry_messages)
        observability_manager.record_llm_usage(
            model_name=getattr(llm, "model", "") or "",
            latency_ms=calculate_duration(llm_start),
        )
        retry_plan = _build_plan_from_llm(retry_response.content)

        if is_replanning:
            completed_steps = [
                s for s in state.get("plan", {}).get("steps", [])
                if s.get("status") == "completed"
            ]
            if completed_steps:
                new_steps = retry_plan.get("steps", [])
                next_id = len(completed_steps) + 1
                for i, step in enumerate(new_steps):
                    step["id"] = next_id + i
                retry_plan["steps"] = completed_steps + new_steps
    except Exception as e:
        logger.error("Plan validation retry failed to generate: %s", str(e))
        retry_plan = plan_dict

    retry_result = validate_plan(retry_plan)
    if retry_result.valid:
        logger.info("Plan validation succeeded on retry.")
        return {"plan": retry_plan}

    # Still invalid after one retry -> reject. Return an empty plan so the
    # executor's routing never reaches execution, and mark INVALID_PLAN.
    logger.error(
        "Plan validation failed after retry (attempt 2): %s",
        retry_result.reason,
    )
    return {
        "plan": {"goal": "", "steps": []},
        "execution_outcome": OUTCOME_INVALID_PLAN,
        "termination_reason": OUTCOME_INVALID_PLAN,
        "_route_to": "executor",
    }


def planner(state: State):
    """Generate or replan a structured plan for achieving the user's goal.

    This node serves dual purposes:
    1. Initial planning: Generate a new plan from scratch
    2. Replanning: Modify an existing plan after failures or changes

    For replanning, the planner receives the previous plan with completed
    steps and only modifies the remaining steps. Completed steps are never
    regenerated.

    Args:
        state: The current LangGraph state.

    Returns:
        A state update dict containing the updated plan.
    """
    start_time = measure_time()
    session_id = state["session_id"]

    # Guardrail: do NOT regenerate a plan after a terminal outcome that
    # forbids replanning (LIMIT_REACHED, TIMEOUT, INVALID_PLAN, ABORTED).
    # Only FAILED may trigger replanning. This prevents infinite replanning
    # loops after a hard termination.
    termination_reason = state.get("termination_reason")
    if termination_reason in NON_REPLAN_OUTCOMES:
        logger.warning(
            "Planner guard: refusing to replan after terminal outcome '%s'",
            termination_reason,
        )
        return {
            "plan": state.get("plan", {}),
        }

    # Load conversation history for context
    from app.Memory.manager import memory_manager
    memory = memory_manager.get_conversation(session_id)

    # Retrieve relevant memories
    relevant_memories = memory_manager.get_relevant_memories(
        session_id=session_id,
        query=state["message"],
        top_k=5,
    )

    # Record planner invocation (initial plan or replan).
    existing_plan = state.get("plan", {})
    is_replanning = bool(existing_plan.get("steps"))
    observability_manager.record_planner_call(is_replan=is_replanning)

    # Build context for the planner
    context_parts = []

    # Add conversation summary if exists
    if memory.messages and memory.messages[0].__class__.__name__ == "SystemMessage":
        summary_msg = memory.messages[0]
        if "Conversation Summary:" in summary_msg.content:
            context_parts.append(f"Conversation Summary:\n{summary_msg.content}")

    # Add relevant memories
    if relevant_memories:
        memories_text = "\n".join([f"- {msg.content}" for msg in relevant_memories])
        context_parts.append(f"Relevant Memories:\n{memories_text}")

    # Add recent conversation (excluding summary)
    recent_messages = []
    for msg in memory.messages:
        if msg.__class__.__name__ == "SystemMessage" and "Conversation Summary:" in msg.content:
            continue
        recent_messages.append(f"{msg.__class__.__name__}: {msg.content}")

    if recent_messages:
        context_parts.append("Recent Conversation:\n" + "\n".join(recent_messages[-10:]))

    # Add execution outcome if present
    execution_outcome = state.get("execution_outcome")
    if execution_outcome:
        context_parts.append(f"Execution Outcome: {execution_outcome}")

    # For replanning, include the existing plan with completed steps
    if is_replanning:
        completed_steps = [s for s in existing_plan.get("steps", []) if s.get("status") == "completed"]
        failed_steps = [s for s in existing_plan.get("steps", []) if s.get("status") == "failed"]

        if completed_steps:
            completed_text = "\n".join([
                f"Step {s['id']}: {s['description']} (completed)"
                for s in completed_steps
            ])
            context_parts.append(f"Completed Steps (DO NOT REGENERATE):\n{completed_text}")

        if failed_steps:
            failed_text = "\n".join([
                f"Step {s['id']}: {s['description']} (failed)"
                for s in failed_steps
            ])
            context_parts.append(f"Failed Steps:\n{failed_text}")

        # Add observation if present
        observation = state.get("observation", {})
        if observation:
            obs_text = f"Latest Observation: {observation.get('result', observation.get('error', ''))}"
            context_parts.append(obs_text)

    # Build the complete prompt
    user_message = f"User request: {state['message']}"

    if context_parts:
        full_context = "\n\n".join(context_parts)
        planner_input = f"{full_context}\n\n{user_message}"
    else:
        planner_input = user_message

    # Call LLM to generate or replan
    messages = [
        SystemMessage(content=_build_planner_prompt()),
        HumanMessage(content=planner_input),
    ]

    try:
        llm_start = measure_time()
        response = llm.invoke(messages)
        observability_manager.record_llm_usage(
            model_name=getattr(llm, "model", "") or "",
            latency_ms=calculate_duration(llm_start),
        )
        plan_dict = _build_plan_from_llm(response.content)

        # If replanning, preserve completed steps from the original plan
        if is_replanning:
            completed_steps = [s for s in existing_plan.get("steps", []) if s.get("status") == "completed"]
            if completed_steps:
                # Merge completed steps with new plan
                new_steps = plan_dict.get("steps", [])
                # Find the next step ID after completed steps
                next_id = len(completed_steps) + 1
                # Renumber new steps
                for i, step in enumerate(new_steps):
                    step["id"] = next_id + i
                # Combine: completed steps + new steps
                plan_dict["steps"] = completed_steps + new_steps

    except Exception as e:
        logger.error("Failed to generate plan: %s", str(e))
        # On failure, keep existing plan if it exists, otherwise create default
        if is_replanning:
            plan_dict = existing_plan
        else:
            plan_dict = _create_default_plan(state["message"])

    plan_type = "Replan" if is_replanning else "Initial plan"
    logger.info(
        "%s generated with %d steps for session %s (goal='%s')",
        plan_type,
        len(plan_dict.get("steps", [])),
        session_id,
        plan_dict.get("goal", "unknown"),
    )

    observability_manager.record_duration("planner", calculate_duration(start_time))

    # Validate the generated plan before it can reach the executor. Invalid
    # plans are retried once; if still invalid, the plan is rejected and the
    # executor is signalled with INVALID_PLAN so it never executes a bad plan.
    return _validate_and_retry(state, plan_dict, is_replanning)
