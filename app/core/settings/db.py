from typing import Literal
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """
    Database configuration settings.
    
    Supports two modes:
    - local_url: Standard connection string for local/direct database access
    - cloudsql_iam: Google Cloud SQL with IAM authentication
    """
    
    # Mode selection
    db_mode: Literal["local_url", "cloudsql_iam"] = "local_url"

    # Local mode settings (required when db_mode="local_url")
    database_url: str = ""

    # Cloud SQL mode settings (required when db_mode="cloudsql_iam")
    cloud_sql_instance: str = ""
    db_name: str = ""
    db_iam_user: str = ""
    migration_iam_user: str = ""
    db_connector_ip_type: Literal["PUBLIC", "PRIVATE"] = "PRIVATE"

    # Connection pool settings (shared across all modes)
    db_pool_size: int = 5
    db_max_overflow: int = 5
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800
    db_pool_pre_ping: bool = True
