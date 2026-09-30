"""Add email_analysis and email_digest_cache tables

Revision ID: h8c9d0e1f2a3
Revises: g7b8c9d0e1f2
Create Date: 2026-09-27 15:30:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "h8c9d0e1f2a3"
down_revision = "g7b8c9d0e1f2"
branch_labels = None
depends_on = None


def _table_exists(table: str) -> bool:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    return table in insp.get_table_names()


def upgrade():
    # 1. email_analysis table
    if not _table_exists("email_analysis"):
        op.create_table(
            "email_analysis",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("email_id", sa.Integer(), sa.ForeignKey("emails.id", ondelete="CASCADE"), nullable=False),
            sa.Column("category", sa.String(length=50), nullable=True),
            sa.Column("subcategory", sa.String(length=100), nullable=True),
            sa.Column("priority_score", sa.Integer(), nullable=True),
            sa.Column("summary_text", sa.Text(), nullable=True),
            sa.Column("action_items_json", sa.Text(), nullable=True),
            sa.Column("deadline", sa.String(length=100), nullable=True),
            sa.Column("classified_at", sa.String(length=100), nullable=True),
            sa.Column("summarized_at", sa.String(length=100), nullable=True),
            sa.Column("extracted_at", sa.String(length=100), nullable=True),
            sa.Column("created_at", sa.String(length=100), nullable=False),
            sa.Column("updated_at", sa.String(length=100), nullable=False),
            sa.UniqueConstraint("email_id", name="uq_email_analysis_email_id"),
        )
        op.create_index("idx_email_analysis_email_id", "email_analysis", ["email_id"])
        op.create_index("idx_email_analysis_category", "email_analysis", ["category"])
        op.create_index("idx_email_analysis_priority", "email_analysis", ["priority_score"])

    # 2. email_digest_cache table
    if not _table_exists("email_digest_cache"):
        op.create_table(
            "email_digest_cache",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("period", sa.String(length=20), nullable=False),
            sa.Column("payload_json", sa.Text(), nullable=False),
            sa.Column("generated_at", sa.String(length=100), nullable=False),
            sa.UniqueConstraint("user_id", "period", name="uq_user_digest_period"),
        )
        op.create_index("idx_email_digest_user_id", "email_digest_cache", ["user_id"])
        op.create_index("idx_email_digest_generated_at", "email_digest_cache", ["generated_at"])


def downgrade():
    if _table_exists("email_digest_cache"):
        op.drop_table("email_digest_cache")
    if _table_exists("email_analysis"):
        op.drop_table("email_analysis")
