from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder
from bot.config import BOT_TOKEN, WEBHOOK_PATH, WEBHOOK_URL
from bot.main_handlers import setup_handlers
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
application = ApplicationBuilder().token(BOT_TOKEN).build()
setup_handlers(application)

@app.post(WEBHOOK_PATH)
async def webhook(request: Request):
    json_data = await request.json()
    logger.info(f"📥 Incoming update: {json_data}")
    update = Update.de_json(json_data, application.bot)
    await application.update_queue.put(update)
    return {"status": "ok"}

@app.on_event("startup")
async def on_startup():
    await application.initialize()
    await application.start()  # <--- это добавляем
    bot = Bot(BOT_TOKEN)
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook set to {WEBHOOK_URL}")

