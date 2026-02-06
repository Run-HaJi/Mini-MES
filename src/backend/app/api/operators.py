from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.models.operator import Operator
from app.schemas.operator import OperatorCreate, OperatorRead, OperatorUpdate

router = APIRouter()

# 1. 获取列表
@router.get("/", response_model=List[OperatorRead])
async def read_operators(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Operator).offset(skip).limit(limit))
    return result.scalars().all()

# 2. 新增工人
@router.post("/", response_model=OperatorRead)
async def create_operator(operator: OperatorCreate, db: AsyncSession = Depends(get_db)):
    # 检查工号是否重复
    result = await db.execute(select(Operator).where(Operator.code == operator.code))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="工号已存在")
    
    new_op = Operator(**operator.dict())
    db.add(new_op)
    await db.commit()
    await db.refresh(new_op)
    return new_op

# 3. 修改信息
@router.put("/{operator_id}", response_model=OperatorRead)
async def update_operator(operator_id: int, operator: OperatorUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Operator).where(Operator.id == operator_id))
    db_operator = result.scalars().first()
    
    if not db_operator:
        raise HTTPException(status_code=404, detail="工人不存在")
    
    # 动态更新字段
    update_data = operator.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_operator, key, value)
        
    await db.commit()
    await db.refresh(db_operator)
    return db_operator

# 4. 删除工人
@router.delete("/{operator_id}")
async def delete_operator(operator_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Operator).where(Operator.id == operator_id))
    db_operator = result.scalars().first()
    
    if not db_operator:
        raise HTTPException(status_code=404, detail="工人不存在")
    
    await db.delete(db_operator)
    await db.commit()
    return {"msg": "Deleted successfully"}