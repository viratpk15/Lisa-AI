"""Initial Workflow Studio Schema (workflow_definitions, workflow_versions, workflow_executions, workflow_node_logs)

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-07-27 17:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def _table_exists(name: str) -> bool:
    conn = op.get_bind()
    return sa.inspect(conn).has_table(name)


def upgrade() -> None:
    if _table_exists("workflow_definitions"):
        return
    # 1. workflow_definitions
    op.create_table(
        "workflow_definitions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("workflow_id", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("definition_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("definition_yaml", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_workflow_id", "workflow_definitions", ["workflow_id"], unique=True)

    # 2. workflow_versions
    op.create_table(
        "workflow_versions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("workflow_id", sa.Integer(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("definition_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["workflow_id"], ["workflow_definitions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_workflow_version", "workflow_versions", ["workflow_id", "version_number"])

    # 3. workflow_executions
    op.create_table(
        "workflow_executions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("execution_id", sa.String(length=100), nullable=False),
        sa.Column("workflow_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default=sa.text("'running'")),
        sa.Column("total_latency_ms", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("total_tokens", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_cost", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["workflow_id"], ["workflow_definitions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_execution_id", "workflow_executions", ["execution_id"], unique=True)
    op.create_index("idx_execution_status", "workflow_executions", ["status"])

    # 4. workflow_node_logs
    op.create_table(
        "workflow_node_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("execution_id", sa.Integer(), nullable=False),
        sa.Column("node_id", sa.String(length=100), nullable=False),
        sa.Column("node_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default=sa.text("'success'")),
        sa.Column("latency_ms", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("input_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("output_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["execution_id"], ["workflow_executions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_node_log_exec_time", "workflow_node_logs", ["execution_id", "timestamp"])


def downgrade() -> None:
    op.drop_table("workflow_node_logs")
    op.drop_table("workflow_executions")
    op.drop_table("workflow_versions")
    op.drop_table("workflow_definitions")
