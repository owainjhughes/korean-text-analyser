from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_key: str = ""
    jwt_secret: str = "dev-secret-key"  # overridden by JWT_SECRET env var in production

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
