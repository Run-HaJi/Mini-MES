from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
import hashlib  # 👈 引入 Python 自带标准库，绝对可靠

# ================= 配置区 =================
SECRET_KEY = "MiniMES_Admin_Secret_Key_2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# ================= 简易哈希工具 (无依赖版) =================
def fake_hash_password(password: str) -> str:
    """用 SHA256 模拟哈希 (仅限开发环境使用，生产环境请换回 bcrypt)"""
    return hashlib.sha256(password.encode()).hexdigest()

# 模拟数据库
FAKE_ADMIN_DB = {
    "admin": {
        "username": "admin",
        # 这里存的是 "admin123" 的 SHA256 值，你可以去网上搜在线生成器验证
        "password_hash": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
    }
}

# ================= 模型定义 =================
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# ================= 核心逻辑 =================
def verify_password(plain_password, hashed_password):
    """直接对比 SHA256 值"""
    return fake_hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ================= 接口 =================
@router.post("/login", response_model=Token)
async def login_for_access_token(user_data: UserLogin):
    user = FAKE_ADMIN_DB.get(user_data.username)
    if not user:
        raise HTTPException(status_code=401, detail="用户名不存在")
    
    # 验证密码
    if not verify_password(user_data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="密码错误")
    
    # 生成 Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # ... (这部分保持不变，或者直接复制下面)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username