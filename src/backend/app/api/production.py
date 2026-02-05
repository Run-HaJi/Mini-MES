from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from io import BytesIO
import pandas as pd
from datetime import datetime
import json
import base64

# 🔒 引入解密库
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from app.core.database import get_db
from app.models.production_log import ProductionLog
from app.schemas.production import ProductionLogCreate

router = APIRouter()

# ================= 配置区 (必须与 Client 端完全一致) =================
SECRET_KEY = b"MiniMES_2026_Ver0.4_Secure_Key!!" 
IV = b"MiniMES_IV_2026!"

# --- 辅助函数：解密 ---
def decrypt_payload(encrypted_base64_str: str) -> dict:
    try:
        # 1. Base64 解码 -> 得到加密的二进制字节
        ciphertext = base64.b64decode(encrypted_base64_str)
        
        # 2. 创建解密器
        cipher = AES.new(SECRET_KEY, AES.MODE_CBC, IV)
        
        # 3. 解密 + 去除填充 (Unpad)
        decrypted_bytes = unpad(cipher.decrypt(ciphertext), AES.block_size)
        
        # 4. 还原成 JSON 字符串 -> 字典
        json_str = decrypted_bytes.decode('utf-8')
        return json.loads(json_str)
    except Exception as e:
        print(f"❌ 解密失败详情: {e}")
        raise ValueError("Decryption failed")

# --- 定义响应模型 ---
class ProductionLogRead(BaseModel):
    id: int
    line_id: str
    device_id: str
    created_at: Any  
    payload: Dict[str, Any]

    class Config:
        from_attributes = True

# --- 接口 1: 上传数据 (已升级 v0.4 安全版) ---
@router.post("/upload", response_model=dict)
async def upload_data(data: ProductionLogCreate, db: AsyncSession = Depends(get_db)):
    """
    接收加密的 Payload -> 解密 -> 存入数据库
    """
    try:
        # 1. 🕵️‍♂️ 执行解密
        print(f"🔒 收到密文: {data.payload[:15]}...")
        try:
            decrypted_payload = decrypt_payload(data.payload)
            print(f"🔓 解密成功: {decrypted_payload}")
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid Encrypted Payload")

        # 2. 注入时间戳 (把外层的时间戳放进 payload 里方便查询)
        final_payload = decrypted_payload.copy()
        final_payload["edge_timestamp"] = data.timestamp

        # 3. 创建数据库对象 (存进去的是明文 JSON，方便之后查报表)
        new_log = ProductionLog(
            line_id=data.line_id,
            device_id=data.device_id,
            operator_id=data.operator_id,
            source_type=data.source_type,
            payload=final_payload 
        )

        # 4. 写入
        db.add(new_log)
        await db.commit()
        await db.refresh(new_log)

        return {
            "code": 200, 
            "msg": "success", 
            "data": {"record_id": new_log.id}
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ 系统错误: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

# --- 接口 2: 获取列表 (保持不变) ---
@router.get("/list", response_model=List[ProductionLogRead])
async def get_logs(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    query = select(ProductionLog).order_by(ProductionLog.id.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()
    return logs

# --- 接口 3: Excel 导出 (保持不变) ---
@router.get("/export")
async def export_data(db: AsyncSession = Depends(get_db)):
    # ... (这一大段保持你之前的 Excel 导出代码即可，不用动) ...
    # 为了节省篇幅，这里省略，请务必保留原有的 export 代码！
    # 如果你不想手动复制，我可以把完整的发给你，但只要你不删原来的就行。
    
    # 临时占位，请确保你的 export 代码还在！
    try:
        # 复制你之前的逻辑
        stmt = select(ProductionLog).order_by(ProductionLog.id.desc())
        result = await db.execute(stmt)
        logs = result.scalars().all()
        
        if not logs:
            raise HTTPException(status_code=404, detail="No data")

        data_list = []
        for log in logs:
            row = {
                "ID": log.id,
                "Line": log.line_id,
                "Device": log.device_id,
                "Time": log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else "",
            }
            if log.payload and isinstance(log.payload, dict):
                row.update(log.payload)
            data_list.append(row)

        df = pd.DataFrame(data_list)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        filename = f"MiniMES_Export_{datetime.now().strftime('%Y%m%d')}.xlsx"
        headers = {'Content-Disposition': f'attachment; filename="{filename}"'}
        return StreamingResponse(output, headers=headers, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))