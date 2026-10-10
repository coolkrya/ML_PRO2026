from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_path: str = "artifact/model_1.0.joblib" 
    database_url: str = "postgresql://postgres:postgres@postgres::5432"
    log_level: str = "INFO"

    model_config = {"env_file": ".env"}

settings = Settings()
