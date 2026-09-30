"""Add email foundation schema (gmail_connections, emails, email_sender_verifications)

Revision ID: g7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-09-27 15:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "g7b8c9d0e1f2"
down_revision = "f6a7b8c9d0e1"
branch_labels = None
depends_on = None


def _table_exists(table: str) -> bool:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    return table in insp.get_table_names()


def upgrade():
    # 1. gmail_connections table
    if not _table_exists("gmail_connections"):
        op.create_table(
            "gmail_connections",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("email_address", sa.String(length=255), nullable=False),
            sa.Column("encrypted_credentials", sa.Text(), nullable=False),
            sa.Column("status", sa.String(length=50), nullable=False, server_default="connected"),
            sa.Column("created_at", sa.String(length=100), nullable=False),
            sa.Column("updated_at", sa.String(length=100), nullable=False),
            sa.Column("last_sync_at", sa.String(length=100), nullable=True),
            sa.UniqueConstraint("user_id", "email_address", name="uq_user_gmail_email"),
        )
        op.create_index("idx_gmail_conn_user_status", "gmail_connections", ["user_id", "status"])
        op.create_index("idx_gmail_conn_user_id", "gmail_connections", ["user_id"])

    # 2. emails table
    if not _table_exists("emails"):
        op.create_table(
            "emails",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("gmail_message_id", sa.String(length=255), nullable=False),
            sa.Column("gmail_thread_id", sa.String(length=255), nullable=False),
            sa.Column("sender", sa.String(length=500), nullable=False),
            sa.Column("sender_domain", sa.String(length=255), nullable=False),
            sa.Column("recipients", sa.Text(), nullable=False, server_default="[]"),
            sa.Column("subject", sa.Text(), nullable=False, server_default=""),
            sa.Column("body_text", sa.Text(), nullable=False, server_default=""),
            sa.Column("body_html", sa.Text(), nullable=True),
            sa.Column("snippet", sa.Text(), nullable=True),
            sa.Column("received_at", sa.String(length=100), nullable=False),
            sa.Column("attachment_metadata", sa.Text(), nullable=False, server_default="[]"),
            sa.Column("gmail_metadata", sa.Text(), nullable=False, server_default="{}"),
            sa.Column("created_at", sa.String(length=100), nullable=False),
            sa.Column("updated_at", sa.String(length=100), nullable=False),
            sa.UniqueConstraint("user_id", "gmail_message_id", name="uq_user_gmail_message_id"),
        )
        op.create_index("idx_emails_user_id", "emails", ["user_id"])
        op.create_index("idx_emails_gmail_msg_id", "emails", ["gmail_message_id"])
        op.create_index("idx_emails_gmail_thread_id", "emails", ["gmail_thread_id"])
        op.create_index("idx_emails_user_received", "emails", ["user_id", "received_at"])
        op.create_index("idx_emails_user_sender_domain", "emails", ["user_id", "sender_domain"])

    # 3. email_sender_verifications table
    if not _table_exists("email_sender_verifications"):
        op.create_table(
            "email_sender_verifications",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("email_id", sa.Integer(), sa.ForeignKey("emails.id", ondelete="CASCADE"), nullable=False),
            sa.Column("spf_status", sa.String(length=50), nullable=False, server_default="unknown"),
            sa.Column("spf_details", sa.Text(), nullable=True),
            sa.Column("dkim_status", sa.String(length=50), nullable=False, server_default="unknown"),
            sa.Column("dkim_details", sa.Text(), nullable=True),
            sa.Column("dmarc_status", sa.String(length=50), nullable=False, server_default="unknown"),
            sa.Column("dmarc_details", sa.Text(), nullable=True),
            sa.Column("raw_auth_results", sa.Text(), nullable=True),
            sa.Column("verification_status", sa.String(length=50), nullable=False, server_default="completed"),
            sa.Column("verified_at", sa.String(length=100), nullable=False),
            sa.UniqueConstraint("email_id", name="uq_verification_email_id"),
        )
        op.create_index("idx_verification_user_email", "email_sender_verifications", ["user_id", "email_id"])
        op.create_index("idx_verification_user_id", "email_sender_verifications", ["user_id"])


def downgrade():
    if _table_exists("email_sender_verifications"):
        op.drop_table("email_sender_verifications")
    if _table_exists("emails"):
        op.drop_table("emails")
    if _table_exists("gmail_connections"):
        op.drop_table("gmail_connections")
