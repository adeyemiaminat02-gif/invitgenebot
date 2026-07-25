from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from services.database import AsyncSessionLocal, BusinessProfile
from sqlalchemy.future import select

BIZ_NAME, BIZ_EMAIL, BIZ_PHONE = range(3)

async def start_profile_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Please enter your *Business Name*:", parse_mode="Markdown")
    return BIZ_NAME

async def save_biz_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['biz_name'] = update.message.text
    await update.message.reply_text("Please enter your *Business Email*:", parse_mode="Markdown")
    return BIZ_EMAIL

async def save_biz_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['biz_email'] = update.message.text
    await update.message.reply_text("Please enter your *Business Phone Number*:", parse_mode="Markdown")
    return BIZ_PHONE

async def save_biz_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data['biz_phone'] = update.message.text

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(BusinessProfile).where(BusinessProfile.user_id == user_id))
        profile = result.scalars().first()
        if not profile:
            profile = BusinessProfile(user_id=user_id)

        profile.business_name = context.user_data['biz_name']
        profile.email = context.user_data['biz_email']
        profile.phone = context.user_data['biz_phone']

        session.add(profile)
        await session.commit()

    await update.message.reply_text("✅ *Business Profile Updated Successfully!*", parse_mode="Markdown")
    return ConversationHandler.END

async def cancel_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Profile setup cancelled.")
    return ConversationHandler.END

profile_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_profile_setup, pattern="^menu_profile$")],
    states={
        BIZ_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_biz_name)],
        BIZ_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_biz_email)],
        BIZ_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_biz_phone)],
    },
    fallbacks=[CommandHandler("cancel", cancel_profile)],
)
