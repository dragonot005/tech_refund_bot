import os
import logging
import urllib.parse
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Supports + Linktree
SUPPORT_1_USERNAME = "dragonot005"
SUPPORT_2_USERNAME = "BruluxOnFlux"
LINKTREE_URL = "https://linktr.ee/mooneytimz"

# 🎥 Vidéos (par plateforme)
VIDEO_LINKS = {
    "android": "https://drive.google.com/file/d/1_3Nv4BH-qlIMuDqLVml0Dk-3Eros7ydf/view",
    "iphone": "https://drive.google.com/file/d/1CFNR9oGKIwSnJZBrqc8JpJX4_qNlKwNY/view",
    "pc": "https://drive.google.com/file/d/1TL__w19MwPqOeIlXqrgmRGMc9EVJ60HV/view",
}

# 📄 PDFs PC (1 par service) — fichiers à mettre dans le dossier projet
TECH_PDF_PC = {
    "amazon": "tech_amazon.pdf",
    "apple": "tech_apple.pdf",
    "refundall": "tech_refund.pdf",
}

# 🎟 Ticket counter (fichier texte)
TICKET_FILE = "ticket_counter.txt"

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


def get_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("lang", "fr")


def lang_flag(lang: str) -> str:
    return "🇫🇷" if lang == "fr" else "🇬🇧"


def get_user_identity(update: Update) -> str:
    user = update.effective_user
    return f"@{user.username}" if user.username else f"User ID: {user.id}"


def get_next_ticket() -> str:
    # crée le fichier si absent
    if not os.path.exists(TICKET_FILE):
        with open(TICKET_FILE, "w", encoding="utf-8") as f:
            f.write("0")

    # lit
    try:
        with open(TICKET_FILE, "r", encoding="utf-8") as f:
            raw = f.read().strip()
            number = int(raw) if raw else 0
    except Exception:
        number = 0

    # incrémente + écrit
    number += 1
    try:
        with open(TICKET_FILE, "w", encoding="utf-8") as f:
            f.write(str(number))
    except Exception:
        # si écriture impossible, on renvoie quand même un ticket basé sur la valeur calculée
        pass

    return f"{number:04d}"  # 0001


def support_prefill(lang: str, tech_label: str, platform_label: str, user_identity: str) -> str:
    ticket = get_next_ticket()
    now = datetime.now().strftime("%H:%M")
    flag = lang_flag(lang)

    if lang == "fr":
        return (
            f"🎟 Ticket: {ticket}\n"
            f"{flag} Demande Support\n\n"
            f"Tech: {tech_label}\n"
            f"Plateforme: {platform_label}\n"
            f"Utilisateur: {user_identity}\n"
            f"Heure: {now}"
        )
    else:
        return (
            f"🎟 Ticket: {ticket}\n"
            f"{flag} Support Request\n\n"
            f"Tech: {tech_label}\n"
            f"Platform: {platform_label}\n"
            f"User: {user_identity}\n"
            f"Time: {now}"
        )


def support_link(username: str, lang: str, tech_label: str, platform_label: str, update: Update) -> str:
    msg = support_prefill(lang, tech_label, platform_label, get_user_identity(update))
    return f"https://t.me/{username}?text={urllib.parse.quote(msg)}"


def lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Français 🇫🇷", callback_data="lang_fr")],
        [InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")],
    ])


def tech_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["tech_amazon"], callback_data="tech_amazon")],
        [InlineKeyboardButton(TEXTS[lang]["tech_apple"], callback_data="tech_apple")],
        [InlineKeyboardButton(TEXTS[lang]["tech_refundall"], callback_data="tech_refundall")],
    ])


def platform_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["pc"], callback_data="platform_pc")],
        [InlineKeyboardButton(TEXTS[lang]["iphone"], callback_data="platform_iphone")],
        [InlineKeyboardButton(TEXTS[lang]["android"], callback_data="platform_android")],
        [InlineKeyboardButton(TEXTS[lang]["btn_back_tech"], callback_data="back_to_tech")],
    ])


def platform_actions_keyboard(lang: str, platform: str, tech: str, update: Update) -> InlineKeyboardMarkup:
    keyboard = []

    # PDF uniquement sur PC
    if platform == "pc":
        keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_pdf"], callback_data="send_pdf_pc")])

    # Vidéo
    video_url = VIDEO_LINKS.get(platform)
    if video_url:
        keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_video"], url=video_url)])

    # Linktree
    keyboard.append([InlineKeyboardButton("🔗 Linktree", url=LINKTREE_URL)])

    # Libellés tech + plateforme (avec emojis déjà dans TEXTS)
    tech_label = TEXTS[lang].get(f"tech_{tech}", tech)
    platform_label = TEXTS[lang].get(platform, platform)

    # Supports sur la même ligne avec message pré-rempli (ticket + heure + user)
    keyboard.append([
        InlineKeyboardButton(
            TEXTS[lang]["btn_support1"],
            url=support_link(SUPPORT_1_USERNAME, lang, tech_label, platform_label, update)
        ),
        InlineKeyboardButton(
            TEXTS[lang]["btn_support2"],
            url=support_link(SUPPORT_2_USERNAME, lang, tech_label, platform_label, update)
        ),
    ])

    # Retour vers plateformes
    keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_back"], callback_data="step_platform")])

    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(TEXTS["fr"]["choose_lang"], reply_markup=lang_keyboard())


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Choix langue -> Choix tech
    if query.data.startswith("lang_"):
        lang = query.data.split("_", 1)[1]
        context.user_data["lang"] = lang
        await query.edit_message_text(TEXTS[lang]["choose_tech"], reply_markup=tech_keyboard(lang))
        return

    lang = get_lang(context)

    # Retour vers choix Tech
    if query.data == "back_to_tech":
        await query.edit_message_text(TEXTS[lang]["choose_tech"], reply_markup=tech_keyboard(lang))
        return

    # Choix tech -> Choix plateforme
    if query.data.startswith("tech_"):
        tech = query.data.split("_", 1)[1]  # amazon / apple / refundall
        context.user_data["tech"] = tech
        await query.edit_message_text(TEXTS[lang]["choose_platform"], reply_markup=platform_keyboard(lang))
        return

    # Retour plateformes
    if query.data == "step_platform":
        await query.edit_message_text(TEXTS[lang]["choose_platform"], reply_markup=platform_keyboard(lang))
        return

    # Choix plateforme -> Actions
    if query.data.startswith("platform_"):
        platform = query.data.split("_", 1)[1]  # pc/iphone/android
        context.user_data["platform"] = platform

        tech = context.user_data.get("tech", "refundall")
        label = TEXTS[lang].get(platform, platform)

        await query.edit_message_text(
            TEXTS[lang]["platform_title"].format(platform=label),
            reply_markup=platform_actions_keyboard(lang, platform, tech, update),
            parse_mode="Markdown",
        )
        return

    # Envoi PDF selon tech choisie (PC)
    if query.data == "send_pdf_pc":
        tech = context.user_data.get("tech", "refundall")
        file_path = TECH_PDF_PC.get(tech)

        if not file_path or not os.path.exists(file_path):
            await query.message.reply_text(TEXTS[lang]["missing_file"])
            return

        with open(file_path, "rb") as f:
            await query.message.reply_document(document=f, caption=TEXTS[lang]["sent_pdf"])
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
