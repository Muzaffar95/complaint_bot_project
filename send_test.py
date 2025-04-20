import asyncio
from telegram import Bot

BOT_TOKEN = "7380342391:AAFXE-_2DDt0LiOSgWZrM4vGLQ48FuzdPyM"
CHAT_ID = "-1002602269591"

async def main():
    bot = Bot(BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text="✅ Тестовое сообщение из send_test.py")

asyncio.run(main())

