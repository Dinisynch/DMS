from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import get_db_url
from sqlalchemy.ext.asyncio import AsyncAttrs


engine = create_async_engine(get_db_url(), echo=True)

new_async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with new_async_session() as session:
        yield session

class Base(AsyncAttrs, DeclarativeBase):
    pass