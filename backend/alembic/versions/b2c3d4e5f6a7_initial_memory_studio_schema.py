"""Initial Memory Studio Schema (episodic_events, memory_entities, memory_relations)

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-27 16:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def _table_exists(name: str) -> bool:
    conn = op.get_bind()
    return sa.inspect(conn).has_table(name)


def upgrade() -> None:
    if _table_exists("episodic_events"):
        return
    # 1. episodic_events
    op.create_table(
        "episodic_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.String(length=255), nullable=False),
        sa.Column("run_id", sa.String(length=255), nullable=True),
        sa.Column("step_index", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("outcome", sa.String(length=50), nullable=False, server_default=sa.text("'success'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.session_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_episodic_session_step", "episodic_events", ["session_id", "step_index"])
    op.create_index("idx_episodic_type", "episodic_events", ["event_type"])

    # 2. memory_entities
    op.create_table(
        "memory_entities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("entity_name", sa.String(length=255), nullable=False),
        sa.Column("entity_category", sa.String(length=100), nullable=False, server_default=sa.text("'Concept'")),
        sa.Column("attributes_json", sa.Text(), nullable=True, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_entities_user", "memory_entities", ["user_id"])
    op.create_index("idx_entities_name", "memory_entities", ["entity_name"])

    # 3. memory_relations
    op.create_table(
        "memory_relations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("subject_entity_id", sa.Integer(), nullable=False),
        sa.Column("object_entity_id", sa.Integer(), nullable=False),
        sa.Column("relation_type", sa.String(length=100), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default=sa.text("1.0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["subject_entity_id"], ["memory_entities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["object_entity_id"], ["memory_entities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_relations_subj", "memory_relations", ["subject_entity_id"])
    op.create_index("idx_relations_obj", "memory_relations", ["object_entity_id"])


def downgrade() -> None:
    op.drop_table("memory_relations")
    op.drop_table("memory_entities")
    op.drop_table("episodic_events")
