from fastapi import FastAPI, Query
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi.staticfiles import StaticFiles
from app.core.database import AsyncSessionLocal
from app.core.models import Threat, SourceEnum
from app.core.database import engine
from app.core import models

app = FastAPI(title="Hate Threat Archive API", version="1.0.0")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
async def init_db():
    """Создает таблицы при запуске"""
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

@app.get("/ui")
async def ui():
    """Отдаёт красивую страницу"""
    from fastapi.responses import FileResponse
    return FileResponse("app/static/index.html")

@app.get("/")
async def home(source: str | None = Query(None)):
    async with AsyncSessionLocal() as db:
        query = select(Threat).options(
            selectinload(Threat.cve_details),
            selectinload(Threat.exploit_details)
        )
        if source and source in [e.value for e in SourceEnum]:
            query = query.where(Threat.source == SourceEnum(source))
        
        query = query.order_by(Threat.published.desc()).limit(100)
        result = await db.execute(query)
        threats = result.scalars().all()
        
        # Превращаем в словари для JSON
        data = []
        for t in threats:
            item = {
                "id": str(t.id),
                "source": t.source.value,
                "title": t.title,
                "link": t.link,
                "published": t.published.isoformat() if t.published else None,
            }
            if t.cve_details:
                item["cvss_score"] = t.cve_details.cvss_score
                item["cve_id"] = t.cve_details.cve_id
            if t.exploit_details:
                item["platform"] = t.exploit_details.platform
            data.append(item)
        
        count_result = await db.execute(select(func.count()).select_from(Threat))
        total = count_result.scalar()
        
    return {"total": total, "threats": data}

@app.get("/health")
async def health():
    return {"status": "ok"}