from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, tuple_
from typing import Optional
from datetime import datetime
import json

from ..models.database import get_db,SaleOut
from ..schemas.query import SaleoutQuery,SaleoutResponse,PageResponse

router = APIRouter(prefix = "/api/saleout",tags = ["出库查询"])

@router.get("/",response_model=PageResponse,summary="查询出库单据列表")
def list_orders(
    page_index: int = Query(1,ge=1,description="页数"),
    page_size: int = Query(1,ge=1,le=100,description="每页数量"),
    start_time: Optional[datetime] = Query(None,description="开始时间"),
    end_time: Optional[datetime] = Query(None,description="结束时间"),
    status: Optional[str] = Query(None,description="状态"),
    io_id: Optional[str] = Query(None,description="出库单号，支持JSON数组格式如 [\"1800327\",\"1800323\"]"),
    o_id: Optional[str] = Query(None,description="内部订单号，支持JSON数组格式"),
    db: Session = Depends(get_db)
):
    # 查询订单列表，支持：
    # - 订单号模糊查询
    # - 按状态、来源系统筛选
    # - 日期范围筛选
    # - 分页返回
    query = db.query(SaleOut)

    # 动态筛选条件
    if io_id:
        # 支持 JSON 数组格式: ["1800327","1800323"]
        try:
            io_id_list = json.loads(io_id) if io_id.startswith('[') else [io_id]
        except:
            io_id_list = [io_id]
        query = query.filter(SaleOut.io_id.in_(io_id_list))
    if o_id:
        # 支持 JSON 数组格式
        try:
            o_id_list = json.loads(o_id) if o_id.startswith('[') else [o_id]
        except:
            o_id_list = [o_id]
        query = query.filter(SaleOut.o_id.in_(o_id_list))
    if status:
        query = query.filter(SaleOut.status == status)
    if start_time:
        query = query.filter(SaleOut.push_time > start_time)
    if end_time:
        query = query.filter(SaleOut.push_time < end_time)

    # 统计总数
    total = query.count()

    # 分页
    orders = query.order_by(SaleOut.push_time.desc()) \
                        .offset((page_index -1) * page_size) \
                        .limit(page_size)\
                        .all()
    return PageResponse(data = orders,total=total,page_size=page_size,page_index=page_index)


@router.get("/stats", summary="订单统计")
def order_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    订单统计数据：
    - 总订单数、总金额
    - 按状态分组统计
    - 按来源系统分组统计
    """
    query = db.query(SaleOut)

    if start_date:
        query = query.filter(SaleOut.push_time >= start_date)
    if end_date:
        query = query.filter(SaleOut.push_time <= end_date)

    # 总体统计
    total_orders = query.count()
    total_amount = query.with_entities(func.sum(SaleOut.amount)).scalar() or 0

    # 按状态分组（按 io_id + sku_id 统计唯一记录数）
    status_stats = query.with_entities(
        SaleOut.status,
        func.count(tuple_(SaleOut.io_id, SaleOut.sku_id)),
        func.sum(SaleOut.amount)
    ).group_by(SaleOut.status).all()

    return {
        "total_orders": total_orders,
        "total_amount": round(total_amount, 2),
        "by_status": [
            {"status": s[0], "count": s[1], "amount": round(s[2] or 0, 2)}
            for s in status_stats
        ]
    }