from telegram import Update
from telegram.ext import ContextTypes

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("⚙️ *Settings*\n\nDefault Currency: `USD`\nTax Rate: `0.0%`", parse_mode="Markdown")
