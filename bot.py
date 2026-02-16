import os
import json
import sqlite3
import logging
import urllib.parse
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional
import asyncio
import aiohttp

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

# ====== CONFIG ======
BOT_VERSION = "v2.9"
BOT_UPDATED = "16/02/2026"

SUPPORT_1_USERNAME = "Drago_JS"
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

# ====== CONFIG CRYPTO ======
BTC_ADDRESS = "bc1qruhf3catg68eaq2trnw5ykfgr8hy3mlf8rn068"
BLOCKCYPHER_TOKEN = "8fd629ba15ae4f09af62be248885c179"
CHECK_INTERVAL = 300
MONITOR_USER_ID = 7067411241

DB_FILE = "tickets.db"
STATS_FILE = "stats.json"

TEXTS = {
    "fr": {
        "choose_tech": "Choisis ton service :",
        "tech_amazon": "📦 Tech Amazon",
        "tech_apple": "🍎 Tech Apple",
        "tech_refundall": "🎁 Tech Refund All (PayPal, Rbnb, PCS…)",

        "choose_platform": "Choisis ta plateforme :",
        "pc": "💻 PC",
        "iphone": "🍎 iPhone",
        "android": "🤖 Android",

        "btn_pdf": "📘 Ebook",
        "btn_video": "🎥 Vidéo",
        "btn_script": "📜 Lien du script",
        "btn_support1": "🛠 Support Drago",
        "btn_support2": "🛠 Support Brulux",
        "btn_faq": "❓ FAQ",
        "btn_back": "⬅ Retour",
        "btn_home": "🏠 Menu principal",

        "support_ready": "🎟 Ticket: {ticket}\nClique ci-dessous pour contacter le support :",
        "missing_file": "❌ Erreur : Ebook introuvable.",
        "open_support": "➡️ Ouvrir le support",

        "version_text": "🛠 *Version du bot*\n\n• Version: `{ver}`\n• Dernière MAJ: `{date}`",

        "faq_title": "❓ FAQ – Questions fréquentes",
        "faq_back": "⬅ Retour FAQ",
    },
    "en": {
        "choose_tech": "Choose your service:",
        "tech_amazon": "📦 Amazon Tech",
        "tech_apple": "🍎 Apple Tech",
        "tech_refundall": "🎁 Tech Refund All (PayPal, Rbnb, PCS…)",

        "choose_platform": "Choose your platform:",
        "pc": "💻 PC",
        "iphone": "🍎 iPhone",
        "android": "🤖 Android",

        "btn_pdf": "📘 Ebook",
        "btn_video": "🎥 Video",
        "btn_script": "📜 Script Link",
        "btn_support1": "🛠 Drago Support",
        "btn_support2": "🛠 Brulux Support",
        "btn_faq": "❓ FAQ",
        "btn_back": "⬅ Back",
        "btn_home": "🏠 Main menu",

        "support_ready": "🎟 Ticket: {ticket}\nClick below to contact support:",
        "missing_file": "❌ Error: Ebook not found.",
        "open_support": "➡️ Open support",

        "version_text": "🛠 *Bot version*\n\n• Version: `{ver}`\n• Last update: `{date}`",

        "faq_title": "❓ FAQ – Frequently Asked Questions",
        "faq_back": "⬅ Back to FAQ",
    }
}

# ====== TIME ======
def paris_now():
    return datetime.now(ZoneInfo("Europe/Paris"))

def start_text_dynamic():
    now = paris_now().strftime("%H:%M")
    return f"👋 Bienvenue ! Il est {now}.\n\nPlease choose your language / Choisissez votre langue :"

# ====== SQLITE ======
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            username TEXT,
            lang TEXT NOT NULL,
            tech TEXT NOT NULL,
            platform TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def init_crypto_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS btc_transactions (
            tx_hash TEXT PRIMARY KEY,
            address TEXT NOT NULL,
            amount_sat BIGINT NOT NULL,
            confirmations INTEGER DEFAULT 0,
            first_seen TEXT NOT NULL,
            last_notified TEXT,
            notified_levels TEXT DEFAULT '[]'
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS btc_balance_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            address TEXT NOT NULL,
            balance_sat BIGINT NOT NULL,
            total_received_sat BIGINT NOT NULL,
            total_sent_sat BIGINT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def create_ticket_in_db(user_id: int, username: Optional[str], lang: str, tech: str, platform: str) -> int:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    created_at = paris_now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute(
        "INSERT INTO tickets (created_at, user_id, username, lang, tech, platform) VALUES (?, ?, ?, ?, ?, ?)",
        (created_at, user_id, username, lang, tech, platform)
    )
    conn.commit()
    ticket_id = cur.lastrowid
    conn.close()
    return int(ticket_id)

def total_tickets_db() -> int:
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

def build_support_message(lang, tech_label, platform_label, update, ticket_str):
    now = paris_now()
    date_now = now.strftime("%d/%m/%Y")
    time_now = now.strftime("%H:%M")
    identity = get_user_identity(update)
    flag = "🇫🇷" if lang == "fr" else "🇬🇧"

    if lang == "fr":
        return (
            f"🎟 Ticket: {ticket_str}\n"
            f"{flag} Demande Support\n\n"
            f"Date: {date_now}\n"
            f"Heure: {time_now}\n\n"
            f"Tech: {tech_label}\n"
            f"Plateforme: {platform_label}\n"
            f"Utilisateur: {identity}"
        )
    else:
        return (
            f"🎟 Ticket: {ticket_str}\n"
            f"{flag} Support Request\n\n"
            f"Date: {date_now}\n"
            f"Time: {time_now}\n\n"
            f"Tech: {tech_label}\n"
            f"Platform: {platform_label}\n"
            f"User: {identity}"
        )

def build_support_url(username, lang, tech_label, platform_label, update, ticket_str):
    msg = build_support_message(lang, tech_label, platform_label, update, ticket_str)
    return f"https://t.me/{username}?text={urllib.parse.quote(msg)}"

def get_or_create_active_ticket(context, update: Update, lang: str, tech_key: str, platform_key: str) -> str:
    active = context.user_data.get("active_ticket")
    if active and active.get("tech") == tech_key and active.get("platform") == platform_key:
        return active["ticket_str"]

    user = update.effective_user
    ticket_id = create_ticket_in_db(
        user_id=int(user.id),
        username=(user.username if user.username else None),
        lang=lang,
        tech=tech_key,
        platform=platform_key
    )
    ticket_str = f"{ticket_id:04d}"
    context.user_data["active_ticket"] = {
        "ticket_id": ticket_id,
        "ticket_str": ticket_str,
        "tech": tech_key,
        "platform": platform_key,
    }
    return ticket_str

# ====== FAQ CONTENT ======
FAQ = {
    "fr": {
        "pc": "💻 Problème PC (Edge)\n\n• Utilise Microsoft Edge\n• Désactive les extensions inutiles\n• Lis l’Ebook entièrement avant de commencer\n\nSi cela ne fonctionne pas :\nRedémarre Edge puis recommence.",
        "android": "🤖 Problème Android (Firefox)\n\n• Utilise Firefox\n• Autorise les téléchargements\n• Suis la vidéo Android étape par étape\n\nSi le script ne s’ouvre pas :\nVide le cache de Firefox puis réessaie.",
        "iphone": "🍎 Problème iPhone (Safari)\n\n• Utilise Safari\n• Active les options nécessaires si demandé\n• Regarde la vidéo iPhone entièrement\n\nEnsuite recommence calmement.",
        "ebook": "📘 Je ne trouve pas l’Ebook\n\nL’Ebook est disponible uniquement sur PC.\n\nSi tu es sur mobile :\nUtilise la vidéo ou le lien du script adapté.",
        "button": "🔘 Le bouton ne fonctionne pas\n\nFerme le bot.\nRelance avec /start.\nRefais le parcours étape par étape.\n\nSi le problème continue, contacte le support.",
        "ticket": "🎟 Question Ticket\n\n• Garde le même ticket pour la même demande\n• Envoie toujours ton numéro de ticket\n• Décris clairement ton problème\n\nCela accélère la réponse.",
        "time": "⏳ Combien de temps pour une réponse ?\n\nLe support répond le plus rapidement possible selon l’affluence.\n\nMerci de rester patient.",
        "pay": "💳 Dois-je payer quelque chose ?\n\nNon.\n\nLe bot fournit uniquement des guides et ressources.\nAucun paiement n’est demandé directement ici.",
        "notwork": "⚠️ Pourquoi cela ne fonctionne pas chez moi ?\n\nChaque appareil est différent :\nversion système, navigateur, configuration…\n\nSi cela ne fonctionne pas, ouvre un ticket support.",
    },
    "en": {
        "pc": "💻 PC Issue (Edge)\n\n• Use Microsoft Edge\n• Disable unnecessary extensions\n• Read the Ebook completely before starting\n\nIf it still fails:\nRestart Edge and try again.",
        "android": "🤖 Android Issue (Firefox)\n\n• Use Firefox\n• Allow downloads\n• Follow the Android video step by step\n\nIf the script doesn’t open:\nClear Firefox cache and try again.",
        "iphone": "🍎 iPhone Issue (Safari)\n\n• Use Safari\n• Enable required options if requested\n• Watch the full iPhone video\n\nThen restart calmly.",
        "ebook": "📘 I can't find the Ebook\n\nThe Ebook is available on PC only.\n\nIf you are on mobile:\nUse the video or the script link.",
        "button": "🔘 Button not working\n\nClose the bot.\nRestart with /start.\nFollow the steps carefully.\n\nIf it continues, contact support.",
        "ticket": "🎟 Ticket Question\n\n• Keep the same ticket for the same request\n• Always provide your ticket number\n• Clearly describe your issue\n\nThis helps us respond faster.",
        "time": "⏳ How long for a response?\n\nSupport replies as quickly as possible depending on demand.\n\nThank you for your patience.",
        "pay": "💳 Do I need to pay?\n\nNo.\n\nThe bot only provides guides and resources.\nNo payment is requested here.",
        "notwork": "⚠️ Why doesn’t it work for me?\n\nEvery device is different:\nsystem version, browser, configuration…\n\nIf it still fails, open a support ticket.",
    }
}

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
        InlineKeyboardButton(TEXTS[lang]["btn_support1"], callback_data="support_drago"),
        InlineKeyboardButton(TEXTS[lang]["btn_support2"], callback_data="support_brulux")
    ])

    keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_faq"], callback_data="faq_menu")])

    keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_home"], callback_data="go_home")])
    keyboard.append([InlineKeyboardButton(TEXTS[lang]["btn_back"], callback_data="step_platform")])
    return InlineKeyboardMarkup(keyboard)

def simple_back_home(lang):
    return InlineKeyboardMarkup([[InlineKeyboardButton(TEXTS[lang]["btn_home"], callback_data="go_home")]])

def faq_menu_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💻 PC (Edge)", callback_data="faq_pc")],
        [InlineKeyboardButton("🤖 Android (Firefox)", callback_data="faq_android")],
        [InlineKeyboardButton("🍎 iPhone (Safari)", callback_data="faq_iphone")],
        [InlineKeyboardButton("📘 Ebook", callback_data="faq_ebook")],
        [InlineKeyboardButton("🔘 Bouton", callback_data="faq_button")],
        [InlineKeyboardButton("🎟 Ticket", callback_data="faq_ticket")],
        [InlineKeyboardButton("⏳ Délai", callback_data="faq_time")],
        [InlineKeyboardButton("💳 Paiement", callback_data="faq_pay")],
        [InlineKeyboardButton("⚠️ Ça marche pas", callback_data="faq_notwork")],
        [InlineKeyboardButton("🛠 Support DragoJS", callback_data="faq_support_drago")],
        [InlineKeyboardButton(TEXTS[lang]["btn_back"], callback_data="faq_back_to_actions")],
    ])

def faq_answer_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["faq_back"], callback_data="faq_menu")],
        [InlineKeyboardButton(TEXTS[lang]["btn_home"], callback_data="go_home")],
    ])

# ====== BTC MONITORING ======
class BTCAddressMonitor:
    def __init__(self, address: str, token: str, user_id: int, bot):
        self.address = address
        self.token = token
        self.user_id = user_id
        self.bot = bot
        self.last_balance = 0
        self.base_url = "https://api.blockcypher.com/v1/btc/main"
        self.running = False
        self.notification_levels = [0, 1, 3, 6, 12]
        
    async def get_address_info(self):
        url = f"{self.base_url}/addrs/{self.address}/balance"
        params = {"token": self.token}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        logging.error(f"Erreur API: {resp.status}")
                        return None
        except Exception as e:
            logging.error(f"Erreur monitoring BTC: {e}")
            return None
    
    async def get_transactions(self, limit: int = 10):
        url = f"{self.base_url}/addrs/{self.address}"
        params = {
            "token": self.token,
            "limit": limit,
            "unspentOnly": "false",
            "includeScript": "false"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    return None
        except Exception as e:
            logging.error(f"Erreur récupération transactions: {e}")
            return None
    
    def satoshi_to_btc(self, satoshi: int) -> float:
        return satoshi / 100_000_000
    
    def format_amount(self, satoshi: int) -> str:
        btc = self.satoshi_to_btc(satoshi)
        return f"{btc:.8f} BTC"
    
    def get_notified_levels(self, tx_hash: str) -> list:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute(
            "SELECT notified_levels FROM btc_transactions WHERE tx_hash = ?",
            (tx_hash,)
        )
        result = cur.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return []
    
    def update_notified_levels(self, tx_hash: str, levels: list):
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute(
            "UPDATE btc_transactions SET notified_levels = ? WHERE tx_hash = ?",
            (json.dumps(levels), tx_hash)
        )
        conn.commit()
        conn.close()
    
    def save_transaction(self, tx_hash: str, amount_sat: int, confirmations: int):
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        
        cur.execute(
            "SELECT confirmations, notified_levels FROM btc_transactions WHERE tx_hash = ?",
            (tx_hash,)
        )
        existing = cur.fetchone()
        
        now = datetime.now().isoformat()
        
        if existing:
            cur.execute(
                """UPDATE btc_transactions 
                   SET confirmations = ?, last_notified = ? 
                   WHERE tx_hash = ?""",
                (confirmations, now if confirmations > existing[0] else None, tx_hash)
            )
        else:
            cur.execute(
                """INSERT INTO btc_transactions 
                   (tx_hash, address, amount_sat, confirmations, first_seen, notified_levels)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (tx_hash, self.address, amount_sat, confirmations, now, '[]')
            )
        
        conn.commit()
        conn.close()
    
    def save_balance_snapshot(self, balance_sat: int, total_received: int, total_sent: int):
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO btc_balance_history 
               (timestamp, address, balance_sat, total_received_sat, total_sent_sat)
               VALUES (?, ?, ?, ?, ?)""",
            (datetime.now().isoformat(), self.address, balance_sat, total_received, total_sent)
        )
        conn.commit()
        conn.close()
    
    async def send_notification(self, message: str, parse_mode: str = "Markdown"):
        try:
            await self.bot.send_message(
                chat_id=self.user_id,
                text=message,
                parse_mode=parse_mode
            )
            logging.info(f"Notification envoyée: {message[:50]}...")
        except Exception as e:
            logging.error(f"Erreur envoi notification: {e}")
    
    async def check_notifications(self):
        try:
            info = await self.get_address_info()
            if not info:
                return
            
            balance = info.get('balance', 0)
            total_received = info.get('total_received', 0)
            total_sent = info.get('total_sent', 0)
            
            if balance != self.last_balance:
                self.save_balance_snapshot(balance, total_received, total_sent)
                self.last_balance = balance
            
            txs_data = await self.get_transactions(limit=5)
            if not txs_data or 'txs' not in txs_data:
                return
            
            for tx in txs_data['txs']:
                tx_hash = tx['hash']
                confirmations = tx.get('confirmations', 0)
                
                amount_sat = 0
                for output in tx.get('outputs', []):
                    if output.get('addresses') and self.address in output['addresses']:
                        amount_sat += output.get('value', 0)
                
                if amount_sat > 0:
                    self.save_transaction(tx_hash, amount_sat, confirmations)
                    
                    notified_levels = self.get_notified_levels(tx_hash)
                    
                    if not notified_levels:
                        btc_amount = self.format_amount(amount_sat)
                        tx_url = f"https://www.blockchain.com/btc/tx/{tx_hash}"
                        
                        message = (
                            f"💰 *NOUVELLE TRANSACTION BTC* 💰\n\n"
                            f"Montant: `{btc_amount}`\n"
                            f"Confirmations: `{confirmations}`\n"
                            f"Hash: `{tx_hash[:16]}...`\n\n"
                            f"[Voir sur Blockchain]({tx_url})"
                        )
                        await self.send_notification(message)
                        notified_levels = [confirmations]
                    
                    for level in self.notification_levels:
                        if confirmations >= level and level not in notified_levels:
                            btc_amount = self.format_amount(amount_sat)
                            tx_url = f"https://www.blockchain.com/btc/tx/{tx_hash}"
                            
                            if level == 0:
                                msg_type = "🕐 Transaction détectée"
                            elif level == 1:
                                msg_type = "✅ 1 confirmation"
                            elif level == 3:
                                msg_type = "🔒 3 confirmations (sûr)"
                            elif level == 6:
                                msg_type = "🔐 6 confirmations (très sûr)"
                            else:
                                msg_type = f"📊 {level} confirmations"
                            
                            message = (
                                f"📈 *Mise à jour transaction* 📈\n\n"
                                f"{msg_type}\n"
                                f"Montant: `{btc_amount}`\n"
                                f"[Voir sur Blockchain]({tx_url})"
                            )
                            await self.send_notification(message)
                            notified_levels.append(level)
                    
                    self.update_notified_levels(tx_hash, notified_levels)
        
        except Exception as e:
            logging.error(f"Erreur dans check_notifications: {e}")
    
    async def run(self):
        self.running = True
        logging.info(f"🚀 Monitoring BTC démarré pour l'adresse {self.address}")
        
        await self.send_notification(
            f"🚀 *Monitoring BTC activé*\n\n"
            f"Adresse: `{self.address}`\n"
            f"Vérification toutes les {CHECK_INTERVAL//60} minutes"
        )
        
        while self.running:
            try:
                await self.check_notifications()
                await asyncio.sleep(CHECK_INTERVAL)
            except Exception as e:
                logging.error(f"Erreur boucle monitoring: {e}")
                await asyncio.sleep(60)
    
    def stop(self):
        self.running = False
        logging.info("🛑 Monitoring BTC arrêté")

btc_monitor = None

# ====== COMMANDES BTC ======
async def start_monitoring(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != MONITOR_USER_ID:
        await update.message.reply_text("⛔ Commande non autorisée")
        return
    
    global btc_monitor
    if btc_monitor and btc_monitor.running:
        await update.message.reply_text("📊 Monitoring déjà actif")
        return
    
    btc_monitor = BTCAddressMonitor(
        address=BTC_ADDRESS,
        token=BLOCKCYPHER_TOKEN,
        user_id=MONITOR_USER_ID,
        bot=context.bot
    )
    
    asyncio.create_task(btc_monitor.run())
    
    await update.message.reply_text(
        f"✅ *Monitoring BTC démarré*\n\n"
        f"Adresse: `{BTC_ADDRESS}`\n"
        f"Intervalle: {CHECK_INTERVAL//60} minutes\n"
        f"Notifications: à 0,1,3,6,12 confirmations",
        parse_mode="Markdown"
    )

async def stop_monitoring(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != MONITOR_USER_ID:
        return
    
    global btc_monitor
    if btc_monitor:
        btc_monitor.stop()
        btc_monitor = None
        await update.message.reply_text("🛑 Monitoring BTC arrêté")
    else:
        await update.message.reply_text("📊 Aucun monitoring actif")

async def btc_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != MONITOR_USER_ID:
        return
    
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT tx_hash, amount_sat, confirmations, first_seen 
        FROM btc_transactions 
        WHERE address = ? 
        ORDER BY first_seen DESC 
        LIMIT 5
    """, (BTC_ADDRESS,))
    
    txs = cur.fetchall()
    
    cur.execute("""
        SELECT balance_sat, timestamp 
        FROM btc_balance_history 
        WHERE address = ? 
        ORDER BY timestamp DESC 
        LIMIT 1
    """, (BTC_ADDRESS,))
    
    balance = cur.fetchone()
    conn.close()
    
    status = "🟢 Actif" if btc_monitor and btc_monitor.running else "🔴 Inactif"
    
    message = f"📊 *Monitoring BTC*\n\n"
    message += f"Statut: {status}\n"
    
    if balance:
        btc_balance = balance[0] / 100_000_000
        message += f"Solde actuel: `{btc_balance:.8f} BTC`\n"
        message += f"Dernier check: {balance[1][:16]}\n\n"
    
    if txs:
        message += "*Dernières transactions:*\n"
        for tx in txs:
            btc_amount = tx[1] / 100_000_000
            message += f"• `{btc_amount:.8f} BTC` ({tx[2]} conf.)\n"
    else:
        message += "\n*Aucune transaction récente*"
    
    await update.message.reply_text(message, parse_mode="Markdown")

async def btc_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != MONITOR_USER_ID:
        return
    
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT tx_hash, amount_sat, confirmations, first_seen 
        FROM btc_transactions 
        WHERE address = ? 
        ORDER BY first_seen DESC
    """, (BTC_ADDRESS,))
    
    txs = cur.fetchall()
    conn.close()
    
    if not txs:
        await update.message.reply_text("📭 Aucune transaction")
        return
    
    message = "📜 *Historique complet BTC*\n\n"
    total_received = 0
    
    for tx in txs:
        btc_amount = tx[1] / 100_000_000
        total_received += btc_amount
        date = tx[3][:10]
        message += f"• {date}: `{btc_amount:.8f} BTC` ({tx[2]} conf.)\n"
    
    message += f"\n*Total reçu:* `{total_received:.8f} BTC`"
    
    if len(message) > 4000:
        parts = [message[i:i+4000] for i in range(0, len(message), 4000)]
        for part in parts:
            await update.message.reply_text(part, parse_mode="Markdown")
    else:
        await update.message.reply_text(message, parse_mode="Markdown")

# ====== HANDLERS PRINCIPAUX ======
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

    # ====== Language ======
    if query.data.startswith("lang_"):
        context.user_data["lang"] = query.data.split("_")[1]
        lang = context.user_data["lang"]
        context.user_data.pop("active_ticket", None)
        await query.edit_message_text(TEXTS[lang]["choose_tech"], reply_markup=tech_keyboard(lang))
        return

    # ====== Tech ======
    if query.data.startswith("tech_"):
        tech_key = query.data.split("_")[1]
        context.user_data["tech"] = tech_key
        context.user_data.pop("active_ticket", None)
        inc_stat("tech_clicks", tech_key)
        await query.edit_message_text(TEXTS[lang]["choose_platform"], reply_markup=platform_keyboard(lang))
        return

    # ====== Platform ======
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

    # ====== Ebook ======
    if query.data == "send_pdf_pc":
        tech = context.user_data.get("tech", "refundall")
        file_path = TECH_PDF_PC.get(tech)
        if not file_path or not os.path.exists(file_path):
            await query.message.reply_text(TEXTS[lang]["missing_file"])
            return
        with open(file_path, "rb") as f:
            await query.message.reply_document(f)
        return

    # ====== Support ======
    if query.data in ("support_drago", "support_brulux"):
        tech_key = context.user_data.get("tech", "refundall")
        platform_key = context.user_data.get("platform", "pc")

        tech_label = TEXTS[lang].get(f"tech_{tech_key}", tech_key)
        platform_label = TEXTS[lang].get(platform_key, platform_key)

        ticket_str = get_or_create_active_ticket(context, update, lang, tech_key, platform_key)
        inc_stat("support_requests")

        if query.data == "support_drago":
            url = build_support_url(SUPPORT_1_USERNAME, lang, tech_label, platform_label, update, ticket_str)
        else:
            url = build_support_url(SUPPORT_2_USERNAME, lang, tech_label, platform_label, update, ticket_str)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(TEXTS[lang]["open_support"], url=url)],
            [InlineKeyboardButton(TEXTS[lang]["btn_home"], callback_data="go_home")],
        ])

        await query.edit_message_text(TEXTS[lang]["support_ready"].format(ticket=ticket_str), reply_markup=keyboard)
        return

    # ====== FAQ ======
    if query.data == "faq_menu":
        await query.edit_message_text(TEXTS[lang]["faq_title"], reply_markup=faq_menu_keyboard(lang))
        return

    if query.data == "faq_back_to_actions":
        platform = context.user_data.get("platform", "pc")
        await query.edit_message_text(TEXTS[lang]["choose_platform"], reply_markup=actions_keyboard(lang, platform))
        return

    if query.data.startswith("faq_") and not query.data == "faq_support_drago":
        key = query.data.split("_", 1)[1]
        text = FAQ.get(lang, FAQ["fr"]).get(key, "FAQ indisponible.")
        await query.edit_message_text(text, reply_markup=faq_answer_keyboard(lang))
        return

    # ====== FAQ Support DragoJS ======
    if query.data == "faq_support_drago":
        tech_key = context.user_data.get("tech", "refundall")
        platform_key = context.user_data.get("platform", "pc")
        
        tech_label = TEXTS[lang].get(f"tech_{tech_key}", tech_key)
        platform_label = TEXTS[lang].get(platform_key, platform_key)
        
        ticket_str = get_or_create_active_ticket(context, update, lang, tech_key, platform_key)
        inc_stat("support_requests")
        
        url = build_support_url(SUPPORT_1_USERNAME, lang, tech_label, platform_label, update, ticket_str)
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(TEXTS[lang]["open_support"], url=url)],
            [InlineKeyboardButton("⬅ Retour FAQ", callback_data="faq_menu")],
            [InlineKeyboardButton(TEXTS[lang]["btn_home"], callback_data="go_home")],
        ])
        
        await query.edit_message_text(
            TEXTS[lang]["support_ready"].format(ticket=ticket_str),
            reply_markup=keyboard
        )
        return

# ====== MAIN ======
if __name__ == "__main__":
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        print("ERREUR : TELEGRAM_TOKEN manquant !")
        print("👉 Vérifie que la variable d'environnement est bien configurée sur Railway")
    else:
        init_db()
        init_crypto_db()
        
        app = Application.builder().token(TOKEN).build()
        
        # Handlers principaux
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler))
        
        # Handlers BTC
        app.add_handler(CommandHandler("startbtc", start_monitoring))
        app.add_handler(CommandHandler("stopbtc", stop_monitoring))
        app.add_handler(CommandHandler("btcstatus", btc_status))
        app.add_handler(CommandHandler("btchistory", btc_history))
        
        print("🚀 Bot démarré - Version de base sans statut support")
        print(f"💰 Adresse BTC surveillée: {BTC_ADDRESS}")
        app.run_polling()
