from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
# 👇哪怕你之前贴过，肯定也漏了这一行！
from typing import List, Dict, Any
# 👇还有这一行！
from pydantic import BaseModel

from app.core.database import get_db
from app.models.production_log import ProductionLog
# 确保这个文件 app/schemas/production.py 也是存在的
from app.schemas.production import ProductionLogCreate

router = APIRouter()

# --- 定义响应模型 (用于 GET 请求返回数据) ---
class ProductionLogRead(BaseModel):
    id: int
    line_id: str
    device_id: str
    created_at: Any  # 偷懒先用 Any
    payload: Dict[str, Any]

    class Config:
        from_attributes = True

# --- 接口 1: 上传数据 ---
@router.post("/upload", response_model=dict)
async def upload_data(data: ProductionLogCreate, db: AsyncSession = Depends(get_db)):
    try:
        # 1. 把边缘端时间戳塞进 payload
        final_payload = data.payload.copy()
        final_payload["edge_timestamp"] = data.timestamp

        # 2. 创建数据库对象
        new_log = ProductionLog(
            line_id=data.line_id,
            device_id=data.device_id,
            operator_id=data.operator_id,
            source_type=data.source_type,
            payload=final_payload
        )

        # 3. 写入
        db.add(new_log)
        await db.commit()
        await db.refresh(new_log)

        return {
            "code": 200, 
            "msg": "success", 
            "data": {"record_id": new_log.id}
        }
        
    except Exception as e:
        print(f"❌ 入库失败: {str(e)}")
        await db.rollback()
        return {"code": 500, "msg": f"Database Error: {str(e)}", "data": None}

# --- 接口 2: 获取列表 ---
@router.get("/list", response_model=List[ProductionLogRead])
async def get_logs(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    query = select(ProductionLog).order_by(ProductionLog.id.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()
    return logs