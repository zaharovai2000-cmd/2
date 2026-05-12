import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./flowers.db"
)

# echo=True выводит SQL-запросы в консоль при разработке
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("APP_ENV", "development") == "development",
    # Для SQLite: отключаем проверку потоков (нужно для async)
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей."""
    pass


async def get_db() -> AsyncSession:
    """
    Dependency для FastAPI.
    Открывает сессию БД на время запроса и гарантированно закрывает её.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_tables():
    """Создаёт все таблицы при старте приложения (если не существуют)."""
    async with engine.begin() as conn:
        # Импорт здесь, чтобы Base знала обо всех моделях
        from models.orm import Product, Order, Review  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)