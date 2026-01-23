from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "smart_workflow_automation"

    DATABASE_URL: str
    RABBITMQ_URL: str

    OPENAI_API_KEY: str | None = None
    SLACK_WEBHOOK_URL: str | None = None
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    REDIS_URL: str
    API_PORT: int
    SMTP_USER: str
    SMTP_PASS: str

    # Tell Pydantic to load from .env
    # model_config = SettingsConfigDict(env_file="../.env", case_sensitive=True)

settings = Settings()
