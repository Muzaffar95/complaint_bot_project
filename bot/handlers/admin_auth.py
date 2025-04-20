from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CommandHandler
from bot.config import ADMINS, WEBHOOK_HOST, JWT_SECRET
from jose import jwt
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
JWT_ALGORITHM = "HS256"

async def auth_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    logger.info(f"[adminpanel] user_id={user_id}, ADMINS={ADMINS}")

    if user_id not in ADMINS:
        await update.message.reply_text("⛔️ У вас нет доступа к админ-панели.")
        return

    expire = datetime.utcnow() + timedelta(hours=2)
    token = jwt.encode({"sub": user_id, "exp": expire}, JWT_SECRET, algorithm=JWT_ALGORITHM)

    url = f"{WEBHOOK_HOST}/html?token={token}"
    keyboard = [[InlineKeyboardButton("🔐 Войти в админ-панель", url=url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Нажмите кнопку ниже, чтобы войти в админ-панель:", reply_markup=reply_markup)


async def chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    msg = (
        f"🧾 Ваш Telegram ID: <code>{user.id}</code>\n"
        f"🆔 Chat ID: <code>{chat.id}</code>\n"
        f"👥 Тип чата: <code>{chat.type}</code>\n"
        f"📛 Название чата: <code>{chat.title or '—'}</code>"
    )

    await update.message.reply_text(msg, parse_mode="HTML")

