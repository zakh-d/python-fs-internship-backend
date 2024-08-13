"""added quizzes

Revision ID: 3cee1ccb6ec8
Revises: ef63600c6cfa
Create Date: 2024-08-13 16:50:11.868718

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '3cee1ccb6ec8'
down_revision: Union[str, None] = 'ef63600c6cfa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'quizzes',
        sa.Column('title', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=250), nullable=True),
        sa.Column('company_id', sa.Uuid(), nullable=False),
        sa.Column('frequency', sa.Integer(), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default='now()', nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default='now()', nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'questions',
        sa.Column('text', sa.String(length=250), nullable=False),
        sa.Column('quizz_id', sa.Uuid(), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default='now()', nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default='now()', nullable=False),
        sa.ForeignKeyConstraint(['quizz_id'], ['quizzes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'answers',
        sa.Column('text', sa.String(length=250), nullable=False),
        sa.Column('question_id', sa.Uuid(), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default='now()', nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default='now()', nullable=False),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('answers')
    op.drop_table('questions')
    op.drop_table('quizzes')
