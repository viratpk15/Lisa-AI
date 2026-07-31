"""
Jarvis AIOS — Prompt Studio Unit Tests
"""

import pytest
from app.Prompts.prompt_manager import PromptManager


@pytest.fixture
def manager():
    return PromptManager()


def test_extract_variables(manager):
    text = "Hello {{name}}, welcome to {{company}}! Please review {{code_snippet}}."
    vars_list = manager.extract_variables(text)
    assert vars_list == ["name", "company", "code_snippet"]


def test_create_and_get_prompt(manager):
    res = manager.create_prompt(
        title="Test Prompt",
        description="A test prompt for unit testing",
        system_prompt="You are a test assistant.",
        user_prompt="Hello {{user_name}}",
        tags=["test", "unit"],
    )
    prompt = res["prompt"]
    version = res["version"]

    assert prompt.title == "Test Prompt"
    assert version.version_tag == "v1.0.0"

    details = manager.get_prompt_details(prompt.id)
    assert details is not None
    assert details["prompt"].id == prompt.id
    assert details["variables"] == ["user_name"]


def test_commit_and_restore_version(manager):
    res = manager.create_prompt(title="Versioned Prompt", user_prompt="User v1")
    prompt = res["prompt"]

    v2 = manager.commit_version(
        prompt_id=prompt.id,
        system_prompt="System v2",
        user_prompt="User v2 {{var}}",
        commit_message="Added {{var}}",
    )
    assert v2.version_tag == "v1.2.0"

    details = manager.get_prompt_details(prompt.id)
    assert details["current_version"].id == v2.id

    # Restore v1
    v1_id = res["version"].id
    restored = manager.restore_version(prompt.id, v1_id)
    assert restored.id == v1_id

    details_restored = manager.get_prompt_details(prompt.id)
    assert details_restored["current_version"].id == v1_id


def test_run_and_evaluate_playground(manager):
    res = manager.create_prompt(title="Playground Prompt", user_prompt="Analyze {{item}}")
    prompt = res["prompt"]

    execution = manager.run_playground(
        prompt_id=prompt.id,
        system_prompt="System instructions",
        user_prompt="Analyze {{item}}",
        variables={"item": "Server Logs"},
        model="gpt-4o",
    )

    assert execution.status == "SUCCESS"
    assert "Server Logs" in execution.raw_output
    assert execution.latency_ms > 0

    evaluation = manager.evaluate_execution(
        execution_id=execution.id,
        correctness=9.8,
        hallucination=0.0,
    )
    assert evaluation.execution_id == execution.id
    assert evaluation.correctness_score == 9.8


def test_clone_template(manager):
    templates = manager.repo.list_templates()
    assert len(templates) > 0

    target = templates[0]
    cloned_res = manager.clone_template(target.id, title_override="My Custom SQL Gen")
    assert cloned_res is not None
    assert cloned_res["prompt"].title == "My Custom SQL Gen"
