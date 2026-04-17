from confluent_kafka import Consumer
import json
import os
from app.core.redis_client import is_cve_sent, mark_cve_sent
from bot.alerts import send_alert
import asyncio

consumer = Consumer({
    'bootstrap.servers': os.getenv('KAFKA_BROKER', 'kafka:9092'),
    'group.id': 'cvelixir-consumer',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe(['raw-security-events'])

async def start_telegram_consumer():
    """Слушает Kafka, форматирует и отправляет в Telegram."""
    
    while True:
        msg = consumer.poll(1.0)  # Ждём сообщение 1 секунду
        
        if msg is None:
            continue  # Если нет сообщений то ждём дальше
        
        if msg.error():
            continue
        
        # Декодируем сообщение
        event = json.loads(msg.value().decode('utf-8'))
        source = event.get('source')

        if source == 'nvd':
            unique_id = event['cve_id']
        elif source == 'hackernews':
            unique_id = event['link']  # Ссылка — уникальный идентификатор
        elif source == 'exploitdb':
            unique_id = event['link']  # Ссылка на эксплойт
        else:
            continue

        if await is_cve_sent(unique_id):
            continue

        if source == 'nvd':
            msg = f"⚠️ Обнаружена критическая уязвимость в базе NVD\n\n"
            msg += f"📛 {event['cve_id']}\n"
            msg += f"❗ CVSS: {event['cvss']}\n"
            msg += f"🔗 {event['link']}"
        elif source == 'hackersnews':
            msg = f"⚠️ Опасная новость на Hacker News, просьба ознакомиться\n\n"
            msg += f"📌 {event['title']}\n"
            msg += f"🔗 {event['link']}"
        elif source == 'exploitdb':
            platform = event.get('platform', 'Unknown')
            cvss = event.get('cvss')

            if platform == "Windows":
                message = f"☣️ Обнаружен Windows Exploit\n\n"
            elif platform == "Linux":
                message = f"☣️ Обнаружен Linux Exploit\n\n"
            elif platform == "Multiple":
                message = f"☣️ Обнаружен Multiple Exploit\n\n"
            else:
                message = f"☣️ Обнаружен Exploit\n\n"
            
            message += f"👁️‍🗨️ {event['title']}\n"
            message += f"🌐 Платформа: {platform}\n"
            if cvss:
                message += f"❗ CVSS: {cvss}\n"
            message += f"🔗 {event['link']}"
        
        await send_alert(message)
        
        # Сохраняем в Redis, чтобы не спамить
        await mark_cve_sent(unique_id)

if __name__ == "__main__":
    asyncio.run(start_telegram_consumer())