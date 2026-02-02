from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class ProductionLog(Base):
    # 表名
    __tablename__ = "production_logs"

    # --- 核心索引字段 (用于快速查询) ---
    id = Column(Integer, primary_key=True, index=True)
    
    # 产线编号 (Line-01 ~ Line-10)
    line_id = Column(String(50), index=True, nullable=False)
    
    # 设备ID (IPC-01)
    device_id = Column(String(50), nullable=False)
    
    # 操作员ID (OP-9527)
    operator_id = Column(String(50), index=True, default="DEFAULT")
    
    # 数据来源 (AUTO / MANUAL)
    source_type = Column(String(20), default="AUTO")
    
    # --- 业务数据包 (JSON 混合存储) ---
    # 关键点：SKU、批次、重量等具体业务字段，全部扔进这个 JSON 里
    # 好处：甲方以后要加字段，咱们不用改表结构！
    payload = Column(JSON, nullable=False)
    
    # --- 系统字段 ---
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    is_deleted = Column(Boolean, default=False)