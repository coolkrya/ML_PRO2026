from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_path: str | None = None
    database_url: str = "postgresql://postgres:postgres@postgres:5432/predictions"
    log_level: str = "INFO"

    model_config = {"env_file": ".env"}

settings = Settings()
