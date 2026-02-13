import os
import logging
import urllib.parse
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

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

TICKET_FILE = "ticket_counter.txt"


def get_next_ticket():
    if not os.path.exists(TICKET_FILE):
        with open(TICKET_FILE, "w") as f:
            f.write("0")

    with open(TICKET_FILE, "r") as f:
        number = int(f.read().strip())

    number += 1

    with open(TICKET_FILE, "w") as f:
        f.write(str(number))

    return f"{number:04d}"  # format 0001


def get_user_identity(update: Update):
    user = update.effective_user
    return f"@{user.username}" if user.username else f"User ID: {user.id}"


def support_link(username, lang, tech, platform, update):
    ticket = get_next_ticket()
    now = datetime.now().strftime("%H:%M")
    user_identity = get_user_identity(update)
    flag = "🇫🇷" if lang == "fr" else "🇬🇧"

    if lang == "fr":
        message = (
            f"🎟 Ticket: {ticket}\n"
            f"{flag} Demande Support\n\n"
            f"Tech: {tech}\n"
            f"Plateforme: {platform}\n"
            f"Utilisateur: {user_identity}\n"
            f"Heure: {now}"
        )
    else:
        message = (
            f"🎟 Ticket: {ticket}\n"
            f"{flag} Support Request\n\n"
            f"Tech: {tech}\n"
            f"Platform: {platform}\n"
            f"User: {user_identity}\n"
            f"Time: {now}"
        )

    return f"https://t.me/{username}?text={urllib.parse.quote(message)}"
