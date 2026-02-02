from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. 数据库连接地址
# 格式: mysql+驱动://用户名:密码@服务名:端口/库名
# 注意: 在 Docker 内部，主机名写 'db' (docker-compose里的服务名)，而不是 localhost
DATABASE_URL = "mysql+asyncmy://root:root@db:3306/minimes_db"

# 2. 创建异步引擎
engine = create_async_engine(DATABASE_URL, echo=True) # echo=True 会打印 SQL 语句，方便调试

# 3. 创建会话工厂 (以后每次操作数据库都找它)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 4. 模型基类 (所有表的祖宗)
Base = declarative_base()

# 5. 获取数据库会话的依赖函数
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session