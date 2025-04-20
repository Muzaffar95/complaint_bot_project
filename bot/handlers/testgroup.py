from telegram import Update
from telegram.ext import ContextTypes
import os
import logging

logger = logging.getLogger("bot.webhook")

async def test_group_notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    notify_chat_id = int(os.getenv("NOTIFY_CHAT_ID", "-1002602269591"))
    test_text = "🚨 ТЕСТ /testgroup — отправка сообщения в группу"

    logger.info("🧪 Команда /testgroup вызвана пользователем: %s", update.effective_user.id)
    logger.info("🔔 Отправка в chat_id = %s", notify_chat_id)

    try:
        response = await context.bot.send_message(
            chat_id=notify_chat_id,
            text=test_text
        )
        logger.info("📤 Ответ от Telegram: %s", response)
        await update.message.reply_text("✅ Сообщение отправлено в группу (проверь лог).")
    except Exception as e:
        logger.error("❌ Ошибка при отправке: %s", e)
        await update.message.reply_text(f"❌ Ошибка: {e}")

