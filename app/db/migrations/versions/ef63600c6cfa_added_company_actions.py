"""added company_actions

Revision ID: ef63600c6cfa
Revises: ae684250f12f
Create Date: 2024-08-01 19:32:34.636172

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'ef63600c6cfa'
down_revision: Union[str, None] = 'ae684250f12f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'company_actions',
        sa.Column('company_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column(
            'type', sa.Enum('INVITATION', 'REQUEST', 'MEMBERSHIP', 'ADMIN', name='companyactiontype'), nullable=False
        ),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default='now()', nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default='now()', nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'user_id', name='unique_company_user'),
    )


def downgrade() -> None:
    op.drop_table('company_actions')
    sa.Enum('INVITATION', 'REQUEST', 'MEMBERSHIP', 'ADMIN', name='companyactiontype').drop(op.get_bind())
