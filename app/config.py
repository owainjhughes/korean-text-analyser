from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_key: str = ""
    jwt_secret: str = "dev-secret-key"  # overridden by JWT_SECRET env var in production
    jwt_ttl_days: int = 7

    # async driver for the app, sync driver for alembic
    database_url: str = "postgresql+asyncpg://saebae:saebae@postgres:5432/saebae"
    database_url_sync: str = "postgresql+psycopg://saebae:saebae@postgres:5432/saebae"

    cookie_secure: bool = False  # True in production (HTTPS via Caddy)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
