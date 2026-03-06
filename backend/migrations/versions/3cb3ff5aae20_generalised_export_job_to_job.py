"""Generalised Export Job to Job

Revision ID: 3cb3ff5aae20
Revises: fe1f93443edf
Create Date: 2026-03-03 13:49:20.836974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3cb3ff5aae20'
down_revision: Union[str, Sequence[str], None] = 'fe1f93443edf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # Drop old table
    op.drop_index("ix_export_jobs_created_at", table_name="export_jobs")
    op.drop_table("export_jobs")

    # Drop old enum
    op.execute("DROP TYPE IF EXISTS exportstatus")

    # Create enums
    op.execute(
        "CREATE TYPE jobstatus AS ENUM ('pending','processing','completed','failed')"
    )
    op.execute(
        "CREATE TYPE jobtype AS ENUM ('export')"
    )

    # Create table using Postgres enum type
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("type", postgresql.ENUM(name="jobtype", create_type=False), nullable=False),
        sa.Column("status", postgresql.ENUM(name="jobstatus", create_type=False), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("processing_started_at", sa.DateTime(), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("next_run_at", sa.DateTime(), nullable=True),
        sa.Column("last_error", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_index("ix_jobs_created_at", "jobs", ["created_at"])



def downgrade() -> None:

    op.drop_index("ix_jobs_created_at", table_name="jobs")
    op.drop_table("jobs")

    op.execute("DROP TYPE IF EXISTS jobtype")
    op.execute("DROP TYPE IF EXISTS jobstatus")

    op.execute(
        "CREATE TYPE exportstatus AS ENUM ('pending','processing','completed','failed')"
    )

    op.create_table(
        "export_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "status",
            postgresql.ENUM(name="exportstatus", create_type=False),
            nullable=False,
        ),
        sa.Column("file_path", sa.String(), nullable=True),
        sa.Column("processing_started_at", sa.DateTime(), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("next_run_at", sa.DateTime(), nullable=True),
        sa.Column("last_error", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_index("ix_export_jobs_created_at", "export_jobs", ["created_at"])