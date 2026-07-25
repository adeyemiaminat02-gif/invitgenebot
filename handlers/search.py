from telegram import Update
from telegram.ext import ContextTypes
from services.database import AsyncSessionLocal, Invoice
from sqlalchemy.future import select

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/search <customer_name_or_number>`", parse_mode="Markdown")
        return

    query_str = f"%{context.args[0]}%"
    user_id = update.effective_user.id

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Invoice).where(
                Invoice.user_id == user_id,
                (Invoice.customer_name.like(query_str)) | (Invoice.invoice_number.like(query_str))
            )
        )
        invoices = result.scalars().all()

    if not invoices:
        await update.message.reply_text("No matching invoices found.")
        return

    text = "🔎 *Search Results:*\n\n"
    for inv in invoices:
        text += f"• *{inv.invoice_number}* | {inv.customer_name} | {inv.currency} {inv.grand_total:.2f}\n"

    await update.message.reply_text(text, parse_mode="Markdown")
