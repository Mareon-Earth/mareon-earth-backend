"""convert_vessel_company_to_single_row

Revision ID: 1a86c76c3028
Revises: 9932494e8e9d
Create Date: 2025-12-26 15:41:35.013631

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a86c76c3028'
down_revision: Union[str, Sequence[str], None] = '9932494e8e9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create temporary table with new structure
    op.create_table(
        'vessel_company_new',
        sa.Column('id', sa.String(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('vessel_id', sa.String(), nullable=False),
        sa.Column('owner_name', sa.String(), nullable=True),
        sa.Column('owner_company_number', sa.String(), nullable=True),
        sa.Column('owner_address', sa.String(), nullable=True),
        sa.Column('manager_name', sa.String(), nullable=True),
        sa.Column('manager_company_number', sa.String(), nullable=True),
        sa.Column('manager_address', sa.String(), nullable=True),
        sa.Column('doc_holder_name', sa.String(), nullable=True),
        sa.Column('doc_holder_company_number', sa.String(), nullable=True),
        sa.Column('doc_holder_address', sa.String(), nullable=True),
        sa.Column('ism_manager_name', sa.String(), nullable=True),
        sa.Column('ism_manager_address', sa.String(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['vessel_id'], ['vessel.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('vessel_id')
    )

    # Migrate existing data: pivot from multi-row to single-row
    op.execute("""
        INSERT INTO vessel_company_new (
            vessel_id,
            owner_name, owner_company_number, owner_address,
            manager_name, manager_company_number, manager_address,
            doc_holder_name, doc_holder_company_number, doc_holder_address,
            ism_manager_name, ism_manager_address
        )
        SELECT 
            vessel_id,
            MAX(CASE WHEN role = 'owner' THEN name END) as owner_name,
            MAX(CASE WHEN role = 'owner' THEN company_number END) as owner_company_number,
            MAX(CASE WHEN role = 'owner' THEN address END) as owner_address,
            MAX(CASE WHEN role = 'manager' THEN name END) as manager_name,
            MAX(CASE WHEN role = 'manager' THEN company_number END) as manager_company_number,
            MAX(CASE WHEN role = 'manager' THEN address END) as manager_address,
            MAX(CASE WHEN role = 'doc_holder' THEN name END) as doc_holder_name,
            MAX(CASE WHEN role = 'doc_holder' THEN company_number END) as doc_holder_company_number,
            MAX(CASE WHEN role = 'doc_holder' THEN address END) as doc_holder_address,
            MAX(CASE WHEN role = 'ism_manager' THEN name END) as ism_manager_name,
            MAX(CASE WHEN role = 'ism_manager' THEN address END) as ism_manager_address
        FROM vessel_company
        GROUP BY vessel_id
    """)

    # Drop old table and rename new one
    op.drop_table('vessel_company')
    op.rename_table('vessel_company_new', 'vessel_company')


def downgrade() -> None:
    """Downgrade schema."""
    # Create temporary table with old structure
    op.create_table(
        'vessel_company_old',
        sa.Column('id', sa.String(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('vessel_id', sa.String(), nullable=False),
        sa.Column('document_id', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('company_number', sa.String(), nullable=True),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['vessel_id'], ['vessel.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['document.id'], ondelete='SET NULL')
    )

    # Migrate data back: unpivot from single-row to multi-row
    op.execute("""
        INSERT INTO vessel_company_old (vessel_id, role, name, company_number, address)
        SELECT vessel_id, 'owner', owner_name, owner_company_number, owner_address
        FROM vessel_company WHERE owner_name IS NOT NULL
        UNION ALL
        SELECT vessel_id, 'manager', manager_name, manager_company_number, manager_address
        FROM vessel_company WHERE manager_name IS NOT NULL
        UNION ALL
        SELECT vessel_id, 'doc_holder', doc_holder_name, doc_holder_company_number, doc_holder_address
        FROM vessel_company WHERE doc_holder_name IS NOT NULL
        UNION ALL
        SELECT vessel_id, 'ism_manager', ism_manager_name, NULL, ism_manager_address
        FROM vessel_company WHERE ism_manager_name IS NOT NULL
    """)

    # Drop new table and rename old one back
    op.drop_table('vessel_company')
    op.rename_table('vessel_company_old', 'vessel_company')
