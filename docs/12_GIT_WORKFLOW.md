# Jarvis AIOS — Git Workflow

**Version:** 1.0  
**Status:** Ratified  

---

## 1. Purpose

This document defines the official Git workflow for the Jarvis AIOS project.

It is an engineering policy — not a Git tutorial. It applies equally to human developers and AI coding assistants. Every contributor must follow these rules.

When the Git Workflow conflicts with the Engineering Constitution (`docs/00_ENGINEERING_CONSTITUTION.md`), the constitution wins.

---

## 2. Scope

This document applies to all repositories in the Jarvis project.

It covers:

- Branching, committing, and merging.
- Pull requests and code review.
- Release and hotfix workflows.
- Rollback and conflict resolution.
- AI assistant Git behaviour.

It does **not** cover:

- CI/CD pipeline configuration (documented separately).
- Issue tracking or project board workflows.
- Deployment environments and infrastructure.

---

## 3. Git Philosophy

Every Git operation in Jarvis is guided by these principles:

| Principle | Meaning |
|---|---|
| **Main is always deployable** | The `main` branch must be in a releasable state at all times. Every commit on `main` is a candidate for production. |
| **One feature = one branch** | Every logical unit of work gets its own branch. No mixing unrelated changes. |
| **Small, reversible commits** | Prefer many small commits over one large commit. A commit should be easy to understand and easy to revert. |
| **Never rewrite shared history** | Once a commit is pushed to a shared branch, it is immutable. Use `git revert`, not `git reset`. |
| **Automation assists, humans decide** | CI automates checks. AI assists with implementation. Humans control what reaches `main`. |

---

## 4. Branch Strategy

Jarvis uses **GitHub Flow** with feature branches.

### Rules

- The `main` branch is the single source of truth. It is always deployable.
- All development happens on feature branches branched from `main`.
- Feature branches merge back into `main` through pull requests.
- No long-lived branches. A branch exists for the duration of a single feature or fix.
- No `develop`, `staging`, or `release` branches. Environments are deployed from `main` using Git tags.

### Branch Lifetime

```
main  ──●────●────●────●────●────●────●────●────●──
         \       /   \       /   \       /
feature   ●──●──●     ●──●──●     ●──●──●
```

---

## 5. Branch Naming Convention

All branches must use a prefix-based naming convention:

| Prefix | Purpose | Example |
|---|---|---|
| `feature/` | New features and enhancements | `feature/tool-web-search` |
| `fix/` | Bug fixes | `fix/calculator-division-by-zero` |
| `docs/` | Documentation changes | `docs/api-endpoints` |
| `refactor/` | Code refactoring (no behaviour change) | `refactor/tool-engine` |
| `hotfix/` | Urgent production fixes | `hotfix/critical-security-patch` |
| `experiment/` | Experimental or exploratory work | `experiment/streaming-prototype` |

### Rules

- Use lowercase with hyphens as separators.
- Keep names descriptive but concise (3-5 words maximum after the prefix).
- Include the issue number if applicable: `feature/42-tool-web-search`.
- Never use personal or author names in branch names.

### Examples

```bash
# Good
git checkout -b feature/tool-web-search
git checkout -b fix/calculator-division-by-zero
git checkout -b hotfix/security-patch-cve-2024-0001

# Bad
git checkout -b my-feature
git checkout -b fix
git checkout -b virats-branch
```

---

## 6. Commit Message Standard

Jarvis uses **Conventional Commits 1.0.0** for all commit messages.

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | When to Use | Example |
|---|---|---|
| `feat` | A new feature for the user or system | `feat(tools): add web search tool` |
| `fix` | A bug fix | `fix(engine): handle division by zero in calculator` |
| `docs` | Documentation changes | `docs(api): document chat endpoint` |
| `refactor` | Code restructuring without behaviour change | `refactor(registry): extract tool discovery logic` |
| `test` | Adding or modifying tests | `test(engine): add unit tests for tool execution` |
| `chore` | Maintenance tasks, dependency updates | `chore(deps): update langgraph to 1.2.9` |
| `perf` | Performance improvements | `perf(memory): cache session lookups` |
| `ci` | CI/CD configuration changes | `ci(actions): add lint check to PR workflow` |
| `build` | Build system or dependency changes | `build(pyproject): add requests dependency` |
| `revert` | Reverting a previous commit | `revert: rollback streaming prototype` |

### Scope

The scope is optional but recommended. It should be a noun representing the module or area affected:

- `tools`, `engine`, `registry`, `memory`, `llm`, `langgraph`, `fastapi`, `runtime`, `api`, `deps`, `config`, `docs`

### Description

- Imperative mood ("add", "fix", "remove" — not "added", "fixed", "removed").
- Lowercase after the type/scope.
- No period at the end.
- Maximum 72 characters.

### Body

- Optional. Use when the change needs additional explanation.
- Separate from the subject by a blank line.
- Wrap at 72 characters.
- Explain *why* the change was made, not *what* (the code shows what).

### Footer

- Optional. Use for breaking changes and issue references.
- Breaking changes: `BREAKING CHANGE:` or append `!` after type/scope.
- Issue references: `Closes #42`, `Refs #128`.

### Examples

```bash
# Simple commit
git commit -m "feat(tools): add web search tool"

# With scope and description
git commit -m "fix(engine): handle division by zero in calculator tool"

# With body
git commit -m "refactor(registry): extract tool discovery logic

Separate tool discovery from registration to support dynamic plugin loading in the future."

# Breaking change
git commit -m "feat(api)!: change chat response format

BREAKING CHANGE: The chat response now returns a structured object instead of a plain string."

# With issue reference
git commit -m "fix(memory): correct session isolation bug

Closes #42"
```

---

## 7. Development Workflow

The standard workflow for every feature, fix, or change:

```
Step 1:  git checkout -b feature/<name>        # Create branch from main
Step 2:  (make changes)                         # Implement
Step 3:  git add <files>                        # Stage related changes
Step 4:  git commit -m "feat(scope): ..."       # Conventional Commit
Step 5:  git push origin feature/<name>         # Push branch
Step 6:  (open pull request)                    # PR with checklists
Step 7:  (request review)                       # At least one reviewer
Step 8:  (address feedback)                     # Additional commits
Step 9:  (squash merge to main)                 # Merge
Step 10: git branch -d feature/<name>           # Delete local branch
Step 11: (delete remote branch)                 # Clean up
```

### Rules

- Always start from the latest `main`: `git checkout main && git pull` before branching.
- Keep your branch up to date with `main` by rebasing (feature branches only): `git rebase main`.
- Never merge `main` into your feature branch — rebase instead.
- Never commit directly to `main`.

---

## 8. Pull Request Workflow

### PR Title

The PR title must follow Conventional Commits format, as it will become the squash merge commit message:

```
feat(tools): add web search tool
```

### PR Description

Every PR description must include:

- **Summary** — What does this change do? (One paragraph.)
- **Motivation** — Why is this change needed?
- **Testing** — What tests were run and what were the results?
- **Related Issues** — Links to any related issues: `Closes #42`.

### Required Checklists

Every PR must include these checklists (completed by the author):

#### Review Checklist

- [ ] Code follows `docs/03_CODING_STANDARDS.md`.
- [ ] Architecture is preserved (no layer violations).
- [ ] No dead code, commented-out code, or placeholder stubs.
- [ ] Type hints are complete and correct.
- [ ] Docstrings are present for all public APIs.
- [ ] Imports are clean, explicit, and correctly grouped.

#### Testing Checklist

- [ ] Tests exist for all new public functions.
- [ ] Tests pass (local and CI).
- [ ] Edge cases and error paths are covered.
- [ ] Tests do not depend on external services or API keys.
- [ ] No regressions introduced.

#### Documentation Checklist

- [ ] Relevant `docs/` files are updated.
- [ ] Module docstrings are up to date.
- [ ] Public API changes are documented.
- [ ] Code examples in docs are synchronised with implementation.

#### Security Checklist

- [ ] No secrets are exposed.
- [ ] No unsafe `eval()`/`exec()` on untrusted input.
- [ ] No hardcoded credentials, API keys, or tokens.
- [ ] All user inputs are validated.
- [ ] LLM output is validated before use.

---

## 9. Code Review Process

### Review Requirements

- Every PR requires at least one reviewer approval before merging.
- AI-generated code requires human review — always.
- Security-sensitive changes require review by someone with security expertise.
- Architectural changes require review by someone familiar with the project architecture.

### What Reviewers Verify

| Concern | What to Check |
|---|---|
| **Architecture Compliance** | No layer violations. No bypassing of Runtime, LangGraph, Tool Engine, or Registry. Dependencies respect the allowed/forbidden table. |
| **Coding Standards Compliance** | Type hints, docstrings, naming, imports, error handling, logging. |
| **AI Agent Rules Compliance** | If AI-generated, verify it follows `docs/14_AI_AGENT_RULES.md`. |
| **Security Implications** | No secrets, no unsafe eval/exec, inputs validated, LLM output validated. |
| **Performance Impact** | No unnecessary LLM calls, no N+1 queries, no blocking I/O in hot paths. |
| **Backward Compatibility** | Public APIs preserved. Breaking changes justified and documented. |
| **Documentation Completeness** | Docs updated, docstrings present, examples synchronised. |

### Review Process

1. Reviewer is assigned or requested.
2. Reviewer reads the PR, examines changed files, runs the code if needed.
3. Reviewer leaves comments on specific lines or general feedback.
4. Author addresses feedback with additional commits (no force-push).
5. Reviewer approves once all concerns are resolved.
6. Author merges (or requests merge from a maintainer).

### Review Etiquette

- Be specific and constructive in feedback.
- Explain *why* something should change, not just *what*.
- Distinguish between required changes and optional suggestions.
- Authors: respond to every comment, even if just acknowledging.

---

## 10. Merge Strategy

### Default: Squash Merge

Most feature branches use **squash merge**. This creates a single commit on `main` with the PR title as the commit message.

```
Before merge:
main:      ●────●
feature:        ●──●──●
                           ↓ squash merge
After merge:
main:      ●────●────●
                      ↑ single commit
```

**When to use:** All standard features, fixes, documentation, refactoring.

### Exception: Preserve History

When the individual commits tell an important story (e.g., a complex refactoring where each intermediate step is meaningful), use **merge commit** to preserve history.

**When to use:** Release branches, complex multi-step refactorings, experimental branches being merged after review.

### Rules

- **Never merge failing CI.** If CI fails, fix it before merging.
- **Never merge without approval.** At least one reviewer must approve.
- **Never merge your own PR without review.** Even trivial changes need a second pair of eyes.
- **Delete the branch after merge.** Both locally and remotely.

---

## 11. Branch Protection Policy

The `main` branch is protected. The following rules are enforced at the repository level:

| Rule | Enforcement |
|---|---|
| Direct pushes to `main` | **Prohibited.** All changes go through PRs. |
| PR approval required | At least one approved review. |
| Passing CI required | All CI checks must pass before merge. |
| Up-to-date branch required | Feature branch must be up to date with `main` before merge. |
| Force pushes to `main` | **Prohibited.** |
| Branch deletion | Only after successful merge. |

These protections are configured in the repository settings and cannot be bypassed by individual contributors.

---

## 12. Release Strategy

### Release Process

1. Ensure `main` is in a deployable state (all CI passes, no known regressions).
2. Determine the new version number according to Semantic Versioning (see section 14).
3. Update the version in `pyproject.toml`.
4. Commit: `chore(release): bump version to X.Y.Z`.
5. Create a signed Git tag: `git tag -s vX.Y.Z -m "vX.Y.Z"`.
6. Push the tag: `git push origin vX.Y.Z`.
7. Generate or update the changelog from commit history since the last tag.
8. Deploy the tagged commit to the target environment.
9. Verify the deployment with a post-release checklist.

### Release Candidate Workflow

For significant releases:

1. Create a release branch: `git checkout -b release/X.Y.Z`.
2. Tag release candidates: `git tag -s vX.Y.Z-rc.1`.
3. Test the RC in a staging environment.
4. Fix issues on the release branch.
5. Tag additional RCs as needed: `vX.Y.Z-rc.2`, `vX.Y.Z-rc.3`.
6. When stable, merge the release branch into `main`.
7. Tag the final release: `git tag -s vX.Y.Z`.

### Post-Release Verification Checklist

- [ ] Version number is correct in `pyproject.toml`.
- [ ] Tag exists and is signed.
- [ ] Changelog is updated.
- [ ] All CI checks pass on the tagged commit.
- [ ] Deployment succeeded.
- [ ] Health check endpoint returns 200.
- [ ] Basic smoke test passes (chat endpoint responds).

---

## 13. Hotfix Workflow

When a critical bug must be fixed in production immediately:

```
1. git checkout v<current-release-tag>
2. git checkout -b hotfix/<description>
3. (fix the bug)
4. git add <files>
5. git commit -m "fix(scope): description"
6. git push origin hotfix/<description>
7. (open PR targeting main)
8. (expedited review — same standards, faster timeline)
9. (merge to main)
10. git tag -s v<incremented-patch-version>
11. git push origin v<incremented-patch-version>
12. (deploy the tagged version)
```

### Rules

- Hotfix branches use the `hotfix/` prefix.
- The same code review and testing standards apply — but the timeline is expedited.
- After merging to `main`, the fix is forward-merged into any active release branches.
- A hotfix that bypasses review is a security incident, not a workflow.

---

## 14. Versioning Strategy

Jarvis follows **Semantic Versioning 2.0.0**.

### Format

```
MAJOR.MINOR.PATCH
```

| Component | When to Increment | Example |
|---|---|---|
| **MAJOR** | Breaking changes to public API or architecture | 2.0.0, 3.0.0 |
| **MINOR** | New features, backward compatible | 1.1.0, 1.2.0 |
| **PATCH** | Bug fixes, backward compatible | 1.0.1, 1.0.2 |

### Pre-Release Tags

Append a dash and identifier for pre-release versions:

- `1.0.0-rc.1` — Release Candidate 1
- `1.0.0-alpha.1` — Alpha release
- `1.0.0-beta.1` — Beta release

### Version Location

The canonical version is stored in `backend/pyproject.toml`:

```toml
[project]
version = "1.0.0"
```

Every release also creates a signed Git tag matching the version:

```bash
git tag -s v1.0.0 -m "v1.0.0"
```

---

## 15. Dependency Update Policy

### General Rules

- Update dependencies through dedicated PRs — not mixed with feature work.
- Review release notes and changelogs before updating.
- Test compatibility: run the full test suite after any dependency update.
- Security updates receive priority — they should be handled within 48 hours.
- Remove unused dependencies regularly. A dependency that is not imported is a liability.

### Dedicated Dependency PRs

```
git checkout -b chore/deps/update-langgraph
# Update pyproject.toml and uv.lock
git add pyproject.toml uv.lock
git commit -m "chore(deps): update langgraph to 1.3.0"
git push origin chore/deps/update-langgraph
```

### Version Pinning

- Specify minimum versions in `pyproject.toml`: `langgraph>=1.2.9`.
- Exact versions are locked in `uv.lock` (or equivalent lock file).
- Never pin to an exact version in `pyproject.toml` unless there is a specific compatibility reason.

---

## 16. Conflict Resolution

### Principles

- Merge conflicts indicate coordination failure. Two branches modified the same code in conflicting ways.
- Conflicts are resolved by the **PR author**, not the reviewer.
- Communicate with the other party whose changes conflicted — they may have context you lack.

### Resolution Process

1. Update your branch with the latest `main`: `git rebase main`.
2. Git will pause at each conflict.
3. Resolve each conflict in the affected files. Use `git mergetool` if desired.
4. After resolving: `git add <resolved-files>` and `git rebase --continue`.
5. Push the resolved branch: `git push --force-with-lease` (only for feature branches).

### Rules

- **Never force-push to a shared branch** (main, release branches).
- **Never force-push to resolve conflicts** on a branch that others have also branched from.
- If conflicts are extensive and complex, consider creating a new branch and manually applying changes rather than resolving a tangled conflict.
- If you are unsure about a conflict resolution, ask the original author of the conflicting code.

---

## 17. Rollback Strategy

### Principle

Shared branches are rolled back using **`git revert`**. Never `git reset` or `git push --force` on shared branches.

`git revert` creates a new commit that undoes the changes of a previous commit. It is safe because it does not rewrite history.

### Revert a Feature

```bash
git checkout main
git pull
git revert <commit-hash-of-feature-merge>
# Git opens an editor for the revert commit message
# Save and close
git push origin main
```

### Revert a Hotfix

```bash
git checkout main
git pull
git revert <commit-hash-of-hotfix-merge>
git push origin main
git tag -s v<incremented-patch-version>
git push origin v<incremented-patch-version>
```

### Revert a Release

```bash
git checkout main
git pull
git revert <commit-hash-of-release-merge>
git push origin main
git tag -s v<incremented-patch-version>
git push origin v<incremented-patch-version>
# Communicate the reversal to the team
```

### What Is Forbidden

| Action | Why Forbidden |
|---|---|
| `git reset --hard` on shared branch | Destroys commits that others may have based work on. |
| `git push --force` on shared branch | Rewrites history. Others' branches will be incompatible. |
| `git commit --amend` on pushed commits | Changes the commit hash. Only safe for unpushed commits. |

### Exception

Repository administrators may use `git push --force` under emergency procedures (e.g., a secret was committed and must be removed from history). This is rare and must be communicated to the entire team.

---

## 18. Working with AI Assistants

### AI Git Rules

AI coding assistants contributing to Jarvis must follow these Git rules:

| Action | Allowed? | Condition |
|---|---|---|
| Read the repository | Yes | Always |
| Stage files (`git add`) | Yes | With human approval |
| Create a branch | Yes | One feature = one branch |
| Commit (`git commit`) | **No** | Never automatically. Human commits. |
| Push (`git push`) | **No** | Never automatically. Human pushes. |
| Merge (`git merge`) | **No** | Never automatically. Human merges. |
| Delete branches | **No** | Never. |
| Rewrite history | **No** | Never. |
| Resolve merge conflicts | **No** | Never. Conflicts require human judgment. |
| Interactive rebase | **No** | Never. |
| Cherry-pick commits | **No** | Unless explicitly instructed by a human. |
| Modify Git configuration | **No** | Never. |

### Why

AI agents lack the context and judgment needed for Git operations. A mistaken push, merge, or history rewrite can affect every contributor. All Git operations that modify the remote repository require human intent and human execution.

---

## 19. Commit Hygiene

### Rules

- **One logical change per commit.** A commit should represent a single, coherent change. If you find yourself writing "and" in the commit message, split the commit.
- **Do not mix refactoring with features.** If a change includes both refactoring and new functionality, split them into separate commits. This makes review easier and reverts safer.
- **Avoid formatting-only commits** unless they are dedicated to formatting (e.g., applying Black across the codebase). Do not mix formatting changes with logic changes.
- **Keep commit history understandable.** A good commit history tells the story of how the code evolved. Someone reading `git log` should understand the progression.
- **Write commits that can be reverted independently.** Each commit should be self-contained enough that it can be reverted without breaking unrelated code.

### Examples

```bash
# Good — one logical change per commit
git commit -m "refactor(registry): extract validation logic"
git commit -m "feat(tools): add web search tool"

# Bad — mixing concerns in one commit
git commit -m "refactor and add feature and fix formatting"
```

---

## 20. Repository Hygiene

### Branch Cleanup

- Delete branches after they are merged. Both locally and remotely.
- Stale branches (no activity for 30+ days) should be reviewed and either deleted or justified.
- Never leave experimental branches indefinitely. If an experiment is abandoned, delete it.

### `.gitignore` Discipline

- Keep `.gitignore` synchronised across all repositories.
- Never commit: virtual environments (`.venv/`, `venv/`), Python cache (`__pycache__/`, `*.pyc`), IDE settings (`.vscode/`, `.idea/`), environment files (`.env`), OS files (`.DS_Store`).
- Commit intentionally versioned artifacts only.

### What Not to Commit

| Artifact | Action |
|---|---|
| Virtual environments | Never commit. Add to `.gitignore`. |
| Compiled Python files (`__pycache__/`) | Never commit. Add to `.gitignore`. |
| IDE settings (`.vscode/`, `.idea/`) | Never commit unless shared intentionally (e.g., shared run configurations). |
| Environment files (`.env`) | Never commit. Contains secrets. |
| OS files (`.DS_Store`) | Never commit. Add to `.gitignore`. |
| Large binary files | Never commit without Git LFS. |
| Dependency lock files (`uv.lock`, `package-lock.json`) | Commit. These are required for reproducible builds. |

---


## 22. Code Review Process (Expanded)

Beyond the checklists in section 8, reviewers must verify:

| Verification | What to Check |
|---|---|
| **Architecture Compliance** | No layer violations. Dependencies respect allowed/forbidden table. |
| **Coding Standards Compliance** | Follows `docs/03_CODING_STANDARDS.md` in full. |
| **AI Agent Rules Compliance** | If AI-generated, follows `docs/14_AI_AGENT_RULES.md`. |
| **Security Implications** | No secrets, no unsafe operations, inputs validated. |
| **Performance Impact** | No unnecessary LLM calls, no N+1 problems, no blocking I/O in hot paths. |
| **Backward Compatibility** | Public APIs unchanged. Breaking changes justified. |
| **Documentation Completeness** | Docs updated, docstrings present, examples accurate. |

Reviewers should also verify that the PR size is reasonable. A PR touching 30+ files is likely too large and should have been split.

---

## 23. Engineering Metrics

These are aspirational goals, not strict requirements:

| Metric | Goal | Why |
|---|---|---|
| **PR Size** | < 300 lines changed per PR | Smaller PRs are reviewed faster and more thoroughly. |
| **Review Cycle Time** | < 24 hours for first review | Fast feedback keeps momentum. |
| **Merge Conflict Frequency** | < 1 per 10 PRs | Frequent conflicts indicate coordination problems. |
| **CI Success Rate** | > 95% on `main` | Main should almost always be green. |
| **Main Branch Releasability** | 100% of the time | Main is always deployable — this is non-negotiable. |

---

## 24. Allowed vs Forbidden Git Actions

| Action | Allowed? | Notes |
|---|---|---|
| `git clone` | Yes | |
| `git checkout -b` | Yes | Must follow naming convention. |
| `git add` | Yes | Stage related changes only. |
| `git commit` | Yes | Must use Conventional Commits format. |
| `git push` (feature branch) | Yes | After commit. |
| `git push` (main) | **No** | Only through PR merge. |
| `git merge` (via PR) | Yes | Through GitHub UI only. |
| `git merge` (local) | **No** | Use rebase instead for feature branches. |
| `git rebase` (feature branch) | Yes | Onto `main` only. |
| `git rebase` (shared branch) | **No** | Rewrites history. |
| `git reset` (unpushed) | Yes | Clean up local commits before pushing. |
| `git reset` (pushed) | **No** | Use `git revert` instead. |
| `git revert` | Yes | Preferred method for undoing changes. |
| `git push --force` | **No** | Never on shared branches. |
| `git push --force-with-lease` | With caution | Only on feature branches after rebase. |
| `git branch -d` | Yes | After merge only. |
| `git tag` | Yes | Signed tags for releases only. |
| `git commit --amend` | Yes | Only if commit has not been pushed. |
| `git cherry-pick` | With caution | Only when explicitly needed and understood. |

---

## 25. Practical Examples

### GOOD Workflow: Adding a New Feature

```
1. git checkout main && git pull
2. git checkout -b feature/tool-web-search
3. (implement the tool, write tests, update docs)
4. git add app/Tools/web_search.py app/Tools/registry.py app/Prompts/agent.py
5. git commit -m "feat(tools): add web search tool"
6. git add tests/test_Tools/test_web_search.py
7. git commit -m "test(tools): add tests for web search tool"
8. git push origin feature/tool-web-search
9. (open PR with checklists, request review)
10. (reviewer approves, address any feedback with additional commits)
11. (squash merge to main)
12. git checkout main && git pull
13. git branch -d feature/tool-web-search
```

### GOOD Workflow: Fixing a Bug

```
1. git checkout main && git pull
2. git checkout -b fix/calculator-division-by-zero
3. (fix the bug)
4. git add app/Tools/calculator.py
5. git commit -m "fix(calculator): handle division by zero"
6. git push origin fix/calculator-division-by-zero
7. (open PR, request review)
8. (merge, delete branch)
```

### BAD Workflow: Everything Wrong

```
1. git checkout main
2. (make changes directly on main — NO!)
3. git add .
4. git commit -m "fix stuff"  — NO: vague message
5. git push origin main        — NO: breaks main
6. (CI fails, main is broken, no review happened)
```

### BAD Workflow: Sloppy Branching

```
1. git checkout -b my-branch                    — NO: wrong naming
2. (work on two unrelated features — NO)
3. git add -A                                    — NO: stages everything
4. git commit -m "updates"                       — NO: meaningless message
5. git push origin my-branch
6. (open PR with no description, no checklists — NO)
7. (merge without review — NO)
8. (forget to delete branch — NO)
```

---

## 26. Git Definition of Done

A Git operation is **done** only when all of the following are true:

### Branch

- [ ] Branch was created from the latest `main`.
- [ ] Branch name follows the naming convention.
- [ ] Branch contains only changes related to a single feature or fix.

### Commits

- [ ] All commits use Conventional Commits format.
- [ ] Each commit represents one logical change.
- [ ] No mixing of refactoring and features in the same commit.
- [ ] No secrets in commit history.

### Pull Request

- [ ] PR title follows Conventional Commits format.
- [ ] PR description includes summary, motivation, and testing.
- [ ] All four checklists (Review, Testing, Documentation, Security) are completed.
- [ ] At least one reviewer has approved.

### CI

- [ ] All CI checks pass (lint, test, build, security scan).
- [ ] Branch is up to date with `main`.

### Merge

- [ ] Merge strategy is appropriate (squash by default).
- [ ] PR is merged, not pushed directly.
- [ ] Branch is deleted after merge (local and remote).
- [ ] If a release: tag exists, is signed, and changelog is updated.

---

## 27. Anti-Patterns

| Anti-Pattern | Why | Solution |
|---|---|---|
| **Committing directly to main** | Bypasses review and CI. Breaks the deployable-main invariant. | Always use feature branches and PRs. |
| **Large PRs (>500 lines)** | Difficult to review. High risk of missed issues. | Split into smaller, logical PRs. |
| **Vague commit messages** | Impossible to understand the intent from history. | Use Conventional Commits. |
| **Mixing unrelated changes** | Impossible to revert one without reverting the other. | One branch = one feature. One commit = one change. |
| **Long-lived branches** | Divergent from main. High conflict risk. | Merge or rebase frequently. Delete stale branches. |
| **Force-pushing to shared branches** | Destroys history. Breaks others' work. | Never. Use `git revert` instead. |
| **Merging failing CI** | Breaks the deployable-main invariant. | Fix CI first, then merge. |
| **Not deleting merged branches** | Repository clutter. Stale branches accumulate. | Delete after merge. Automate if possible. |
| **Rebasing shared branches** | Rewrites history. Causes conflicts for everyone. | Never. Only rebase feature branches. |
| **AI committing or pushing without human approval** | Loses human accountability for repository state. | AI stages and plans; humans execute Git operations. |

---

## 28. Engineering Motto

**Every branch has a purpose.**

**Every commit tells a story.**

**Main is always releasable.**

**History is preserved.**

**Quality is never bypassed for speed.**

---

## 29. Future Evolution

This document evolves through the same RFC-based amendment process as the Engineering Constitution.

### Versioning

- The document uses semantic versioning: `MAJOR.MINOR`.
- **Major** — Changes to branch strategy, merge strategy, or core workflow.
- **Minor** — Clarifications, new sections, expanded guidance.

### Transition Period

When this document is updated, existing branches and PRs should conform as soon as practical. Long-running branches may be exempted until their next merge.

---

*This Git workflow defines how code moves from development to production in Jarvis. It is an engineering policy, not a suggestion.*