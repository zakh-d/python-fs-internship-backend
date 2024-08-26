"""added notification

Revision ID: 217bc160447e
Revises: 2e80001e00eb
Create Date: 2024-08-26 18:38:56.580795

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '217bc160447e'
down_revision: Union[str, None] = '2e80001e00eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'notifications',
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=50), nullable=False),
        sa.Column('body', sa.String(length=250), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_defualt=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('notifications')
