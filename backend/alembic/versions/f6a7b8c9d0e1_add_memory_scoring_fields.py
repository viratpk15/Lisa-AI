"""Add memory scoring fields and lifecycle status to episodic_events and memory_entities

Adds importance_score, confidence_score, retrieval_count, status, pinned columns
to episodic_events and memory_entities tables to support the Intelligent Memory Engine.

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-07-29 14:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f6a7b8c9d0e1"
down_revision = "e5f6a7b8c9d0"
branch_labels = None
depends_on = None


def _column_exists(table: str, column: str) -> bool:
    conn = op.get_bind()
    cols = [row[1] for row in conn.execute(sa.text(f"PRAGMA table_info({table})"))]
    return column in cols


def upgrade():
    # -----------------------------------------------------------------------
    # episodic_events — add scoring and lifecycle fields
    # -----------------------------------------------------------------------
    for col_name, col_def in [
        ("importance_score", "REAL NOT NULL DEFAULT 0.75"),
        ("confidence_score", "REAL NOT NULL DEFAULT 1.0"),
        ("retrieval_count", "INTEGER NOT NULL DEFAULT 0"),
        ("status", "VARCHAR(50) NOT NULL DEFAULT 'active'"),
        ("pinned", "INTEGER NOT NULL DEFAULT 0"),
    ]:
        if not _column_exists("episodic_events", col_name):
            op.execute(sa.text(f"ALTER TABLE episodic_events ADD COLUMN {col_name} {col_def}"))

    # -----------------------------------------------------------------------
    # memory_entities — add scoring and lifecycle fields
    # -----------------------------------------------------------------------
    for col_name, col_def in [
        ("importance_score", "REAL NOT NULL DEFAULT 0.85"),
        ("confidence_score", "REAL NOT NULL DEFAULT 1.0"),
        ("retrieval_count", "INTEGER NOT NULL DEFAULT 0"),
        ("status", "VARCHAR(50) NOT NULL DEFAULT 'active'"),
        ("pinned", "INTEGER NOT NULL DEFAULT 0"),
    ]:
        if not _column_exists("memory_entities", col_name):
            op.execute(sa.text(f"ALTER TABLE memory_entities ADD COLUMN {col_name} {col_def}"))


def downgrade():
    # SQLite does not support DROP COLUMN in older versions. Document only.
    pass
