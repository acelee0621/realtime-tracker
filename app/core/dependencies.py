# app/core/dependencies.py
from __future__ import annotations
from typing import TYPE_CHECKING

from app.core.notifier import PostgresNotifier
from app.core.websocket import manager as ws_manager  # 仅用于类型标注

if TYPE_CHECKING:
    from asyncpg import Connection

# 可替换的依赖存根
notifier: PostgresNotifier | None = None
manager = ws_manager