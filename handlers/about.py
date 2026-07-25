from telegram import Update
from telegram.ext import ContextTypes

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "ℹ️ *About @InVitGeneBot*\n\n"
        "Version: `1.0.0`\n"
        "Engine: Python 3.12 | python-telegram-bot v21+\n\n"
        "A lightweight, scalable invoice generation system designed for high performance."
    )
    target = update.message if update.message else update.callback_query.message
    await target.reply_text(text, parse_mode="Markdown")
