# Jarvis AIOS — AI Engineering Guide

Version: 1.0

---

# Mission

You are contributing to Jarvis AIOS.

Jarvis is a production-grade AI Operating System built for extensibility, maintainability, security, and production deployment.

Your responsibility is to improve the project while preserving architectural integrity.

Never optimize for short-term convenience at the expense of long-term maintainability.

---

# Required Reading

Before implementing ANY feature, read:

1. docs/00_ENGINEERING_CONSTITUTION.md
2. docs/02_ARCHITECTURE.md
3. docs/03_CODING_STANDARDS.md
4. docs/14_AI_AGENT_RULES.md

Then read only the document relevant to your task.

Examples:

Memory → docs/06_MEMORY.md

Tool Engine → docs/05_TOOL_ENGINE.md

LangGraph → docs/04_LANGGRAPH.md

FastAPI → docs/08_FASTAPI.md

Security → docs/09_SECURITY.md

Deployment → docs/15_DEPLOYMENT.md

---

# Core Architecture

FastAPI

↓

Runtime

↓

LangGraph

↓

Tool Engine

↓

Tool Registry

↓

Individual Tools

↓

LLM

Runtime is the only public entry point.

LangGraph orchestrates.

Tool Engine executes.

Tools implement business logic.

Never bypass these layers.

---

# Engineering Principles

Preserve architecture.

Prefer readability.

Prefer maintainability.

Prefer explicit code.

Avoid hidden behavior.

Single Responsibility Principle.

Composition over duplication.

Production quality over shortcuts.

Documentation is part of the feature.

---

# Allowed Changes

Implement requested features.

Improve readability.

Improve performance.

Fix bugs.

Add tests.

Expand documentation.

Refactor without changing public behavior.

---

# Forbidden Changes

Do not rename folders.

Do not change architecture.

Do not introduce unnecessary dependencies.

Do not rewrite working systems.

Do not remove existing features.

Do not modify Runtime API without approval.

Do not create duplicate implementations.

Do not hardcode secrets.

---

# Tool Rules

Every tool must:

Have one responsibility.

Be registered.

Validate input.

Return structured output.

Handle failures gracefully.

Be independently testable.

Never execute automatically.

Always execute through Tool Engine.

---

# LangGraph Rules

LangGraph is orchestration only.

No business logic inside graph nodes.

Keep nodes small.

Keep state minimal.

Never access storage directly.

Never access FastAPI directly.

---

# Memory Rules

Memory must remain session-based.

Always access through MemoryManager.

Support future persistent storage.

Never tightly couple memory to LangGraph.

---

# Security Rules

Never expose API keys.

Never print secrets.

Avoid unsafe eval.

Avoid unsafe exec.

Validate all user inputs.

Restrict filesystem access.

Never trust LLM output blindly.

---

# Git Rules

Never commit automatically.

Never push automatically.

Never merge automatically.

Never delete branches.

Never rewrite Git history.

Never resolve merge conflicts automatically.

---

# Documentation Rules

Every architectural change updates documentation.

Every new module documents its purpose.

Keep examples synchronized with implementation.

---

# Code Review Rules

Explain every significant modification.

List modified files.

Explain why each file changed.

Mention risks.

Mention future improvements.

---

# Output Expectations

When implementing a feature:

1. Explain your plan.

2. List affected files.

3. Implement.

4. Explain modifications.

5. Mention potential improvements.

Never silently modify the project.

---

# Final Rule

If architecture and implementation conflict,

architecture always wins.