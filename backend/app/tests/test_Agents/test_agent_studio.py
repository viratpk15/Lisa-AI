"""
Jarvis AIOS — Agent Studio Unit Tests (Sprint 6.4B)

Tests cover:
- Agent CRUD (manager layer)
- Version management with is_current demotion
- Cycle detection for team graphs
- is_active soft-delete propagation
- Error handling for missing agents
"""

import pytest
from unittest.mock import MagicMock, patch

from app.Agents.models import Agent, AgentVersion, AgentTeam, TeamAgentNode, TeamEdge
from app.Agents.manager import (
    create_new_agent,
    update_existing_agent,
    delete_existing_agent,
    create_agent_version,
    create_agent_team,
    _has_cycle,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_session() -> MagicMock:
    """Return a mock SQLAlchemy session."""
    session = MagicMock()
    return session


def _make_agent(agent_id: int = 1, name: str = "TestAgent") -> Agent:
    agent = Agent()
    agent.id = agent_id
    agent.name = name
    agent.description = "Test description"
    agent.is_active = True
    return agent


def _make_version(version_id: int = 10, agent_id: int = 1, is_current: bool = True) -> AgentVersion:
    v = AgentVersion()
    v.id = version_id
    v.agent_id = agent_id
    v.version_number = 1
    v.is_current = is_current
    return v


def _make_node(node_id: int, team_id: int = 0, agent_version_id: int = 1) -> TeamAgentNode:
    node = TeamAgentNode()
    node.id = node_id
    node.team_id = team_id
    node.agent_version_id = agent_version_id
    return node


def _make_edge(source: int, target: int) -> TeamEdge:
    edge = TeamEdge()
    edge.source_node_id = source
    edge.target_node_id = target
    return edge


# ---------------------------------------------------------------------------
# Cycle detection
# ---------------------------------------------------------------------------

class TestHasCycle:
    def test_no_cycle_linear(self):
        """A -> B -> C should not be detected as cyclic."""
        nodes = [_make_node(1), _make_node(2), _make_node(3)]
        edges = [_make_edge(1, 2), _make_edge(2, 3)]
        assert _has_cycle(nodes, edges) is False

    def test_simple_cycle(self):
        """A -> B -> A is a direct cycle."""
        nodes = [_make_node(1), _make_node(2)]
        edges = [_make_edge(1, 2), _make_edge(2, 1)]
        assert _has_cycle(nodes, edges) is True

    def test_three_node_cycle(self):
        """A -> B -> C -> A is a cycle."""
        nodes = [_make_node(1), _make_node(2), _make_node(3)]
        edges = [_make_edge(1, 2), _make_edge(2, 3), _make_edge(3, 1)]
        assert _has_cycle(nodes, edges) is True

    def test_empty_graph_no_cycle(self):
        """Empty graph has no cycles."""
        assert _has_cycle([], []) is False

    def test_single_node_no_cycle(self):
        """Single node with no edges has no cycle."""
        nodes = [_make_node(1)]
        assert _has_cycle(nodes, []) is False

    def test_disconnected_nodes_no_cycle(self):
        """Two nodes with no edges between them have no cycle."""
        nodes = [_make_node(1), _make_node(2)]
        assert _has_cycle(nodes, []) is False


# ---------------------------------------------------------------------------
# create_new_agent
# ---------------------------------------------------------------------------

class TestCreateNewAgent:
    @patch("app.Agents.manager.create_agent")
    def test_creates_agent_with_correct_fields(self, mock_create):
        session = _make_session()
        mock_agent = _make_agent(name="My Agent")
        mock_create.return_value = mock_agent

        result = create_new_agent(session, name="My Agent", description="Desc")

        mock_create.assert_called_once()
        call_args = mock_create.call_args[0]
        created_agent = call_args[1]
        assert created_agent.name == "My Agent"
        assert created_agent.description == "Desc"
        assert result is mock_agent

    @patch("app.Agents.manager.create_agent")
    def test_creates_agent_without_description(self, mock_create):
        session = _make_session()
        mock_create.return_value = _make_agent()
        create_new_agent(session, name="Agent")
        created_agent = mock_create.call_args[0][1]
        assert created_agent.description is None


# ---------------------------------------------------------------------------
# update_existing_agent
# ---------------------------------------------------------------------------

class TestUpdateExistingAgent:
    @patch("app.Agents.manager.update_agent")
    @patch("app.Agents.manager.get_agent")
    def test_updates_name(self, mock_get, mock_update):
        session = _make_session()
        agent = _make_agent(name="OldName")
        mock_get.return_value = agent
        mock_update.return_value = agent

        update_existing_agent(session, agent_id=1, name="NewName")

        assert agent.name == "NewName"
        mock_update.assert_called_once_with(session, agent)

    @patch("app.Agents.manager.update_agent")
    @patch("app.Agents.manager.get_agent")
    def test_applies_is_active_soft_delete(self, mock_get, mock_update):
        """is_active=False should soft-delete the agent."""
        session = _make_session()
        agent = _make_agent()
        assert agent.is_active is True
        mock_get.return_value = agent
        mock_update.return_value = agent

        update_existing_agent(session, agent_id=1, is_active=False)

        assert agent.is_active is False

    @patch("app.Agents.manager.get_agent")
    def test_raises_value_error_when_agent_not_found(self, mock_get):
        session = _make_session()
        mock_get.return_value = None

        with pytest.raises(ValueError, match="not found"):
            update_existing_agent(session, agent_id=999, name="X")

    @patch("app.Agents.manager.update_agent")
    @patch("app.Agents.manager.get_agent")
    def test_none_fields_are_not_applied(self, mock_get, mock_update):
        """Passing None for name/description should not overwrite existing values."""
        session = _make_session()
        agent = _make_agent(name="Stable")
        mock_get.return_value = agent
        mock_update.return_value = agent

        update_existing_agent(session, agent_id=1, name=None, description=None)

        assert agent.name == "Stable"


# ---------------------------------------------------------------------------
# delete_existing_agent
# ---------------------------------------------------------------------------

class TestDeleteExistingAgent:
    @patch("app.Agents.manager.delete_agent")
    @patch("app.Agents.manager.get_agent")
    def test_deletes_agent(self, mock_get, mock_delete):
        session = _make_session()
        agent = _make_agent()
        mock_get.return_value = agent

        delete_existing_agent(session, agent_id=1)

        mock_delete.assert_called_once_with(session, agent)

    @patch("app.Agents.manager.get_agent")
    def test_raises_when_not_found(self, mock_get):
        session = _make_session()
        mock_get.return_value = None

        with pytest.raises(ValueError, match="not found"):
            delete_existing_agent(session, agent_id=99)


# ---------------------------------------------------------------------------
# create_agent_version (is_current logic)
# ---------------------------------------------------------------------------

class TestCreateAgentVersion:
    @patch("app.Agents.manager.create_version")
    @patch("app.Agents.manager.update_version")
    @patch("app.Agents.manager.list_versions")
    def test_demotes_previous_current_version(self, mock_list, mock_update_version, mock_create):
        """Previously is_current versions must be demoted before creating a new one."""
        session = _make_session()
        old_version = _make_version(version_id=5, is_current=True)
        mock_list.return_value = [old_version]
        new_version = _make_version(version_id=6, is_current=True)
        mock_create.return_value = new_version

        create_agent_version(session, agent_id=1, version_number=2)

        # Old version must have been demoted
        assert old_version.is_current is False
        # update_version (not update_agent) must have been called on it
        mock_update_version.assert_called_once_with(session, old_version)

    @patch("app.Agents.manager.create_version")
    @patch("app.Agents.manager.update_version")
    @patch("app.Agents.manager.list_versions")
    def test_new_version_is_current(self, mock_list, mock_update_version, mock_create):
        """Newly created version must have is_current=True."""
        session = _make_session()
        mock_list.return_value = []
        created = _make_version(is_current=True)
        mock_create.return_value = created

        result = create_agent_version(session, agent_id=1, version_number=1)

        call_args = mock_create.call_args[0]
        version_obj = call_args[1]
        assert version_obj.is_current is True
        assert result is created


# ---------------------------------------------------------------------------
# create_agent_team (cycle guard)
# ---------------------------------------------------------------------------

class TestCreateAgentTeam:
    @patch("app.Agents.manager.create_team")
    def test_creates_team_with_valid_graph(self, mock_create):
        session = _make_session()
        nodes = [_make_node(1), _make_node(2)]
        edges = [_make_edge(1, 2)]
        team = AgentTeam()
        mock_create.return_value = team

        result = create_agent_team(session, agent_id=1, name="My Team", nodes=nodes, edges=edges)

        mock_create.assert_called_once()
        assert result is team

    def test_raises_on_cyclic_graph(self):
        session = _make_session()
        nodes = [_make_node(1), _make_node(2)]
        edges = [_make_edge(1, 2), _make_edge(2, 1)]  # cycle!

        with pytest.raises(ValueError, match="cycle"):
            create_agent_team(session, agent_id=1, name="Bad Team", nodes=nodes, edges=edges)
