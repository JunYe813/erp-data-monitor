import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()  # 从 .env 读取数据库配置，密钥不入库

# 数据库连接（DB_URL 在 .env 中配置；CHANGE_ME 仅为占位示例）
engine = create_engine(os.getenv("DB_URL", "postgresql+psycopg2://postgres:CHANGE_ME@localhost:5432/erp"))

st.set_page_config(page_title="ERP 数据同步监控",layout="wide")
st.title("📊 聚水潭 ↔ 金蝶 数据同步监控")

# ============ 侧边栏筛选 ============
st.sidebar.header("筛选条件")
date_range = st.sidebar.date_input(
   "时间范围",
   value = (datetime.now() - timedelta(days=7),datetime.now()) 
)
# 状态选择
status_filter = st.sidebar.multiselect(
    "同步状态",
    ["成功","失败","待处理","重新同步"],
    default=["失败","待处理","重新同步"]
)

# 【新增】订单号搜索
order_keyword = st.sidebar.text_input("🔍 按订单号搜索（支持模糊匹配）", placeholder="输入订单号...")

# 数据展示 - 一次查询 + 缓存
@st.cache_data(ttl=60)
def get_dashboard_stats():
    """获取看板统计数据，缓存 60 秒"""
    query = """
        SELECT
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE status = '成功') as success,
            COUNT(*) FILTER (WHERE status = '失败') as failed,
            COUNT(*) FILTER (WHERE status = '待处理') as pending,
            COUNT(*) FILTER (WHERE status = '重新同步') as retrying
        FROM sync_logs
    """
    return pd.read_sql(query, engine).iloc[0]

stats = get_dashboard_stats()
col1,col2,col3,col4,col5 = st.columns(5)
with col1:
    st.metric("总同步数", stats["total"])
with col2:
    st.metric("成功", stats["success"])
with col3:
    st.metric("失败", stats["failed"], delta=f"-{stats['failed']}" if stats["failed"] > 0 else None)
with col4:
    st.metric("待处理", stats["pending"])
with col5:
    st.metric("重新同步", stats["retrying"])


# ============ 异常订单列表 ============
# st.subheader("异常订单列表")

querySql = """
    SELECT
        order_id,
        source_system,
        target_system,
        status,
        error_type,
        error_message,
        amount,
        created_at,
        retry_count
    FROM sync_logs
    WHERE created_at BETWEEN %s AND %s
    AND status = ANY(%s)
    ORDER BY created_at DESC
"""
df = pd.read_sql(querySql,engine,params=(date_range[0],date_range[1],status_filter))

# 【新增】按订单号模糊搜索
if order_keyword:
    df = df[df["order_id"].str.contains(order_keyword, case=False, na=False)]
# print(f"查询返回结果:{df.empty}")
# 无数据返回结果:Empty DataFrame
failedResults = df[df["status"] == "失败"]
# 错误类型统计cl
if not failedResults.empty:
    st.subheader("失败原因汇总")
    # print(f"查询的失败数据:{df[df["status"] == "失败"]}")
    error_counts = df[df["status"] == "失败"]["error_type"].value_counts()
    st.bar_chart(error_counts)
else:
    st.subheader("暂无失败数据")


# 显示表格
st.subheader("筛选数据结果（默认展示未成功数据）")

# 【新增】分页功能
PAGE_SIZE = 10
total_rows = len(df)
total_pages = max((total_rows + PAGE_SIZE - 1) // PAGE_SIZE, 1)

col_page1, col_page2, col_page3 = st.columns([1, 2, 1])
with col_page2:
    page = st.number_input("页码", min_value=1, max_value=total_pages, value=1, step=1)
start_idx = (page - 1) * PAGE_SIZE
end_idx = start_idx + PAGE_SIZE
df_page = df.iloc[start_idx:end_idx]

st.caption(f"📊 共 {total_rows} 条数据，第 {page}/{total_pages} 页，每页 {PAGE_SIZE} 条")

st.dataframe(
    df_page,
    width='stretch',
    column_config={
        "order_id": "订单号",
        "source_system": "源系统",
        "target_system": "目标系统",
        "status": "状态",
        "error_type": "错误类型",
        "error_message": "错误详情",
        "amount": "金额",
        "created_at": "同步时间",
        "retry_count": "重试次数",
    }
)

# 修改数据库字段重推数据
def tryRepushOrders (orderArr):
    orderStr = "'" + "','".join(orderArr) + "'"
    with engine.begin() as conn:
        updateResults = conn.execute(text(f"UPDATE sync_logs set status = '重新同步',updated_at = CURRENT_TIMESTAMP WHERE order_id in ({orderStr})"))
    return updateResults



# ============ 操作区 ============
st.subheader("批量操作")
col1,col2 = st.columns(2)
with col1:
    if st.button("🔄 重新同步选中订单", type="primary"):
        selected_orders = df[df["status"].isin(["失败", "待处理"])]["order_id"].tolist()
        if selected_orders:
            # 调用重新同步逻辑
            with st.spinner("重新同步"):
                result = tryRepushOrders(selected_orders)
                st.success(f"同步完成：影响行数:{result.rowcount}")
        else:
            st.warning("没有需要同步的订单")

with col2:
    if st.button("📥 导出异常订单"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="下载 CSV",
            data=csv,
            file_name=f"异常订单_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# 导入excel文件
# 定义一个通用的导入数据库的函数
def import_data_topg(target_tabel,target_column,target_values,conflict_column,update_column):
    # 数据较多的话要分批
    batch_size = 100 if len(target_values) > 100 else len(target_values)
    target_df = pd.DataFrame(target_values)
    rows = target_df.to_dict(orient="records")
    # print(len(rows))
    val_column = ', '.join(f'"{col}"' for col in target_column)
    conflict_column = ', '.join(f'"{col}"'for col in conflict_column)
    update_set = ", ".join(f'"{x}" = EXCLUDED."{x}"' for x in update_column)
    val_str = ", ".join(f':{x}' for x in target_column)
    # 构建sql语句
    sql = f"""
                INSERT INTO {target_tabel} ({val_column})
                VALUES ({val_str})
                ON CONFLICT ({conflict_column})
                DO UPDATE SET {update_set}
            """
    success_count = 0
    progress_bar = st.progress(0, text="正在导入...")
    for i in range(0,len(rows),batch_size):
        batch = rows[i:i+batch_size]
        with engine.begin() as conn:
            executeResults = conn.execute(text(sql),batch)
            success_count += executeResults.rowcount
        progress = success_count / len(rows)
        progress_bar.progress(progress, text=f"已插入 {success_count}/{len(rows)} 条")
    progress_bar.empty()
    st.success(f"✅ 导入完成，共插入 {success_count} 条数据，导入成功之后请手动删除文件可以继续导入")

        

st.subheader("导入出库单据（Excel文件）")
# col1 = st.columns(1)
# with col1:
uploaded_file = st.file_uploader("📊 导入excel文件",type=["xlsx","xls"])
if uploaded_file:
    df_import = pd.read_excel(uploaded_file)
    st.success(f"读取到{len(df_import)}条数据，并展示到界面，可以核对是否有问题，如果没问题直接点击导入数据库即可")
    st.dataframe(df_import)
    target_tabel = "saleout_json"
    conflict_key = ["IoId","SkuId"]
    if st.button("🚀 导入数据库", type="primary"):
        try:
            colums = df_import.columns.tolist()
            if "出库单号" in colums:
                # 定义出库map映射
                saleout_map = {
                    "出库单号": "IoId",
                    "内部订单号": "Oid",
                    "线上单号": "SoId",
                    "商品编码": "SkuId",
                    "推送时间": "PushTime",
                    "数量": "Qty",
                    "金额": "Amount"
                }
                # 拿到文字对应的数据库字段
                col_arr = [saleout_map.get(c,c) for c in colums]
                # 更新的冲突字段
                update_str = [saleout_map.get(c,c) for c in colums if saleout_map.get(c,c) not in conflict_key]
                # 带key的值
                df_import = df_import.rename(columns=saleout_map)
            # 调用通用的插入函数
            insertResult = import_data_topg(target_tabel,col_arr,df_import,conflict_key,update_str)
        except Exception as e:
            st.error(f"❌️ 导入失败:{e}")
