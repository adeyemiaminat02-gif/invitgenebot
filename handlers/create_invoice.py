import os
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from services.database import AsyncSessionLocal, Invoice, InvoiceItem, BusinessProfile, UserSettings
from services.calculations import calculate_invoice_totals
from services.pdf_generator import generate_pdf_invoice
from sqlalchemy.future import select

CUST_NAME, ITEM_DESC, ITEM_PRICE = range(3)

async def start_create_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['invoice_items'] = []
    await query.message.reply_text("Enter *Customer Name*:", parse_mode="Markdown")
    return CUST_NAME

async def save_cust_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['cust_name'] = update.message.text
    await update.message.reply_text("Enter Item/Service *Description*:", parse_mode="Markdown")
    return ITEM_DESC

async def save_item_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['temp_item_desc'] = update.message.text
    await update.message.reply_text("Enter Item *Unit Price* (e.g. 50.00):", parse_mode="Markdown")
    return ITEM_PRICE

async def save_item_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = float(update.message.text)
    except ValueError:
        await update.message.reply_text("Invalid price. Please enter a valid number:")
        return ITEM_PRICE

    context.user_data['invoice_items'].append({
        "description": context.user_data['temp_item_desc'],
        "quantity": 1.0,
        "unit_price": price
    })

    keyboard = [
        [InlineKeyboardButton("➕ Add Another Item", callback_data="add_item")],
        [InlineKeyboardButton("✅ Generate Invoice PDF", callback_data="finalize_invoice")]
    ]
    await update.message.reply_text(
        f"Item added! Current Total Items: {len(context.user_data['invoice_items'])}\nWhat would you like to do next?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END

async def handle_finalize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    async with AsyncSessionLocal() as session:
        prof_res = await session.execute(select(BusinessProfile).where(BusinessProfile.user_id == user_id))
        profile = prof_res.scalars().first()

        sett_res = await session.execute(select(UserSettings).where(UserSettings.user_id == user_id))
        settings = sett_res.scalars().first()

        inv_num = f"{settings.invoice_prefix if settings else 'INV-'}{uuid.uuid4().hex[:6].upper()}"
        currency = settings.currency if settings else "USD"

        items = context.user_data.get('invoice_items', [])
        totals = calculate_invoice_totals(items)

        # Save to DB
        invoice = Invoice(
            invoice_number=inv_num,
            user_id=user_id,
            customer_name=context.user_data.get('cust_name', 'Customer'),
            currency=currency,
            subtotal=totals['subtotal'],
            tax_total=totals['tax_total'],
            grand_total=totals['grand_total'],
            status="Draft"
        )
        session.add(invoice)
        await session.commit()
        await session.refresh(invoice)

        for item in items:
            inv_item = InvoiceItem(
                invoice_id=invoice.id,
                description=item['description'],
                quantity=item['quantity'],
                unit_price=item['unit_price'],
                line_total=item['quantity'] * item['unit_price']
            )
            session.add(inv_item)
        await session.commit()

        # Build PDF data struct
        pdf_data = {
            "invoice_number": inv_num,
            "business_name": profile.business_name if profile else "My Business",
            "business_email": profile.email if profile else "",
            "business_phone": profile.phone if profile else "",
            "customer_name": invoice.customer_name,
            "currency": currency,
            "items": items,
            "subtotal": totals['subtotal'],
            "grand_total": totals['grand_total']
        }

        os.makedirs("temp", exist_ok=True)
        pdf_path = f"temp/{inv_num}.pdf"
        generate_pdf_invoice(pdf_data, pdf_path)

        await query.message.reply_document(
            document=open(pdf_path, 'rb'),
            filename=f"{inv_num}.pdf",
            caption=f"📄 *Invoice {inv_num} generated successfully!*",
            parse_mode="Markdown"
        )

        if os.path.exists(pdf_path):
            os.remove(pdf_path)

create_invoice_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_create_invoice, pattern="^menu_create$")],
    states={
        CUST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_cust_name)],
        ITEM_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_item_desc)],
        ITEM_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_item_price)],
    },
    fallbacks=[],
)
