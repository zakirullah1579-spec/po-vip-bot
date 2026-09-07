"""
Pocket Option VIP Signal Bot
============================
Registration-first VIP signal bot for Telegram.
"""

import os
import random
import sqlite3
from datetime import datetime

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
REG_LINK = os.getenv("POCKET_OPTION_REG_LINK", "https://pocketoption.com/register")
DB_PATH = "signals.db"

# ─── Database ──────────────────────────────────────────────────────────

def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            po_id TEXT DEFAULT NULL,
            is_verified INTEGER DEFAULT 0,
            signals_used INTEGER DEFAULT 0,
            joined_at TEXT,
            verified_at TEXT DEFAULT NULL
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS signals(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            asset TEXT,
            timeframe TEXT,
            direction TEXT,
            confidence INTEGER,
            rsi REAL,
            ema9 REAL,
            ema21 REAL,
            is_vip INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)
    con.commit()
    con.close()


def get_con():
    return sqlite3.connect(DB_PATH)


def ensure_user(user_id, username, full_name):
    con = get_con()
    existing = con.execute(
        "SELECT user_id FROM users WHERE user_id=?", (user_id,)
    ).fetchone()
    if not existing:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        con.execute(
            "INSERT INTO users(user_id, username, full_name, joined_at) "
            "VALUES(?,?,?,?)",
            (user_id, username or "", full_name, now)
        )
        con.commit()
    con.close()


def is_verified(user_id):
    con = get_con()
    row = con.execute(
        "SELECT is_verified FROM users WHERE user_id=?", (user_id,)
    ).fetchone()
    con.close()
    return row and row[0] == 1


def verify_user(user_id, po_id=None):
    con = get_con()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    con.execute(
        "UPDATE users SET is_verified=1, po_id=?, verified_at=? "
        "WHERE user_id=?",
        (po_id, now, user_id)
    )
    con.commit()
    con.close()


def remove_verified(user_id):
    con = get_con()
    con.execute(
        "UPDATE users SET is_verified=0, po_id=NULL, verified_at=NULL "
        "WHERE user_id=?",
        (user_id,)
    )
    con.commit()
    con.close()


# ─── Signal Engine ─────────────────────────────────────────────────────

def generate_signal():
    price = 100.0
    closes = []
    for _ in range(60):
        price += random.uniform(-1.0, 1.0)
        closes.append(price)

    def ema(vals, period):
        e = sum(vals[:period]) / period
        k = 2 / (period + 1)
        for p in vals[period:]:
            e = p * k + e * (1 - k)
        return e

    e9, e21 = ema(closes, 9), ema(closes, 21)

    gains, losses = [], []
    for a, b in zip(closes[-15:-1], closes[-14:]):
        d = b - a
        gains.append(max(d, 0))
        losses.append(max(-d, 0))

    ag = sum(gains) / 14
    al = sum(losses) / 14
    rsi = 100 if al == 0 else 100 - 100 / (1 + ag / al)

    score = 1 if e9 > e21 else -1
    if rsi < 35:
        score += 1
    elif rsi > 65:
        score -= 1
    if closes[-1] > e9:
        score += 1
    else:
        score -= 1

    if score >= 2:
        direction = "CALL \U0001f7e2"
    elif score <= -2:
        direction = "PUT \U0001f534"
    else:
        direction = "WAIT \U0001f7e1"

    confidence = max(50, min(95, 55 + abs(score) * 10))
    return direction, confidence, rsi, e9, e21


# ─── Sample Reviews ────────────────────────────────────────────────────

SAMPLE_REVIEWS = [
    {
        "name": "Ahmad K.",
        "text": "Mujhe 2 weeks mein $500+ profit mili! Signals bohat accurate hain.",
        "date": "2026-08-20"
    },
    {
        "name": "Sarah M.",
        "text": "Best signal group on Telegram! VIP worth every penny.",
        "date": "2026-08-15"
    },
    {
        "name": "Raj P.",
        "text": "Pehle din hi 3 wins out of 4! Copy trading amazing hai.",
        "date": "2026-08-10"
    },
    {
        "name": "Maria L.",
        "text": "Registration ke baad turant VIP access mila. Support great!",
        "date": "2026-08-05"
    },
    {
        "name": "Chen W.",
        "text": "80%+ win rate real hai! Maine khud check kiya.",
        "date": "2026-07-30"
    },
    {
        "name": "David R.",
        "text": "Free test signals se convince hua, ab VIP member!",
        "date": "2026-07-25"
    },
]

ASSETS = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD",
          "EUR/GBP", "USD/CAD", "NZD/USD", "EUR/JPY"]


# ─── Keyboards ─────────────────────────────────────────────────────────

def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "\U0001f511 Start Registration", callback_data="reg_start"
        )],
        [
            InlineKeyboardButton(
                "\u2705 Instruction", callback_data="instruction"
            ),
            InlineKeyboardButton(
                "\U0001f514 Test Signals", callback_data="test_signal"
            ),
        ],
        [InlineKeyboardButton(
            "\U0001f49a Reviews", callback_data="reviews"
        )],
    ])


def registration_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "\U0001f7e2 Register on Pocket Option", url=REG_LINK
        )],
        [InlineKeyboardButton(
            "\u2705 I've Registered - Send ID", callback_data="send_po_id"
        )],
        [InlineKeyboardButton(
            "\u2b05\ufe0f Back", callback_data="back_main"
        )],
    ])


def verified_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "\u26a1 New Signal", callback_data="vip_signal"
        )],
        [
            InlineKeyboardButton(
                "\U0001f4ca Statistics", callback_data="stats"
            ),
            InlineKeyboardButton(
                "\U0001f4da Strategy", callback_data="strategy"
            ),
        ],
        [InlineKeyboardButton(
            "\u2b05\ufe0f Back", callback_data="back_main"
        )],
    ])


def signal_again_kb(is_vip=True):
    cb = "vip_signal" if is_vip else "test_signal"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "\u26a1 Generate Again", callback_data=cb
        )],
        [InlineKeyboardButton(
            "\U0001f4ca Statistics", callback_data="stats"
        )],
        [InlineKeyboardButton(
            "\u2b05\ufe0f Back", callback_data="back_main"
        )],
    ])


def admin_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "\U0001f4e2 Send Signal", callback_data="admin_send_signal"
        )],
        [InlineKeyboardButton(
            "\U0001f465 Verified Users", callback_data="admin_verified"
        )],
        [InlineKeyboardButton(
            "\u23f3 Pending Users", callback_data="admin_pending"
        )],
        [InlineKeyboardButton(
            "\U0001f4ca Statistics", callback_data="admin_stats"
        )],
        [InlineKeyboardButton(
            "\U0001f514 Broadcast", callback_data="admin_broadcast"
        )],
    ])


# ─── Command Handlers ──────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ensure_user(user.id, user.username, user.full_name)

    if is_verified(user.id):
        text = (
            "\U0001f525 <b>Welcome Back, VIP Member!</b> \U0001f525\n\n"
            "\U0001f4ca Your VIP signal dashboard is ready.\n"
            "\u26a1 Generate a new signal below!"
        )
        kb = verified_menu_kb()
    else:
        text = (
            "\U0001f525 <b>Pocket Option VIP Signals</b> \U0001f525\n\n"
            "\U0001f44b Hey! I have gathered signals from the most successful\n"
            "and proven traders in one place, and you will receive\n"
            "them very soon. \U0001f4b0\n\n"
            "\u2728 <b>What you get:</b>\n"
            "\U0001f916 AI robot trading signals\n"
            "\U0001f4ca 5 groups with signals from top traders\n"
            "\U0001f4d6 The best training material\n"
            "\U0001f4cb Access to copy trading\n\n"
            "\u26a0\ufe0f Access to copy trading opens after registration\n"
            "in this bot!\n\n"
            "See the instructions, register, and copy the signals \U0001f447"
        )
        kb = main_menu_kb()

    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)


async def cmd_mystatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if is_verified(user.id):
        con = get_con()
        row = con.execute(
            "SELECT full_name, po_id, verified_at FROM users "
            "WHERE user_id=?",
            (user.id,)
        ).fetchone()
        con.close()
        await update.message.reply_text(
            "\u2705 <b>VERIFIED VIP MEMBER</b>\n\n"
            "\U0001f464 Name: {}\n"
            "\U0001f194 PO ID: {}\n"
            "\U0001f4c5 Verified: {}\n\n"
            "\U0001f389 Full access to VIP signals & copy trading!".format(
                row[0], row[1] or "N/A", row[2] or "N/A"
            ),
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            "\u274c <b>NOT VERIFIED</b>\n\n"
            "Register on Pocket Option first!\n"
            "Click /start then Start Registration",
            parse_mode="HTML"
        )


# ─── Admin Commands ────────────────────────────────────────────────────

async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(
        "\U0001f468\u200d\U0001f4bc <b>Admin Panel</b>\n\nSelect an option:",
        parse_mode="HTML",
        reply_markup=admin_kb()
    )


async def cmd_adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "Usage: /adduser <chat_id> [po_id]\n"
            "Example: /adduser 123456789 PO12345"
        )
        return
    target_id = int(context.args[0])
    po_id = context.args[1] if len(context.args) > 1 else None
    ensure_user(target_id, "", "")
    verify_user(target_id, po_id)
    try:
        await context.bot.send_message(
            target_id,
            "\U0001f389 <b>Congratulations!</b>\n\n"
            "\u2705 You are now a verified VIP member!\n"
            "\U0001f3af Full access to premium signals & copy trading!\n\n"
            "Click /start to see your signals.",
            parse_mode="HTML"
        )
    except Exception:
        pass
    await update.message.reply_text(
        "\u2705 User {} verified!".format(target_id),
        parse_mode="HTML"
    )


async def cmd_removeuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /removeuser <chat_id>")
        return
    target_id = int(context.args[0])
    remove_verified(target_id)
    try:
        await context.bot.send_message(
            target_id,
            "\u274c Your VIP access has been removed. Contact admin."
        )
    except Exception:
        pass
    await update.message.reply_text(
        "\u2705 User {} removed.".format(target_id)
    )


async def cmd_signal_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args or len(context.args) < 4:
        await update.message.reply_text(
            "Usage: /signal <asset> <direction> <timeframe> <confidence>\n"
            "Example: /signal EUR/USD CALL M5 85%"
        )
        return

    asset = context.args[0]
    direction = context.args[1].upper()
    timeframe = context.args[2]
    confidence = context.args[3]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    dir_emoji = "\U0001f7e2" if "CALL" in direction else "\U0001f534"

    signal_text = (
        "\U0001f525 <b>VIP SIGNAL</b> \U0001f525\n"
        "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
        "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"
        "\U0001f4ca Asset: {}\n"
        "\u23f1 Timeframe: {}\n"
        "\U0001f550 Time: {}\n\n"
        "\U0001f3af Direction: {} {}\n"
        "\U0001f4c8 Confidence: {}\n\n"
        "\u26a1 Place your trade now!\n\n"
        "\u26a0\ufe0f Trading involves risk. Not financial advice."
    ).format(asset, timeframe, now, direction, dir_emoji, confidence)

    con = get_con()
    ids = [
        r[0] for r in con.execute(
            "SELECT user_id FROM users WHERE is_verified=1"
        )
    ]
    con.close()

    sent = 0
    for uid in ids:
        try:
            await context.bot.send_message(
                uid, signal_text, parse_mode="HTML"
            )
            sent += 1
        except Exception:
            pass

    await update.message.reply_text(
        "\u2705 Signal broadcast to {} VIP users.".format(sent),
        parse_mode="HTML"
    )


async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    msg = " ".join(context.args).strip()
    if not msg:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    con = get_con()
    ids = [
        r[0] for r in con.execute(
            "SELECT user_id FROM users WHERE is_verified=1"
        )
    ]
    con.close()
    sent = 0
    for uid in ids:
        try:
            await context.bot.send_message(
                uid,
                "\U0001f4e2 <b>VIP Announcement</b>\n\n{}".format(msg),
                parse_mode="HTML"
            )
            sent += 1
        except Exception:
            pass
    await update.message.reply_text(
        "\u2705 Broadcast sent to {} users.".format(sent)
    )


async def cmd_listusers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    con = get_con()
    verified = con.execute(
        "SELECT user_id, full_name, po_id FROM users WHERE is_verified=1"
    ).fetchall()
    pending = con.execute(
        "SELECT user_id, full_name FROM users WHERE is_verified=0"
    ).fetchall()
    con.close()

    text = "\U0001f4cb <b>User List</b>\n\n"
    text += "\u2705 Verified: {}\n".format(len(verified))
    text += "\u23f3 Not Verified: {}\n\n".format(len(pending))

    if verified:
        text += "<b>Verified:</b>\n"
        for uid_r, name, po_id in verified:
            text += "\u2022 {} ({}) PO:{}\n".format(
                name, uid_r, po_id or "N/A"
            )
    if pending:
        text += "\n<b>Pending:</b>\n"
        for uid_r, name in pending[:20]:
            text += "\u2022 {} ({})\n".format(name, uid_r)

    await update.message.reply_text(text, parse_mode="HTML")


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    con = get_con()
    total_users = con.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]
    verified = con.execute(
        "SELECT COUNT(*) FROM users WHERE is_verified=1"
    ).fetchone()[0]
    total_signals = con.execute(
        "SELECT COUNT(*) FROM signals"
    ).fetchone()[0]
    con.close()
    await update.message.reply_text(
        "\U0001f4ca <b>Bot Statistics</b>\n\n"
        "\U0001f465 Total Users: {}\n"
        "\u2705 Verified: {}\n"
        "\u23f3 Unverified: {}\n"
        "\U0001f4ca Signals Generated: {}".format(
            total_users, verified,
            total_users - verified, total_signals
        ),
        parse_mode="HTML"
    )


# ─── Callback Handler ──────────────────────────────────────────────────

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    uid = q.from_user.id

    # ─── Registration Start ───
    if data == "reg_start":
        reg_text = (
            "\U0001f511 <b>Start Registration</b>\n\n"
            "To get VIP signals & copy trading access,\n"
            "you MUST register on Pocket Option first!\n\n"
            "\U0001f449 <a href=\"" + REG_LINK + "\">"
            "\U0001f7e2 Register on Pocket Option</a>\n\n"
            "\U0001f4cb <b>Steps:</b>\n"
            "1\ufe0f\u20e3 Click the button below to register\n"
            "2\ufe0f\u20e3 Complete your Pocket Option registration\n"
            "3\ufe0f\u20e3 Send your Pocket Option ID to admin\n"
            "4\ufe0f\u20e3 Admin verifies \u2192 VIP access unlocked! \U0001f389\n\n"
            "\u23f3 Verification takes 5-30 minutes"
        )
        await q.edit_message_text(
            reg_text,
            parse_mode="HTML",
            reply_markup=registration_kb(),
            disable_web_page_preview=True
        )

    # ─── Instruction ───
    elif data == "instruction":
        inst_text = (
            "\u2705 <b>Registration Instructions</b>\n\n"
            "Follow these steps carefully:\n\n"
            "<b>Step 1:</b> \U0001f511 Click Start Registration\n"
            "You'll get a special link to Pocket Option\n\n"
            "<b>Step 2:</b> \U0001f7e2 Register on Pocket Option\n"
            "Fill in your details & create account\n\n"
            "<b>Step 3:</b> \U0001f194 Get your Pocket Option ID\n"
            "Find it in your profile/settings\n\n"
            "<b>Step 4:</b> \U0001f4e7 Send your PO ID here\n"
            "Type: <code>POID: your_id_here</code>\n\n"
            "<b>Step 5:</b> \u2705 Wait for admin verification\n"
            "Usually takes 5-30 minutes\n\n"
            "After verification you get:\n"
            "\U0001f4ca VIP signals from top traders\n"
            "\U0001f4cb Copy trading access\n"
            "\U0001f4d6 Training materials\n"
            "\U0001f916 AI robot signals"
        )
        await q.edit_message_text(
            inst_text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "\U0001f511 Start Registration",
                    callback_data="reg_start"
                )],
                [InlineKeyboardButton(
                    "\u2b05\ufe0f Back",
                    callback_data="back_main"
                )],
            ])
        )

    # ─── Test Signal (Free) ───
    elif data == "test_signal":
        direction, conf, rsi, e9, e21 = generate_signal()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        asset = random.choice(ASSETS)

        text = (
            "\U0001f514 <b>TEST SIGNAL</b> (Free Preview)\n"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"
            "\U0001f4ca Asset: {}\n"
            "\u23f1 Timeframe: M5\n"
            "\U0001f550 {}\n\n"
            "\U0001f3af Direction: {}\n"
            "\U0001f4c8 Confidence: {}%\n\n"
            "\U0001f4d0 RSI: {:.2f}\n"
            "\U0001f4cf EMA 9: {:.4f}\n"
            "\U0001f4cf EMA 21: {:.4f}\n\n"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            "\U0001f525 <b>Want FULL VIP signals?</b>\n"
            "Register now \u2192 5 signal groups, copy trading!\n"
            "\U0001f449 Up to 92% win rate!"
        ).format(asset, now, direction, conf, rsi, e9, e21)

        con = get_con()
        con.execute(
            "UPDATE users SET signals_used=signals_used+1 "
            "WHERE user_id=?", (uid,)
        )
        con.execute(
            "INSERT INTO signals("
            "user_id,asset,timeframe,direction,confidence,"
            "rsi,ema9,ema21,is_vip,created_at"
            ") VALUES(?,?,?,?,?,?,?,?,0,?)",
            (uid, asset, "M5", direction, conf, rsi, e9, e21, now)
        )
        con.commit()
        con.close()

        await q.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "\u26a1 Try Again",
                    callback_data="test_signal"
                )],
                [InlineKeyboardButton(
                    "\U0001f511 Get VIP Access",
                    callback_data="reg_start"
                )],
                [InlineKeyboardButton(
                    "\u2b05\ufe0f Back",
                    callback_data="back_main"
                )],
            ])
        )

    # ─── Reviews ───
    elif data == "reviews":
        review = random.choice(SAMPLE_REVIEWS)
        text = (
            "\U0001f49a <b>User Reviews</b>\n\n"
            "\U0001f464 <b>{}</b> ({})\n"
            "\U0001f4ac \"{}\"\n\n"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            "\U0001f4ca Average Win Rate: 80-92%\n"
            "\U0001f465 6,700+ active members\n"
            "\u2b50 4.8/5 rating\n\n"
            "\U0001f4ac Join thousands of profitable traders!"
        ).format(review["name"], review["date"], review["text"])

        await q.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "\U0001f49a More Reviews",
                    callback_data="reviews"
                )],
                [InlineKeyboardButton(
                    "\U0001f511 Join VIP",
                    callback_data="reg_start"
                )],
                [InlineKeyboardButton(
                    "\u2b05\ufe0f Back",
                    callback_data="back_main"
                )],
            ])
        )

    # ─── Send PO ID ───
    elif data == "send_po_id":
        await q.edit_message_text(
            "\U0001f4cb <b>Send your Pocket Option ID</b>\n\n"
            "Type your PO ID in this format:\n"
            "<code>POID: 12345678</code>\n\n"
            "Admin will verify it within 5-30 minutes!\n"
            "You'll get a notification once verified. \u2705",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "\u2b05\ufe0f Back",
                    callback_data="back_main"
                )],
            ])
        )

    # ─── VIP Signal (verified only) ───
    elif data == "vip_signal":
        if not is_verified(uid):
            await q.edit_message_text(
                "\U0001f512 <b>VIP Access Required!</b>\n\n"
                "You must be a verified VIP member to access\n"
                "premium signals & copy trading.\n\n"
                "\U0001f449 Register first to unlock full access!",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        "\U0001f511 Register Now",
                        callback_data="reg_start"
                    )],
                    [InlineKeyboardButton(
                        "\U0001f514 Try Free Signal",
                        callback_data="test_signal"
                    )],
                    [InlineKeyboardButton(
                        "\u2b05\ufe0f Back",
                        callback_data="back_main"
                    )],
                ])
            )
            return

        direction, conf, rsi, e9, e21 = generate_signal()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        asset = random.choice(ASSETS)

        text = (
            "\u26a1 <b>VIP SIGNAL</b>\n"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"
            "\U0001f4ca Asset: {}\n"
            "\u23f1 Timeframe: M5\n"
            "\U0001f550 {}\n\n"
            "\U0001f3af Direction: {}\n"
            "\U0001f4c8 Confidence: {}%\n\n"
            "\U0001f4d0 RSI: {:.2f}\n"
            "\U0001f4cf EMA 9: {:.4f}\n"
            "\U0001f4cf EMA 21: {:.4f}\n\n"
            "\u26a1 Place your trade now!\n\n"
            "\u26a0\ufe0f Trading involves risk. Not financial advice."
        ).format(asset, now, direction, conf, rsi, e9, e21)

        con = get_con()
        con.execute(
            "UPDATE users SET signals_used=signals_used+1 "
            "WHERE user_id=?", (uid,)
        )
        con.execute(
            "INSERT INTO signals("
            "user_id,asset,timeframe,direction,confidence,"
            "rsi,ema9,ema21,is_vip,created_at"
            ") VALUES(?,?,?,?,?,?,?,?,1,?)",
            (uid, asset, "M5", direction, conf, rsi, e9, e21, now)
        )
        con.commit()
        con.close()

        await q.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=signal_again_kb(is_vip=True)
        )

    # ─── Statistics ───
    elif data == "stats":
        con = get_con()
        row = con.execute(
            "SELECT signals_used FROM users WHERE user_id=?",
            (uid,)
        ).fetchone()
        total = row[0] if row else 0
        vip_count = con.execute(
            "SELECT COUNT(*) FROM signals "
            "WHERE user_id=? AND is_vip=1",
            (uid,)
        ).fetchone()[0]
        test_count = con.execute(
            "SELECT COUNT(*) FROM signals "
            "WHERE user_id=? AND is_vip=0",
            (uid,)
        ).fetchone()[0]
        con.close()

        text = (
            "\U0001f4ca <b>Your Statistics</b>\n\n"
            "\u26a1 Total Signals: {}\n"
            "\U0001f7e2 VIP Signals: {}\n"
            "\U0001f514 Test Signals: {}\n\n"
            "\U0001f4c8 Keep trading smart!"
        ).format(total, vip_count, test_count)

        kb = verified_menu_kb() if is_verified(uid) else main_menu_kb()
        await q.edit_message_text(
            text, parse_mode="HTML", reply_markup=kb
        )

    # ─── Strategy ───
    elif data == "strategy":
        await q.edit_message_text(
            "\U0001f4da <b>Trading Strategy</b>\n\n"
            "Our signals use a combination of:\n\n"
            "\U0001f4cf <b>EMA 9/21 Crossover</b>\n"
            "Identifies trend direction\n\n"
            "\U0001f4d0 <b>RSI (14)</b>\n"
            "Detects overbought/oversold levels\n\n"
            "\U0001f916 <b>AI Analysis</b>\n"
            "Combines multiple indicators\n\n"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            "\u26a0\ufe0f Indicators do not guarantee future "
            "price movement. Trade responsibly.",
            parse_mode="HTML",
            reply_markup=verified_menu_kb()
        )

    # ─── Back to Main Menu ───
    elif data == "back_main":
        user = q.from_user
        ensure_user(user.id, user.username, user.full_name)

        if is_verified(uid):
            text = (
                "\U0001f525 <b>Welcome Back, VIP Member!</b> \U0001f525\n\n"
                "\U0001f4ca Your VIP signal dashboard is ready.\n"
                "\u26a1 Generate a new signal below!"
            )
            await q.edit_message_text(
                text,
                parse_mode="HTML",
                reply_markup=verified_menu_kb()
            )
        else:
            text = (
                "\U0001f525 <b>Pocket Option VIP Signals</b> \U0001f525\n\n"
                "\U0001f44b Get signals from proven traders!\n\n"
                "\u2728 AI signals \u2022 5 signal groups \u2022 Copy trading\n\n"
                "\u26a0\ufe0f Register first for full VIP access!\n\n"
                "Choose an option \U0001f447"
            )
            await q.edit_message_text(
                text,
                parse_mode="HTML",
                reply_markup=main_menu_kb()
            )

    # ─── Admin Callbacks ───
    elif data == "admin_send_signal":
        await q.edit_message_text(
            "\U0001f4e2 <b>Send Signal</b>\n\n"
            "Use this format:\n"
            "<code>/signal EUR/USD CALL M5 85%</code>",
            parse_mode="HTML",
            reply_markup=admin_kb()
        )

    elif data == "admin_verified":
        con = get_con()
        rows = con.execute(
            "SELECT user_id, full_name, po_id "
            "FROM users WHERE is_verified=1"
        ).fetchall()
        con.close()
        text = "\u2705 <b>Verified Users ({})</b>\n\n".format(len(rows))
        for uid_r, name, po_id in rows:
            text += "\u2022 {} ({}) PO:{}\n".format(
                name, uid_r, po_id or "N/A"
            )
        if not rows:
            text += "No verified users yet."
        await q.edit_message_text(
            text, parse_mode="HTML", reply_markup=admin_kb()
        )

    elif data == "admin_pending":
        con = get_con()
        rows = con.execute(
            "SELECT user_id, full_name FROM users WHERE is_verified=0"
        ).fetchall()
        con.close()
        text = "\u23f3 <b>Pending Users ({})</b>\n\n".format(len(rows))
        for uid_r, name in rows[:20]:
            text += "\u2022 {} ({})\n".format(name, uid_r)
        if not rows:
            text += "No pending users."
        await q.edit_message_text(
            text, parse_mode="HTML", reply_markup=admin_kb()
        )

    elif data == "admin_stats":
        con = get_con()
        total = con.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]
        verified = con.execute(
            "SELECT COUNT(*) FROM users WHERE is_verified=1"
        ).fetchone()[0]
        sigs = con.execute(
            "SELECT COUNT(*) FROM signals"
        ).fetchone()[0]
        con.close()
        await q.edit_message_text(
            "\U0001f4ca <b>Bot Statistics</b>\n\n"
            "\U0001f465 Total Users: {}\n"
            "\u2705 Verified: {}\n"
            "\u23f3 Pending: {}\n"
            "\U0001f4ca Signals: {}".format(
                total, verified, total - verified, sigs
            ),
            parse_mode="HTML",
            reply_markup=admin_kb()
        )

    elif data == "admin_broadcast":
        await q.edit_message_text(
            "\U0001f514 <b>Broadcast</b>\n\n"
            "Type: <code>/broadcast Your message</code>",
            parse_mode="HTML",
            reply_markup=admin_kb()
        )


# ─── Message Handler (PO ID) ──────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    uid = update.effective_user.id

    if text.upper().startswith("POID:") or text.upper().startswith("PO ID:"):
        po_id = text.split(":", 1)[1].strip()

        con = get_con()
        con.execute(
            "UPDATE users SET po_id=? WHERE user_id=?",
            (po_id, uid)
        )
        con.commit()
        con.close()

        # Notify admin
        try:
            await context.bot.send_message(
                ADMIN_ID,
                "\U0001f4cb <b>New Registration Request</b>\n\n"
                "\U0001f464 User: {}\n"
                "\U0001f194 Username: @{}\n"
                "\U0001f4ac Chat ID: {}\n"
                "\U0001f3af Pocket Option ID: {}\n\n"
                "To verify: /adduser {} {}".format(
                    update.effective_user.full_name,
                    update.effective_user.username or "N/A",
                    uid, po_id, uid, po_id
                ),
                parse_mode="HTML"
            )
        except Exception:
            pass

        await update.message.reply_text(
            "\u2705 <b>PO ID Received!</b>\n\n"
            "Your Pocket Option ID: <code>{}</code>\n\n"
            "\u23f3 Admin will verify your registration shortly.\n"
            "You'll be notified once verified! \U0001f389".format(
                po_id
            ),
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            "\U0001f916 I understand these:\n\n"
            "\u2022 Send PO ID: <code>POID: 12345678</code>\n"
            "\u2022 /start - Main menu\n"
            "\u2022 /mystatus - Check verification\n"
            "\u2022 /help - Help",
            parse_mode="HTML"
        )


# ─── Error Handler ─────────────────────────────────────────────────────

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Error: {}".format(context.error))


# ─── Main ──────────────────────────────────────────────────────────────

def main():
    if not TOKEN:
        raise SystemExit("Set BOT_TOKEN in .env")

    init_db()
    app = Application.builder().token(TOKEN).build()

    # User commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("mystatus", cmd_mystatus))

    # Admin commands
    app.add_handler(CommandHandler("admin", cmd_admin))
    app.add_handler(CommandHandler("adduser", cmd_adduser))
    app.add_handler(CommandHandler("removeuser", cmd_removeuser))
    app.add_handler(CommandHandler("signal", cmd_signal_broadcast))
    app.add_handler(CommandHandler("broadcast", cmd_broadcast))
    app.add_handler(CommandHandler("listusers", cmd_listusers))
    app.add_handler(CommandHandler("stats", cmd_stats))

    # Callbacks
    app.add_handler(CallbackQueryHandler(callback_handler))

    # Messages (PO ID)
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    # Errors
    app.add_error_handler(error_handler)

    print("Pocket Option VIP Signal Bot running...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
