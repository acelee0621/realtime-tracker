# app/models/mixin.py
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings


class DateTimeMixin:
    if settings.DB_TYPE == "postgres":
        # PostgreSQL 原生支持 now() 和 onupdate
        created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
            index=True,
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )
    else:
        # SQLite: 使用 Python 层默认值模拟
        created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            default=datetime.now(timezone.utc),  # 插入时用应用层时间
            nullable=False,
            index=True,
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            default=datetime.now(timezone.utc),
            onupdate=datetime.now(timezone.utc),  # 更新时用应用层时间
            nullable=False,
        )