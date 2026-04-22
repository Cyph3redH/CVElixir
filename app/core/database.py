from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",    # PostgreSQL
)

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """
    async with - завершит сессию после конца функции
    AsyncSessionLocal() - Создает новую сессию (подключение к БД)
    as session - кладёт сессию в переменную
    """
    async with AsyncSessionLocal() as session:
        yield session   # Тут программа зависнет пока другой код будет работать с БД