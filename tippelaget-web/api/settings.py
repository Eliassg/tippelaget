from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    cognite_project: str
    cognite_base_url: str
    cognite_client_id: str
    cognite_client_secret: str
    cognite_token_url: str
    cognite_scopes: str = "https://bluefield.cognitedata.com/.default"

    openai_api_key: str

    # Data model (match tippelaget.core.config)
    default_space: str = "tippelaget_space_name"
    default_view: str = "Bet"
    default_view_version: str = "fcb537cee9eba5"
    event_view: str = "Event"
    event_view_version: str = "1.0.3"

    workflow_external_id: str = "wf_tippelaget_workflow"
    workflow_version: str = "1"

    openai_prophet_model: str = "gpt-4.1-mini"
    openai_king_model: str = "gpt-5-mini"

    # Repo root for serving player PNGs (optional). In Docker / Cloud Run, default /app (no PNGs unless you add them).
    repo_root: str = "../.."

    # Comma-separated extra CORS origins, e.g. https://youruser.github.io for GitHub Pages
    cors_extra_origins: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
