import asyncio
from app.core.celery_app import app
from app.bot.alerts import send_alert
from app.parser.nvd import search_critical_cve
from app.parser.hackernews import fetch_dangerous_articles
from app.core.redis_client import is_cve_sent, mark_cve_sent
import html

@app.task
def check_all_sources():
    """Собирает данные со всех парсеров новостей (NVD, TheHackersNews)"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_async_check())

async def _async_check():
    # Данные от NVD
    cves = search_critical_cve()
    for cve in cves:
        cve_id = cve['cve_id']

        if await is_cve_sent(cve_id):
            print(f"⏭️ CVE {cve_id} уже отправлялась, пропускаем")
            continue
        
        msg = f"⚠️ Обнаружена критическая уязвимость в базе NVD\n\n"
        msg += f"📛 {cve['cve_id']}\n"
        msg += f"❗ CVSS: {cve['cvss']}\n"
        msg += f"🔗 {cve['link']}"
        await send_alert(msg)
        # Сохранение в кэш
        await mark_cve_sent(cve_id)
    
    # Данные от Hacker News
    articles = fetch_dangerous_articles()
    for article in articles:

        link = article['link']
        
        if await is_cve_sent(link):
            continue

        msg = f"⚠️ Опасная новость на Hacker News, просьба ознакомиться\n\n"
        msg += f"📌 {article['title']}\n"
        msg += f"🔗 {article['link']}"
        await send_alert(msg)
        # Сохранение в кэш
        await mark_cve_sent(link)