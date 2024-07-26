"""added cascade delete to company

Revision ID: e83d86da0071
Revises: ae684250f12f
Create Date: 2024-07-26 16:29:10.179039

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e83d86da0071'
down_revision: Union[str, None] = 'ae684250f12f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('companies_owner_id_fkey', 'companies', type_='foreignkey')
    op.create_foreign_key(None, 'companies', 'users', ['owner_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    op.drop_constraint(None, 'companies', type_='foreignkey')
    op.create_foreign_key('companies_owner_id_fkey', 'companies', 'users', ['owner_id'], ['id'])
