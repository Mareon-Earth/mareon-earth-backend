"""add vessel org name unique constraint

Revision ID: 7cbec28ec1d8
Revises: 62b0299e882a
Create Date: 2025-12-21 10:25:15.553458

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7cbec28ec1d8'
down_revision: Union[str, Sequence[str], None] = '62b0299e882a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add unique constraint on (org_id, name) for vessel upserts
    op.create_unique_constraint('vessel_org_id_name_key', 'vessel', ['org_id', 'name'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('vessel_org_id_name_key', 'vessel', type_='unique')
