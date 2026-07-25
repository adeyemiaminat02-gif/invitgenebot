from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("➕ Create Invoice", callback_data="menu_create")],
        [InlineKeyboardButton("📄 My Invoices", callback_data="menu_history"), InlineKeyboardButton("👤 Profile", callback_data="menu_profile")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings"), InlineKeyboardButton("❓ Help", callback_data="menu_help")],
        [InlineKeyboardButton("ℹ️ About", callback_data="menu_about")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_status_keyboard(invoice_id: int):
    keyboard = [
        [InlineKeyboardButton("Paid", callback_data=f"status_{invoice_id}_Paid"),
         InlineKeyboardButton("Sent", callback_data=f"status_{invoice_id}_Sent")],
        [InlineKeyboardButton("Cancelled", callback_data=f"status_{invoice_id}_Cancelled")]
    ]
    return InlineKeyboardMarkup(keyboard)
