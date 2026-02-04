from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from pydantic import BaseModel
from fastapi.responses import StreamingResponse # 🆕 新增: 用于文件下载
from io import BytesIO                          # 🆕 新增: 内存文件操作
import pandas as pd                             # 🆕 新增: 处理 Excel
from datetime import datetime                   # 🆕 新增:用于文件名时间戳

# 引入你的依赖
from app.core.database import get_db
from app.models.production_log import ProductionLog
from app.schemas.production import ProductionLogCreate

router = APIRouter()

# --- 定义响应模型 (保持不变) ---
class ProductionLogRead(BaseModel):
    id: int
    line_id: str
    device_id: str
    created_at: Any  
    payload: Dict[str, Any]

    class Config:
        from_attributes = True

# --- 接口 1: 上传数据 (保持不变) ---
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
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

# --- 接口 2: 获取列表 (保持不变) ---
@router.get("/list", response_model=List[ProductionLogRead])
async def get_logs(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    query = select(ProductionLog).order_by(ProductionLog.id.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()
    return logs

# --- 🆕 接口 3: Excel 导出 (新增) ---
@router.get("/export")
async def export_data(db: AsyncSession = Depends(get_db)):
    """
    导出所有生产数据为 Excel 文件 (Stream 流式下载)
    """
    try:
        print("🔍 开始执行导出任务...")
        
        # 1. 查询所有数据 (按时间倒序)
        stmt = select(ProductionLog).order_by(ProductionLog.id.desc())
        result = await db.execute(stmt)
        logs = result.scalars().all()
        
        if not logs:
            raise HTTPException(status_code=404, detail="当前没有数据可导出")

        # 2. 数据清洗 (JSON 转 表格)
        data_list = []
        for log in logs:
            # 基础字段
            row = {
                "流水号 (ID)": log.id,
                "产线编号": log.line_id,
                "设备ID": log.device_id,
                "操作员": log.operator_id,
                "入库时间": log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else "",
            }
            
            # 💡 核心逻辑：把 JSON payload 摊平
            # 注意：这里适配了你的字段名 `log.payload`
            if log.payload and isinstance(log.payload, dict):
                row.update(log.payload)
            
            data_list.append(row)

        # 3. 生成 Pandas DataFrame
        df = pd.DataFrame(data_list)

        # 4. 写入内存 Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='生产记录')
        
        output.seek(0) # 指针归位

        # 5. 生成文件名
        filename = f"MiniMES_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # 6. 返回流式响应
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
        return StreamingResponse(
            output, 
            headers=headers, 
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        print(f"❌ 导出失败: {e}")
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")