import asyncio
from app.core.celery_app import app
from app.bot.alerts import send_alert
from app.parser.nvd import search_critical_cve
from app.parser.hackernews import fetch_dangerous_articles
from app.parser.exploitdb import fetch_latest_exploits
from app.core.redis_client import is_cve_sent, mark_cve_sent
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.core.models import Threat, CVEDetails, ExploitDetails, SourceEnum
from datetime import datetime


async def save_threat_to_db(
    source: SourceEnum,
    title: str,
    link: str,
    published,
    details_data: dict # Платформа, CVSS, CVE в формате списка
):
    """
    Универсальная функция сохранения угрозы в БД.
    Проверяет link, создает Threat и дочернюю запись.
    """
    async with AsyncSessionLocal() as db:
        # Проверяет существование записи
        result = await db.execute(select(Threat).where(Threat.link == link))
        existing_threat = result.scalar_one_or_none()
        
        if existing_threat:
            return None
        
        # Создает родительскую запись Threat
        threat = Threat(
            source=source,
            title=title,
            link=link,
            published=published
        )
        db.add(threat)
        await db.flush()    # Генерация UUID
        
        # Создает дочернюю запись в зависимости от источника
        if source == SourceEnum.NVD:
            cve_detail = CVEDetails(
                id=threat.id, # Использует тот же UUID что и в Threat
                cve_id=details_data.get('cve_id'),
                cvss_score=details_data.get('cvss_score'),
                vector=details_data.get('vector')
            )
            db.add(cve_detail)
            
        elif source == SourceEnum.EXPLOIT_DB:
            exploit_detail = ExploitDetails(
                id=threat.id,
                platform=details_data.get('platform'),
                exploit_code_link=details_data.get('exploit_code_link')
            )
            db.add(exploit_detail)
            
        elif source == SourceEnum.HACKER_NEWS:
            # Для HackerNews пока нет отдельной таблицы деталей, просто Threat
            pass
        
        await db.commit()
        return threat


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
            continue
        
        msg = f"⚠️ Обнаружена критическая уязвимость в базе NVD\n\n"
        msg += f"📛 {cve['cve_id']}\n"
        msg += f"❗ CVSS: {cve['cvss']}\n"
        msg += f"🔗 {cve['link']}"
        await send_alert(msg)
        # Сохранение в кэш
        await mark_cve_sent(cve_id)

        await save_threat_to_db(
            source=SourceEnum.NVD,
            title=cve['cve_id'],
            link = cve['link'],
            published = datetime.now(),
            details_data={
                'cve_id': cve['cve_id'],
                'cvss_score': cve['cvss']
            }
        )
    
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

        await save_threat_to_db(
            source=SourceEnum.HACKER_NEWS,
            title=article['title'],
            link=article['link'],
            published=datetime.now(),
            details_data={}    # Деталей для HackersNews нету
        )
    
    # ExploitDB 
    exploits = fetch_latest_exploits()
    for exploit in exploits:
        # Использует title+link как уникальный ключ
        unique_id = f"exploit_{exploit['link'].split('/')[-1]}"
        
        if await is_cve_sent(unique_id):
            continue
        
        cvss_str = f"CVSS: {exploit['cvss']}" if exploit['cvss'] else "CVSS: N/A"
        msg = (f"☣️ Exploit-DB обнаружен новый эксплойт\n\n"
               f"📛 {exploit['title']}\n"
               f"💻 Платформа: {exploit['platform']}\n"
               f"❗ {cvss_str}\n"
               f"📅 {exploit['published']}\n"
               f"🔗 {exploit['link']}")
        await send_alert(msg)
        await mark_cve_sent(unique_id)

        await save_threat_to_db(
            source=SourceEnum.EXPLOIT_DB,
            title=exploit['title'],
            link=exploit['link'],
            published=exploit['published'],
            details_data={
                'platform': exploit['platform']
            }
        )