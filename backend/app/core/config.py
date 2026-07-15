from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "여행씰 API"
    database_url: str = "sqlite:///./localhub.db"
    frontend_origin: str = "http://localhost:5173"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    data_root: str = ""

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def allowed_origins(self) -> list[str]:
        origins = {origin.strip() for origin in self.frontend_origin.split(",") if origin.strip()}
        local_origins = {"http://localhost:5173", "http://127.0.0.1:5173"}
        if origins & local_origins:
            origins.update(local_origins)
        return sorted(origins)

    @property
    def resolved_database_url(self) -> str:
        if not self.database_url.startswith("sqlite:///./"):
            return self.database_url
        backend_root = Path(__file__).resolve().parents[2]
        database_name = self.database_url.removeprefix("sqlite:///./")
        return f"sqlite:///{(backend_root / database_name).as_posix()}"

    @property
    def resolved_data_root(self) -> Path:
        if self.data_root:
            return Path(self.data_root).resolve()
        return Path(__file__).resolve().parents[3] / "data"


@lru_cache
def get_settings() -> Settings:
    return Settings()
