# Jarvis AIOS Engineering Constitution

**Version:** 1.0  
**Status:** Ratified  


---

## 1. Purpose

This document is the supreme governing document of the Jarvis AIOS project. Every contributor—human or AI—must follow it.

When any other document, rule, or instruction contradicts this constitution, **this constitution wins**.

This document defines:

- Why Jarvis exists.
- How engineering decisions must be made.
- What qualifies as complete, correct work.
- How the constitution itself evolves.

---

## 2. Mission

Jarvis is a production-grade AI Operating System.

We do not build prototypes. We build a system that is:

- **Extensible** — new capabilities plug in without modifying core architecture.
- **Maintainable** — any engineer can understand and modify any part of the system.
- **Secure** — user data, secrets, and system integrity are never optional.
- **Production-deployable** — observability, resilience, and operational readiness are built in, not bolted on.

Every line of code must serve this mission. Code that compromises these goals for short-term speed is rejected.

---

## 3. Engineering Philosophy

### 3.1 Architecture Over Convenience

The architecture is the product. If a shortcut violates the architecture, it is not a shortcut—it is technical debt. Never optimise for short-term convenience at the expense of long-term maintainability.

### 3.2 Explicit Over Implicit

Hidden behaviour, magic imports, and implicit side effects have no place in Jarvis. Every dependency, every data flow, every side effect must be visible and auditable.

### 3.3 Composition Over Duplication

Duplication is the root of inconsistency. When the same logic appears in two places, extract it into one. When a pattern emerges, abstract it. Reuse through composition, not inheritance.

### 3.4 Production Quality Is Not Optional

Logging, error handling, input validation, and security are not "future work." They are part of the feature. If a feature cannot be observed, diagnosed, and secured in production, it is not complete.

### 3.5 Discipline Over Genius

Write code that is boring, obvious, and correct.

Clever code is a liability.

Readable code is the highest form of optimisation because readable systems are easier to debug, extend, review, and maintain.

### 3.6 Continuous Improvement

No design is considered final.

Every component should become simpler, safer, faster, and easier to maintain over time.

Refactoring is encouraged whenever it improves architecture without breaking public behaviour.

Technical debt must be tracked, documented, and reduced continuously rather than ignored.
---

## 4. Core Principles

### 4.1 Architecture & Layering

| Layer | Responsibility | Access |
|---|---|---|
| FastAPI | HTTP transport, request validation | Routes only |
| Runtime | Public entry point, state construction | Allowed to call LangGraph |
| LangGraph | Orchestration only | No business logic, no storage access |
| Tool Engine | Tool lookup and execution | Registry only |
| Tool Registry | Tool registration and discovery | Engine only |
| Tools | Business logic | Engine only |
| LLM | Model inference | Agent node only |
| Memory | Session storage | Manager only |
| Prompts | Templates | Nodes only |

- Never bypass a layer. Lower layers are invisible to higher layers.
- LangGraph nodes must never access storage, FastAPI, or the LLM directly.
- The Runtime is the only public API. No other module is exposed externally.

### 4.2 Code Quality

- Every function must have a single responsibility.
- Every function should have a single clear responsibility and remain easy to understand. Prefer smaller functions when doing so improves readability and maintainability.
- All Python code must use type hints. The `Any` type must be justified with a comment.
- every import must be explicit. No star imports (`from x import *`).
- Every module must have a docstring explaining its purpose.
- No dead code. If a function, class, or file is unused, remove it.
- No commented-out code. Version control exists for that.

### 4.3 AI Engineering

Jarvis is an AI-native system.

Engineering practices must acknowledge that Large Language Models are probabilistic rather than deterministic.

- Never assume model outputs are correct.
- Validate every structured response.
- Prefer structured outputs over free-form text.
- Keep prompts version controlled.
- Separate prompts from business logic.
- Design prompts as reusable assets.
- Always support future model replacement without architectural changes.

### 4.4 Security

- Never hardcode secrets. Use environment variables loaded via `.env` or a secrets manager.
- Never use `eval()` or `exec()` on untrusted input. If unavoidable, sandbox strictly.
- Validate every user-supplied input at the API boundary.
- Restrict file system access to approved directories. Never allow arbitrary paths.
- Never trust LLM output blindly. Validate structure, types, and bounds before use.
- Never print or log secrets, API keys, or personally identifiable information.
- Never trust AI-generated code without human review.


### 4.5 Documentation

- Every architectural change must update the relevant documentation.
- Every new module must include a docstring and a documentation file in `docs/`.
- Every code example in documentation must be tested or verifiable.
- Documentation is part of the feature. A feature without documentation is incomplete.

### 4.6 Operations

- Every service must log at startup with its version and configuration.
- Every error must be logged with enough context to diagnose without reproduction.
- Every public endpoint must have a health check.
- Every change must be revertible. One feature = one branch = one deploy.


### 4.7 Performance

Performance should be measured rather than assumed.

- Avoid premature optimisation.
- Profile before optimising.
- Minimise unnecessary LLM calls.
- Reduce latency without sacrificing readability.
- Prefer scalable solutions over micro-optimisations.

### 4.8 Dependency Management

Every dependency increases maintenance cost.

- Prefer the Python standard library whenever practical.
- Introduce third-party libraries only with clear technical justification.
- Remove unused dependencies promptly.
- Keep dependency versions explicit and reproducible.


---

## 5. Decision-Making Framework

### 5.1 Hierarchy of Authority

When facing a trade-off, resolve it in this order:

1. **Constitution** — This document. It overrides everything below.
2. **Architecture** — The layered architecture defined in `docs/02_ARCHITECTURE.md`.
3. **Coding Standards** — The language-specific rules in `docs/03_CODING_STANDARDS.md`.
4. **Module Docs** — The documentation for the specific module (LangGraph, Tools, Memory, etc.).
5. **Pragmatism** — When the above do not prescribe an answer, use engineering judgment, but document the decision and justify it against this constitution.

### 5.2 Decision Process for Ambiguous Choices

1. State the decision to be made and why it is ambiguous.
2. List at least two alternatives with pros and cons.
3. Evaluate each alternative against Sections 2 (Mission), 3 (Philosophy), and 4 (Principles).
4. Select the alternative that best satisfies the constitution.
5. Document the decision and the reasoning in a comment or commit message.

### 5.3 When to Say No

- If a change weakens the layered architecture, reject it.
- If a change introduces a security vulnerability, reject it.
- If a change duplicates existing functionality, reject it.
- If a change cannot be tested, reject it.
- If a change adds a dependency without clear justification, reject it.

---

## 6. Definition of Done

A feature or change is **done** only when all of the following are true:

### 6.1 Code

- [ ] All new code follows the principles and standards in this constitution.
- [ ] No dead code, commented-out code, or unnecessary files are introduced.
- [ ] All type hints are present and correct.
- [ ] All functions have docstrings.
- [ ] Imports are clean and explicit.

### 6.2 Testing

- [ ] Unit tests exist for all new business logic.
- [ ] Integration tests exist for all new API endpoints or LangGraph nodes.
- [ ] All existing tests pass.
- [ ] Edge cases and failure modes are tested.

### 6.3 Documentation

- [ ] Relevant `docs/` files are updated or created.
- [ ] Inline comments explain non-obvious logic.
- [ ] Module docstrings are updated.
- [ ] Examples in documentation are synchronised with the implementation.

### 6.4 Security

- [ ] No secrets are exposed.
- [ ] All user inputs are validated.
- [ ] No unsafe `eval()`, `exec()`, or unrestricted file access is introduced.
- [ ] LLM output is validated before use.

### 6.5 Production Readiness

- [ ] Errors are logged with sufficient context.
- [ ] The change is revertible (atomic commit, feature-flagged if risky).
- [ ] No new warnings or lint errors are introduced.
- [ ] The change does not degrade performance without documented justification.

---

## 7 Engineering Motto

Jarvis follows these engineering values in every component:

- Readable
- Maintainable
- Secure
- Observable
- Extensible
- Testable
- Production Ready

---
## 8. Future Evolution

### 8.1 Amendment Process

This constitution is not static. To amend it:

1. **Propose** — Open a GitHub Discussion or issue titled `RFC: [summary of change]`.
2. **Debate** — Allow at least 72 hours for review and comment.
3. **Refine** — Incorporate feedback. The final text must include the exact wording changes.
4. **Ratify** — A maintainer merges the change. If the change modifies Section 4 (Core Principles) or Section 5 (Decision-Making Framework), it requires two maintainers to approve.

### 8.2 Versioning

- The constitution uses semantic versioning: `MAJOR.MINOR`.
- **Major** — Changes to Core Principles or Decision-Making Framework.
- **Minor** — Clarifications, new Purpose or Philosophy entries, new subsections under existing Principles.

### 8.3 Transition Period

When this constitution is updated, existing code that violates the new rules is flagged as technical debt. It must be resolved within two sprints or be explicitly exempted with a documented rationale in the relevant module's documentation.




---

*This constitution is the foundation of Jarvis AIOS. Everything else is commentary.*