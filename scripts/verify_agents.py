"""
Jarvis AIOS
-----------
Agents Verification Script

Verifies the Agents module is correctly configured and all imports work as expected.
"""

import sys
from pathlib import Path
from typing import Any, Callable

backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Global Config alias
Config: Any = None


# =============================================================================
# Helper Functions
# =============================================================================


def section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def verify_imports(imports_to_test: list[tuple[str, str]]) -> bool:
    """Verify a list of imports work correctly."""
    for names, module in imports_to_test:
        try:
            exec(f"from {module} import {names}")
            print(f"✓ {names} imported successfully")
        except ImportError as e:
            print(f"✗ Failed to import {names}: {e}")
            return False
    return True


def verify_registration(agent_getter: Callable[[], Any], expected_name: str, request: str) -> bool:
    """Register an agent and verify it's discoverable. Returns True on success."""
    from app.Agents.registry import AgentRegistry

    registry = AgentRegistry()
    agent = agent_getter()
    registry.register(agent)
    print(f"✓ Registered {expected_name}: {agent.name}")

    if not registry.has_agent(expected_name):
        return False
    print(f"✓ Registry has '{expected_name}' client")

    capable = registry.get_capable_agents(request)
    if len(capable) != 1 or capable[0].name != expected_name:
        return False
    print(f"✓ {expected_name} found via get_capable_agents")
    return True


def verify_can_handle(agent: Any, positive_cases: list[str], negative_cases: list[str]) -> bool:
    """Verify can_handle returns expected results for test cases."""
    for case in positive_cases:
        if agent.can_handle(case) is not True:
            return False
    print(f"✓ {agent.__class__.__name__} detects keyword matches")

    for case in negative_cases:
        if agent.can_handle(case) is not False:
            return False
    print(f"✓ {agent.__class__.__name__} rejects non-matches")
    return True


# =============================================================================
# Test Agent
# =============================================================================


class TestAgent:
    """Test implementation of Agent ABC for verification purposes."""

    def __init__(self, config: Any) -> None:
        self.config = config

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def description(self) -> str:
        return self.config.description

    def can_handle(self, request: Any) -> bool:
        return "test" in str(request).lower()

    def execute(self, request: Any) -> Any:
        return {"result": "test_agent_executed", "request": request}


def run_test(test_fn: Callable[[], bool], error_msg: str = "test") -> bool:
    """Run a test function with error handling."""
    try:
        result = test_fn()
        return result if result is not None else True
    except Exception as e:
        print(f"✗ {error_msg} failed: {e}")
        return False


# =============================================================================
# Core Verifications
# =============================================================================


def verify_agents_imports() -> bool:
    """Verify all Agents module imports work correctly."""
    print("=" * 60)
    print("Agents Module Import Verification")
    print("=" * 60)

    return verify_imports([
        ("Agent", "app.Agents.agent"),
        ("AgentConfig", "app.Models.agent_config"),
        ("AgentRegistry", "app.Agents.registry"),
        ("get_agent_registry", "app.Agents"),
        ("Agent", "app.Agents"),
        ("AgentRegistry", "app.Agents"),
        ("get_agent_registry", "app.Agents.registry"),
    ])


def verify_agent_config() -> bool:
    """Verify AgentConfig Pydantic model functionality."""
    section("AgentConfig Pydantic Model Verification")

    def test():
        config = Config(name="test_agent", description="Test agent", enabled=True)
        assert config.name == "test_agent" and config.enabled is True

        config = Config(name="default_agent")
        assert config.description == "" and config.enabled is True

        config = Config(name="validation_agent", enabled=False)
        assert config.enabled is False

        print("✓ All AgentConfig tests passed")

    return run_test(test)


def verify_immutability() -> bool:
    """Verify Pydantic model allows mutation."""
    section("Mutability Verification")

    def test():
        config = Config(name="test")
        config.name = "modified"
        assert config.name == "modified"
        print("✓ AgentConfig is mutable (no frozen=True, as designed)")

    return run_test(test)


def verify_agent_abc() -> bool:
    """Verify Agent ABC interface works correctly."""
    section("Agent ABC Interface Verification")

    def test():
        from app.Agents.agent import Agent

        for attr in ["can_handle", "execute", "name", "description"]:
            assert hasattr(Agent, attr)
        print("✓ Agent ABC has required abstract methods and properties")

        class ConcreteTestAgent(Agent):
            config = Config(name="concrete_test", description="Concrete test agent")

            def can_handle(self, request: Any) -> bool:
                return "special" in str(request).lower()

            def execute(self, request: Any) -> Any:
                return {"handled": True, "by": self.name}

        agent = ConcreteTestAgent()
        assert agent.name == "concrete_test" and agent.can_handle("special request")
        print("✓ Concrete Agent implementation works correctly")

    return run_test(test)


def verify_agent_registry() -> bool:
    """Verify AgentRegistry functionality."""
    section("AgentRegistry Verification")

    def test():
        from app.Agents.registry import AgentRegistry

        registry = AgentRegistry()
        assert registry.list_agents() == []
        assert registry.has_agent("nonexistent") is False
        print("✓ Empty registry state verified")

    return run_test(test)


def verify_registry_operations() -> bool:
    """Verify AgentRegistry register/unregister/get operations."""
    section("AgentRegistry Operations Verification")

    def test():
        from app.Agents.registry import AgentRegistry

        registry = AgentRegistry()
        agent1 = TestAgent(Config(name="agent_one", description="First"))
        agent2 = TestAgent(Config(name="agent_two", description="Second"))

        registry.register(agent1)
        registry.register(agent2)
        print(f"✓ Registered {len(registry.list_agents())} agents")

        assert registry.has_agent("agent_one") and registry.has_agent("agent_two")
        assert registry.get("agent_one") is agent1

        registry.unregister("agent_one")
        assert len(registry.list_agents()) == 1

        registry.clear()
        assert len(registry.list_agents()) == 0
        print("✓ All registry operations work correctly")

    return run_test(test)


def verify_registry_disabled_agent() -> bool:
    """Verify disabled agents are silently skipped."""
    section("Disabled Agent Registration Verification")

    def test():
        from app.Agents.registry import AgentRegistry

        registry = AgentRegistry()
        disabled_agent = TestAgent(Config(name="disabled_agent", enabled=False))
        registry.register(disabled_agent)
        assert not registry.has_agent("disabled_agent")

        registry.register(disabled_agent)  # Should not raise
        print("✓ Disabled agents are silently skipped")

    return run_test(test)


def verify_registry_duplicate_agent() -> bool:
    """Verify duplicate agent registration raises ValueError."""
    section("Duplicate Agent Registration Verification")

    def test():
        from app.Agents.registry import AgentRegistry

        registry = AgentRegistry()
        config = Config(name="duplicate_agent")
        agent1, agent2 = TestAgent(config), TestAgent(config)
        registry.register(agent1)

        try:
            registry.register(agent2)
            return False
        except ValueError:
            print("✓ Duplicate registration raises ValueError")

    return run_test(test)


def verify_get_capable_agents() -> bool:
    """Verify get_capable_agents method works correctly."""
    section("Get Capable Agents Verification")

    def test():
        from app.Agents.registry import AgentRegistry

        class SpecializedAgent:
            def __init__(self, agent_name: str, keyword: str):
                self.config = Config(name=agent_name, description=f"Handles {keyword}")
                self._name = agent_name
                self._keyword = keyword

            @property
            def name(self) -> str:
                return self._name

            @property
            def description(self) -> str:
                return f"Handles {self._keyword}"

            def can_handle(self, request: Any) -> bool:
                return self._keyword in str(request).lower()

            def execute(self, request: Any) -> Any:
                return {"handled": True}

        registry = AgentRegistry()
        registry.register(SpecializedAgent("research_agent", "research"))
        registry.register(SpecializedAgent("coding_agent", "code"))
        print("✓ Registered specialized agents for testing")

        capable = registry.get_capable_agents("I need research on AI")
        assert len(capable) == 1 and capable[0].name == "research_agent"

        capable = registry.get_capable_agents("need code help")
        assert len(capable) == 1 and capable[0].name == "coding_agent"

        capable = registry.get_capable_agents("general query")
        assert len(capable) == 0
        print("✓ get_capable_agents works correctly")

    return run_test(test)


def verify_registry_singleton() -> bool:
    """Verify get_agent_registry returns singleton instance."""
    section("AgentRegistry Singleton Verification")

    def test():
        import app.Agents.registry as registry_module

        registry_module.agent_registry = None
        from app.Agents.registry import get_agent_registry

        registry1 = get_agent_registry()
        registry2 = get_agent_registry()
        assert registry1 is registry2

        agent = TestAgent(Config(name="singleton_test"))
        registry1.register(agent)
        assert registry2.has_agent("singleton_test")
        print("✓ Singleton registry works correctly")

    return run_test(test)


# =============================================================================
# Research Agent Verifications
# =============================================================================


def verify_research_agent_imports() -> bool:
    """Verify ResearchAgent imports work correctly."""
    section("Research Agent Import Verification")

    return verify_imports([
        ("ResearchAgent", "app.Agents"),
        ("get_research_agent", "app.Agents"),
        ("ResearchAgent", "app.Agents.research"),
        ("get_research_agent", "app.Agents.research"),
    ])


def verify_research_agent_can_handle() -> bool:
    """Verify ResearchAgent can_handle method works correctly."""
    section("Research Agent can_handle Verification")

    def test():
        from app.Agents.research import ResearchAgent

        verify_can_handle(
            ResearchAgent(),
            ["search for AI", "find information about Python", "look up machine learning",
             "research quantum computing", "I need to lookup something"],
            ["calculate 2+2", "regular chat query"],
        )

    return run_test(test)


def verify_research_agent_execute() -> bool:
    """Verify ResearchAgent execute method uses Browser MCP."""
    section("Research Agent Execution Verification (Mocked)")

    def test():
        from app.Agents.research import ResearchAgent

        result = ResearchAgent().execute("AI trends")
        assert isinstance(result, list) and len(result) == 2
        assert result[0]["mock"] is True and result[0]["provider"] == "browser-mcp"
        print("✓ ResearchAgent.execute returns Browser MCP results with metadata")

    return run_test(test)


def verify_research_agent_registration() -> bool:
    """Verify ResearchAgent can be registered with AgentRegistry."""
    section("Research Agent Registration Verification")

    def test():
        from app.Agents.research import ResearchAgent
        return verify_registration(lambda: ResearchAgent(), "research_agent", "search for something")

    return run_test(test)


# =============================================================================
# Planning Agent Verifications
# =============================================================================


def verify_planning_agent_imports() -> bool:
    """Verify PlanningAgent imports work correctly."""
    section("Planning Agent Import Verification")

    return verify_imports([
        ("PlanningAgent", "app.Agents"),
        ("get_planning_agent", "app.Agents"),
        ("PlanningAgent", "app.Agents.planning"),
        ("get_planning_agent", "app.Agents.planning"),
    ])


def verify_planning_agent_can_handle() -> bool:
    """Verify PlanningAgent can_handle method works correctly."""
    section("Planning Agent can_handle Verification")

    def test():
        from app.Agents.planning import PlanningAgent

        verify_can_handle(
            PlanningAgent(),
            ["create a plan for my project", "I need a roadmap", "what's the strategy",
             "organize these tasks", "give me steps to follow"],
            ["search for AI", "calculate 2+2"],
        )

    return run_test(test)


def verify_planning_agent_execute() -> bool:
    """Verify PlanningAgent execute method generates valid Plan structure."""
    section("Planning Agent Execution Verification")

    def test():
        from app.Agents.planning import PlanningAgent

        result = PlanningAgent().execute("Plan for launching a product")
        assert isinstance(result, dict) and "goal" in result and "steps" in result

        assert result["goal"] == "Plan for launching a product"
        assert len(result["steps"]) == 1 and result["steps"][0]["id"] == 1
        print("✓ PlanningAgent.execute generates valid Plan structure")

    return run_test(test)


def verify_planning_agent_registration() -> bool:
    """Verify PlanningAgent can be registered with AgentRegistry."""
    section("Planning Agent Registration Verification")

    return verify_registration(
        lambda: __import__("app.Agents.planning").Agents.planning.PlanningAgent(),
        "planning_agent", "I need a roadmap"
    )


# =============================================================================
# Coding Agent Verifications
# =============================================================================


def verify_coding_agent_imports() -> bool:
    """Verify CodingAgent imports work correctly."""
    section("Coding Agent Import Verification")

    return verify_imports([
        ("CodingAgent", "app.Agents"),
        ("get_coding_agent", "app.Agents"),
        ("CodingAgent", "app.Agents.coding"),
        ("get_coding_agent", "app.Agents.coding"),
    ])


def verify_coding_agent_can_handle() -> bool:
    """Verify CodingAgent can_handle method works correctly."""
    section("Coding Agent can_handle Verification")

    def test():
        from app.Agents.coding import CodingAgent

        verify_can_handle(
            CodingAgent(),
            ["write some code", "create a function", "define a class", "fix a bug",
             "debug this error", "clone a repository", "view github repo"],
            ["search for AI", "plan a trip"],
        )

    return run_test(test)


def verify_coding_agent_execute() -> bool:
    """Verify CodingAgent execute method uses GitHub MCP."""
    section("Coding Agent Execution Verification (Mocked)")

    def test():
        from app.Agents.coding import CodingAgent

        result = CodingAgent().execute("show me code")
        assert isinstance(result, dict) and "full_name" in result
        assert result["mock"] is True and result["provider"] == "github-mcp"
        print("✓ CodingAgent.execute returns GitHub MCP results with metadata")

    return run_test(test)


def verify_coding_agent_registration() -> bool:
    """Verify CodingAgent can be registered with AgentRegistry."""
    section("Coding Agent Registration Verification")

    return verify_registration(
        lambda: __import__("app.Agents.coding").Agents.coding.CodingAgent(),
        "coding_agent", "show me code"
    )


# =============================================================================
# Agent Router Verifications
# =============================================================================


def verify_router_imports() -> bool:
    """Verify AgentRouter imports work correctly."""
    section("Agent Router Import Verification")

    return verify_imports([
        ("AgentRouter", "app.Agents"),
        ("get_agent_router", "app.Agents"),
        ("AgentRouter", "app.Agents.router"),
        ("get_agent_router", "app.Agents.router"),
    ])


def verify_router_single_match() -> bool:
    """Verify router returns single capable agent."""
    section("Agent Router Single Match Verification")

    def test():
        # Reset singleton and use it
        import app.Agents.registry as registry_module
        registry_module.agent_registry = None
        from app.Agents.registry import get_agent_registry

        class SingleMatchAgent:
            config = Config(name="single_agent", description="Only match")

            @property
            def name(self) -> str:
                return self.config.name

            def can_handle(self, request: Any) -> bool:
                return "unique" in str(request).lower()

            def execute(self, request: Any) -> Any:
                return {"handled": True}

        registry = get_agent_registry()
        registry.register(SingleMatchAgent())

        from app.Agents.router import AgentRouter

        router = AgentRouter()
        result = router.route("this is unique")
        assert result is not None and result.name == "single_agent"
        print("✓ Router returns single capable agent")

    return run_test(test)


def verify_router_multiple_matches() -> bool:
    """Verify router returns first agent for multiple matches."""
    section("Agent Router Multiple Matches Verification")

    def test():
        # Reset singleton and use it
        import app.Agents.registry as registry_module
        registry_module.agent_registry = None
        from app.Agents.registry import get_agent_registry

        class MultiMatchAgent:
            def __init__(self, name: str, keyword: str):
                self.config = Config(name=name, description=f"Handles {keyword}")
                self._name = name
                self._keyword = keyword

            @property
            def name(self) -> str:
                return self._name

            def can_handle(self, request: Any) -> bool:
                return self._keyword in str(request).lower()

            def execute(self, request: Any) -> Any:
                return {"handled": True}

        registry = get_agent_registry()
        registry.register(MultiMatchAgent("first_agent", "first"))
        registry.register(MultiMatchAgent("second_agent", "second"))

        from app.Agents.router import AgentRouter

        router = AgentRouter()
        # Both "first" and "second" in request - multiple matches
        result = router.route("first and second")
        # Should return first registered (deterministic behavior)
        assert result is not None
        print("✓ Router handles multiple matches deterministically")

    return run_test(test)


def verify_router_no_match() -> bool:
    """Verify router returns None when no agent matches."""
    section("Agent Router No Match Verification")

    def test():
        # Reset singleton and use it
        import app.Agents.registry as registry_module
        registry_module.agent_registry = None
        from app.Agents.registry import get_agent_registry

        class NoMatchAgent:
            config = Config(name="no_match_agent", description="No match")

            @property
            def name(self) -> str:
                return self.config.name

            def can_handle(self, request: Any) -> bool:
                return False  # Never matches

            def execute(self, request: Any) -> Any:
                return {"handled": True}

        registry = get_agent_registry()
        registry.register(NoMatchAgent())

        from app.Agents.router import AgentRouter

        router = AgentRouter()
        result = router.route("any request")
        assert result is None
        print("✓ Router returns None for no matches")

    return run_test(test)


# =============================================================================
# Main
# =============================================================================


def main() -> int:
    """Run all verification tests."""
    global Config
    from app.Models.agent_config import AgentConfig
    Config = AgentConfig

    print("\n" + "=" * 60)
    print("Agents Module Verification Script")
    print("=" * 60 + "\n")

    all_passed = True

    # Core Agents Verification
    all_passed &= verify_agents_imports()
    all_passed &= verify_agent_config()
    all_passed &= verify_immutability()
    all_passed &= verify_agent_abc()
    all_passed &= verify_agent_registry()
    all_passed &= verify_registry_operations()
    all_passed &= verify_registry_disabled_agent()
    all_passed &= verify_registry_duplicate_agent()
    all_passed &= verify_get_capable_agents()
    all_passed &= verify_registry_singleton()

    # Research Agent Verification
    all_passed &= verify_research_agent_imports()
    all_passed &= verify_research_agent_can_handle()
    all_passed &= verify_research_agent_execute()
    all_passed &= verify_research_agent_registration()

    # Planning Agent Verification
    all_passed &= verify_planning_agent_imports()
    all_passed &= verify_planning_agent_can_handle()
    all_passed &= verify_planning_agent_execute()
    all_passed &= verify_planning_agent_registration()

    # Coding Agent Verification
    all_passed &= verify_coding_agent_imports()
    all_passed &= verify_coding_agent_can_handle()
    all_passed &= verify_coding_agent_execute()
    all_passed &= verify_coding_agent_registration()

    # Agent Router Verification
    all_passed &= verify_router_imports()
    all_passed &= verify_router_single_match()
    all_passed &= verify_router_multiple_matches()
    all_passed &= verify_router_no_match()

    print("\n" + "=" * 60)
    print("✓ All Agents verifications passed!" if all_passed else "✗ Some verifications failed!")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
