"""removed pending

Revision ID: 61880850651d
Revises: ef63600c6cfa
Create Date: 2024-08-09 12:21:07.646958

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '61880850651d'
down_revision: Union[str, None] = 'ef63600c6cfa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('company_actions', 'pending')


def downgrade() -> None:
    op.add_column('company_actions', sa.Column('pending', sa.BOOLEAN(), autoincrement=False, nullable=False))
