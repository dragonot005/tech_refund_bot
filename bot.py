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

# ====== ID ADMIN ======
MONITOR_USER_ID = 7067411241  # Ton ID
ADMIN_IDS = [7067411241, 6489634519]  # Toi et Brulux

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

STATUS_TYPES = {
    "online": "🟢 En ligne - Réponse rapide",
    "busy": "🟡 Occupé - Réponse sous 1h",
    "offline": "🔴 Hors ligne - Réponse sous 24h",
    "pause": "☕ En pause - Reviens dans 30 min"
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

# ====== COMMANDES POUR CHANGER LES STATUTS ======
async def set_staff_status(update: Update, context: ContextTypes.DEFAULT_TYPE, staff: str, status: str):
    """Change le statut d'un support"""
    # Vérifie que l'utilisateur est admin
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Commande réservée aux admins")
        return
    
    if staff not in SUPPORT_STAFF:
        await update.message.reply_text("❌ Support inconnu")
        return
    
    if status not in STATUS_TYPES:
        await update.message.reply_text("❌ Statut inconnu")
        return
    
    # Règles : seul toi peut modifier Brulux
    if staff == "brulux" and update.effective_user.id == 6489634519:
        # Brulux change son propre statut
        pass
    elif staff == "brulux" and update.effective_user.id == 7067411241:
        # Toi changes le statut de Brulux
        pass
    elif staff == "drago" and update.effective_user.id == 7067411241:
        # Toi changes ton propre statut
        pass
    elif staff == "drago" and update.effective_user.id == 6489634519:
        await update.message.reply_text("⛔ Tu ne peux changer que ton propre statut")
        return
    
    # Applique le changement
    SUPPORT_STAFF[staff]["online"] = (status == "online")
    SUPPORT_STAFF[staff]["message"] = STATUS_TYPES[status]
    SUPPORT_STAFF[staff]["updated_at"] = paris_now().strftime("%H:%M")
    SUPPORT_STAFF[staff]["updated_by"] = update.effective_user.username or "Admin"
    
    await update.message.reply_text(
        f"✅ {SUPPORT_STAFF[staff]['name']} est maintenant : {STATUS_TYPES[status]}\n"
        f"Mis à jour par : @{update.effective_user.username}"
    )

# Commandes pour Drago
async def drago_enligne(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_staff_status(update, context, "drago", "online")

async def drago_occupe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_staff_status(update, context, "drago", "busy")

async def drago_horsligne(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_staff_status(update, context, "drago", "offline")

async def drago_pause(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_staff_status(update, context, "drago", "pause")

# Commandes pour Brulux
async def brulux_enligne(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_staff_status(update, context, "brulux", "online")

async def brulux_occupe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_staff_status(update, context, "brulux", "busy")

async def brulux_horsligne(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_staff_status(update, context, "brulux", "offline")

async def brulux_pause(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_staff_status(update, context, "brulux", "pause")

# ====== HANDLERS DES BOUTONS ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bienvenue ! Choisis une option :",
        reply_markup=main_menu()
    )

async def show_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche le statut des supports (version qui fonctionne)"""
    query = update.callback_query
    await query.answer()
    
    # 🔥 IMPORTANT: On lit les données à jour dans SUPPORT_STAFF
    message = "📊 *Statut du support*\n\n"
    
    for staff_id, staff in SUPPORT_STAFF.items():
        message += f"👤 **{staff['name']}** : {staff['message']}\n"
        if staff['updated_at']:
            message += f"   └ Mis à jour à {staff['updated_at']}"
            if staff['updated_by']:
                message += f" par @{staff['updated_by']}"
            message += "\n"
        message += "\n"
    
    message += "💡 Clique sur un support pour contacter :"
    
    # Récupère les statuts actuels pour les emojis
    drago_emoji = "🟢" if SUPPORT_STAFF["drago"]["online"] else "🔴"
    brulux_emoji = "🟢" if SUPPORT_STAFF["brulux"]["online"] else "🔴"
    
    keyboard = [
        [InlineKeyboardButton(f"{drago_emoji} Contacter Drago", callback_data="support_drago")],
        [InlineKeyboardButton(f"{brulux_emoji} Contacter Brulux", callback_data="support_brulux")],
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
    
    # Commandes de démarrage
    app.add_handler(CommandHandler("start", start))
    
    # Commandes pour changer les statuts
    app.add_handler(CommandHandler("drago_enligne", drago_enligne))
    app.add_handler(CommandHandler("drago_occupe", drago_occupe))
    app.add_handler(CommandHandler("drago_horsligne", drago_horsligne))
    app.add_handler(CommandHandler("drago_pause", drago_pause))
    
    app.add_handler(CommandHandler("brulux_enligne", brulux_enligne))
    app.add_handler(CommandHandler("brulux_occupe", brulux_occupe))
    app.add_handler(CommandHandler("brulux_horsligne", brulux_horsligne))
    app.add_handler(CommandHandler("brulux_pause", brulux_pause))
    
    # Gestionnaire des boutons
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🚀 Bot démarré avec gestion des statuts")
    print(f"👤 Admins: toi (7067411241) et Brulux (6489634519)")
    print("✅ Commandes disponibles :")
    print("   /drago_enligne, /drago_occupe, /drago_horsligne, /drago_pause")
    print("   /brulux_enligne, /brulux_occupe, /brulux_horsligne, /brulux_pause")
    print("✅ Le bouton Statut du support fonctionne après chaque changement !")
    
    app.run_polling()
