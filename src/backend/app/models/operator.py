from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Operator(Base):
    __tablename__ = "operators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)        # 姓名
    code = Column(String(20), unique=True, index=True) # 工号 (唯一)
    role = Column(String(20), default="worker")      # 角色: worker/admin
    is_active = Column(Boolean, default=True)        # 是否在职
    created_at = Column(DateTime(timezone=True), server_default=func.now())