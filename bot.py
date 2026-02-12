import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

SUPPORT_URL = "https://t.me/dragonot005"

# 🎥 Liens vidéos
VIDEO_LINKS = {
    "android": "https://drive.google.com/file/d/1_3Nv4BH-qlIMuDqLVml0Dk-3Eros7ydf/view",
    "iphone": "https://drive.google.com/file/d/1CFNR9oGKIwSnJZBrqc8JpJX4_qNlKwNY/view",
    "pc": "https://drive.google.com/file/d/1TL__w19MwPqOeIlXqrgmRGMc9EVJ60HV/view",
}

# 📄 PDF uniquement pour PC
REFUND_PDF_PC = "refund_pc.pdf"

TEXTS = {
    "fr": {
        "choose_lang": "Please choose your language / Choisissez votre langue :",
        "intro": (
            "✅ Bienvenue chez *Tech Refund* !\n\n"
            "Choisis ta plateforme pour accéder aux vidéos et au support.\n\n"
            "Clique *Continuer* 👇"
        ),
        "continue": "➡️ Continuer",
        "choose_platform": "📱 Choisis ta plateforme :",
        "pc": "💻 PC",
        "iphone": "🍎 iPhone",
        "android": "🤖 Android",
        "platform_title": "📦 Plateforme : *{platform}*\nChoisis une action :",
        "btn_refund_pdf": "📄 PDF Refund",
        "btn_video": "🎥 Vidéo",
        "btn_support": "🛠 Support",
        "btn_back": "⬅ Retour",
        "sent_refund": "✅ Voici ton PDF Refund.",
        "missing_file": "❌ Erreur : le fichier est introuvable.",
    },
    "en": {
        "choose_lang": "Please choose your language / Choisissez votre langue :",
        "intro": (
            "✅ Welcome to *Tech Refund*!\n\n"
            "Choose your platform to access videos and support.\n\n"
            "Tap *Continue* 👇"
        ),
        "continue": "➡️ Continue",
        "choose_platform": "📱 Choose your platform:",
        "pc": "💻 PC",
        "iphone": "🍎 iPhone",
        "android": "🤖 Android",
        "platform_title": "📦 Platform: *{platform}*\nChoose an action:",
        "btn_refund_pdf": "📄 Refund PDF",
        "btn_video": "🎥 Video",
        "btn_support": "🛠 Support",
        "btn_back": "⬅ Back",
        "sent_refund": "✅ Here is your Refund PDF.",
        "missing_file": "❌ Error: file not found.",
    },
}

def get_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("lang", "fr")

def lang_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Français 🇫🇷", callback_data="lang_fr")],
        [InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")],
    ])

def continue_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["continue"], callback_data="step_platform")]
    ])

def platform_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["pc"], callback_data="platform_pc")],
        [InlineKeyboardButton(TEXTS[lang]["iphone"], callback_data="platform_iphone")],
        [InlineKeyboardButton(TEXTS[lang]["android"], callback_data="platform_android")],
    ])

def platform_actions_keyboard(lang, platform):
    keyboard = []

    # 🎥 Vidéo (pour toutes plateformes)
    video_url = VIDEO_LINKS.get(platform)
    if video_url:
        keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_video"], url=video_url)])

    # 📄 PDF uniquement pour PC
    if platform == "pc":
        keyboard.insert(0, [InlineKeyboardButton(TEXTS[lang]["btn_refund_pdf"], callback_data="refund_pc")])

    keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_support"], url=SUPPORT_URL)])
    keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_back"], callback_data="step_platform")])

    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(TEXTS["fr"]["choose_lang"], reply_markup=lang_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("lang_"):
        lang = query.data.split("_")[1]
        context.user_data["lang"] = lang
        await query.edit_message_text(TEXTS[lang]["intro"], reply_markup=continue_keyboard(lang), parse_mode="Markdown")
        return

    lang = get_lang(context)

    if query.data == "step_platform":
        await query.edit_message_text(TEXTS[lang]["choose_platform"], reply_markup=platform_keyboard(lang))
        return

    if query.data.startswith("platform_"):
        platform = query.data.split("_")[1]
        label = TEXTS[lang].get(platform, platform)
        await query.edit_message_text(
            TEXTS[lang]["platform_title"].format(platform=label),
            reply_markup=platform_actions_keyboard(lang, platform),
            parse_mode="Markdown",
        )
        return

    # Envoi PDF PC uniquement
    if query.data == "refund_pc":
        if not os.path.exists(REFUND_PDF_PC):
            await query.message.reply_text(TEXTS[lang]["missing_file"])
            return
        try:
            with open(REFUND_PDF_PC, "rb") as f:
                await query.message.reply_document(document=f, caption=TEXTS[lang]["sent_refund"])
        except Exception:
            await query.message.reply_text(TEXTS[lang]["missing_file"])
        return

if __name__ == "__main__":
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        print("ERREUR : TELEGRAM_TOKEN manquant !")
    else:
        app = Application.builder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler))
        print("--- BOT TECH REFUND DÉMARRÉ ---")
        app.run_polling()
