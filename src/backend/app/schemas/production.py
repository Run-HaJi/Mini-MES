from pydantic import BaseModel
from typing import Dict, Any

class ProductionLogCreate(BaseModel):
    line_id: str
    device_id: str
    operator_id: str = "DEFAULT"
    source_type: str = "AUTO"
    timestamp: int
    payload: Dict[str, Any]