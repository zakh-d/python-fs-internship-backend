"""added requests and invitations tables

Revision ID: 7d301e65fc57
Revises: 832dd5574134
Create Date: 2024-07-28 14:00:12.735416

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '7d301e65fc57'
down_revision: Union[str, None] = '832dd5574134'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'invitations',
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('company_id', sa.Uuid(), nullable=False),
        sa.Column('pending', sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='invitation_status'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'company_id'),
    )
    op.create_table(
        'requests',
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('company_id', sa.Uuid(), nullable=False),
        sa.Column('pending', sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='request_status'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'company_id'),
    )


def downgrade() -> None:
    op.drop_table('requests')
    op.drop_table('invitations')
