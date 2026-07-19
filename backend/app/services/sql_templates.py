"""
核心 SQL 模板：4 个高频分析场景的预定义 SQL。

供 LangChain Agent 和前端快捷面板使用。
所有 SQL 都使用命名参数（:param_name），调用方需用 SQLAlchemy text() 传参。
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.logging import get_logger

log = get_logger(__name__)


# ===== 1. 各工序良率 =====
SQL_YIELD_RATE_BY_PROCESS = text("""
SELECT
    process_code,
    process_name,
    SUM(total_qty)        AS total_qty,
    SUM(qualified_qty)    AS qualified_qty,
    ROUND(
        SUM(qualified_qty) * 100.0 / NULLIF(SUM(total_qty), 0),
        2
    ) AS yield_rate
FROM production_process
WHERE record_date BETWEEN :start_date AND :end_date
GROUP BY process_code, process_name
ORDER BY yield_rate DESC
""".strip())


# ===== 2. 不良数量 TOP N 产品 =====
SQL_TOP_DEFECT_PRODUCTS = text("""
SELECT
    p.product_code,
    p.product_name,
    p.category,
    SUM(d.defect_qty)    AS total_defect,
    COUNT(d.defect_id)   AS defect_count
FROM quality_defect d
JOIN dim_product p ON p.product_code = d.product_code
WHERE d.defect_date >= :start_date
GROUP BY p.product_code, p.product_name, p.category
ORDER BY total_defect DESC
LIMIT :top_n
""".strip())


# ===== 3. 设备停机率 =====
SQL_EQUIPMENT_DOWNTIME_RATE = text("""
SELECT
    e.equipment_code,
    e.equipment_name,
    e.equipment_type,
    e.line_code,
    COUNT(d.id)                AS downtime_count,
    SUM(d.downtime_minutes)    AS total_minutes,
    ROUND(
        SUM(d.downtime_minutes) * 100.0 / (24 * 60 * :days),
        2
    ) AS downtime_rate_pct
FROM equipment e
LEFT JOIN equipment_downtime d
    ON d.equipment_code = e.equipment_code
    AND d.downtime_date BETWEEN :start_date AND :end_date
GROUP BY e.equipment_code, e.equipment_name, e.equipment_type, e.line_code
HAVING COUNT(d.id) > 0
ORDER BY total_minutes DESC
""".strip())


# ===== 4. 各产线近 N 天产量趋势 =====
SQL_PRODUCTION_TREND_BY_LINE = text("""
SELECT
    w.line_code,
    l.line_name,
    p.record_date,
    SUM(p.total_qty)     AS total_qty,
    SUM(p.qualified_qty) AS qualified_qty,
    ROUND(
        SUM(p.qualified_qty) * 100.0 / NULLIF(SUM(p.total_qty), 0),
        2
    ) AS yield_rate
FROM production_process p
JOIN production_workorder w ON w.workorder_id = p.workorder_id
JOIN dim_line l ON l.line_code = w.line_code
WHERE p.record_date BETWEEN :start_date AND :end_date
GROUP BY w.line_code, l.line_name, p.record_date
ORDER BY p.record_date, w.line_code
""".strip())


# ===== 模板注册表 =====
SQL_TEMPLATES: dict[str, Any] = {
    "yield_rate_by_process": SQL_YIELD_RATE_BY_PROCESS,
    "top_defect_products": SQL_TOP_DEFECT_PRODUCTS,
    "equipment_downtime_rate": SQL_EQUIPMENT_DOWNTIME_RATE,
    "production_trend_by_line": SQL_PRODUCTION_TREND_BY_LINE,
}


def execute_template(
    db: Session, name: str, params: dict[str, Any]
) -> list[dict[str, Any]]:
    """执行命名 SQL 模板并返回字典列表。"""
    if name not in SQL_TEMPLATES:
        raise ValueError(f"Unknown SQL template: {name}. "
                         f"Available: {list(SQL_TEMPLATES.keys())}")
    stmt = SQL_TEMPLATES[name]
    log.info("sql.template_execute", name=name, params=params)
    result = db.execute(stmt, params)
    # 转字典列表
    keys = result.keys()
    return [dict(zip(keys, row)) for row in result.fetchall()]


def list_templates() -> list[dict[str, str]]:
    """列出所有可用模板。"""
    return [
        {
            "name": name,
            "description": _TEMPLATE_DESCRIPTIONS.get(name, ""),
        }
        for name in SQL_TEMPLATES
    ]


_TEMPLATE_DESCRIPTIONS: dict[str, str] = {
    "yield_rate_by_process": "各工序良率（按时间范围统计）",
    "top_defect_products": "不良数量 TOP N 产品（按时间范围）",
    "equipment_downtime_rate": "设备停机率（按时间范围 + 天数）",
    "production_trend_by_line": "各产线近 N 天产量趋势（按日）",
}
