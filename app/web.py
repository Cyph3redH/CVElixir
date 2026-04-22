from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.database import engine
from app.core import models

app = FastAPI(title="Hate Threat Archive API", version="1.0.0")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Создание таблиц при запуске
@app.on_event("startup")
async def init_db():
    """Создает таблицы при запуске"""
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

# Веб интерфейс
@app.get("/ui")
async def ui():
    """Отдаёт красивую страницу"""
    from fastapi.responses import FileResponse
    return FileResponse("app/static/index.html")