"""Loyihaning barcha sozlamalari shu yerda, .env faylidan avtomatik o'qiladi."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    encryption_key: str

    # GETOLOG bosh botining tokeni va owner ID'si — .env'da to'ldiriladi
    main_bot_token: str
    owner_telegram_id: int

    webhook_base_url: str
    webhook_server_port: int = 8080

    # Dashboard (Next.js, app.getolog.uz) uchun: JWT imzolash kaliti va CORS ruxsati
    jwt_secret_key: str
    dashboard_origin: str = "https://app.getolog.uz"


settings = Settings()
