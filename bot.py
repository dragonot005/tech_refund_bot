import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Configuration des logs pour voir les erreurs sur Railway
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Textes du bot
TEXTS = {
    'fr': {
        'welcome': "✅ Bienvenue chez **Tech Refund** !\n\nChoisissez une option ci-dessous :",
        'btn_refund': "📁 Obtenir le fichier Tech Refund",
        'sent': "Voici votre fichier ! Si vous avez des questions, contactez le support.",
        'error': "❌ Erreur : Le fichier 'tech_refund.pdf' est manquant sur le serveur."
    },
    'en': {
        'welcome': "✅ Welcome to **Tech Refund**!\n\nChoose an option below:",
        'btn_refund': "📁 Get Tech Refund file",
        'sent': "Here is your file! If you have any questions, contact support.",
        'error': "❌ Error: The file 'tech_refund.pdf' is missing on the server."
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /start : Choix de la langue"""
    keyboard = [
        [InlineKeyboardButton("Français 🇫🇷", callback_data='lang_fr')],
        [InlineKeyboardButton("English 🇬🇧", callback_data='lang_en')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose your language / Choisissez votre langue :", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les clics sur les boutons"""
    query = update.callback_query
    await query.answer()
    
    # Si l'utilisateur choisit une langue
    if query.data.startswith('lang_'):
        lang = query.data.split('_')[1]
        context.user_data['lang'] = lang
        
        keyboard = [[InlineKeyboardButton(TEXTS[lang]['btn_refund'], callback_data='send_file')]]
        await query.edit_message_text(TEXTS[lang]['welcome'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    # Si l'utilisateur demande le fichier
    elif query.data == 'send_file':
        lang = context.user_data.get('lang', 'fr')
        file_path = 'tech_refund.pdf'
        
        if os.path.exists(file_path):
            await query.message.reply_document(
                document=open(file_path, 'rb'), 
                caption=TEXTS[lang]['sent']
            )
        else:
            await query.message.reply_text(TEXTS[lang]['error'])

if __name__ == '__main__':
    # Récupération du Token (Variable Railway)
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    if not TOKEN:
        print("ERREUR : La variable TELEGRAM_TOKEN est vide sur Railway !")
    else:
        app = Application.builder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler))
        
        print("--- BOT TECH REFUND DÉMARRÉ ---")
        app.run_polling()