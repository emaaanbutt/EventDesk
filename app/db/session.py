from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(str(settings.database_url))
AsyncSession = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

async def get_db():
    async with AsyncSession() as db:
        yield db

    
