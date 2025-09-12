# app/core/notifier.py
from __future__ import annotations

import asyncio
import json
from typing import Callable, Coroutine, Any

import asyncpg
from loguru import logger

# 精确类型：协程函数
Handler = Callable[[dict], Coroutine[Any, Any, None]]

class PostgresNotifier:
    def __init__(self, dsn: str, *, channel: str = "inventory_channel") -> None:
        self.dsn: str = dsn
        self.channel: str = channel
        self._conn: asyncpg.Connection | None = None
        self._handlers: list[Handler] = []
        self._task: asyncio.Task[None] | None = None

    # ---------- 对外 API ----------
    def add_handler(self, handler: Handler) -> None:
        self._handlers.append(handler)

    async def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._listen_forever())

    async def stop(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._conn:
            await self._conn.close()
            self._conn = None
        logger.info("PostgresNotifier 已停止")

    # ---------- 内部 ----------
    async def _listen_forever(self) -> None:
        while True:
            try:
                self._conn = await asyncpg.connect(self.dsn)
                # 类型守卫：保证下面不是 None
                conn = self._conn
                if conn is None:
                    raise RuntimeError("连接未建立")
                await conn.add_listener(self.channel, self._raw_callback)
                logger.info(f"开始监听 PostgreSQL channel: {self.channel}")
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                logger.info("监听任务被取消，退出重连循环")
                break
            except Exception as e:
                logger.exception(f"连接丢失，5 秒后重连: {e}")
                await asyncio.sleep(5)
            finally:
                if self._conn:
                    await self._conn.close()
                    self._conn = None

    def _raw_callback(
        self, conn: asyncpg.Connection, pid: int, channel: str, payload: str
    ) -> None:
        try:
            data = json.loads(payload)
        except Exception as e:
            logger.warning(f"非法 JSON: {e}")
            return
        # handler 签名是 Coroutine → create_task 合法
        for handler in self._handlers:
            asyncio.create_task(handler(data))