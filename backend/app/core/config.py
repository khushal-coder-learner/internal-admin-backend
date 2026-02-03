from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "internal-admin-backend"
    description: str = "Management-System"
    version: str = "0.1.0"
    env: str = "development"

    database_url: str = ""
    test_database_url: str = ""
    secret_key: str = ""
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
    )


settings = Settings()
