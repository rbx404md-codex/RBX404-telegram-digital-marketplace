"""Main entry point for the Telegram Digital Marketplace Bot."""

import asyncio
import sys
from pathlib import Path

from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from bot.config import get_settings
from bot.database import init_db, get_db_instance
from bot.handlers import (
    start_handler,
    help_handler,
    language_handler,
    callback_handler,
    unknown_handler,
    error_handler
)
from bot.middlewares import (
    UserMiddleware,
    RateLimitMiddleware,
    LoggingMiddleware,
    i18n_middleware
)
from bot.utils.logger import setup_logging, log
from bot.utils.constants import Command


async def initialize() -> None:
    """Initialize all components before starting the bot."""
    
    # Setup logging
    settings = get_settings()
    setup_logging(log_dir=settings.logs_dir)
    
    log.info("🚀 Starting Telegram Digital Marketplace Bot")
    log.info(f"Bot name: {settings.bot_name}")
    log.info(f"Bot username: {settings.bot_username}")
    
    # Initialize database
    await init_db()
    log.info("✓ Database initialized")
    
    # Create initial admin if not exists
    db = get_db_instance()
    async with db.session() as session:
        from bot.database.repositories import UserRepository
        user_repo = UserRepository(session)
        
        # Check if owner exists
        owner = await user_repo.get_by_telegram_id(settings.owner_id)
        if not owner:
            from telegram import User as TelegramUser
            # Create admin user with owner role
            # Note: We need to get user info from Telegram API here
            # For now, we'll create a minimal admin
            from bot.database.models import User
            admin = User(
                telegram_id=settings.owner_id,
                first_name="Admin",
                username="admin",
                role="owner",
                is_active=True
            )
            session.add(admin)
            await session.flush()
            
            # Generate referral code
            import random
            import string
            code = ''.join(random.choices(
                string.ascii_uppercase + string.digits,
                k=8
            ))
            admin.referral_code = code
            await session.flush()
            
            log.info(f"✓ Created owner account for {settings.owner_id}")
    
    log.info("✓ All components initialized")


async def main() -> None:
    """Main bot entry point."""
    
    try:
        # Initialize all components
        await initialize()
        
        settings = get_settings()
        
        # Create application
        application = Application.builder().token(
            settings.bot_token.get_secret_value()
        ).build()
        
        # Add middleware
        application.update_persistent_state(UserMiddleware())
        application.update_persistent_state(RateLimitMiddleware())
        application.update_persistent_state(LoggingMiddleware())
        
        # Add handlers
        application.add_handler(CommandHandler("start", start_handler))
        application.add_handler(CommandHandler("help", help_handler))
        application.add_handler(CommandHandler("language", language_handler))
        
        # Callback handlers
        application.add_handler(CallbackQueryHandler(callback_handler))
        
        # Message handlers
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_handler))
        
        # Error handler
        application.add_error_handler(error_handler)
        
        # Start polling
        log.info("✓ Bot is polling...")
        await application.run_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"]
        )
        
    except KeyboardInterrupt:
        log.info("🛑 Bot stopped by user")
    except Exception as e:
        log.error(f"❌ Fatal error: {e}", exc_info=True)
        raise
    finally:
        # Cleanup
        db = get_db_instance()
        await db.close()
        log.info("✓ Database connection closed")


if __name__ == "__main__":
    asyncio.run(main())
