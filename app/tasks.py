import asyncio
from app.core.celery_app import app
from app.bot.alerts import send_alert
from app.parser.nvd import search_critical_cve
from app.parser.hackernews import fetch_dangerous_articles


@app.task
def check_all_sources():
    """Собирает данные со всех парсеров новостей (NVD, TheHackersNews)"""
    loop = asyncio.get_event_loop
    loop.run_until_complite(_async_check())

async def _async_check():
    # Данные от NVD
    cves = search_critical_cve()
    for cve in cves:
        msg = f"⚠️ Обнаружена критическая уязвимость в базе NVD</b>\n\n"
        msg += f"📛 <b>{cve['cve_id']}</b>\n"
        msg += f"❗ CVSS: {cve['cvss']}\n"
        msg += f"🔗 {cve['link']}"
        await send_alert(msg)
    
    # Данные от Hacker News
    articles = fetch_dangerous_articles()
    for article in articles:
        msg = f"⚠️ <b>Опасная новость на Hacker News, просьба ознакомиться</b>\n\n"
        msg += f"📌 {article['title']}\n"
        msg += f"🔗 {article['link']}"
        await send_alert(msg)