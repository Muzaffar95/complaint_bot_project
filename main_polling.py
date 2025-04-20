from telegram.ext import ApplicationBuilder
from bot.config import BOT_TOKEN
from bot.main_handlers import setup_handlers

import asyncio

application = ApplicationBuilder().token(BOT_TOKEN).build()
setup_handlers(application)

print("✅ Бот запущен в режиме polling")

# Прямой вызов, без run/asyncio — работает в macOS и IDE
application.run_polling()
