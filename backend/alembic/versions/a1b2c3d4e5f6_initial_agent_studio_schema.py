"""Initial Agent Studio schema

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-07-26 00:00:00.000000

Creates all Agent Studio tables:
  - agent
  - agentversion
  - agentpromptbinding
  - agenttoolbinding
  - agentmemorybinding
  - agentmodelbinding
  - agentexecution
  - executionstep
  - agentteam
  - teamagentnode
  - teamedge
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = None
branch_labels = None
depends_on = None


def _table_exists(name: str) -> bool:
    conn = op.get_bind()
    return sa.inspect(conn).has_table(name)


def upgrade() -> None:
    if _table_exists("agent"):
        return
    op.create_table(
        "agent",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_name"), "agent", ["name"], unique=False)

    op.create_table(
        "agentversion",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("changelog", sa.Text(), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["agent_id"], ["agent.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "agentpromptbinding",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column("prompt_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["version_id"], ["agentversion.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "agenttoolbinding",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column("tool_name", sa.String(), nullable=False),
        sa.Column("config_json", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["version_id"], ["agentversion.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "agentmemorybinding",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column("memory_key", sa.String(), nullable=False),
        sa.Column("config_json", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["version_id"], ["agentversion.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "agentmodelbinding",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column("model_name", sa.String(), nullable=False),
        sa.Column("parameters_json", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["version_id"], ["agentversion.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "agentexecution",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default=sa.text("'draft'")),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["version_id"], ["agentversion.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "executionstep",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("execution_id", sa.Integer(), nullable=False),
        sa.Column("step_index", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("input_data", sa.Text(), nullable=True),
        sa.Column("output_data", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["execution_id"], ["agentexecution.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "agentteam",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["agent_id"], ["agent.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "teamagentnode",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("agent_version_id", sa.Integer(), nullable=False),
        sa.Column("position_x", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("position_y", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.ForeignKeyConstraint(["agent_version_id"], ["agentversion.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["agentteam.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "teamedge",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("source_node_id", sa.Integer(), nullable=False),
        sa.Column("target_node_id", sa.Integer(), nullable=False),
        sa.Column("condition_json", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["source_node_id"], ["teamagentnode.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_node_id"], ["teamagentnode.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["agentteam.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("teamedge")
    op.drop_table("teamagentnode")
    op.drop_table("agentteam")
    op.drop_table("executionstep")
    op.drop_table("agentexecution")
    op.drop_table("agentmodelbinding")
    op.drop_table("agentmemorybinding")
    op.drop_table("agenttoolbinding")
    op.drop_table("agentpromptbinding")
    op.drop_table("agentversion")
    op.drop_index(op.f("ix_agent_name"), table_name="agent")
    op.drop_table("agent")
