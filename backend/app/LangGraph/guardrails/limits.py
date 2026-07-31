"""
Execution Guardrail Limits

Named constants that bound plan execution. Every bound used by the
guardrails layer is defined here so that no magic numbers appear in
validation or executor logic.
"""

# Maximum number of steps allowed in a single plan.
MAX_PLAN_STEPS: int = 20

# Maximum number of replanning events allowed per request execution.
MAX_REPLANS: int = 3

# Maximum number of retries for a single tool execution before the step
# is marked failed permanently.
MAX_TOOL_RETRIES: int = 2

# Maximum number of consecutive step failures before execution is aborted.
MAX_CONSECUTIVE_FAILURES: int = 3

# Maximum wall-clock execution time (seconds) before a timeout termination.
MAX_EXECUTION_TIME_SECONDS: int = 120

# Maximum number of executor iterations before a limit-reached termination.
MAX_EXECUTOR_ITERATIONS: int = 50
