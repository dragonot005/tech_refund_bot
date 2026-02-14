import os
import json
import sqlite3
import logging
import urllib.parse
from datetime import datetime
from zoneinfo import ZoneInfo
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

# ====== CONFIG ======
BOT_VERSION = "v1.6"
BOT_UPDATED = "14/02/2026"

SUPPORT_1_USERNAME = "dragonot005"
SUPPORT_2_USERNAME = "BruluxOnFlux"

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

# ✅ SQLite DB
DB_FILE = "tickets.db"

# Stats
STATS_FILE = "stats.json"

TEXTS = {
    "fr": {
        "choose_lang": "Choisissez votre langue :",
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

        "btn_home": "🏠 Menu principal",

        "support_ready": "🎟 Ticket: {ticket}\nClique ci-dessous pour contacter le support :",
        "missing_file": "❌ Erreur : fichier introuvable.",
        "open_support": "➡️ Ouvrir le support",

        "version_text": "🛠 *Version du bot*\n\n• Version: `{ver}`\n• Dernière MAJ: `{date}`",
        "stats_title": "📊 *Statistiques*",
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

        "btn_home": "🏠 Main menu",

        "support_ready": "🎟 Ticket: {ticket}\nClick below to contact support:",
        "missing_file": "❌ Error: file not found.",
        "open_support": "➡️ Open support",

        "version_text": "🛠 *Bot version*\n\n• Version: `{ver}`\n• Last update: `{date}`",
        "stats_title": "📊 *Statistics*",
    }
}

# ====== TIME ======
def paris_now():
    return datetime.now(ZoneInfo("Europe/Paris"))

def start_text_dynamic():
    now = paris_now().strftime("%H:%M")
    return f"👋 Bienvenue ! Il est {now}.\n\nChoisissez votre langue :"

# ====== SQLITE ======
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_next_ticket():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    now = paris_now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO tickets (created_at) VALUES (?)", (now,))
    conn.commit()

    ticket_id = cur.lastrowid
    conn.close()

    return f"{ticket_id:04d}"

def total_tickets_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM tickets")
    total = cur.fetchone()[0]
    conn.close()
    return int(total)

# ====== STATS ======
def _default_stats():
    return {
        "support_requests": 0,
        "tech_clicks": {"amazon": 0, "apple": 0, "refundall": 0},
        "platform_clicks": {"pc": 0, "iphone": 0, "android": 0},
    }

def load_stats():
    if not os.path.exists(STATS_FILE):
        return _default_stats()
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        base = _default_stats()
        base["support_requests"] = int(data.get("support_requests", 0))
        for k in base["tech_clicks"]:
            base["tech_clicks"][k] = int(data.get("tech_clicks", {}).get(k, 0))
        for k in base["platform_clicks"]:
            base["platform_clicks"][k] = int(data.get("platform_clicks", {}).get(k, 0))
        return base
    except Exception:
        return _default_stats()

def save_stats(stats):
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def inc_stat(kind, key=None):
    stats = load_stats()
    if kind == "support_requests":
        stats["support_requests"] += 1
    elif kind == "tech_clicks" and key in stats["tech_clicks"]:
        stats["tech_clicks"][key] += 1
    elif kind == "platform_clicks" and key in stats["platform_clicks"]:
        stats["platform_clicks"][key] += 1
    save_stats(stats)

def stats_text(lang):
    stats = load_stats()
    total = total_tickets_db()
    if lang == "fr":
        return (
            "📊 *Statistiques*\n\n"
            f"Tickets total: `{total}`\n"
            f"Demandes support: `{stats['support_requests']}`\n\n"
            "*Clics par Tech*\n"
            f"📦 Amazon: `{stats['tech_clicks']['amazon']}`\n"
            f"🍎 Apple: `{stats['tech_clicks']['apple']}`\n"
            f"🎁 Refund All: `{stats['tech_clicks']['refundall']}`\n\n"
            "*Clics par Plateforme*\n"
            f"💻 PC: `{stats['platform_clicks']['pc']}`\n"
            f"🍎 iPhone: `{stats['platform_clicks']['iphone']}`\n"
            f"🤖 Android: `{stats['platform_clicks']['android']}`"
        )
    else:
        return (
            "📊 *Statistics*\n\n"
            f"Total tickets: `{total}`\n"
            f"Support requests: `{stats['support_requests']}`\n\n"
            "*Clicks by Tech*\n"
            f"📦 Amazon: `{stats['tech_clicks']['amazon']}`\n"
            f"🍎 Apple: `{stats['tech_clicks']['apple']}`\n"
            f"🎁 Refund All: `{stats['tech_clicks']['refundall']}`\n\n"
            "*Clicks by Platform*\n"
            f"💻 PC: `{stats['platform_clicks']['pc']}`\n"
            f"🍎 iPhone: `{stats['platform_clicks']['iphone']}`\n"
            f"🤖 Android: `{stats['platform_clicks']['android']}`"
        )

# ====== HELPERS ======
def get_lang(context):
    return context.user_data.get("lang", "fr")

def get_user_identity(update):
    user = update.effective_user
    return f"@{user.username}" if user.username else f"User ID: {user.id}"

def build_support_message(lang, tech_label, platform_label, update, ticket):
    now = paris_now()
    date_now = now.strftime("%d/%m/%Y")
    time_now = now.strftime("%H:%M")
    identity = get_user_identity(update)
    flag = "🇫🇷" if lang == "fr" else "🇬🇧"

    if lang == "fr":
        return (
            f"🎟 Ticket: {ticket}\n"
            f"{flag} Demande Support\n\n"
            f"Date: {date_now}\n"
            f"Heure: {time_now}\n\n"
            f"Tech: {tech_label}\n"
            f"Plateforme: {platform_label}\n"
            f"Utilisateur: {identity}"
        )
    else:
        return (
            f"🎟 Ticket: {ticket}\n"
            f"{flag} Support Request\n\n"
            f"Date: {date_now}\n"
            f"Time: {time_now}\n\n"
            f"Tech: {tech_label}\n"
            f"Platform: {platform_label}\n"
            f"User: {identity}"
        )

def build_support_url(username, lang, tech_label, platform_label, update, ticket):
    msg = build_support_message(lang, tech_label, platform_label, update, ticket)
    return f"https://t.me/{username}?text={urllib.parse.quote(msg)}"

def get_or_create_active_ticket(context, tech_key, platform_key):
    active = context.user_data.get("active_ticket")
    if active and active.get("tech") == tech_key and active.get("platform") == platform_key:
        return active["ticket"]

    ticket = get_next_ticket()
    context.user_data["active_ticket"] = {"ticket": ticket, "tech": tech_key, "platform": platform_key}
    return ticket

# ====== KEYBOARDS ======
def lang_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Français 🇫🇷", callback_data="lang_fr")],
        [InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")],
        [InlineKeyboardButton("🛠 Version", callback_data="show_version")],
        [InlineKeyboardButton("📊 Stats", callback_data="show_stats")],
    ])

def tech_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["tech_amazon"], callback_data="tech_amazon")],
        [InlineKeyboardButton(TEXTS[lang]["tech_apple"], callback_data="tech_apple")],
        [InlineKeyboardButton(TEXTS[lang]["tech_refundall"], callback_data="tech_refundall")],
        [InlineKeyboardButton(TEXTS[lang]["btn_home"], callback_data="go_home")],
    ])

def platform_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["pc"], callback_data="platform_pc")],
        [InlineKeyboardButton(TEXTS[lang]["iphone"], callback_data="platform_iphone")],
        [InlineKeyboardButton(TEXTS[lang]["android"], callback_data="platform_android")],
        [InlineKeyboardButton(TEXTS[lang]["btn_home"], callback_data="go_home")],
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

    keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_home"], callback_data="go_home")])
    keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_back"], callback_data="step_platform")])
    return InlineKeyboardMarkup(keyboard)

def simple_back_home(lang):
    return InlineKeyboardMarkup([[InlineKeyboardButton(TEXTS[lang]["btn_home"], callback_data="go_home")]])

# ====== HANDLERS ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(start_text_dynamic(), reply_markup=lang_keyboard())

async def go_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.callback_query.edit_message_text(start_text_dynamic(), reply_markup=lang_keyboard())

async def show_version(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    text = TEXTS[lang]["version_text"].format(ver=BOT_VERSION, date=BOT_UPDATED)
    await update.callback_query.edit_message_text(text, reply_markup=simple_back_home(lang), parse_mode="Markdown")

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    text = stats_text(lang)
    await update.callback_query.edit_message_text(text, reply_markup=simple_back_home(lang), parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "go_home":
        await go_home(update, context)
        return

    if query.data == "show_version":
        await show_version(update, context)
        return

    if query.data == "show_stats":
        await show_stats(update, context)
        return

    lang = get_lang(context)

    if query.data.startswith("lang_"):
        context.user_data["lang"] = query.data.split("_")[1]
        lang = context.user_data["lang"]
        context.user_data.pop("active_ticket", None)
        await query.edit_message_text(TEXTS[lang]["choose_tech"], reply_markup=tech_keyboard(lang))
        return

    if query.data.startswith("tech_"):
        tech_key = query.data.split("_")[1]
        context.user_data["tech"] = tech_key
        context.user_data.pop("active_ticket", None)
        inc_stat("tech_clicks", tech_key)
        await query.edit_message_text(TEXTS[lang]["choose_platform"], reply_markup=platform_keyboard(lang))
        return

    if query.data.startswith("platform_"):
        platform = query.data.split("_")[1]
        context.user_data["platform"] = platform
        context.user_data.pop("active_ticket", None)
        inc_stat("platform_clicks", platform)
        await query.edit_message_text(TEXTS[lang]["choose_platform"], reply_markup=actions_keyboard(lang, platform))
        return

    if query.data == "step_platform":
        await query.edit_message_text(TEXTS[lang]["choose_platform"], reply_markup=platform_keyboard(lang))
        return

    if query.data == "send_pdf_pc":
        tech = context.user_data.get("tech", "refundall")
        file_path = TECH_PDF_PC.get(tech)
        if not file_path or not os.path.exists(file_path):
            await query.message.reply_text(TEXTS[lang]["missing_file"])
            return
        with open(file_path, "rb") as f:
            await query.message.reply_document(f)
        return

    if query.data in ("support_dragonot", "support_brulux"):
        tech_key = context.user_data.get("tech", "refundall")
        platform_key = context.user_data.get("platform", "pc")

        tech_label = TEXTS[lang].get(f"tech_{tech_key}", tech_key)
        platform_label = TEXTS[lang].get(platform_key, platform_key)

        ticket = get_or_create_active_ticket(context, tech_key, platform_key)
        inc_stat("support_requests")

        if query.data == "support_dragonot":
            url = build_support_url(SUPPORT_1_USERNAME, lang, tech_label, platform_label, update, ticket)
        else:
            url = build_support_url(SUPPORT_2_USERNAME, lang, tech_label, platform_label, update, ticket)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(TEXTS[lang]["open_support"], url=url)],
            [InlineKeyboardButton(TEXTS[lang]["btn_home"], callback_data="go_home")],
        ])

        await query.edit_message_text(TEXTS[lang]["support_ready"].format(ticket=ticket), reply_markup=keyboard)
        return

# ====== MAIN ======
if __name__ == "__main__":
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        print("ERREUR : TELEGRAM_TOKEN manquant !")
    else:
        init_db()
        app = Application.builder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.run_polling()
