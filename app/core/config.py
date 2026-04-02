from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/app"
    SECRET_KEY: str = "change-me-in-production"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
