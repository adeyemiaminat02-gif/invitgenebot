from telegram import Update
from telegram.ext import ContextTypes
from services.database import AsyncSessionLocal, Invoice
from sqlalchemy.future import select

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    target = update.message if update.message else update.callback_query.message

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Invoice).where(Invoice.user_id == user_id).order_by(Invoice.id.desc()).limit(10)
        )
        invoices = result.scalars().all()

    if not invoices:
        await target.reply_text("No invoices found in history.")
        return

    res_text = "📜 *Your Recent Invoices:*\n\n"
    for inv in invoices:
        res_text += f"• *{inv.invoice_number}* | {inv.customer_name} | {inv.currency} {inv.grand_total:.2f} | `{inv.status}`\n"

    await target.reply_text(res_text, parse_mode="Markdown")
