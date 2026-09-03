from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from erp_api.models.database import engine, Base
from erp_api.routers import saleout


# 创建数据库表
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ERP 数据查询服务",
    description="提供订单的 RESTful 查询接口",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(saleout.router)

@app.get("/health", summary="健康检查")
def health():
    return {"status": "healthy"}

# 启动服务器
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)