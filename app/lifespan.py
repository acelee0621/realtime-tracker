# app/lifespan.py
from typing import TypedDict
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)

from app.core.config import get_settings, settings
from app.core.notifier import PostgresNotifier
from app.core import dependencies as deps
from app.core.database import (
    setup_database_connection,
    close_database_connection,
    create_db_and_tables,
)


class AppState(TypedDict):
    """
    定义应用生命周期中共享状态的结构。
    这为类型检查器和编辑器提供了明确的类型信息。
    """

    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[AppState]:
    # -------- 启动 --------
    get_settings()
    engine, session_factory = await setup_database_connection()
    logger.info("🚀 应用启动，数据库已就绪。")
    await create_db_and_tables(engine)

    global notifier
    notifier = PostgresNotifier(
        settings.DATABASE_URL.replace("+asyncpg", ""),
        channel="inventory_channel",
    )
    notifier.add_handler(lambda data: deps.manager.broadcast(data))
    await notifier.start()  # 非阻塞

    # 注入到依赖层，以便其他模块使用（可选）
    deps.notifier = notifier

    # 更加类型安全的写法
    yield AppState(
        engine=engine,
        session_factory=session_factory,
    )

    # -------- 关闭 --------
    if notifier:
        await notifier.stop()
    await close_database_connection(engine)
    logger.info("应用关闭，资源已释放。")
