"""Initial Model Studio Schema (provider_configs, llm_model_configs, routing_policies, benchmark_runs)

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-07-27 17:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def _table_exists(name: str) -> bool:
    conn = op.get_bind()
    return sa.inspect(conn).has_table(name)


def upgrade() -> None:
    if _table_exists("provider_configs"):
        return
    # 1. provider_configs
    op.create_table(
        "provider_configs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("provider_name", sa.String(length=50), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("api_base_url", sa.String(length=255), nullable=False),
        sa.Column("encrypted_api_key", sa.Text(), nullable=True),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("is_healthy", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("latency_ms", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_provider_name", "provider_configs", ["provider_name"], unique=True)

    # 2. llm_model_configs
    op.create_table(
        "llm_model_configs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("provider_id", sa.Integer(), nullable=False),
        sa.Column("model_id", sa.String(length=100), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("context_window", sa.Integer(), nullable=False, server_default=sa.text("128000")),
        sa.Column("max_output_tokens", sa.Integer(), nullable=False, server_default=sa.text("4096")),
        sa.Column("input_cost_per_1k", sa.Float(), nullable=False, server_default=sa.text("0.0015")),
        sa.Column("output_cost_per_1k", sa.Float(), nullable=False, server_default=sa.text("0.0020")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("routing_priority", sa.Integer(), nullable=False, server_default=sa.text("10")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["provider_id"], ["provider_configs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_model_id", "llm_model_configs", ["model_id"], unique=True)
    op.create_index("idx_model_provider", "llm_model_configs", ["provider_id"])

    # 3. routing_policies
    op.create_table(
        "routing_policies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("policy_name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("config_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_routing_policy_name", "routing_policies", ["policy_name"], unique=True)

    # 4. benchmark_runs
    op.create_table(
        "benchmark_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("model_id", sa.String(length=100), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("completion_tokens", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_latency_ms", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("ttft_ms", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("status", sa.String(length=50), nullable=False, server_default=sa.text("'success'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_benchmark_model_date", "benchmark_runs", ["model_id", "created_at"])


def downgrade() -> None:
    op.drop_table("benchmark_runs")
    op.drop_table("routing_policies")
    op.drop_table("llm_model_configs")
    op.drop_table("provider_configs")
