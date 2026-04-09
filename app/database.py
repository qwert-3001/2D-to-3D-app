from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import decl_base, sessionmaker

engine = create_async_engine("sqlite+aiosqlite:///./test.db")
async_session = async_sessionmaker(engine, expire_on_commit=False)

