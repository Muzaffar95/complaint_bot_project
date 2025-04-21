from telegram import (
    Update, ReplyKeyboardMarkup, ReplyKeyboardRemove,
    InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, Bot
)
from telegram.ext import (
    CommandHandler, MessageHandler, filters, ContextTypes,
    ConversationHandler, CallbackQueryHandler
)
from bot.db import SessionLocal
from bot.models import Complaint
from bot.pdf_generator import generate_pdf
from bot.config import ADMINS, BOT_TOKEN, NOTIFY_CHAT_ID
from bot.handlers.admin_auth import auth_panel

CHOICE_TYPE, FIO, TEL, COMMENT = range(4)

# /start — с кнопкой "Отправить номер"
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_btn = KeyboardButton("📱 Отправить номер телефона", request_contact=True)
    markup = ReplyKeyboardMarkup([[contact_btn]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Пожалуйста, отправьте ваш номер телефона:", reply_markup=markup)

# Обработка контактных данных
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    if contact and contact.phone_number:
        context.user_data["tel"] = contact.phone_number
        # Меню
        keyboard = [
            ["📨 Подать жалобу"],
            ["ℹ️ Помощь", "🆔 Мой ID"],
            ["🔐 Админка"] if str(update.effective_user.id) in ADMINS else []
        ]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Номер сохранён. Выберите действие:", reply_markup=markup)

# Кнопки → Команды
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📨 Подать жалобу":
        return await report(update, context)
    elif text == "ℹ️ Помощь":
        return await help_command(update, context)
    elif text == "🆔 Мой ID":
        return await get_id(update, context)
    elif text == "🔐 Админка":
        return await auth_panel(update, context)

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Вы можете:\n📨 Подать жалобу\n🆔 Узнать свой ID\n🔐 Войти в админку (если доступ есть)"
    )

# /report → выбор типа жалобы
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🤐 Анонимно", callback_data="anon")],
        [InlineKeyboardButton("👤 Публично", callback_data="public")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Как вы хотите оставить жалобу?", reply_markup=markup)
    return CHOICE_TYPE

# Выбор аноним/публично
async def choose_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Выбор типа жалобы принят")
    query = update.callback_query
    await query.answer()

    context.user_data["type"] = "Анонимная" if query.data == "anon" else "Публичная"

    if query.data == "anon":
        context.user_data["fio"] = "Аноним"
        context.user_data["tel"] = "Скрыт"
        await query.message.reply_text("Введите текст жалобы:")
        return COMMENT
    else:
        await query.message.reply_text("Введите ваше ФИО:")
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
    complaint_type = context.user_data.get("type", "Публичная")

    session = SessionLocal()
    complaint = Complaint(
        user_id=user_id,
        full_name=fio,
        phone=tel,
        comment=comment,
        complaint_type=complaint_type
    )
    session.add(complaint)
    session.commit()
    session.close()

    # Генерация PDF
    pdf_file = generate_pdf(fio, tel, comment, complaint_type)
    pdf_file = pdf_file.lstrip("./")
    pdf_url = f"https://mdmgasn.uz/{pdf_file}"

    # Telegram уведомление
    bot = Bot(BOT_TOKEN)
    await bot.send_message(
        chat_id=NOTIFY_CHAT_ID,
        text=(
            f"📬 *Новая жалоба!*\n\n"
            f"*Тип:* {complaint_type}\n"
            f"*ФИО:* {fio}\n"
            f"*Телефон:* {tel}\n"
            f"*Комментарий:* {comment}\n"
            f"[📎 PDF]({pdf_url})"
        ),
        parse_mode="Markdown"
    )

    await update.message.reply_text("Жалоба принята. Спасибо!")

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Жалоба отменена.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# /id
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 Ваш Telegram ID: {update.effective_user.id}")

# Регистрация всех обработчиков
def setup_handlers(app):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("report", report)],
        states={
            CHOICE_TYPE: [CallbackQueryHandler(choose_type)],
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
    app.add_handler(CommandHandler("adminpanel", auth_panel))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(conv_handler)

# from telegram import Update, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, Bot
# from telegram.ext import (
#     CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
# )
# from bot.db import SessionLocal
# from bot.models import Complaint
# from bot.pdf_generator import generate_pdf
# from bot.config import ADMINS, BOT_TOKEN, NOTIFY_CHAT_ID
# from bot.handlers.admin_auth import auth_panel  # ← добавлено
#
# FIO, TEL, COMMENT = range(3)
#
#
# # /start
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("Добро пожаловать! Чтобы оставить жалобу, используйте команду /report.")
#
#
# # /help
# async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text(
#         "Команды:\n/report - подать жалобу\n/FIO - ФИО\n/tel - номер телефона\n/comment - комментарий\n/accept - подтвердить"
#     )
#
#
# # /report
# async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("Введите ваше ФИО:")
#     return FIO
#
#
# # ФИО
# async def fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     context.user_data["fio"] = update.message.text
#     await update.message.reply_text("Введите номер телефона:")
#     return TEL
#
#
# # Телефон
# async def tel(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     context.user_data["tel"] = update.message.text
#     await update.message.reply_text("Введите текст жалобы:")
#     return COMMENT
#
#
# # Комментарий
# async def comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     context.user_data["comment"] = update.message.text
#     await update.message.reply_text("Для отправки жалобы введите /accept")
#     return ConversationHandler.END
#
#
# # /accept
# async def accept(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = update.message.from_user.id
#     fio = context.user_data.get("fio", "Не указано")
#     tel = context.user_data.get("tel", "Не указано")
#     comment = context.user_data.get("comment", "Не указано")
#
#     session = SessionLocal()
#     complaint = Complaint(
#         user_id=user_id,
#         full_name=fio,
#         phone=tel,
#         comment=comment
#     )
#     session.add(complaint)
#     session.commit()
#     session.close()
#
#     # Генерация PDF
#     # pdf_file = generate_pdf(fio, tel, comment)
#     # pdf_url = f"https://mdmgasn.uz/{pdf_file}"
#
#     # Уведомление в Telegram-группу
#     # bot = Bot(BOT_TOKEN)
#     # await bot.send_message(
#     #    chat_id=NOTIFY_CHAT_ID,
#     #    text=(
#     #        f"<b>📬 Новая жалоба!</b>\n\n"
#     #        f"<b>ФИО:</b> {fio}\n"
#     #        f"<b>Телефон:</b> {tel}\n"
#     #        f"<b>Комментарий:</b> {comment}\n"
#     #        f"<a href='{pdf_url}'>📎 Открыть PDF</a>"
#     #    ),
#     #    parse_mode="HTML"
#     # )
#     # Генерация PDF
#     pdf_file = generate_pdf(fio, tel, comment)
#
#     # Очистим путь от "./"
#     pdf_file = pdf_file.lstrip("./")
#
#     # Сформируем абсолютную ссылку
#     pdf_url = f"https://mdmgasn.uz/{pdf_file}"
#
#     # Уведомление в Telegram-группу
#     bot = Bot(BOT_TOKEN)
#     await bot.send_message(
#         chat_id=NOTIFY_CHAT_ID,
#         text=(
#             f"📬 *Новая жалоба!*\n\n"
#             f"*ФИО:* {fio}\n"
#             f"*Телефон:* {tel}\n"
#             f"*Комментарий:* {comment}\n"
#             f"[📎 Открыть PDF]({pdf_url})"
#         ),
#         parse_mode="Markdown"
#     )
#
#     await update.message.reply_text(f"PDF с жалобой сохранён: {pdf_file}")
#     await update.message.reply_text("Жалоба принята. Спасибо!")
#
#
# # Отмена
# async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("Жалоба отменена.", reply_markup=ReplyKeyboardRemove())
#     return ConversationHandler.END
#
#
# # Найти Telegram ID
# # async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
# #     await update.message.reply_text(f"🆔 Ваш Telegram ID: {update.effective_user.id}")
#
#
# # /id — выдать ID пользователя и чата
# async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = update.effective_user.id
#     chat_id = update.effective_chat.id
#     await update.message.reply_text(
#         f"👤 Ваш Telegram ID: `{user_id}`\n💬 Chat ID: `{chat_id}`",
#         parse_mode="Markdown"
#     )
#
#
# def setup_handlers(app):
#     conv_handler = ConversationHandler(
#         entry_points=[CommandHandler("report", report)],
#         states={
#             FIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, fio)],
#             TEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, tel)],
#             COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, comment)],
#         },
#         fallbacks=[CommandHandler("cancel", cancel)]
#     )
#
#     app.add_handler(CommandHandler("start", start))
#     app.add_handler(CommandHandler("help", help_command))
#     app.add_handler(CommandHandler("accept", accept))
#     app.add_handler(CommandHandler("id", get_id))
#     app.add_handler(CommandHandler("adminpanel", auth_panel))  # ← добавлено
#     app.add_handler(conv_handler)
