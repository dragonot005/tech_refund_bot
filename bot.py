import os
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

# ====== CONFIG ======
BOT_VERSION = "v1.4"
BOT_UPDATED = "14/02/2026"

SUPPORT_1_USERNAME = "Drago_JS"
SUPPORT_2_USERNAME = "BruluxOnFlux"

# ====== STATUT SUPPORT ======
SUPPORT_STAFF = {
    "drago": {
        "name": "Drago",
        "online": True,
        "message": "🟢 En ligne - Réponse rapide",
        "updated_at": None,
        "updated_by": None
    },
    "brulux": {
        "name": "Brulux",
        "online": True,
        "message": "🟢 En ligne - Réponse rapide",
        "updated_at": None,
        "updated_by": None
    }
}

# ====== TIME ======
def paris_now():
    return datetime.now(ZoneInfo("Europe/Paris"))

# ====== KEYBOARDS ======
def main_menu():
    keyboard = [
        [InlineKeyboardButton("📊 Statut du support", callback_data="show_status")],
        [InlineKeyboardButton("🛠 Support Drago", callback_data="support_drago")],
        [InlineKeyboardButton("🛠 Support Brulux", callback_data="support_brulux")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ====== HANDLERS ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bienvenue ! Choisis une option :",
        reply_markup=main_menu()
    )

async def show_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche le statut des supports"""
    query = update.callback_query
    await query.answer()
    
    message = "📊 *Statut du support*\n\n"
    
    for staff_id, staff in SUPPORT_STAFF.items():
        message += f"👤 **{staff['name']}** : {staff['message']}\n\n"
    
    message += "💡 Clique sur un support pour contacter :"
    
    keyboard = [
        [InlineKeyboardButton("🟢 Contacter Drago", callback_data="support_drago")],
        [InlineKeyboardButton("🟢 Contacter Brulux", callback_data="support_brulux")],
        [InlineKeyboardButton("🔄 Rafraîchir", callback_data="refresh_status")],
        [InlineKeyboardButton("⬅ Retour", callback_data="back_main")]
    ]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def refresh_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rafraîchit l'affichage du statut"""
    query = update.callback_query
    await query.answer()
    await show_status(update, context)

async def back_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Retour au menu principal"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "👋 Bienvenue ! Choisis une option :",
        reply_markup=main_menu()
    )

async def support_drago(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Contacte Drago"""
    query = update.callback_query
    await query.answer()
    
    url = f"https://t.me/{SUPPORT_1_USERNAME}"
    keyboard = [[InlineKeyboardButton("💬 Ouvrir la discussion", url=url)]]
    keyboard.append([InlineKeyboardButton("⬅ Retour", callback_data="back_main")])
    
    await query.edit_message_text(
        f"Clique ci-dessous pour contacter Drago :",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def support_brulux(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Contacte Brulux"""
    query = update.callback_query
    await query.answer()
    
    url = f"https://t.me/{SUPPORT_2_USERNAME}"
    keyboard = [[InlineKeyboardButton("💬 Ouvrir la discussion", url=url)]]
    keyboard.append([InlineKeyboardButton("⬅ Retour", callback_data="back_main")])
    
    await query.edit_message_text(
        f"Clique ci-dessous pour contacter Brulux :",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestionnaire principal des boutons"""
    query = update.callback_query
    await query.answer()
    
    print(f"🔍 Callback reçu: {query.data}")  # DEBUG
    
    if query.data == "show_status":
        await show_status(update, context)
    elif query.data == "refresh_status":
        await refresh_status(update, context)
    elif query.data == "back_main":
        await back_main(update, context)
    elif query.data == "support_drago":
        await support_drago(update, context)
    elif query.data == "support_brulux":
        await support_brulux(update, context)
    else:
        await query.edit_message_text(f"❌ Bouton inconnu: {query.data}")

# ====== MAIN ======
if __name__ == "__main__":
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        print("❌ ERREUR : TELEGRAM_TOKEN manquant !")
        TOKEN = input("Entre ton token Telegram : ")
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🚀 Bot de test démarré")
    print("✅ Teste le bouton 'Statut du support'")
    app.run_polling()
