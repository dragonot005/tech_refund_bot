import os
import logging
import urllib.parse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

SUPPORT_1_USERNAME = "dragonot005"
SUPPORT_2_USERNAME = "BruluxOnFlux"
LINKTREE_URL = "https://linktr.ee/mooneytimz"

VIDEO_LINKS = {
    "android": "https://drive.google.com/file/d/1_3Nv4BH-qlIMuDqLVml0Dk-3Eros7ydf/view",
    "iphone": "https://drive.google.com/file/d/1CFNR9oGKIwSnJZBrqc8JpJX4_qNlKwNY/view",
    "pc": "https://drive.google.com/file/d/1TL__w19MwPqOeIlXqrgmRGMc9EVJ60HV/view",
}

TECH_PDF_PC = {
    "amazon": "tech_amazon.pdf",
    "apple": "tech_apple.pdf",
    "refundall": "tech_refund.pdf",
}

TEXTS = {
    "fr": {
        "choose_lang": "Choisissez votre langue / Please choose your language :",
        "choose_tech": "✅ Choisis ton service :",
        "tech_amazon": "📦 Tech Amazon",
        "tech_apple": "🍎 Tech Apple",
        "tech_refundall": "🎁 Tech Refund All (PayPal, Rbnb, PCS…)",
        "choose_platform": "📱 Choisis ta plateforme :",
        "pc": "💻 PC",
        "iphone": "🍎 iPhone",
        "android": "🤖 Android",
        "platform_title": "📦 Plateforme : *{platform}*\nChoisis une action :",
        "btn_pdf": "📄 PDF",
        "btn_video": "🎥 Vidéo",
        "btn_support1": "🛠 Support Dragonot",
        "btn_support2": "🛠 Support Brulux",
        "btn_back": "⬅ Retour",
        "btn_back_tech": "⬅ Retour (Tech)",
        "sent_pdf": "✅ Voici ton fichier.",
        "missing_file": "❌ Erreur : fichier introuvable.",
    },
    "en": {
        "choose_lang": "Please choose your language:",
        "choose_tech": "✅ Choose your service:",
        "tech_amazon": "📦 Amazon Tech",
        "tech_apple": "🍎 Apple Tech",
        "tech_refundall": "🎁 Tech Refund All (PayPal, Rbnb, PCS…)",
        "choose_platform": "📱 Choose your platform:",
        "pc": "💻 PC",
        "iphone": "🍎 iPhone",
        "android": "🤖 Android",
        "platform_title": "📦 Platform: *{platform}*\nChoose an action:",
        "btn_pdf": "📄 PDF",
        "btn_video": "🎥 Video",
        "btn_support1": "🛠 Dragonot Support",
        "btn_support2": "🛠 Brulux Support",
        "btn_back": "⬅ Back",
        "btn_back_tech": "⬅ Back (Tech)",
        "sent_pdf": "✅ Here is your file.",
        "missing_file": "❌ Error: file not found.",
    },
}


def get_lang(context):
    return context.user_data.get("lang", "fr")


def get_user_identity(update: Update):
    user = update.effective_user
    if user.username:
        return f"@{user.username}"
    else:
        return f"User ID: {user.id}"


def support_link(username: str, lang: str, tech: str, platform: str, user_identity: str):
    flag = "🇫🇷" if lang == "fr" else "🇬🇧"

    if lang == "fr":
        message = (
            f"{flag} Support\n"
            f"Tech: {TEXTS[lang][f'tech_{tech}']}\n"
            f"Plateforme: {TEXTS[lang][platform]}\n"
            f"Utilisateur: {user_identity}"
        )
    else:
        message = (
            f"{flag} Support\n"
            f"Tech: {TEXTS[lang][f'tech_{tech}']}\n"
            f"Platform: {TEXTS[lang][platform]}\n"
            f"User: {user_identity}"
        )

    return f"https://t.me/{username}?text={urllib.parse.quote(message)}"


def lang_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Français 🇫🇷", callback_data="lang_fr")],
        [InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")],
    ])


def tech_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["tech_amazon"], callback_data="tech_amazon")],
        [InlineKeyboardButton(TEXTS[lang]["tech_apple"], callback_data="tech_apple")],
        [InlineKeyboardButton(TEXTS[lang]["tech_refundall"], callback_data="tech_refundall")],
    ])


def platform_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["pc"], callback_data="platform_pc")],
        [InlineKeyboardButton(TEXTS[lang]["iphone"], callback_data="platform_iphone")],
        [InlineKeyboardButton(TEXTS[lang]["android"], callback_data="platform_android")],
        [InlineKeyboardButton(TEXTS[lang]["btn_back_tech"], callback_data="back_to_tech")],
    ])


def platform_actions_keyboard(lang, platform, tech, update):
    keyboard = []

    if platform == "pc":
        keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_pdf"], callback_data="send_pdf_pc")])

    video_url = VIDEO_LINKS.get(platform)
    if video_url:
        keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_video"], url=video_url)])

    keyboard.append([InlineKeyboardButton("🔗 Linktree", url=LINKTREE_URL)])

    user_identity = get_user_identity(update)

    keyboard.append([
        InlineKeyboardButton(
            TEXTS[lang]["btn_support1"],
            url=support_link(SUPPORT_1_USERNAME, lang, tech, platform, user_identity)
        ),
        InlineKeyboardButton(
            TEXTS[lang]["btn_support2"],
            url=support_link(SUPPORT_2_USERNAME, lang, tech, platform, user_identity)
        ),
    ])

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
        await query.edit_message_text(TEXTS[lang]["choose_tech"], reply_markup=tech_keyboard(lang))
        return

    lang = get_lang(context)

    if query.data == "back_to_tech":
        await query.edit_message_text(TEXTS[lang]["choose_tech"], reply_markup=tech_keyboard(lang))
        return

    if query.data.startswith("tech_"):
        tech = query.data.split("_")[1]
        context.user_data["tech"] = tech
        await query.edit_message_text(TEXTS[lang]["choose_platform"], reply_markup=platform_keyboard(lang))
        return

    if query.data == "step_platform":
        await query.edit_message_text(TEXTS[lang]["choose_platform"], reply_markup=platform_keyboard(lang))
        return

    if query.data.startswith("platform_"):
        platform = query.data.split("_")[1]
        context.user_data["platform"] = platform
        tech = context.user_data.get("tech", "refundall")

        await query.edit_message_text(
            TEXTS[lang]["platform_title"].format(platform=TEXTS[lang][platform]),
            reply_markup=platform_actions_keyboard(lang, platform, tech, update),
            parse_mode="Markdown",
        )
        return

    if query.data == "send_pdf_pc":
        tech = context.user_data.get("tech", "refundall")
        file_path = TECH_PDF_PC.get(tech)

        if not file_path or not os.path.exists(file_path):
            await query.message.reply_text(TEXTS[lang]["missing_file"])
            return

        with open(file_path, "rb") as f:
            await query.message.reply_document(document=f, caption=TEXTS[lang]["sent_pdf"])


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
