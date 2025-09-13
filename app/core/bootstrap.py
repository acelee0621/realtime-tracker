# app/core/bootstrap.py
import asyncio
import pathlib
import asyncpg
from loguru import logger

SQL_FILE = pathlib.Path(__file__).resolve().parent.parent / "setup_database.sql"

async def bootstrap_db(dsn: str):
    """项目第一次启动时调用，保证表、函数、触发器全到位。"""
    sql = SQL_FILE.read_text(encoding="utf-8")

    conn: asyncpg.Connection = await asyncpg.connect(dsn)
    try:
        # 在一个事务里整包执行
        async with conn.transaction():
            await conn.execute(sql)
        logger.info("✅ 数据库初始化完成（表 / 触发器 / 函数）")
    except asyncpg.exceptions.DuplicateObjectError:
        # 重复跑也不炸
        logger.info("✅ 数据库结构已存在，跳过初始化")
    finally:
        await conn.close()

# 本地脚本直接 `python -m db.bootstrap` 就能跑
if __name__ == "__main__":
    dsn = "postgresql://postgres:postgres@localhost:5432/tracker"
    asyncio.run(bootstrap_db(dsn))