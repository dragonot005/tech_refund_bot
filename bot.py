import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Supports + Linktree
SUPPORT_1 = "https://t.me/dragonot005"
SUPPORT_2 = "https://t.me/BruluxOnFlux"
LINKTREE_URL = "https://linktr.ee/mooneytimz"

# 🎥 Vidéos (par plateforme)
VIDEO_LINKS = {
    "android": "https://drive.google.com/file/d/1_3Nv4BH-qlIMuDqLVml0Dk-3Eros7ydf/view",
    "iphone": "https://drive.google.com/file/d/1CFNR9oGKIwSnJZBrqc8JpJX4_qNlKwNY/view",
    "pc": "https://drive.google.com/file/d/1TL__w19MwPqOeIlXqrgmRGMc9EVJ60HV/view",
}

# 📄 PDFs PC (1 par service)
# Mets ces fichiers dans ton dossier projet + sur GitHub
TECH_PDF_PC = {
    "amazon": "tech_amazon.pdf",
    "apple": "tech_apple.pdf",
    "refundall": "tech_refund.pdf",
}

TEXTS = {
    "fr": {
        "choose_lang": "Please choose your language / Choisissez votre langue :",
        "choose_tech": "✅ Choisis ton service :",
        "tech_amazon": "🟧 Tech Amazon",
        "tech_apple": "🍎 Tech Apple",
        "tech_refundall": "✅ Refund All",

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

        "sent_pdf": "✅ Voici ton fichier.",
        "missing_file": "❌ Erreur : fichier introuvable.",
    },
    "en": {
        "choose_lang": "Please choose your language / Choisissez votre langue :",
        "choose_tech": "✅ Choose your service:",
        "tech_amazon": "🟧 Amazon Tech",
        "tech_apple": "🍎 Apple Tech",
        "tech_refundall": "✅ Refund All",

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

        "sent_pdf": "✅ Here is your file.",
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


def tech_keyboard(lang: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["tech_amazon"], callback_data="tech_amazon")],
        [InlineKeyboardButton(TEXTS[lang]["tech_apple"], callback_data="tech_apple")],
        [InlineKeyboardButton(TEXTS[lang]["tech_refundall"], callback_data="tech_refundall")],
    ])


def platform_keyboard(lang: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["pc"], callback_data="platform_pc")],
        [InlineKeyboardButton(TEXTS[lang]["iphone"], callback_data="platform_iphone")],
        [InlineKeyboardButton(TEXTS[lang]["android"], callback_data="platform_android")],
    ])


def platform_actions_keyboard(lang: str, platform: str, tech: str):
    keyboard = []

    # PDF uniquement si PC (et seulement si on a un PDF pour ce service)
    if platform == "pc":
        keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_pdf"], callback_data="send_pdf_pc")])

    # Vidéo
    video_url = VIDEO_LINKS.get(platform)
    if video_url:
        keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_video"], url=video_url)])

    # Linktree
    keyboard.append([InlineKeyboardButton("🔗 Linktree", url=LINKTREE_URL)])

    # Supports sur la même ligne
    keyboard.append([
        InlineKeyboardButton(TEXTS[lang]["btn_support1"], url=SUPPORT_1),
        InlineKeyboardButton(TEXTS[lang]["btn_support2"], url=SUPPORT_2),
    ])

    # Retour (retour plateformes)
    keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_back"], callback_data="step_platform")])

    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(TEXTS["fr"]["choose_lang"], reply_markup=lang_keyboard())


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # 1) Choix langue -> choix service
    if query.data.startswith("lang_"):
        lang = query.data.split("_", 1)[1]
        context.user_data["lang"] = lang
        await query.edit_message_text(
            TEXTS[lang]["choose_tech"],
            reply_markup=tech_keyboard(lang),
        )
        return

    lang = get_lang(context)

    # 2) Choix service -> plateformes
    if query.data.startswith("tech_"):
        tech = query.data.split("_", 1)[1]  # amazon / apple / refundall
        context.user_data["tech"] = tech
        await query.edit_message_text(
            TEXTS[lang]["choose_platform"],
            reply_markup=platform_keyboard(lang),
        )
        return

    # Retour plateformes
    if query.data == "step_platform":
        await query.edit_message_text(
            TEXTS[lang]["choose_platform"],
            reply_markup=platform_keyboard(lang),
        )
        return

    # 3) Choix plateforme -> actions
    if query.data.startswith("platform_"):
        platform = query.data.split("_", 1)[1]  # pc/iphone/android
        context.user_data["platform"] = platform

        tech = context.user_data.get("tech", "refundall")
        label = TEXTS[lang].get(platform, platform)

        await query.edit_message_text(
            TEXTS[lang]["platform_title"].format(platform=label),
            reply_markup=platform_actions_keyboard(lang, platform, tech),
            parse_mode="Markdown",
        )
        return

    # 4) Envoi PDF (PC) selon le service choisi
    if query.data == "send_pdf_pc":
        tech = context.user_data.get("tech", "refundall")
        platform = context.user_data.get("platform", "pc")

        if platform != "pc":
            # sécurité : normalement impossible
            return

        file_path = TECH_PDF_PC.get(tech)

        if not file_path or not os.path.exists(file_path):
            await query.message.reply_text(TEXTS[lang]["missing_file"])
            return

        try:
            with open(file_path, "rb") as f:
                await query.message.reply_document(document=f, caption=TEXTS[lang]["sent_pdf"])
        except Exception as e:
            logging.exception("Erreur envoi PDF: %s", e)
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
