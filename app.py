import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from utils.config import Config
from utils.logger import logger
from services.database import init_db

from handlers.start import start_command
from handlers.profile import profile_handler
from handlers.create_invoice import create_invoice_handler, handle_finalize
from handlers.history import history_command
from handlers.help import help_command
from handlers.about import about_command
from handlers.search import search_command
from handlers.settings import settings_command

async def main():
    logger.info("Initializing database...")
    await init_db()

    logger.info("Starting Telegram Bot application...")
    application = Application.builder().token(Config.BOT_TOKEN).build()

    # Commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("settings", settings_command))

    # Conversation Handlers
    application.add_handler(profile_handler)
    application.add_handler(create_invoice_handler)

    # Callbacks
    application.add_handler(CallbackQueryHandler(start_command, pattern="^menu_start$"))
    application.add_handler(CallbackQueryHandler(history_command, pattern="^menu_history$"))
    application.add_handler(CallbackQueryHandler(help_command, pattern="^menu_help$"))
    application.add_handler(CallbackQueryHandler(about_command, pattern="^menu_about$"))
    application.add_handler(CallbackQueryHandler(settings_command, pattern="^menu_settings$"))
    application.add_handler(CallbackQueryHandler(handle_finalize, pattern="^finalize_invoice$"))

    # Start Polling
    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    logger.info("Bot is active and polling for updates.")
    
    # Keep application alive
    stop_event = asyncio.Event()
    await stop_event.wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
