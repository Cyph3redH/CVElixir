import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv
import random

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MY_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # личный ID
HACKER_IMAGE_URL=["https://images.interestingengineering.com/img/iea/QjOdpBaKOd/jbs-restoring-systems-with-backup-vulnerabilities-remain.jpg",
                  "https://i.ytimg.com/vi/nz7eU-Zcwbo/maxresdefault.jpg",
                  "https://cdn.mos.cms.futurecdn.net/WhwNyWzQHzVnY49UeT8UsS.jpg",
                  "https://img.freepik.com/premium-photo/global-cybersecurity-threat-map-red-blue-world-map-displaying-cyber-threats_706399-10977.jpg?w=2000",
                  ]

def get_random_image():
    """Возвращает случайную ссылку на картинку"""
    return random.choice(HACKER_IMAGE_URL)

# БЕЛЫЙ СПИСОК
ALLOWED_USERS = [int(MY_CHAT_ID)]  # Можно добавить ещё ID через запятую

async def send_alert(message: str, target_chat_id: int = None):
    """
    Отправляет сообщение. Если target_chat_id не указан — шлёт всем в ALLOWED_USERS.
    Если указан — проверяет, есть ли он в белом списке.
    """
    if not TOKEN:
        print("Токен не задан в .env")
        return
    
    bot = Bot(token=TOKEN)

    image_url = get_random_image()
    
    # Если цель не указана — шлём всем разрешённым
    if target_chat_id is None:
        for chat_id in ALLOWED_USERS:
            await bot.send_photo(
                chat_id=chat_id,
                photo=image_url,
                caption=message,
                parse_mode='HTML'
            )
        return
    
    # Если цель указана — проверяем, есть ли она в белом списке
    if target_chat_id not in ALLOWED_USERS:
        print(f"Доступ запрещён для {target_chat_id}")
        return
    
    await bot.send_photo(
        chat_id=target_chat_id,
        photo=image_url,
        caption=message,
        parse_mode='HTML'
    )

# Тест
if __name__ == "__main__":
    # asyncio.run(send_alert("<b>CVElixir запущен!</b>"))
    
    # Бесконечное ожидание (чтобы контейнер не падал)
    import time
    while True:
        time.sleep(3600)