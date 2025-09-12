# app/main.py
from pathlib import Path
from fastapi import Depends, FastAPI, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.config import settings
from app.core.database import get_db
from app.lifespan import lifespan
from app.routers.router import router


app = FastAPI(
    title=settings.APP_NAME,
    description="FastAPI 数据库实时跟踪示例",
    lifespan=lifespan,
)


# 路由引入
app.include_router(router)


@app.get("/health")
async def health_check(response: Response):
    response.status_code = 200
    return {"status": "ok 👍 "}


@app.get("/db-check")
async def db_check(db: AsyncSession = Depends(get_db)):
    """
    一个简单的端点，用于检查数据库连接是否正常工作。
    """
    try:
        # 执行一个简单的查询来验证连接
        result = await db.execute(text("SELECT 1"))
        if result.scalar_one() == 1:
            return {"status": "ok", "message": "数据库连接成功！"}
    except Exception as e:
        return {"status": "error", "message": f"数据库连接失败: {e}"}


# 项目根目录 /static
STATIC_DIR = Path(__file__).parent.parent / "static"

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
