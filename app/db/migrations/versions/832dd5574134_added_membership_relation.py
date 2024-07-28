"""added membership relation

Revision ID: 832dd5574134
Revises: ae684250f12f
Create Date: 2024-07-28 10:26:38.670815

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '832dd5574134'
down_revision: Union[str, None] = 'ae684250f12f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'membership_table',
        sa.Column('company_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('company_id', 'user_id'),
    )


def downgrade() -> None:
    op.drop_table('membership_table')
