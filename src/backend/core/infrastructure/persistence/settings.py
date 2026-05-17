from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[5]


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="GAMIF_DB_",
        env_file=(_REPO_ROOT / ".env", ".env"),
        extra="ignore",
    )

    host: str = "localhost"
    port: int = 5432
    user: str
    password: str
    name: str
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10

    @property
    def url(self) -> str:
        return (
            f"postgresql+psycopg://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )
