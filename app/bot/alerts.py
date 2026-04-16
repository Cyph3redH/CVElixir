import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def send_alert(message: str):
    """Отправляет сообщение в Telegram."""
    if not TOKEN or not CHAT_ID:
        print("❌ Токен или Chat ID не заданы в .env")
        return
    
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='HTML')

# Тест
if __name__ == "__main__":
    asyncio.run(send_alert("🚨 <b>CVElixir запущен!</b>"))