from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "internal-admin-backend"
    description: str = "Management-System"
    version: str = "0.1.0"
    env: str = "development"
    frontend_origin: str = "http://localhost:5173"

    database_url: str
    test_database_url: str
    redis_url: str
    test_redis_url: str
    export_dir: str = "/data/exports"
    exports_download_url: str | None = None

    secret_key: str
    jwt_secret_key: str

    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 3
    log_level: str = "INFO"
    log_dir: str = str(BASE_DIR / "logs")
    log_file: str = "app.log"
    log_max_bytes: int = 5 * 1024 * 1024
    log_backup_count: int = 5

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        case_sensitive=False,  # optional but recommended
    )


settings = Settings() # type: ignore
