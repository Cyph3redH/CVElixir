from fastapi import FastAPI, Request, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.core.database import AsyncSessionLocal
from app.core.models import Threat, SourceEnum

# Настройка шаблонов
templates = Jinja2Templates(directory="app/templates")

# Создаем FastAPI приложение
app = FastAPI(title="Hate Threat Archive", version="1.0.0")

@app.get("/")
async def home(
    request: Request,
    source: str | None = Query(None, description="Фильтр по источнику")
):
    async with AsyncSessionLocal() as db:
        # Базовый запрос с подгрузкой дочерних таблиц
        query = select(Threat).options(
        selectinload(Threat.cve_details),
        selectinload(Threat.exploit_details)
        ).order_by(Threat.published.desc()).limit(100)
        
        # Фильтр по источнику (если передан)
        if source and source in [e.value for e in SourceEnum]:
            query = query.where(Threat.source == SourceEnum(source))
        
        # Сортировка: сначала новые
        query = query.order_by(Threat.published.desc()).limit(100)
        
        result = await db.execute(query)
        threats = result.scalars().all()
        
        # Считаем общее количество записей
        count_query = select(func.count()).select_from(Threat)
        if source and source in [e.value for e in SourceEnum]:
            count_query = count_query.where(Threat.source == SourceEnum(source))
        total_result = await db.execute(count_query)
        total = total_result.scalar()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "threats": threats,
        "total": total,
        "source": source
    })

@app.get("/health")
async def health():
    """Эндпоинт для проверки, что сервер жив."""
    return {"status": "ok"}