"""added company actions

Revision ID: a997c65dc5ee
Revises: 832dd5574134
Create Date: 2024-07-29 16:07:54.482704

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a997c65dc5ee'
down_revision: Union[str, None] = '832dd5574134'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'company_actions',
        sa.Column('company_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('pending', sa.Boolean(), nullable=False, default=True),
        sa.Column('type', sa.Enum('INVITATION', 'REQUEST', name='companyactiontype'), nullable=False),
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
