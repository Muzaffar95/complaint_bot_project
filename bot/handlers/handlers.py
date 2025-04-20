
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
)
from bot.db import SessionLocal
from bot.models import Complaint
from bot.pdf_generator import generate_pdf
from bot.handlers.admin_auth import auth_panel, chat_id
from bot.handlers.testgroup import test_group_notify
import os

FIO, TEL, COMMENT = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать! Чтобы оставить жалобу, используйте команду /report.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Команды:\n/report - подать жалобу\n/FIO - ФИО\n/tel - номер телефона\n/comment - комментарий\n/accept - подтвердить"
)

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите ваше ФИО:")
    return FIO

async def fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fio"] = update.message.text
    await update.message.reply_text("Введите номер телефона:")
    return TEL

async def tel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tel"] = update.message.text
    await update.message.reply_text("Введите текст жалобы:")
    return COMMENT

async def comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["comment"] = update.message.text
    await update.message.reply_text("Для отправки жалобы введите /accept")
    return ConversationHandler.END

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
    session.refresh(complaint)
    session.close()

    pdf_file = generate_pdf(fio, tel, comment)
    await update.message.reply_text(f"PDF с жалобой сохранён: {pdf_file}")

    notify_chat_id = int(os.getenv("NOTIFY_CHAT_ID", "-1002602269591"))
    pdf_name = f"{fio.replace(' ', '_')}_{complaint.created_at.strftime('%Y%m%d%H%M')}.pdf"
    pdf_url = f"{os.getenv('WEBHOOK_HOST', 'https://mdmgasn.uz')}/pdfs/{pdf_name}"

    print("🧾 complaint ID:", complaint.id)
    print("📢 notify_chat_id:", notify_chat_id)
    print("🔗 PDF link:", pdf_url)

    try:
        await context.bot.send_message(
            chat_id=notify_chat_id,
            text=f"📢 Новая жалоба\n"
                 f"👤 ФИО: {fio}\n"
                 f"📞 Тел: {tel}\n"
                 f"📝 Комментарий: {comment}\n"
                 f"📎 PDF: {pdf_url}"
        )
    except Exception as e:
        print("❌ Ошибка при отправке уведомления:", e)

    await update.message.reply_text("Жалоба принята. Спасибо!")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Жалоба отменена.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def setup_handlers(app):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("report", report)],
        states={
            FIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, fio)],
            TEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, tel)],
            COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, comment)],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("accept", accept)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("accept", accept))
    app.add_handler(CommandHandler("adminpanel", auth_panel))
    app.add_handler(CommandHandler("id", chat_id))
    app.add_handler(CommandHandler("testgroup", test_group_notify))
    app.add_handler(conv_handler)
