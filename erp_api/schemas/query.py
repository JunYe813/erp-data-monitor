from pydantic import BaseModel, Field,ConfigDict
from typing import Optional, List
from datetime import datetime

# 定义接口请求参数
class SaleoutQuery(BaseModel):
    # 出库查询参数
    page_index: int = Field(1,ge=1,description="页数")
    page_size: int = Field(1,ge=1,le=100,description="每页数量")
    start_time: Optional[datetime] = Field(None,description="开始时间")
    end_time: Optional[datetime] = Field(None,description="结束时间")
    status: Optional[str] = Field(None,description="状态")
    io_id: Optional[list[str]] = Field(None,description="出库单号")
    o_id: Optional[list[str]] = Field(None,description="内部订单号")

# 接口响应
class SaleoutResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    io_id:str
    o_id:str
    so_id:str
    sku_id:str
    push_time:datetime
    qty:int
    amount:float
    db_create_time:datetime
    db_update_time:datetime

# 分页响应
class PageResponse(BaseModel):
    data: List[SaleoutResponse]
    total:int
    page_size:int
    page_index:int