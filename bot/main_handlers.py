from telegram import Update, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import (
    CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
)
from bot.db import SessionLocal
from bot.models import Complaint
from bot.pdf_generator import generate_pdf
from bot.config import ADMINS, BOT_TOKEN, NOTIFY_CHAT_ID
from bot.handlers.admin_auth import auth_panel  # ← добавлено

FIO, TEL, COMMENT = range(3)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать! Чтобы оставить жалобу, используйте команду /report.")

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Команды:\n/report - подать жалобу\n/FIO - ФИО\n/tel - номер телефона\n/comment - комментарий\n/accept - подтвердить"
    )

# /report
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите ваше ФИО:")
    return FIO

# ФИО
async def fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fio"] = update.message.text
    await update.message.reply_text("Введите номер телефона:")
    return TEL

# Телефон
async def tel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tel"] = update.message.text
    await update.message.reply_text("Введите текст жалобы:")
    return COMMENT

# Комментарий
async def comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["comment"] = update.message.text
    await update.message.reply_text("Для отправки жалобы введите /accept")
    return ConversationHandler.END

# /accept
async def accept(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    fio = context.user_data.get("fio", "Не указано")
    tel = context.user_data.get("tel", "Не указано")
    comment = context.user_data.get("comment", "Не указано")

    session = SessionLocal()
    complaint = Complaint(
        user_id=user_id,
        full_name=fio,
        phone=tel,
        comment=comment
    )
    session.add(complaint)
    session.commit()
    session.close()

    # Генерация PDF
    #pdf_file = generate_pdf(fio, tel, comment)
    #pdf_url = f"https://mdmgasn.uz/{pdf_file}"
    
    # Уведомление в Telegram-группу
    #bot = Bot(BOT_TOKEN)
    #await bot.send_message(
    #    chat_id=NOTIFY_CHAT_ID,
    #    text=(
    #        f"<b>📬 Новая жалоба!</b>\n\n"
    #        f"<b>ФИО:</b> {fio}\n"
    #        f"<b>Телефон:</b> {tel}\n"
    #        f"<b>Комментарий:</b> {comment}\n"
    #        f"<a href='{pdf_url}'>📎 Открыть PDF</a>"
    #    ),
    #    parse_mode="HTML"
    #)
    # Генерация PDF
    pdf_file = generate_pdf(fio, tel, comment)

    # Очистим путь от "./"
    pdf_file = pdf_file.lstrip("./")

    # Сформируем абсолютную ссылку
    pdf_url = f"https://mdmgasn.uz/{pdf_file}"

    # Уведомление в Telegram-группу
    bot = Bot(BOT_TOKEN)
    await bot.send_message(
        chat_id=NOTIFY_CHAT_ID,
        text=(
            f"📬 *Новая жалоба!*\n\n"
            f"*ФИО:* {fio}\n"
            f"*Телефон:* {tel}\n"
            f"*Комментарий:* {comment}\n"
            f"[📎 Открыть PDF]({pdf_url})"
        ),
        parse_mode="Markdown"
)



    await update.message.reply_text(f"PDF с жалобой сохранён: {pdf_file}")
    await update.message.reply_text("Жалоба принята. Спасибо!")

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Жалоба отменена.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Найти Telegram ID
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 Ваш Telegram ID: {update.effective_user.id}")

def setup_handlers(app):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("report", report)],
        states={
            FIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, fio)],
            TEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, tel)],
            COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, comment)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("accept", accept))
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(CommandHandler("adminpanel", auth_panel))  # ← добавлено
    app.add_handler(conv_handler)

