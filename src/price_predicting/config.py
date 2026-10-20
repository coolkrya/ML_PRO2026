from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_path: str = "artifact/model_1.0.joblib" 
    database_url: str | None =  None
    model_aliaas: str = "champion"
    mlflow_tracking_uri: str = "http://127.0.0.1:5000"
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "protected_namespaces": ()}

settings = Settings()
