from telegram import Update
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "❓ *Help & Usage Guide*\n\n"
        "• Use /create or click 'Create Invoice' to issue a new bill.\n"
        "• Set up your company info under 'Profile' so it shows up on PDFs.\n"
        "• View all prior generated PDFs under /history.\n"
        "• Modify default currencies and tax rates under /settings."
    )
    target = update.message if update.message else update.callback_query.message
    await target.reply_text(text, parse_mode="Markdown")
