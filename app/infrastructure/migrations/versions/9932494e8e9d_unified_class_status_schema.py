"""unified class status schema - add dimensions, tonnage tables and expand identity

Revision ID: 9932494e8e9d
Revises: 7cbec28ec1d8
Create Date: 2025-12-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9932494e8e9d'
down_revision: Union[str, Sequence[str], None] = '7cbec28ec1d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    # ===================================================================
    # 1. Add new columns to vessel_identity
    # ===================================================================
    
    # Identification fields
    op.add_column('vessel_identity', sa.Column('class_number', sa.String(), nullable=True))
    op.add_column('vessel_identity', sa.Column('official_number', sa.String(), nullable=True))
    op.add_column('vessel_identity', sa.Column('equipment_number', sa.String(), nullable=True))
    
    # Class state
    op.add_column('vessel_identity', sa.Column('class_state', sa.String(), nullable=True))
    op.add_column('vessel_identity', sa.Column('other_state', sa.String(), nullable=True))
    op.add_column('vessel_identity', sa.Column('lifecycle_state', sa.String(), nullable=True))
    op.add_column('vessel_identity', sa.Column('dual_class', sa.Boolean(), nullable=True))
    op.add_column('vessel_identity', sa.Column('previous_class_society', sa.String(), nullable=True))
    
    # Vessel description
    op.add_column('vessel_identity', sa.Column('vessel_description', sa.String(), nullable=True))
    
    # Build dates (new)
    op.add_column('vessel_identity', sa.Column('delivery_date', sa.Date(), nullable=True))
    
    # Construction info
    op.add_column('vessel_identity', sa.Column('shipyard', sa.String(), nullable=True))
    op.add_column('vessel_identity', sa.Column('hull_number', sa.String(), nullable=True))
    
    # Regulatory categories
    op.add_column('vessel_identity', sa.Column('solas_category', sa.String(), nullable=True))
    op.add_column('vessel_identity', sa.Column('marpol_category', sa.String(), nullable=True))
    op.add_column('vessel_identity', sa.Column('ibc_igc_category', sa.String(), nullable=True))
    op.add_column('vessel_identity', sa.Column('ism_category', sa.String(), nullable=True))
    
    # Additional notations and restrictions
    op.add_column('vessel_identity', sa.Column('additional_notations', sa.String(), nullable=True))
    op.add_column('vessel_identity', sa.Column('service_restrictions', sa.String(), nullable=True))
    op.add_column('vessel_identity', sa.Column('record_comments', sa.String(), nullable=True))
    
    # Freeboard
    op.add_column('vessel_identity', sa.Column('freeboard_assignment', sa.String(), nullable=True))
    op.add_column('vessel_identity', sa.Column('freeboard_type', sa.String(), nullable=True))
    op.add_column('vessel_identity', sa.Column('freeboard_displacement', sa.Numeric(10, 2), nullable=True))
    op.add_column('vessel_identity', sa.Column('freeboard_deadweight', sa.Numeric(10, 2), nullable=True))
    op.add_column('vessel_identity', sa.Column('freeboard_calculated', sa.Numeric(10, 2), nullable=True))
    op.add_column('vessel_identity', sa.Column('freeboard_state', sa.String(), nullable=True))
    
    # DNV-specific
    op.add_column('vessel_identity', sa.Column('tanks_and_spaces_annual', sa.String(), nullable=True))
    
    # ABS condition status flags
    op.add_column('vessel_identity', sa.Column('conditions_of_class_reported', sa.Boolean(), nullable=True))
    op.add_column('vessel_identity', sa.Column('statutory_conditions_reported', sa.Boolean(), nullable=True))
    op.add_column('vessel_identity', sa.Column('special_recommendations_reported', sa.Boolean(), nullable=True))
    op.add_column('vessel_identity', sa.Column('special_additional_requirements_reported', sa.Boolean(), nullable=True))
    
    # ===================================================================
    # 2. Create vessel_dimensions table
    # ===================================================================
    
    op.create_table('vessel_dimensions',
        sa.Column('id', sa.String(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('vessel_id', sa.String(), nullable=False),
        sa.Column('length_overall_m', sa.Numeric(10, 2), nullable=True),
        sa.Column('length_between_perpendiculars', sa.Numeric(10, 2), nullable=True),
        sa.Column('breadth_moulded_m', sa.Numeric(10, 2), nullable=True),
        sa.Column('depth_moulded_m', sa.Numeric(10, 2), nullable=True),
        sa.Column('summer_draft_m', sa.Numeric(10, 2), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['vessel_id'], ['vessel.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vessel_id')
    )
    
    # ===================================================================
    # 3. Create vessel_tonnage table
    # ===================================================================
    
    op.create_table('vessel_tonnage',
        sa.Column('id', sa.String(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('vessel_id', sa.String(), nullable=False),
        sa.Column('gross_tonnage', sa.Integer(), nullable=True),
        sa.Column('gross_tonnage_pre69', sa.Integer(), nullable=True),
        sa.Column('net_tonnage', sa.Integer(), nullable=True),
        sa.Column('deadweight_tonnage', sa.Integer(), nullable=True),
        sa.Column('suez_gross_tonnage', sa.Numeric(10, 2), nullable=True),
        sa.Column('suez_net_tonnage', sa.Numeric(10, 2), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['vessel_id'], ['vessel.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vessel_id')
    )
    
    # ===================================================================
    # 4. Migrate existing tonnage data from vessel_identity to vessel_tonnage
    # ===================================================================
    
    # First, check if the columns exist before trying to migrate
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('vessel_identity')]
    
    if 'gross_tonnage' in columns and 'gross_tonnage_pre69' in columns:
        # Migrate existing data
        op.execute("""
            INSERT INTO vessel_tonnage (vessel_id, gross_tonnage, gross_tonnage_pre69)
            SELECT vessel_id, gross_tonnage, gross_tonnage_pre69
            FROM vessel_identity
            WHERE vessel_id IS NOT NULL
            ON CONFLICT (vessel_id) DO NOTHING
        """)
        
        # Drop old tonnage columns from vessel_identity
        op.drop_column('vessel_identity', 'gross_tonnage')
        op.drop_column('vessel_identity', 'gross_tonnage_pre69')


def downgrade() -> None:
    """Downgrade schema."""
    
    # Add back tonnage columns to vessel_identity
    op.add_column('vessel_identity', sa.Column('gross_tonnage', sa.Integer(), nullable=True))
    op.add_column('vessel_identity', sa.Column('gross_tonnage_pre69', sa.Integer(), nullable=True))
    
    # Migrate data back from vessel_tonnage
    op.execute("""
        UPDATE vessel_identity
        SET gross_tonnage = vt.gross_tonnage,
            gross_tonnage_pre69 = vt.gross_tonnage_pre69
        FROM vessel_tonnage vt
        WHERE vessel_identity.vessel_id = vt.vessel_id
    """)
    
    # Drop new tables
    op.drop_table('vessel_tonnage')
    op.drop_table('vessel_dimensions')
    
    # Drop new columns from vessel_identity
    op.drop_column('vessel_identity', 'special_additional_requirements_reported')
    op.drop_column('vessel_identity', 'special_recommendations_reported')
    op.drop_column('vessel_identity', 'statutory_conditions_reported')
    op.drop_column('vessel_identity', 'conditions_of_class_reported')
    op.drop_column('vessel_identity', 'tanks_and_spaces_annual')
    op.drop_column('vessel_identity', 'freeboard_state')
    op.drop_column('vessel_identity', 'freeboard_calculated')
    op.drop_column('vessel_identity', 'freeboard_deadweight')
    op.drop_column('vessel_identity', 'freeboard_displacement')
    op.drop_column('vessel_identity', 'freeboard_type')
    op.drop_column('vessel_identity', 'freeboard_assignment')
    op.drop_column('vessel_identity', 'record_comments')
    op.drop_column('vessel_identity', 'service_restrictions')
    op.drop_column('vessel_identity', 'additional_notations')
    op.drop_column('vessel_identity', 'ism_category')
    op.drop_column('vessel_identity', 'ibc_igc_category')
    op.drop_column('vessel_identity', 'marpol_category')
    op.drop_column('vessel_identity', 'solas_category')
    op.drop_column('vessel_identity', 'hull_number')
    op.drop_column('vessel_identity', 'shipyard')
    op.drop_column('vessel_identity', 'delivery_date')
    op.drop_column('vessel_identity', 'vessel_description')
    op.drop_column('vessel_identity', 'previous_class_society')
    op.drop_column('vessel_identity', 'dual_class')
    op.drop_column('vessel_identity', 'lifecycle_state')
    op.drop_column('vessel_identity', 'other_state')
    op.drop_column('vessel_identity', 'class_state')
    op.drop_column('vessel_identity', 'equipment_number')
    op.drop_column('vessel_identity', 'official_number')
    op.drop_column('vessel_identity', 'class_number')

