import os
import logging
import urllib.parse
from datetime import datetime
from zoneinfo import ZoneInfo
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

SUPPORT_1_USERNAME = "dragonot005"
SUPPORT_2_USERNAME = "BruluxOnFlux"
LINKTREE_URL = "https://linktr.ee/mooneytimz"

SCRIPT_LINK_DOCS = "https://docs.google.com/document/d/1Wwuxkzn8eRPadaykz419WK1l9yMPo8TJ7GKQwhE-ViE/edit?tab=t.0"
SCRIPT_LINK_IPHONE = "https://www.dropbox.com/scl/fi/1l2cmo11ct8z9xjud09ju/script.js?rlkey=1irwd80aexss2zkkge4j6jwmq&st=4kc6mk21&dl=1"

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

TICKET_FILE = "ticket_counter.txt"

TEXTS = {
    "fr": {
        "choose_lang": "Choisissez votre langue / Please choose your language :",
        "choose_tech": "Choisis ton service :",
        "tech_amazon": "📦 Tech Amazon",
        "tech_apple": "🍎 Tech Apple",
        "tech_refundall": "🎁 Tech Refund All (PayPal, Rbnb, PCS…)",
        "choose_platform": "Choisis ta plateforme :",
        "pc": "💻 PC",
        "iphone": "🍎 iPhone",
        "android": "🤖 Android",
        "btn_pdf": "📄 PDF",
        "btn_video": "🎥 Vidéo",
        "btn_script": "📜 Lien du script",
        "btn_support1": "🛠 Support Dragonot",
        "btn_support2": "🛠 Support Brulux",
        "btn_back": "⬅ Retour",
        "support_ready": "🎟 Ticket: {ticket}\nClique ci-dessous pour contacter le support :",
        "missing_file": "❌ Erreur : fichier introuvable.",
        "open_support": "➡️ Ouvrir le support",
    },
    "en": {
        "choose_lang": "Please choose your language:",
        "choose_tech": "Choose your service:",
        "tech_amazon": "📦 Amazon Tech",
        "tech_apple": "🍎 Apple Tech",
        "tech_refundall": "🎁 Tech Refund All (PayPal, Rbnb, PCS…)",
        "choose_platform": "Choose your platform:",
        "pc": "💻 PC",
        "iphone": "🍎 iPhone",
        "android": "🤖 Android",
        "btn_pdf": "📄 PDF",
        "btn_video": "🎥 Video",
        "btn_script": "📜 Script Link",
        "btn_support1": "🛠 Dragonot Support",
        "btn_support2": "🛠 Brulux Support",
        "btn_back": "⬅ Back",
        "support_ready": "🎟 Ticket: {ticket}\nClick below to contact support:",
        "missing_file": "❌ Error: file not found.",
        "open_support": "➡️ Open support",
    }
}

def get_lang(context):
    return context.user_data.get("lang", "fr")

def get_next_ticket():
    if not os.path.exists(TICKET_FILE):
        with open(TICKET_FILE, "w") as f:
            f.write("0")

    with open(TICKET_FILE, "r") as f:
        number = int(f.read().strip())

    number += 1

    with open(TICKET_FILE, "w") as f:
        f.write(str(number))

    return f"{number:04d}"

def get_user_identity(update):
    user = update.effective_user
    return f"@{user.username}" if user.username else f"User ID: {user.id}"

def build_support_message(lang, tech_label, platform_label, update, ticket):
    now = datetime.now(ZoneInfo("Europe/Paris"))
    date_now = now.strftime("%d/%m/%Y")
    time_now = now.strftime("%H:%M")
    identity = get_user_identity(update)

    if lang == "fr":
        return (
            f"🎟 Ticket: {ticket}\n"
            f"Date: {date_now}\n"
            f"Heure: {time_now}\n\n"
            f"Tech: {tech_label}\n"
            f"Plateforme: {platform_label}\n"
            f"Utilisateur: {identity}"
        )
    else:
        return (
            f"🎟 Ticket: {ticket}\n"
            f"Date: {date_now}\n"
            f"Time: {time_now}\n\n"
            f"Tech: {tech_label}\n"
            f"Platform: {platform_label}\n"
            f"User: {identity}"
        )

def build_support_url(username, lang, tech_label, platform_label, update, ticket):
    msg = build_support_message(lang, tech_label, platform_label, update, ticket)
    return f"https://t.me/{username}?text={urllib.parse.quote(msg)}"

def lang_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Français 🇫🇷", callback_data="lang_fr")],
        [InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")]
    ])

def tech_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["tech_amazon"], callback_data="tech_amazon")],
        [InlineKeyboardButton(TEXTS[lang]["tech_apple"], callback_data="tech_apple")],
        [InlineKeyboardButton(TEXTS[lang]["tech_refundall"], callback_data="tech_refundall")]
    ])

def platform_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["pc"], callback_data="platform_pc")],
        [InlineKeyboardButton(TEXTS[lang]["iphone"], callback_data="platform_iphone")],
        [InlineKeyboardButton(TEXTS[lang]["android"], callback_data="platform_android")],
        [InlineKeyboardButton(TEXTS[lang]["btn_back"], callback_data="back_to_tech")]
    ])

def actions_keyboard(lang, platform):
    keyboard = []

    if platform == "pc":
        keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_pdf"], callback_data="send_pdf_pc")])

    if platform in ["pc", "android"]:
        keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_script"], url=SCRIPT_LINK_DOCS)])
    elif platform == "iphone":
        keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_script"], url=SCRIPT_LINK_IPHONE)])

    keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_video"], url=VIDEO_LINKS[platform])])

    keyboard.append([
        InlineKeyboardButton(TEXTS[lang]["btn_support1"], callback_data="support_dragonot"),
        InlineKeyboardButton(TEXTS[lang]["btn_support2"], callback_data="support_brulux")
    ])

    keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_back"], callback_data="step_platform")])

    return InlineKeyboardMarkup(keyboard)

def get_or_create_active_ticket(context, tech_key, platform_key):
    active = context.user_data.get("active_ticket")
    if active and active.get("tech") == tech_key and active.get("platform") == platform_key:
        return active["ticket"]

    ticket = get_next_ticket()
    context.user_data["active_ticket"] = {
        "ticket": ticket,
        "tech": tech_key,
        "platform": platform_key,
    }
    return ticket

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(TEXTS["fr"]["choose_lang"], reply_markup=lang_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)

    if query.data.startswith("lang_"):
        context.user_data["lang"] = query.data.split("_")[1]
        context.user_data.pop("active_ticket", None)
        await query.edit_message_text(TEXTS[lang]["choose_tech"], reply_markup=tech_keyboard(lang))
        return

    if query.data.startswith("tech_"):
        context.user_data["tech"] = query.data.split("_")[1]
        context.user_data.pop("active_ticket", None)
        await query.edit_message_text(TEXTS[lang]["choose_platform"], reply_markup=platform_keyboard(lang))
        return

    if query.data.startswith("platform_"):
        platform = query.data.split("_")[1]
        context.user_data["platform"] = platform
        context.user_data.pop("active_ticket", None)
        await query.edit_message_text(
            TEXTS[lang]["choose_platform"],
            reply_markup=actions_keyboard(lang, platform)
        )
        return

    if query.data == "send_pdf_pc":
        tech = context.user_data.get("tech", "refundall")
        file_path = TECH_PDF_PC.get(tech)
        if file_path and os.path.exists(file_path):
            with open(file_path, "rb") as f:
                await query.message.reply_document(f)
        return

    if query.data in ("support_dragonot", "support_brulux"):
        tech_key = context.user_data.get("tech", "refundall")
        platform_key = context.user_data.get("platform", "pc")

        tech_label = TEXTS[lang].get(f"tech_{tech_key}", tech_key)
        platform_label = TEXTS[lang].get(platform_key, platform_key)

        ticket = get_or_create_active_ticket(context, tech_key, platform_key)

        if query.data == "support_dragonot":
            url = build_support_url(SUPPORT_1_USERNAME, lang, tech_label, platform_label, update, ticket)
        else:
            url = build_support_url(SUPPORT_2_USERNAME, lang, tech_label, platform_label, update, ticket)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(TEXTS[lang]["open_support"], url=url)]
        ])

        await query.edit_message_text(
            TEXTS[lang]["support_ready"].format(ticket=ticket),
            reply_markup=keyboard
        )
        return

if __name__ == "__main__":
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
