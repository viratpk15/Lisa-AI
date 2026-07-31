"""Initial Deployment Studio Schema (deployment_environments, deployment_targets, deployment_releases, secret_vault_entries, database_backups, deployment_audit_logs)

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-07-27 17:39:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e5f6a7b8c9d0"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None


def _table_exists(name: str) -> bool:
    conn = op.get_bind()
    return sa.inspect(conn).has_table(name)


def upgrade() -> None:
    if _table_exists("deployment_environments"):
        return
    # 1. deployment_environments
    op.create_table(
        "deployment_environments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("env_id", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("tier", sa.String(length=50), nullable=False, server_default=sa.text("'production'")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_env_id", "deployment_environments", ["env_id"], unique=True)

    # 2. deployment_targets
    op.create_table(
        "deployment_targets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("env_id", sa.Integer(), nullable=False),
        sa.Column("provider_type", sa.String(length=50), nullable=False),
        sa.Column("config_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("status", sa.String(length=50), nullable=False, server_default=sa.text("'active'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["env_id"], ["deployment_environments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_target_provider", "deployment_targets", ["provider_type"])

    # 3. deployment_releases
    op.create_table(
        "deployment_releases",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("release_id", sa.String(length=100), nullable=False),
        sa.Column("env_id", sa.Integer(), nullable=False),
        sa.Column("version_tag", sa.String(length=50), nullable=False),
        sa.Column("strategy", sa.String(length=50), nullable=False, server_default=sa.text("'blue_green'")),
        sa.Column("status", sa.String(length=50), nullable=False, server_default=sa.text("'running'")),
        sa.Column("rollout_duration_s", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("deployed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["env_id"], ["deployment_environments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_release_id", "deployment_releases", ["release_id"], unique=True)
    op.create_index("idx_release_status", "deployment_releases", ["status"])

    # 4. secret_vault_entries
    op.create_table(
        "secret_vault_entries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("env_id", sa.Integer(), nullable=False),
        sa.Column("secret_key", sa.String(length=100), nullable=False),
        sa.Column("encrypted_value", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["env_id"], ["deployment_environments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_secret_env_key", "secret_vault_entries", ["env_id", "secret_key"], unique=True)

    # 5. database_backups
    op.create_table(
        "database_backups",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("env_id", sa.Integer(), nullable=False),
        sa.Column("snapshot_name", sa.String(length=150), nullable=False),
        sa.Column("storage_path", sa.String(length=255), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["env_id"], ["deployment_environments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_backup_snapshot", "database_backups", ["snapshot_name"], unique=True)

    # 6. deployment_audit_logs
    op.create_table(
        "deployment_audit_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("release_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("operator_user", sa.String(length=100), nullable=False, server_default=sa.text("'admin'")),
        sa.Column("details_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["release_id"], ["deployment_releases.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("deployment_audit_logs")
    op.drop_table("database_backups")
    op.drop_table("secret_vault_entries")
    op.drop_table("deployment_releases")
    op.drop_table("deployment_targets")
    op.drop_table("deployment_environments")
