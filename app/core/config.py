# /app/core/config.py
from functools import lru_cache
from typing import Literal

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置（支持 PostgreSQL 和 SQLite，含连接池设置）"""

    APP_NAME: str = "FastAPI Realtime Tracker"
    DEBUG: bool = False

    # 数据库类型
    DB_TYPE: Literal["postgres", "sqlite"] = "postgres"

    # PostgreSQL 配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "fastapi_users"

    # 连接池配置（仅 PostgreSQL 有效）
    # --- 必选参数：中等并发常用 ---
    POOL_SIZE: int = 20  # 连接池基础大小，低：- 高：+
    MAX_OVERFLOW: int = 10  # 超出 pool_size 的最大连接数，低：- 高：+
    POOL_TIMEOUT: int = 30  # 获取连接超时时间（秒），低：+ 高：-
    POOL_PRE_PING: bool = True  # 取连接前是否检查可用性，低：False 高：True

    # --- 可选调优参数（高级场景） ---
    POOL_RECYCLE: int = (
        3600  # 连接最大存活时间（秒），低：+ 高：-，避免长连接被数据库踢掉
    )
    # POOL_USE_LIFO: bool = False # 连接池取连接顺序，False=FIFO（默认），True=LIFO 可提高高并发命中率
    ECHO: bool = False  # 是否打印 SQL，开发可打开，生产关闭

    # SQLite 配置
    SQLITE_PATH: str = "./db.sqlite3"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        if self.DB_TYPE == "postgres":
            return (
                f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
        elif self.DB_TYPE == "sqlite":
            return f"sqlite+aiosqlite:///{self.SQLITE_PATH}"
        else:
            raise ValueError(f"Unsupported DB_TYPE: {self.DB_TYPE}")

    @computed_field
    @property
    def SQLALCHEMY_ENGINE_OPTIONS(self) -> dict:
        """统一封装 engine options，供 create_async_engine 使用"""
        if self.DB_TYPE == "postgres":
            return {
                "pool_size": self.POOL_SIZE,
                "max_overflow": self.MAX_OVERFLOW,
                "pool_timeout": self.POOL_TIMEOUT,
                "pool_recycle": self.POOL_RECYCLE,
                # "pool_use_lifo": self.POOL_USE_LIFO,
                "echo": self.ECHO,
            }
        # SQLite 不支持 pool 设置，返回最小参数
        return {"echo": self.ECHO}

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
