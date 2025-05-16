import asyncio
from logging.config import fileConfig
from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection
from app.database import Base
from app.models.user import User
from app.core.config import get_db_url

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

DATABASE_URL = get_db_url()

target_metadata = Base.metadata

async_engine = create_async_engine(DATABASE_URL, future=True)

def do_run_migrations(connection: AsyncConnection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    async with async_engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

if context.is_offline_mode():
    context.configure(url=DATABASE_URL, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()
else:
    asyncio.run(run_migrations_online())