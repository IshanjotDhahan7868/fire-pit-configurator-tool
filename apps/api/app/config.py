from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Fire Pit Configurator API"
    environment: str = "development"
    secret_key: str = "dev-secret-key-change"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8
    cors_origins: str = "http://localhost:3000"
    database_url: str = "sqlite:///./firepit.db"
    email_output_dir: str = "generated_emails"
    pdf_output_dir: str = "generated_pdfs"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, value: str):
        if len(value) < 16:
            raise ValueError("SECRET_KEY must be at least 16 characters")
        return value

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
