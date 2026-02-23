import os

# Set test environment variables BEFORE any project imports
os.environ["ENCRYPTION_KEY"] = "fxR172i-F8GuRaVJVmrbZh8paoeNPynsSXZqNy3o19Y="
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///test.db")
os.environ.setdefault("BOT_TOKEN", "123:test")
os.environ.setdefault("ENV", "development")
