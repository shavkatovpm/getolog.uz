import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    # Main bot
    bot_token: str = os.getenv("BOT_TOKEN", "")

    # Database
    database_url: str = os.getenv("DATABASE_URL", "")

    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Encryption
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "")

    # Moderators
    moderator_ids: list[int] = field(default_factory=list)

    # Server
    server_url: str = os.getenv("SERVER_URL", "https://getolog.uz")
    webhook_port: int = int(os.getenv("WEBHOOK_PORT", "8443"))

    # Sentry
    sentry_dsn: str = os.getenv("SENTRY_DSN", "")

    # Environment
    env: str = os.getenv("ENV", "production")

    def __post_init__(self):
        raw_ids = os.getenv("MODERATOR_IDS", "")
        self.moderator_ids = [
            int(id_.strip()) for id_ in raw_ids.split(",") if id_.strip()
        ]

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    @property
    def webhook_url(self) -> str:
        return f"{self.server_url}/webhook"


config = Config()
