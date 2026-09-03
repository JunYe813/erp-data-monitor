import os
from dotenv import load_dotenv
from sqlalchemy import Column, String, Float, Numeric, DateTime, Integer, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

load_dotenv()  # 从 .env 读取数据库配置，密钥不入库

Base = declarative_base()

# 建立数据库链接（DB_URL 在 .env 中配置；CHANGE_ME 仅为占位示例）
DATABASE_URL = os.getenv("DB_URL", "postgresql+psycopg2://postgres:CHANGE_ME@localhost:5432/erp")
# 创建引擎
engine = create_engine(DATABASE_URL)
# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 依赖注入：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# 定义数据库字段
class SaleOut(Base):
    """销售出库表"""
    __tablename__ = "saleout_json"

    io_id = Column("IoId",String(100), primary_key=True,comment="出库单号")
    o_id = Column("Oid",String(100),comment="内部订单号")
    so_id = Column("SoId",String(100), comment="线上单号")
    sku_id = Column("SkuId",String(100), comment="商品编码")
    push_time = Column("PushTime",DateTime,comment="推送时间")
    qty = Column("Qty",Integer, comment="数量")
    amount = Column("Amount",Numeric(10,2), comment="金额")
    status = Column("Status",String(20), comment="状态")
    db_create_time = Column("DbCreateTime",DateTime, comment="创建时间")
    db_update_time = Column("DbUpdateTime",DateTime, comment="更新时间")