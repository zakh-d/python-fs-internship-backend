"""created companies table

Revision ID: ae684250f12f
Revises: f2bbdfd9a884
Create Date: 2024-07-24 14:08:06.450069

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'ae684250f12f'
down_revision: Union[str, None] = 'f2bbdfd9a884'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('companies',
                    sa.Column('name', sa.String(length=50), nullable=False),
                    sa.Column('description', sa.String(length=250), nullable=True),
                    sa.Column('hidden', sa.Boolean(), nullable=False),
                    sa.Column('owner_id', sa.Uuid(), nullable=False),
                    sa.Column('id', sa.Uuid(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), server_default='now()', nullable=False),
                    sa.Column('updated_at', sa.DateTime(), server_default='now()', nullable=False),
                    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id'))
    op.create_index(op.f('ix_companies_name'), 'companies', ['name'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_companies_name'), table_name='companies')
    op.drop_table('companies')
