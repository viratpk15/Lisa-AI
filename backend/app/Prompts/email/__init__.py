"""
Jarvis AIOS — Email Prompt Templates Package
--------------------------------------------
Provides template loading and {{var}} variable interpolation for email intelligence:
- classify_v1.txt
- summarize_v1.txt
- extract_actions_v1.txt
"""

import os
import re
from typing import Dict

_PROMPTS_DIR = os.path.dirname(os.path.abspath(__file__))
_VARIABLE_REGEX = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")


def load_email_prompt(template_name: str) -> str:
    """Load raw prompt template string by filename."""
    if not template_name.endswith(".txt"):
        template_name = f"{template_name}.txt"
    filepath = os.path.join(_PROMPTS_DIR, template_name)
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Email prompt template not found: {template_name}")
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def render_email_prompt(template_name: str, variables: Dict[str, str]) -> str:
    """Render prompt template by replacing {{var}} placeholders."""
    template = load_email_prompt(template_name)

    def _replace(match: re.Match) -> str:
        key = match.group(1)
        return variables.get(key, "")

    return _VARIABLE_REGEX.sub(_replace, template)
