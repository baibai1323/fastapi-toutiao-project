import os
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from dotenv import load_dotenv

# 加载 .env（如果已经在外层加载过，这行可以省略，但多加载一次也没问题）
load_dotenv()

ASYNC_DATABASE_URL = os.getenv("DATABASE_URL")

if not ASYNC_DATABASE_URL:
    raise ValueError("未找到 DATABASE_URL 环境变量")

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
