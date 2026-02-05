from pydantic import BaseModel
from typing import Dict, Any, Optional

# 👇 修改这里
class ProductionLogCreate(BaseModel):
    line_id: str
    device_id: str
    operator_id: str
    source_type: str
    timestamp: str  # 边缘端发过来的是字符串时间
    # payload: Dict[str, Any]  <-- 删掉或注释掉这行
    payload: str             # <-- 改成这样！现在它是密文传输