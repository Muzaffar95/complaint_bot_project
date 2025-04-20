import os
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "complaints")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", f"{WEBHOOK_HOST}{WEBHOOK_PATH}")
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key")

ADMINS = os.getenv("ADMINS", "").split(",")
DB_URL = os.getenv("DB_URL", "postgresql://admin:admin@db:5432/complaintdb")
NOTIFY_CHAT_ID = os.getenv("NOTIFY_CHAT_ID")
