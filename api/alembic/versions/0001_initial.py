"""initial tasks table

Revision ID: 0001_initial
Revises:
Create Date: 2025-09-12 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # 1) ENUM-Typen idempotent anlegen (nur falls noch nicht vorhanden)
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'task_status') THEN
                CREATE TYPE task_status AS ENUM ('open','doing','done');
            END IF;
        END$$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'task_priority') THEN
                CREATE TYPE task_priority AS ENUM ('low','normal','high');
            END IF;
        END$$;
        """
    )

    # 2) Bestehende Typen referenzieren (kein implizites CREATE TYPE)
    status_enum = postgresql.ENUM(name='task_status', create_type=False)
    priority_enum = postgresql.ENUM(name='task_priority', create_type=False)

    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', status_enum, nullable=False, server_default='open'),
        sa.Column('priority', priority_enum, nullable=False, server_default='normal'),
        sa.Column('due_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_tasks_created_at', 'tasks', ['created_at'], unique=False)
    op.create_index('ix_tasks_status', 'tasks', ['status'], unique=False)

def downgrade():
    op.drop_index('ix_tasks_status', table_name='tasks')
    op.drop_index('ix_tasks_created_at', table_name='tasks')
    op.drop_table('tasks')
    op.execute("DROP TYPE IF EXISTS task_priority")
    op.execute("DROP TYPE IF EXISTS task_status")
