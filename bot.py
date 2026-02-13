import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

SUPPORT_1 = "https://t.me/dragonot005"
SUPPORT_2 = "https://t.me/BruluxOnFlux"
LINKTREE_URL = "https://linktr.ee/mooneytimz"

VIDEO_LINKS = {
    "android": "https://drive.google.com/file/d/1_3Nv4BH-qlIMuDqLVml0Dk-3Eros7ydf/view",
    "iphone": "https://drive.google.com/file/d/1CFNR9oGKIwSnJZBrqc8JpJX4_qNlKwNY/view",
    "pc": "https://drive.google.com/file/d/1TL__w19MwPqOeIlXqrgmRGMc9EVJ60HV/view",
}

REFUND_PDF_PC = "tech_refund.pdf"

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
        "btn_support1": "🛠 Support 1",
        "btn_support2": "🛠 Support 2",
        "btn_back": "⬅ Retour",
        "sent_refund": "✅ Voici ton PDF Refund.",
        "missing_file": "❌ Erreur : fichier introuvable.",
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
        "btn_support1": "🛠 Support 1",
        "btn_support2": "🛠 Support 2",
        "btn_back": "⬅ Back",
        "sent_refund": "✅ Here is your Refund PDF.",
        "missing_file": "❌ Error: file not found.",
    },
}

def get_lang(context):
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

    # PDF uniquement PC
    if platform == "pc":
        keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_refund_pdf"], callback_data="refund_pc")])

    # Vidéo
    video_url = VIDEO_LINKS.get(platform)
    if video_url:
        keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_video"], url=video_url)])

    # Linktree
    keyboard.append([InlineKeyboardButton("🔗 Linktree", url=LINKTREE_URL)])

    # 2 Supports
    keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_support1"], url=SUPPORT_1)])
    keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_support2"], url=SUPPORT_2)])

    # Retour
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

    if query.data == "refund_pc":
        if not os.path.exists(REFUND_PDF_PC):
            await query.message.reply_text(TEXTS[lang]["missing_file"])
            return
        with open(REFUND_PDF_PC, "rb") as f:
            await query.message.reply_document(document=f, caption=TEXTS[lang]["sent_refund"])

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
