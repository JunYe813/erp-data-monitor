-- =====================================================
-- ERP 数据同步监控系统 - 建表语句与样例数据
-- 数据库：PostgreSQL
-- =====================================================

-- 1. 同步日志表（核心表）
CREATE TABLE IF NOT EXISTS sync_logs (
    order_id VARCHAR(50) PRIMARY KEY,           -- 订单号
    source_system VARCHAR(20) NOT NULL,      -- 源系统：jushuitan/kingdee
    target_system VARCHAR(20) NOT NULL,      -- 目标系统：jushuitan/kingdee
    status VARCHAR(10) NOT NULL DEFAULT '待处理',  -- 状态：成功/失败/待处理
    error_type VARCHAR(50),                  -- 错误类型
    error_message TEXT,                      -- 错误详情
    amount DECIMAL(12, 2),                   -- 订单金额
    customer_name VARCHAR(100),              -- 客户名称
    retry_count INTEGER DEFAULT 0,           -- 重试次数
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- 更新时间
);

-- 创建索引（优化查询性能）
CREATE INDEX idx_sync_logs_order_id ON sync_logs(order_id);
CREATE INDEX idx_sync_logs_status ON sync_logs(status);
CREATE INDEX idx_sync_logs_created_at ON sync_logs(created_at);
CREATE INDEX idx_sync_logs_error_type ON sync_logs(error_type);

-- 2. 订单主表（可选，用于关联查询）
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) UNIQUE NOT NULL,    -- 订单号
    customer_name VARCHAR(100),              -- 客户名称
    customer_code VARCHAR(50),               -- 客户编码
    amount DECIMAL(12, 2) NOT NULL,          -- 订单金额
    order_date DATE,                         -- 订单日期
    status VARCHAR(20) DEFAULT '待处理',      -- 订单状态
    source_system VARCHAR(20),               -- 来源系统
    remark TEXT,                             -- 备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_order_id ON orders(order_id);
CREATE INDEX idx_orders_status ON orders(status);

-- =====================================================
-- 插入样例数据
-- =====================================================

-- 插入同步日志数据（30条，包含各种状态和错误类型）
INSERT INTO sync_logs (order_id, source_system, target_system, status, error_type, error_message, amount, customer_name, retry_count, created_at) VALUES

-- 成功的订单（10条）
('ORD-20260601-001', 'jushuitan', 'kingdee', '成功', NULL, NULL, 1250.00, '上海贸易有限公司', 0, '2026-06-22 08:15:00'),
('ORD-20260601-002', 'jushuitan', 'kingdee', '成功', NULL, NULL, 3680.50, '北京科技有限公司', 0, '2026-06-22 08:20:00'),
('ORD-20260601-003', 'kingdee', 'jushuitan', '成功', NULL, NULL, 890.00, '广州贸易商行', 0, '2026-06-22 08:25:00'),
('ORD-20260601-004', 'jushuitan', 'kingdee', '成功', NULL, NULL, 5420.00, '深圳电子科技', 0, '2026-06-22 09:00:00'),
('ORD-20260601-005', 'jushuitan', 'kingdee', '成功', NULL, NULL, 2150.75, '杭州网络有限公司', 0, '2026-06-22 09:10:00'),
('ORD-20260601-006', 'kingdee', 'jushuitan', '成功', NULL, NULL, 4300.00, '南京软件科技', 0, '2026-06-22 09:15:00'),
('ORD-20260601-007', 'jushuitan', 'kingdee', '成功', NULL, NULL, 1680.00, '成都商贸有限公司', 0, '2026-06-22 09:30:00'),
('ORD-20260601-008', 'jushuitan', 'kingdee', '成功', NULL, NULL, 920.50, '武汉信息技术公司', 0, '2026-06-22 10:00:00'),
('ORD-20260601-009', 'kingdee', 'jushuitan', '成功', NULL, NULL, 7650.00, '重庆进出口贸易', 0, '2026-06-22 10:15:00'),
('ORD-20260601-010', 'jushuitan', 'kingdee', '成功', NULL, NULL, 3100.25, '天津制造有限公司', 0, '2026-06-22 10:30:00'),

-- 失败的订单 - 金额不匹配（5条）
('ORD-20260601-011', 'jushuitan', 'kingdee', '失败', '金额不匹配', '源系统金额(1250.00)与目标系统金额(1200.00)不一致', 1250.00, '上海贸易有限公司', 2, '2026-06-22 11:00:00'),
('ORD-20260601-012', 'jushuitan', 'kingdee', '失败', '金额不匹配', '源系统金额(3680.50)与目标系统金额(3680.00)不一致', 3680.50, '北京科技有限公司', 1, '2026-06-22 11:10:00'),
('ORD-20260601-013', 'kingdee', 'jushuitan', '失败', '金额不匹配', '源系统金额(890.00)与目标系统金额(850.00)不一致', 890.00, '广州贸易商行', 3, '2026-06-22 11:15:00'),
('ORD-20260601-014', 'jushuitan', 'kingdee', '失败', '金额不匹配', '源系统金额(5420.00)与目标系统金额(5400.00)不一致', 5420.00, '深圳电子科技', 1, '2026-06-22 11:20:00'),
('ORD-20260601-015', 'jushuitan', 'kingdee', '失败', '金额不匹配', '源系统金额(2150.75)与目标系统金额(2150.00)不一致', 2150.75, '杭州网络有限公司', 2, '2026-06-22 11:25:00'),

-- 失败的订单 - 客户不存在（4条）
('ORD-20260601-016', 'jushuitan', 'kingdee', '失败', '客户不存在', '客户编码[KH-001]在金蝶系统中不存在', 4300.00, '南京软件科技', 1, '2026-06-22 11:30:00'),
('ORD-20260601-017', 'jushuitan', 'kingdee', '失败', '客户不存在', '客户名称[成都商贸有限公司]匹配失败，找到多个相似客户', 1680.00, '成都商贸有限公司', 2, '2026-06-22 11:35:00'),
('ORD-20260601-018', 'kingdee', 'jushuitan', '失败', '客户不存在', '客户[JST-CUST-005]在聚水潭中未找到', 920.50, '武汉信息技术公司', 1, '2026-06-22 11:40:00'),
('ORD-20260601-019', 'jushuitan', 'kingdee', '失败', '客户不存在', '客户编码为空，无法匹配', 7650.00, '重庆进出口贸易', 3, '2026-06-22 11:45:00'),

-- 失败的订单 - 商品编码错误（3条）
('ORD-20260601-020', 'jushuitan', 'kingdee', '失败', '商品编码错误', '商品[SKU-001]在金蝶中不存在，映射关系未配置', 3100.25, '天津制造有限公司', 1, '2026-06-22 12:00:00'),
('ORD-20260601-021', 'jushuitan', 'kingdee', '失败', '商品编码错误', '商品[SKU-002]已停用，无法同步', 1850.00, '上海贸易有限公司', 2, '2026-06-22 12:10:00'),
('ORD-20260601-022', 'kingdee', 'jushuitan', '失败', '商品编码错误', '商品[ITEM-003]的规格型号不匹配', 4200.00, '北京科技有限公司', 1, '2026-06-22 12:15:00'),

-- 失败的订单 - 接口超时（3条）
('ORD-20260601-023', 'jushuitan', 'kingdee', '失败', '接口超时', '调用金蝶接口超时，响应时间超过30秒', 2500.00, '广州贸易商行', 1, '2026-06-22 14:00:00'),
('ORD-20260601-024', 'kingdee', 'jushuitan', '失败', '接口超时', '聚水潭API返回504 Gateway Timeout', 6800.00, '深圳电子科技', 2, '2026-06-22 14:15:00'),
('ORD-20260601-025', 'jushuitan', 'kingdee', '失败', '接口超时', '网络连接超时，请检查网络状态', 1200.00, '杭州网络有限公司', 1, '2026-06-22 14:30:00'),

-- 失败的订单 - 数据格式错误（2条）
('ORD-20260601-026', 'jushuitan', 'kingdee', '失败', '数据格式错误', '日期格式不正确：2026/06/22，期望：2026-06-22', 3500.00, '南京软件科技', 1, '2026-06-22 15:00:00'),
('ORD-20260601-027', 'jushuitan', 'kingdee', '失败', '数据格式错误', '金额字段包含非数字字符：1,250.00', 1250.00, '成都商贸有限公司', 2, '2026-06-22 15:15:00'),

-- 待处理的订单（3条）
('ORD-20260601-028', 'jushuitan', 'kingdee', '待处理', NULL, NULL, 4800.00, '武汉信息技术公司', 0, '2026-06-22 16:00:00'),
('ORD-20260601-029', 'kingdee', 'jushuitan', '待处理', NULL, NULL, 2100.50, '重庆进出口贸易', 0, '2026-06-22 16:15:00'),
('ORD-20260601-030', 'jushuitan', 'kingdee', '待处理', NULL, NULL, 5600.00, '天津制造有限公司', 0, '2026-06-22 16:30:00');


-- =====================================================
-- 查询验证语句
-- =====================================================

-- 查看各状态数量
SELECT status, COUNT(*) as 数量
FROM sync_logs
GROUP BY status;

-- 查看各错误类型数量
SELECT error_type, COUNT(*) as 数量
FROM sync_logs
WHERE error_type IS NOT NULL
GROUP BY error_type
ORDER BY 数量 DESC;

-- 查看最近的异常订单
SELECT
    order_id as 订单号,
    source_system as 源系统,
    target_system as 目标系统,
    status as 状态,
    error_type as 错误类型,
    error_message as 错误详情,
    amount as 金额,
    customer_name as 客户名称,
    retry_count as 重试次数,
    created_at as 创建时间
FROM sync_logs
WHERE status IN ('失败', '待处理')
ORDER BY created_at DESC;
