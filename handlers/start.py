from telegram import Update
from telegram.ext import ContextTypes
from keyboards.inline import get_main_keyboard
from services.database import AsyncSessionLocal, User, UserSettings
from sqlalchemy.future import select

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            user = User(id=user_id, username=username)
            settings = UserSettings(user_id=user_id)
            session.add_all([user, settings])
            await session.commit()

    welcome_text = (
        "🧾 *Welcome to Invoice Generator Bot!*\n\n"
        "Create beautiful, professional invoices in minutes. Add your business details, "
        "customer information, products or services, taxes, discounts, and export invoices as PDF directly inside Telegram."
    )
    
    if update.message:
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())
    elif update.callback_query:
        await update.callback_query.message.edit_text(welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())
