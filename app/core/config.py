import json
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Jeejal API"
    api_prefix: str = "/api"
    secret_key: str = "change-this-in-production"
    access_token_expire_minutes: int = 10080
    database_url: str = "sqlite:///./jeejal.db"
    upload_dir: str = "uploads"
    generated_report_dir: str = "generated_reports"
    allowed_cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def model_post_init(self, __context):
        if isinstance(self.allowed_cors_origins, str):
            self.allowed_cors_origins = json.loads(self.allowed_cors_origins)

    @property
    def base_dir(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def upload_path(self) -> Path:
        return self.base_dir / self.upload_dir

    @property
    def report_path(self) -> Path:
        return self.base_dir / self.generated_report_dir

    def ensure_directories(self) -> None:
        self.upload_path.mkdir(parents=True, exist_ok=True)
        self.report_path.mkdir(parents=True, exist_ok=True)
        (self.upload_path / "ultrasounds").mkdir(parents=True, exist_ok=True)
        (self.upload_path / "signatures").mkdir(parents=True, exist_ok=True)


settings = Settings()
