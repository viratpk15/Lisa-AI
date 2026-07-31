"""
Jarvis AIOS — Prompt Studio Repository Layer
"""

from typing import List, Optional, Dict
from datetime import datetime, timezone
from app.Prompts.models import (
    Prompt,
    PromptVersion,
    PromptFolder,
    PromptTag,
    PromptTemplate,
    PromptVariable,
    PromptExecution,
    PromptEvaluation,
)


class PromptRepository:
    """In-memory & DB-backed persistence repository for Prompt Studio."""

    def __init__(self):
        self._prompts: Dict[str, Prompt] = {}
        self._versions: Dict[str, List[PromptVersion]] = {}
        self._folders: Dict[str, PromptFolder] = {}
        self._tags: Dict[str, PromptTag] = {}
        self._variables: Dict[str, List[PromptVariable]] = {}
        self._executions: Dict[str, PromptExecution] = {}
        self._evaluations: Dict[str, PromptEvaluation] = {}
        self._templates: Dict[str, PromptTemplate] = {}

        self._seed_default_templates()

    def _seed_default_templates(self):
        defaults = [
            PromptTemplate(
                id="tmpl_sql",
                name="SQL Query Generator",
                category="SQL",
                description="Generates optimized PostgreSQL queries from natural language specs.",
                system_prompt="You are an expert database administrator and SQL developer.",
                user_prompt="Write a SQL query to retrieve {{metrics}} from {{table_name}} filtered by {{date_range}}.",
                default_variables={
                    "metrics": "count(*)",
                    "table_name": "users",
                    "date_range": "last_30_days",
                },
            ),
            PromptTemplate(
                id="tmpl_rag",
                name="RAG Context Synthesizer",
                category="RAG",
                description="Synthesizes vector search context into grounded responses.",
                system_prompt="You are a RAG answer engine. Answer strictly using the provided context snippets.",
                user_prompt="Context:\n{{context}}\n\nQuestion: {{question}}",
                default_variables={
                    "context": "Jarvis AIOS v1.0 released in 2026.",
                    "question": "When was Jarvis v1.0 released?",
                },
            ),
            PromptTemplate(
                id="tmpl_code_review",
                name="Code Security Auditor",
                category="Coding",
                description="Audits Python and TypeScript code snippets for security vulnerabilities.",
                system_prompt="You are a principal security engineer. Inspect the code for SQL injection, XSS, and authorization flaws.",
                user_prompt="Audit the following {{language}} code:\n```\n{{code_snippet}}\n```",
                default_variables={
                    "language": "Python",
                    "code_snippet": "def login(user):\n    pass",
                },
            ),
            PromptTemplate(
                id="tmpl_summarize",
                name="Executive Summarizer",
                category="Summarization",
                description="Summarizes long documentation into executive key takeaways.",
                system_prompt="You are a senior analyst. Summarize documents into 3 bullet points.",
                user_prompt="Document Text:\n{{document_text}}",
                default_variables={"document_text": "Insert long document text here..."},
            ),
        ]
        for tmpl in defaults:
            self._templates[tmpl.id] = tmpl

    def save_prompt(self, prompt: Prompt) -> Prompt:
        prompt.updated_at = datetime.now(timezone.utc)
        self._prompts[prompt.id] = prompt
        return prompt

    def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        return self._prompts.get(prompt_id)

    def list_prompts(
        self,
        folder_id: Optional[str] = None,
        tag: Optional[str] = None,
        query: Optional[str] = None,
        is_favorite: Optional[bool] = None,
        is_archived: bool = False,
    ) -> List[Prompt]:
        results = [p for p in self._prompts.values() if p.is_archived == is_archived]
        if folder_id is not None:
            results = [p for p in results if p.folder_id == folder_id]
        if is_favorite is not None:
            results = [p for p in results if p.is_favorite == is_favorite]
        if tag is not None:
            results = [p for p in results if tag in (p.tags or [])]
        if query:
            q = query.lower()
            results = [p for p in results if q in p.title.lower() or q in p.description.lower()]
        return sorted(results, key=lambda x: x.updated_at, reverse=True)

    def delete_prompt(self, prompt_id: str) -> bool:
        if prompt_id in self._prompts:
            self._prompts[prompt_id].is_archived = True
            return True
        return False

    def add_version(self, version: PromptVersion) -> PromptVersion:
        if version.prompt_id not in self._versions:
            self._versions[version.prompt_id] = []
        self._versions[version.prompt_id].insert(0, version)
        return version

    def get_versions(self, prompt_id: str) -> List[PromptVersion]:
        return self._versions.get(prompt_id, [])

    def get_version(self, prompt_id: str, version_id: str) -> Optional[PromptVersion]:
        versions = self.get_versions(prompt_id)
        for v in versions:
            if v.id == version_id:
                return v
        return None

    def save_folder(self, folder: PromptFolder) -> PromptFolder:
        self._folders[folder.id] = folder
        return folder

    def list_folders(self) -> List[PromptFolder]:
        return list(self._folders.values())

    def list_templates(self) -> List[PromptTemplate]:
        return list(self._templates.values())

    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        return self._templates.get(template_id)

    def save_execution(self, execution: PromptExecution) -> PromptExecution:
        self._executions[execution.id] = execution
        return execution

    def list_executions(self, prompt_id: Optional[str] = None) -> List[PromptExecution]:
        if prompt_id:
            return [e for e in self._executions.values() if e.prompt_id == prompt_id]
        return sorted(self._executions.values(), key=lambda x: x.executed_at, reverse=True)

    def save_evaluation(self, evaluation: PromptEvaluation) -> PromptEvaluation:
        self._evaluations[evaluation.id] = evaluation
        return evaluation

    def get_evaluation(self, execution_id: str) -> Optional[PromptEvaluation]:
        for ev in self._evaluations.values():
            if ev.execution_id == execution_id:
                return ev
        return None
