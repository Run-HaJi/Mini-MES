from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.production_log import ProductionLog
# 记得复用之前的 Operator 依赖，用来校验工号是否存在

router = APIRouter()

# 定义手动录入的数据模型
class ManualEntrySchema(BaseModel):
    line_id: str
    operator_id: str  # 👈 核心：必须要知道是谁录的
    device_id: str    # 哪个工位/设备
    sku: str
    weight: float
    batch_id: str

@router.post("/submit")
async def submit_manual_entry(entry: ManualEntrySchema, db: AsyncSession = Depends(get_db)):
    # 1. (可选) 校验 operator_id 是否有效，这里先略过，假设前端已校验
    
    # 2. 构造日志，显式标记 source="MANUAL"
    new_log = ProductionLog(
        line_id=entry.line_id,
        device_id=entry.device_id,
        content={
            "sku": entry.sku,
            "weight": entry.weight,
            "batch": entry.batch_id,
            "operator_id": entry.operator_id, # 👈 记录人
            "source": "MANUAL",               # 👈 记录来源 
            "timestamp": datetime.now().timestamp()
        }
    )
    
    db.add(new_log)
    await db.commit()
    await db.refresh(new_log)
    
    return {"msg": "Manual entry success", "log_id": new_log.id}