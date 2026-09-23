from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(str(settings.DATABASE_URL))
AsyncSession = async_sessionmaker(bind=engine, expire_on_commit=False, autoFLush=False)

async def get_db():
    async with AsyncSession() as db:
        yield db

    
