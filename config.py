"""
Central configuration. Everything is read from .env so the same codebase
runs unchanged on Termux, a VPS, or Railway — only the .env values differ.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _int_list(raw: str) -> list[int]:
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
ADMIN_IDS: list[int] = _int_list(os.getenv("ADMIN_IDS", ""))

STORAGE_CHANNEL_ID: int = int(os.getenv("STORAGE_CHANNEL_ID", "0"))
BACKUP_CHANNEL_ID: int = int(os.getenv("BACKUP_CHANNEL_ID", "0"))

BACKUP_INTERVAL_MINUTES: int = int(os.getenv("BACKUP_INTERVAL_MINUTES", "60"))
REFERRAL_REWARD_COIN: int = int(os.getenv("REFERRAL_REWARD_COIN", "20"))

DB_PATH: str = os.getenv("DB_PATH", "data/bot.db")


def validate() -> None:
    """Fail loudly and clearly instead of crashing with a cryptic trace."""
    missing = []
    if not BOT_TOKEN:
        missing.append("BOT_TOKEN")
    if not ADMIN_IDS:
        missing.append("ADMIN_IDS")
    if not STORAGE_CHANNEL_ID:
        missing.append("STORAGE_CHANNEL_ID")
    if not BACKUP_CHANNEL_ID:
        missing.append("BACKUP_CHANNEL_ID")

    if missing:
        raise SystemExit(
            "\n❌ .env এ এই ভ্যালুগুলো সেট করা নেই: "
            + ", ".join(missing)
            + "\n👉 .env.example কপি করে .env বানান এবং মান বসান।\n"
        )
