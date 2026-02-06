from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 基础字段
class OperatorBase(BaseModel):
    name: str
    code: str
    role: Optional[str] = "worker"
    is_active: Optional[bool] = True

# 创建时需要的字段
class OperatorCreate(OperatorBase):
    pass

# 更新时需要的字段 (所有字段可选)
class OperatorUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

# 返回给前端的字段
class OperatorRead(OperatorBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True