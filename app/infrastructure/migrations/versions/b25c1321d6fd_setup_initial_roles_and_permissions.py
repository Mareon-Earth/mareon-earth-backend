"""setup initial roles and permissions

Revision ID: b25c1321d6fd
Revises: 173332464ab6
Create Date: 2025-12-16 20:21:10.397981

"""

from typing import Sequence, Union

from alembic import op
from app.core.config import get_settings


# revision identifiers, used by Alembic.
revision: str = "<new_revision_id>"  # <-- PASTE THE NEW REVISION ID HERE
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Sets up the core database roles and default permissions by reading from settings.
    This ensures the setup is portable across different environments (prod, staging, etc.).
    """
    settings = get_settings()

    if settings.db_mode != "cloudsql_iam":
        print("Skipping role creation in non-CloudSQL IAM mode.")
        return

    api_user = settings.db_iam_user
    migration_user = settings.migration_iam_user

    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'api_role') THEN
                CREATE ROLE api_role;
            END IF;
        END
        $$;
    """)

    op.execute(f'GRANT api_role TO "{api_user}";')
    op.execute(f'GRANT CREATE, USAGE ON SCHEMA public TO "{migration_user}";')

    op.execute(f"""
        ALTER DEFAULT PRIVILEGES FOR ROLE "{migration_user}" IN SCHEMA public
        GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO api_role;

        ALTER DEFAULT PRIVILEGES FOR ROLE "{migration_user}" IN SCHEMA public
        GRANT USAGE, SELECT ON SEQUENCES TO api_role;
    """)


def downgrade() -> None:
    settings = get_settings()
    if settings.db_mode != "cloudsql_iam":
        return

    api_user = settings.db_iam_user
    migration_user = settings.migration_iam_user

    op.execute(f"""
        ALTER DEFAULT PRIVILEGES FOR ROLE "{migration_user}" IN SCHEMA public
        REVOKE SELECT, INSERT, UPDATE, DELETE ON TABLES FROM api_role;

        ALTER DEFAULT PRIVILEGES FOR ROLE "{migration_user}" IN SCHEMA public
        REVOKE USAGE, SELECT ON SEQUENCES FROM api_role;
    """)
    op.execute(f'REVOKE CREATE, USAGE ON SCHEMA public FROM "{migration_user}";')
    op.execute(f'REVOKE api_role FROM "{api_user}";')
    op.execute("DROP ROLE IF EXISTS api_role;")
