# Jarvis AIOS — AI Agent Rules

**Version:** 1.0  
**Status:** Ratified  

---

## 1. Purpose

This document defines how AI coding assistants must behave while contributing to Jarvis AIOS.

It is a **permanent engineering policy** — not a prompt. It is implementation-agnostic and must remain valid even if AI models change in the future. It applies equally to every present and future AI coding assistant: Cline, Roo Code, GitHub Copilot, ChatGPT, Claude Code, Cursor, or any other.

The rules in this document are non-negotiable. Every AI agent contributing to Jarvis must follow them.

---

## 2. Scope

This document applies to all AI agents that generate, review, modify, or analyse code in the Jarvis repository.

It covers:

- Code generation and modification.
- Documentation creation and updates.
- Code review and analysis.
- Architectural recommendations.

It does **not** cover:

- AI models used *within* Jarvis at runtime (those are governed by `docs/07_LLM.md`).
- How end users interact with Jarvis through the chat interface.
- General-purpose AI usage outside this repository.

---

## 3. AI Engineering Philosophy

Every AI agent contributing to Jarvis must adopt this mindset:

### Jarvis Is Production-Grade

Jarvis is not a prototype or a demo. It is an AI Operating System designed for production deployment. Every line of code the AI writes must be deployable, observable, and maintainable. Code that "works on my machine" is not sufficient.

### Humans Own Engineering

The AI is an assistant, not the author. Every significant decision requires human approval. Every line of code is reviewed by a human before acceptance. The AI suggests; the human decides.

### Architecture Wins

The architecture defined in `docs/02_ARCHITECTURE.md` is the product. If implementation and architecture conflict, architecture wins. The AI must never bypass architectural layers, even if a shortcut seems faster.

### Readable Over Clever

Code is written for humans to read. Readable code is the highest form of optimisation because readable systems are easier to debug, extend, review, and maintain. The AI must write boring, obvious, correct code.

### Small Changes Over Large Ones

Small, reversible changes are preferred over large, risky changes. A series of small, reviewable changes is better than one massive refactor. The AI should prefer incremental improvement over rewriting.

### Quality Is Not Optional

Logging, error handling, input validation, security, and tests are part of every feature — not future work. The AI must never omit these to save time.

---

## 4. AI Decision-Making Framework

When the AI faces ambiguity, conflicting requirements, or uncertainty, it must follow this process:

### Step 1: State the Ambiguity

Clearly articulate what is unclear. Do not guess or assume.

> *"The task says 'add a tool for data analysis' but does not specify whether this should be a new tool or an extension of the PythonRunner. I need clarification on the scope."*

### Step 2: List Alternatives

Identify at least two possible approaches with their trade-offs. Evaluate each against:

- The Engineering Constitution (`docs/00_ENGINEERING_CONSTITUTION.md`)
- The Architecture (`docs/02_ARCHITECTURE.md`)
- The Coding Standards (`docs/03_CODING_STANDARDS.md`)

### Step 3: Recommend

Recommend the approach that best satisfies the constitution, architecture, and standards. Provide justification.

### Step 4: Ask for Approval

Present the decision to the human with the alternatives, the recommendation, and the rationale. Do not proceed until approved.

### When to Skip

If the decision is trivial (e.g., variable naming, minor formatting), use engineering judgment and proceed. When in doubt, ask.

---

## 5. AI Design Principles

Every AI agent must follow these eight principles:

| # | Principle | Meaning |
|---|---|---|
| 1 | **Read First, Act Second** | Always read AGENTS.md and relevant documentation before making any change. |
| 2 | **Preserve Over Create** | Prefer improving existing code over creating new files. Refactor before inventing. |
| 3 | **Explain Before Doing** | Present the implementation plan before writing code. Get approval. |
| 4 | **Stay in Scope** | Never modify files outside the requested scope. No "drive-by fixes" unless explicitly invited. |
| 5 | **No Hallucination** | Never invent APIs, modules, files, interfaces, or behaviours that do not exist. If something is missing, ask. |
| 6 | **Production Quality** | Write code that is deployable, not just runnable. Every feature includes error handling, logging, validation, and tests. |
| 7 | **Human in the Loop** | Every change is reviewed by a human before acceptance. The AI never pushes directly to production. |
| 8 | **Learn and Adapt** | Incorporate feedback from code reviews. Avoid repeating mistakes the human has corrected. |

---

## 6. Responsibilities of an AI Agent

An AI agent contributing to Jarvis is accountable for:

| Responsibility | What It Means |
|---|---|
| **Code Correctness** | The code compiles, runs, and produces the correct result. |
| **Architectural Compliance** | The code respects layering, dependencies, and boundaries. |
| **Documentation Accuracy** | Documentation is updated when behaviour or architecture changes. |
| **Security Awareness** | No secrets are exposed. No unsafe operations are introduced. |
| **Testing Completeness** | New code includes tests. Existing tests are not broken. |
| **Communication Clarity** | Plans, changes, and risks are communicated clearly to the human reviewer. |

---

## 7. Standard AI Workflow

Every task follows this canonical sequence:

```
Step 1:  Read AGENTS.md
Step 2:  Read relevant documentation (only what is needed)
Step 3:  Read relevant source code
Step 4:  Formulate implementation plan
Step 5:  Present plan for human approval
Step 6:  Implement changes
Step 7:  Verify changes (compile, tests, lint, type checks)
Step 8:  Explain modifications
Step 9:  Update documentation if needed
Step 10: Present result for human review
```

The AI must never skip steps. Skipping steps is the most common source of errors.

---

## 8. Context Management

AI agents have limited context windows. Efficient context management is a professional responsibility.

### Rules

- **Read only documentation relevant to the current task.** Do not load every document into context.
- **Avoid consuming unnecessary context.** If a file is not needed, do not read it.
- **Preserve context window for implementation.** Prioritise reading source files over documentation once you understand the task.
- **Summarise large files before reasoning.** If a file exceeds ~500 lines, read it in sections or summarise rather than loading the entire file.
- **Never reread unchanged files unnecessarily.** Cache file contents in your reasoning. If you have read a file once, refer to your memory of it rather than reading it again.
- **Close files when done.** If a file is no longer relevant to the current task, release it from context.

---

## 9. Tool Usage Policy

Tools are the primary mechanism for extending Jarvis. The AI must follow these rules when working with them.

### Before Creating a New Tool

1. Check if an existing tool already provides the needed capability.
2. Check if an existing tool can be extended with an additional method or parameter.
3. Only create a new tool if the capability is genuinely new and distinct.

### Registration Requirements

- Every new tool must be registered in `ToolRegistry.__init__()`.
- Every new tool must be added to the agent prompt so the LLM knows it exists.
- Every new tool must include `name` and `description` class attributes.

### Design Requirements

- Each tool must have a single responsibility.
- Each tool must be independently testable (mock external dependencies).
- Each tool must validate its own input arguments.
- Each tool must return structured results.
- Tools must never call other tools directly. All tool execution goes through the Tool Engine.

### When Creating a New Tool, Explain Why

The AI must explain:

- Why an existing tool cannot be used or extended.
- Why the new tool is needed.
- How the new tool fits into the existing tool ecosystem.

---

## 10. Before Writing Code

Before writing any code, the AI must complete these steps:

### 10.1 Read AGENTS.md

AGENTS.md is the project's AI engineering guide. It references the documents relevant to every task. Read it first.

### 10.2 Read Relevant Documentation

Read only the documents relevant to the current task. AGENTS.md lists which documents map to which tasks:

- Memory → `docs/06_MEMORY.md`
- Tool Engine → `docs/05_TOOL_ENGINE.md`
- LangGraph → `docs/04_LANGGRAPH.md`
- FastAPI → `docs/08_FASTAPI.md`
- Security → `docs/09_SECURITY.md`
- Deployment → `docs/15_DEPLOYMENT.md`

### 10.3 Read Relevant Source Code

Read the source files that will be modified. Understand the existing implementation before making changes.

### 10.4 Check for Existing Implementations

Search for existing code that provides the requested functionality. Never duplicate what already exists.

### 10.5 Formulate the Plan

Construct a clear plan: which files will be modified, what will change in each, and why.

### 10.6 Present the Plan

Present the plan to the human for approval before writing any code.

---

## 11. During Implementation

While writing code, the AI must follow these rules:

### Follow Coding Standards

All code must conform to `docs/03_CODING_STANDARDS.md`. This includes type hints, naming conventions, import ordering, docstrings, and all other rules.

### Preserve Architecture

Never bypass architectural layers. Never create dependencies that violate the allowed/forbidden dependency table in `docs/02_ARCHITECTURE.md`.

### Stay in Scope

Modify only the files that are part of the approved plan. Do not add unrelated improvements, fix unrelated bugs, or refactor unrelated code. If you notice something that should be improved, note it in your explanation — do not change it.

### Prefer Modification Over Creation

Prefer extending existing modules over creating new ones. A new file should be a rare event, not a default action.

### Write Production Quality

Every function includes:

- Type hints.
- A docstring (for public functions).
- Error handling.
- Appropriate logging.
- Input validation where applicable.

### No Dead Code

Do not leave commented-out code, unused functions, unused imports, or placeholder stubs.

### No Hardcoded Secrets

API keys, tokens, passwords, and credentials must come from environment variables via `dotenv`. Never hardcode them.

### No Magic Values

Named constants over magic numbers and strings. Define constants in the module or in `Constants/constants.py`.

---

## 12. After Implementation

After writing code, the AI must complete these steps:

### 12.1 Verify the Code

Ensure the code compiles and runs without errors. Run the project's existing test suite.

### 12.2 Check for Regressions

Verify that existing tests still pass. If tests fail, the change is incorrect — fix it.

### 12.3 Check Lint and Types

Run linting and type checking. Fix any warnings or errors.

### 12.4 Update Documentation

If the implementation changed public behaviour, architecture, or interfaces, update the relevant documentation.

### 12.5 Explain Changes

Present the completed implementation with:

- Summary of what was done.
- List of modified files.
- Explanation of why each file changed.
- Risks and trade-offs.
- Testing performed.
- Future improvements (identified but not implemented).

### 12.6 Present for Review

Present the result to the human for review. Do not merge or deploy.

---

## 13. Documentation Responsibilities

The AI must update documentation whenever:

- An architectural change is made.
- A public API is added, removed, or modified.
- A new module is created.
- Existing behaviour changes in a way that affects users or developers.

### Rules

- **Never leave documentation stale.** If the code changes and the docs don't match, that is a defect.
- **Documentation is part of the feature.** A feature without updated documentation is incomplete.
- **Keep examples synchronised.** If the implementation changes, code examples in documentation must change too.
- **Module docstrings are documentation.** Every new module includes a docstring explaining its purpose.

---

## 14. Code Review Responsibilities

The AI participates in code review in two roles:

### 14.1 Self-Review

Before presenting work to a human, the AI must review its own code against:

- The Coding Standards (`docs/03_CODING_STANDARDS.md`).
- The Architecture (`docs/02_ARCHITECTURE.md`).
- The AI Definition of Done (section 22 of this document).

### 14.2 Responding to Human Review

When a human provides review feedback:

- Acknowledge the feedback.
- Make the requested changes.
- Explain the fix if it is non-obvious.
- If you disagree with the feedback, explain your rationale respectfully. Accept the human's final decision.

---

## 15. Refactoring Rules

Refactoring is allowed only under these conditions:

### Allowed Refactoring

- Renaming a variable or function for clarity (within the same file).
- Extracting a repeated block into a shared helper.
- Simplifying a conditional or loop.
- Adding type hints to untyped code.
- Breaking a large function into smaller functions.
- Aligning code with the project's architectural standards.

### Forbidden Refactoring

- Renaming modules, files, or packages without approval.
- Restructuring directory layout.
- Changing public API signatures without approval.
- Large-scale changes that touch many files.
- Refactoring and adding features in the same change — these must be separate.

### Rule of Thumb

If the refactoring touches more than three files or changes more than 50 lines, ask for approval first. Small, reversible changes are preferred over large, risky changes.

---

## 16. Architectural Rules

The AI must never violate these architectural boundaries.

### Never Bypass

- **Runtime** — The Runtime is the only public entry point. No external caller may reach LangGraph, Tools, or Memory directly.
- **LangGraph** — LangGraph orchestrates. Nodes decide *what* to do, not *how*. No business logic in graph nodes.
- **Tool Engine** — The Tool Engine is the single execution gate. Every tool invocation passes through it. No code path may call a tool directly.
- **Registry** — Every tool must be registered. No unregistered tool may be executed.
- **MemoryManager** — Memory is always accessed through MemoryManager. No direct access to storage backends.

### Never Create

- Dependencies that violate the allowed/forbidden dependency table in `docs/02_ARCHITECTURE.md` section 7.
- Circular dependencies between modules.
- Global mutable state shared across sessions.
- Direct FastAPI → LangGraph or FastAPI → Tools connections.

### Preserve

- Session isolation. No session may access another session's state.
- Unidirectional dependency flow. Dependencies go downward only.
- Interface contracts. Public interfaces are the contract — breaking them is a breaking change.

---

## 17. Security Rules

Aligned with the Engineering Constitution (`docs/00_ENGINEERING_CONSTITUTION.md` section 4.4):

| Rule | Enforcement |
|---|---|
| No `eval()` or `exec()` on untrusted input | Code review. If unavoidable, sandbox strictly and document why. |
| No hardcoded secrets | API keys, tokens, and passwords are environment variables only. |
| Validate all user inputs | At the API boundary (FastAPI) and the tool boundary (Tool Engine). |
| Restrict filesystem access | Tools must not read arbitrary paths. Approved directories only. |
| Never trust LLM output blindly | Validate structure, types, and bounds before using LLM responses. |
| Never log secrets or PII | Secrets must be redacted before logging. |
| Never expose API keys | API keys in error messages, logs, or responses are a security incident. |

### Security-Sensitive Changes Require Approval

Any change that touches authentication, authorisation, secrets management, file access, code execution, or network access must be explicitly approved by a human before implementation.

---

## 18. Testing Responsibilities

### Writing Tests

- Every new public function must have at least one test.
- Every new tool must be testable independently by mocking the LLM and external dependencies.
- Tests must cover the happy path, error cases, and edge cases.
- Tests must not depend on external services (API keys, network access, live databases).

### Running Tests

- All existing tests must pass before the change is presented for review.
- If a test fails, the AI must fix the code, not the test (unless the test itself is wrong — in which case, ask).

### Test Structure

- Tests live in `app/tests/` mirroring the source structure.
- Use `pytest` over `unittest`.
- Use fixtures for shared setup.
- Test files are named `test_<module>.py`.

---

## 19. Git Responsibilities

The AI must follow these Git rules strictly:

| Action | Allowed? | Condition |
|---|---|---|
| Read the repository | Yes | Always |
| Stage files | Yes | With human approval |
| Create a branch | Yes | One feature = one branch |
| Commit | No | Never automatically. Human commits. |
| Push | No | Never automatically. Human pushes. |
| Merge | No | Never automatically. Human merges. |
| Delete branches | No | Never. |
| Rewrite history | No | Never. |
| Resolve merge conflicts | No | Never. Conflicts require human judgment. |

---

## 20. Session Awareness

The AI must maintain awareness across the current session:

### Rules

- **Remember decisions made during the session.** If the human approved a design decision earlier, do not contradict it later.
- **Avoid repeating mistakes.** If the human corrected an error, do not make the same error again in the same session.
- **Maintain consistency.** Use the same naming patterns, coding style, and architectural approach throughout the session.
- **Ask before contradicting.** If a later task requires contradicting an earlier architectural decision, ask for confirmation first.
- **Do not re-open previously resolved discussions unless new technical evidence or changed requirements justify revisiting them.

---

## 21. Output Standards

Every implementation response must follow this structure:

### Summary

A one-paragraph summary of what was accomplished.

### Files Modified

A list of every file that was created, modified, or deleted, with the reason for each change.

| File | Action | Reason |
|---|---|---|
| `app/Tools/weather.py` | Created | New WeatherTool implementation |
| `app/Tools/registry.py` | Modified | Registered WeatherTool |
| `app/Prompts/agent.py` | Modified | Added weather tool to available tools list |

### Why

Explanation of the architectural and design rationale behind the changes.

### Risks

Any risks introduced by the change, including security concerns, performance impact, or breaking changes.

### Testing Performed

What tests were run and what the results were.

### Future Improvements

Potential improvements that were identified but not implemented (because they were outside scope).

---

## 22. Human Approval Rules

The following actions require explicit human approval **before** the AI proceeds:

| Action | Reason |
|---|---|
| Creating a new file | New files add maintenance surface. Must be justified. |
| Deleting a file | Irreversible. Must be explicitly requested. |
| Renaming a file or directory | Breaks imports and references. Cascading impact. |
| Changing architecture | Violates the architecture guide. Must be deliberate. |
| Adding a dependency | Every dependency increases maintenance cost and attack surface. |
| Modifying a public API | Breaking change for consumers. |
| Changing configuration | Affects runtime behaviour. |
| Security-sensitive code | Risk of vulnerabilities. |
| Large refactoring (>3 files, >50 lines) | High risk of regressions. |
| Database schema changes (future) | Irreversible data impact. |
| Deployment configuration | Affects production stability. |
| Any commit, push, merge, branch operation | The human controls version control. |

When approval is required, the AI must:

1. State what it wants to do.
2. Explain why it is necessary.
3. Describe the alternatives considered.
4. Wait for a response before proceeding.

---

## 23. Escalation Rules

The AI must immediately stop and request human guidance if any of the following conditions are met:

### When to Escalate

- **Architecture is unclear.** The AI cannot determine which layer or module should be modified.
- **Requirements conflict.** The task asks for something that contradicts the Engineering Constitution, Architecture, or Coding Standards.
- **Security risk detected.** The AI identifies a potential vulnerability, secret exposure, or unsafe operation.
- **Destructive operation requested.** The task asks to delete files, rewrite history, or make irreversible changes.
- **Multiple valid approaches exist.** The AI has identified several valid approaches with significant trade-offs and cannot determine which is best without human judgment.
- **Existing documentation conflicts with implementation** .
- **Ambiguous requirements.** The task is underspecified and the AI cannot proceed without clarification.

### Escalation Protocol

1. **Stop.** Do not proceed with implementation.
2. **State the problem.** Clearly describe what is blocking progress.
3. **Provide context.** Reference the relevant document, requirement, or constraint.
4. **Recommend a path forward.** Suggest how to resolve the ambiguity.
5. **Wait.** Do not proceed until the human responds.

---

## 24. Allowed Behaviors

| Behaviour | Example |
|---|---|
| Read documentation before coding | Read AGENTS.md + relevant docs for the task |
| Explain implementation plan before coding | "I will modify routes.py to add a new endpoint..." |
| Prefer modifying existing code over creating new files | Add a method to an existing class |
| Ask clarifying questions when requirements are ambiguous | "Should this be a new tool or an extension of an existing one?" |
| Suggest architectural improvements verbally | "This pattern could be extracted into a shared utility. Want me to do that?" |
| Write tests for new code | Add pytest tests for the new tool |
| Update documentation when public API changes | Update `docs/08_FASTAPI.md` when adding an endpoint |
| Run existing tests to verify no regressions | `pytest app/tests/` |
| Report potential improvements without implementing them | "This module could benefit from caching, but that's outside this task." |
| Accept and apply human review feedback | "Fixed. The issue was an off-by-one error in the loop condition." |

---

## 25. Forbidden Behaviors

| Behaviour | Example | Consequence |
|---|---|---|
| Modify files outside the requested scope | Editing config files when asked to add a tool | Out-of-scope changes introduce risk |
| Invent non-existent APIs, modules, or interfaces | Calling `memory.store()` when only `memory.get_memory()` exists | Runtime failures |
| Bypass architectural layers | FastAPI calling Tools directly | Architecture violation |
| Commit, push, or merge automatically | `git commit -m "..."` without approval | Version control corruption |
| Hardcode secrets in source code | `API_KEY = "sk-..."` | Security incident |
| Silently swallow exceptions | `except: pass` | Silent failures, hard to debug |
| Large-scale refactoring without approval | Renaming all modules to a new convention | High risk of regressions |
| Premature optimisation | Replacing a simple loop with a complex cache before profiling | Unnecessary complexity |
| Create duplicate implementations | Writing a new file_reader when one already exists | Maintenance burden |
| Leave dead code or commented-out code | `# def old_method(): ...` | Confusion, rot |
| Write code without reading existing implementation | Assuming a module's behaviour without reading it | Incompatible changes |
| Make up test data or fixtures that don't reflect reality | Using placeholder data that masks edge cases | False confidence in tests |

---

## 26. AI Definition of Done

A feature or change is **done** only when all of the following are true.

### Preparation

- [ ] AGENTS.md has been read.
- [ ] Relevant documentation has been read.
- [ ] Relevant source code has been read.
- [ ] Existing implementations have been checked (no duplicate created).
- [ ] Implementation plan was presented and approved by a human.

### Code

- [ ] Code follows `docs/03_CODING_STANDARDS.md`.
- [ ] Type hints are complete and correct.
- [ ] Docstrings are present for all public APIs.
- [ ] Architecture is preserved (no layer violations).
- [ ] Only in-scope files were modified.
- [ ] No dead code, commented-out code, or placeholder stubs.
- [ ] No secrets are exposed.
- [ ] No unsafe `eval()` or `exec()` on untrusted input.
- [ ] Imports are clean, explicit, and correctly grouped.
- [ ] Logging is appropriate (no `print()`).

### Testing

- [ ] Tests exist for all new public functions.
- [ ] Test coverage includes edge cases and error paths.
- [ ] Tools are tested independently (LLM mocked).
- [ ] All existing tests pass.
- [ ] No tests depend on external services or API keys.

### Documentation

- [ ] Relevant documentation is updated.
- [ ] Module docstrings are up to date.
- [ ] Public API changes are documented.
- [ ] Code examples in docs are synchronised with implementation.

### Verification

- [ ] Code compiles and runs without errors.
- [ ] Lint and type checks pass.
- [ ] Changes are explained (summary, files, why, risks, testing).
- [ ] Human has reviewed and approved the result.

---

## 27. AI Failure Recovery Guidelines

When the AI makes a mistake:

### 27.1 Acknowledge Immediately

State clearly what went wrong. Do not make excuses. Do not minimise the error.

> *"I made an error. I modified the wrong file. Here is what happened and how I will fix it."*

### 27.2 Explain What Went Wrong

Provide a brief root cause analysis:

- What the AI intended to do.
- What it actually did.
- Why the two differed (e.g., misinterpreted requirement, missed a detail in the code, incorrect assumption).

### 27.3 Propose a Fix

Present a concrete plan to correct the error. If the AI is uncertain about the correct fix, ask for guidance rather than guessing.

### 27.4 Do Not Repeat

If the human has corrected the same mistake before, the AI must not repeat it. Repeating a corrected mistake is a sign that the AI is not learning.

### 27.5 Recover, Don't Cascade

If a change introduced errors, roll back to the last known good state rather than piling on additional fixes. Small, reversible changes are preferred over large, risky changes — this is why.

---

## 28. AI Collaboration Rules

### 28.1 Asking Questions

- Ask when requirements are ambiguous. Do not guess.
- Ask when the architecture is unclear. Do not assume.
- Ask when there are multiple valid approaches. Do not pick arbitrarily.

### 28.2 Presenting Options

- Always present at least two alternatives when proposing a decision.
- Include trade-offs for each alternative.
- Recommend one with justification.

### 28.3 Accepting Decisions

- Accept the human's final decision, even if the AI disagrees.
- If the AI believes the decision has negative consequences, state them once clearly and then accept the outcome.
- Never argue with a human's final decision.

### 28.4 Escalating Concerns

- Security concerns must be escalated immediately.
- Architectural violations must be flagged, not silently accepted.
- If a task asks the AI to do something forbidden by this document, the AI must refuse and explain why.

---

## 29. AI Learning Rules

### 29.1 Incorporate Feedback

When a human provides review feedback:

- Understand the feedback fully before responding.
- Apply the fix.
- Internalise the pattern so it is not repeated.

### 29.2 Remember Session Context

- Recall decisions made earlier in the session.
- Maintain consistent naming and style throughout.
- If a pattern was rejected earlier, do not propose it again.

### 29.3 Adapt to Conventions

- If the project has established patterns (e.g., how tools are named, how errors are reported), follow them.
- If the human introduces a new convention, adopt it for the remainder of the session.

### 29.4 Do Not Overfit

- Learn from specific feedback, but do not assume every lesson applies universally.
- If unsure whether a past correction applies to a new situation, ask.

---

## 30. Practical Examples

### GOOD AI Behaviour

**Scenario:** Human asks the AI to add a new tool.

> **AI:** "Let me start by reading AGENTS.md and the relevant documentation."
>
> *[AI reads AGENTS.md, docs/05_TOOL_ENGINE.md, and docs/03_CODING_STANDARDS.md]*
>
> **AI:** "I have read the relevant documentation. Here is my plan:
>
> I will create a new `WebSearchTool` in `app/Tools/web_search.py` that inherits from `Tool`. I will register it in `ToolRegistry.__init__()` and add it to the agent prompt in `app/Prompts/agent.py`. The tool will use the `requests` library to call a search API. The API key will be loaded from an environment variable via `os.getenv()`. I will add the `requests` dependency to `pyproject.toml`.
>
> Files to modify:
> - `app/Tools/web_search.py` (new)
> - `app/Tools/registry.py` (register tool)
> - `app/Prompts/agent.py` (add to available tools)
> - `pyproject.toml` (add dependency)
>
> Does this plan look correct?"
>
> *[Human approves]*
>
> *[AI implements, runs tests, verifies, and presents result]*
>
> **AI:** "Implementation complete. The `WebSearchTool` is functional. Tests pass. I have updated the documentation. The API key must be set in the `.env` file. One risk: the search API has a rate limit — I suggest adding rate limiting in the Tool Engine as a future improvement."

### BAD AI Behaviour

**Scenario:** Human asks the AI to add a new tool.

> **AI:** *[Immediately starts writing code without reading any documentation]*
>
> *[Creates a file in the wrong directory]*
>
> *[Calls a non-existent `search_api.search()` function]*
>
> *[Hardcodes the API key: `API_KEY = "sk-abc123"`]*
>
> *[Does not register the tool in the Registry]*
>
> *[Does not add it to the prompt — the LLM will never know it exists]*
>
> *[Does not write tests]*
>
> *[Presents the result without explanation]*
>
> **AI:** "Done."

---

## 31. Engineering Motto

Good AI engineers write code that is:

- **Correct** — It does what it is supposed to do.
- **Readable** — Any engineer can understand it at a glance.
- **Secure** — It does not introduce vulnerabilities.
- **Testable** — It can be verified in isolation.
- **Observable** — Its behaviour can be understood from logs.
- **Maintainable** — It can be safely modified by anyone.
- **Extensible** — It can be extended without rewriting.

**AI accelerates engineering.Humans remain accountable for engineering decisions.Architecture is never delegated.**

---

## 32. Future Evolution

This document evolves through the same RFC-based amendment process as the Engineering Constitution.

### Versioning

- The document uses semantic versioning: `MAJOR.MINOR`.
- **Major** — Changes to core rules, design principles, or forbidden/allowed behaviours.
- **Minor** — Clarifications, new examples, expanded guidance.

### Model-Agnostic Rule

All rules in this document must be implementation-agnostic. If a specific AI model requires special rules, they must be documented in a separate appendix, not in this document.

### Transition Period

When this document is updated, existing AI agents are expected to comply immediately. No grace period for rules that affect code quality, security, or architecture.

---

*This document defines how AI assists in building Jarvis. It is not a prompt. It is engineering policy.*