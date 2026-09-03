"""
Single entry point. `git clone` -> fill .env -> `python main.py` and
everything (db restore/creation, scheduled backups, handlers) wires itself
up automatically. No manual setup steps beyond .env.
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, ErrorEvent

import config
from database.models import init_db
from database.backup_restore import restore_latest, backup_and_pin
from handlers import root_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("main")


async def on_error(event: ErrorEvent) -> bool:
    """
    Catches any exception raised inside a handler so one bad update never
    takes the whole bot down — it just gets logged, and the user's update
    is skipped instead of crashing the polling loop.
    """
    log.error("Unhandled error while processing update: %s", event.exception, exc_info=event.exception)
    return True


async def periodic_backup(bot: Bot) -> None:
    interval = max(5, config.BACKUP_INTERVAL_MINUTES) * 60
    while True:
        await asyncio.sleep(interval)
        try:
            await backup_and_pin(bot, note="auto")
        except Exception as e:  # noqa: BLE001 — never let a backup failure kill the bot
            log.error("Auto-backup failed: %s", e)


async def main() -> None:
    config.validate()

    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(root_router)
    dp.errors.register(on_error)

    await bot.set_my_commands([
        BotCommand(command="start", description="বট শুরু করুন / মেনু দেখুন"),
        BotCommand(command="cancel", description="চলমান কাজ বাতিল করুন"),
        BotCommand(command="admin", description="অ্যাডমিন প্যানেল (শুধু অ্যাডমিনদের জন্য)"),
    ])

    log.info("Checking for an existing backup to restore...")
    restored = await restore_latest(bot)
    log.info("Restored from backup channel." if restored else "Starting with local/fresh database.")

    await init_db()
    log.info("Database ready at %s", config.DB_PATH)

    asyncio.create_task(periodic_backup(bot))

    log.info("Bot starting (long polling)...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Bot stopped.")
