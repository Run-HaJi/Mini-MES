from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import engine, Base
from app.api import production  # <--- 1. 导入新写的路由模块

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ 数据库表已就绪！")
    yield
    print("🛑 服务已关闭")

app = FastAPI(title="Mini-MES Backend", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. 注册路由 ---
# 这样 /api/v1/data/upload 就生效了
app.include_router(production.router, prefix="/api/v1/data", tags=["Data"])

@app.get("/")
def read_root():
    return {"status": "online", "msg": "Mini-MES Backend is running!"}

