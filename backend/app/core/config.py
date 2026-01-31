from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "smart_workflow_automation"

    DATABASE_URL: str
    RABBITMQ_URL: str

    OPENAI_API_KEY: Optional[str]
    SLACK_WEBHOOK_URL: Optional[str]
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    REDIS_URL: str
    API_PORT: int
    IMAP_SERVER: str
    IMAP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_MAILBOX: str
    LOCAL_LLM_MODEL: str
    AIRFLOW_USERNAME: str
    AIRFLOW_PASSWORD: str
    AIRFLOW_FIRST_NAME: str
    AIRFLOW_LAST_NAME: str
    AIRFLOW_ROLE: str

    # Tell Pydantic to load from .env
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
