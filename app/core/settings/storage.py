from pydantic_settings import BaseSettings


class StorageSettings(BaseSettings):
    gcs_bucket_name: str = "mareon-prod-app-data"
