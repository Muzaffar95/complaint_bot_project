import asyncio
import uvicorn
from telegram import Bot
from bot.config import BOT_TOKEN, WEBHOOK_URL
from bot.webhook import app

async def set_webhook():
    bot = Bot(BOT_TOKEN)
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook set to {WEBHOOK_URL}")

if __name__ == "__main__":
    asyncio.run(set_webhook())
