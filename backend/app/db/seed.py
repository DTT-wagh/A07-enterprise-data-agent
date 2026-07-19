"""
Faker 样例数据生成脚本。

生成 10 张表的演示数据，每张 100+ 行，覆盖最近 90 天。

用法：
    python -m app.db.seed              # 重新生成所有表
    python -m app.db.seed --rows 200   # 每个工单生成 200 行工序
    python -m app.db.seed --reset      # 先清空再生成

跨平台：pathlib + 环境无关。
"""
from __future__ import annotations

import argparse
import random
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# 允许 `python -m app.db.seed` 直接运行
if __name__ in ("__main__", "app.db.seed", "app.db.__main__"):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy import delete  # noqa: E402

from app.core.logging import get_logger, setup_logging  # noqa: E402
from app.db.session import SessionLocal, init_db  # noqa: E402
from app.models.dim import DimLine, DimProduct  # noqa: E402
from app.models.equipment import Equipment, EquipmentDowntime  # noqa: E402
from app.models.inventory import InventoryBalance, Material, Warehouse  # noqa: E402
from app.models.production import ProductionProcess, ProductionWorkorder  # noqa: E402
from app.models.quality import QualityDefect, QualityInspection  # noqa: E402

setup_logging()
log = get_logger("seed")

# 固定种子，结果可复现
random.seed(42)

# 业务参数
PRODUCT_CATEGORIES = ["电子产品", "机械零件", "注塑件", "包装材料", "化工原料"]
LINE_WORKSHOP = [("L01", "一号车间"), ("L02", "一号车间"), ("L03", "二号车间"),
                 ("L04", "二号车间"), ("L05", "三号车间")]
PROCESS_NAMES = [("P01", "下料"), ("P02", "加工"), ("P03", "组装"), ("P04", "检验"), ("P05", "包装")]
DEFECT_TYPES = ["划伤", "变形", "色差", "尺寸偏差", "杂质", "气泡", "断裂", "锈蚀"]
DEFECT_REASONS = ["设备故障", "物料异常", "操作失误", "工艺参数偏移", "环境因素", "待定"]
DOWN_REASONS = ["故障停机", "保养维护", "换模", "待料", "停电", "其他"]
EQUIPMENT_TYPES = ["CNC加工中心", "注塑机", "冲压机", "焊接机", "贴片机", "包装机", "检测仪"]
MATERIAL_CATEGORIES = ["原材料", "半成品", "辅料", "包装材料"]
WAREHOUSES = [("W01", "主原料仓", "厂区A"), ("W02", "半成品仓", "厂区B"),
              ("W03", "成品仓", "厂区C")]


def _date_range(days: int = 90) -> list[date]:
    """生成最近 N 天的日期列表。"""
    today = date.today()
    return [today - timedelta(days=i) for i in range(days)]


def gen_dim_products(n: int = 20) -> list[DimProduct]:
    """生成产品维度。"""
    items = []
    for i in range(n):
        cat = random.choice(PRODUCT_CATEGORIES)
        items.append(
            DimProduct(
                product_code=f"P{1000 + i}",
                product_name=f"{cat}-型号{i:03d}",
                category=cat,
                spec=f"规格-{random.choice(['A', 'B', 'C', 'D'])}",
                unit=random.choice(["件", "套", "kg", "米"]),
            )
        )
    return items


def gen_dim_lines() -> list[DimLine]:
    """生成产线维度。"""
    return [
        DimLine(line_code=code, line_name=f"{name}-{code}", workshop=name,
                capacity_per_shift=random.choice([800, 1000, 1200, 1500]))
        for code, name in LINE_WORKSHOP
    ]


def gen_workorders(n: int = 100, products: list[str] = None,
                   lines: list[str] = None) -> list[ProductionWorkorder]:
    """生成工单。"""
    products = products or [f"P{1000 + i}" for i in range(20)]
    lines = lines or [code for code, _ in LINE_WORKSHOP]
    items = []
    for i in range(n):
        start = date.today() - timedelta(days=random.randint(0, 89))
        plan = random.choice([500, 800, 1000, 1500, 2000])
        actual = int(plan * random.uniform(0.85, 1.05))
        end = start + timedelta(days=random.randint(3, 15)) if random.random() > 0.3 else None
        status = "已完成" if end and end < date.today() else random.choice(["进行中", "进行中", "已完成"])
        items.append(
            ProductionWorkorder(
                workorder_id=f"WO{20260000 + i}",
                product_code=random.choice(products),
                line_code=random.choice(lines),
                plan_qty=plan,
                actual_qty=actual,
                start_date=start,
                end_date=end,
                status=status,
            )
        )
    return items


def gen_process(workorders: list[ProductionWorkorder]) -> list[ProductionProcess]:
    """生成工序产量（每个工单 3-5 个工序）。"""
    items = []
    pid = 0
    for wo in workorders:
        n_proc = random.randint(3, 5)
        proc_indices = random.sample(range(len(PROCESS_NAMES)), n_proc)
        for idx in proc_indices:
            code, name = PROCESS_NAMES[idx]
            total = random.randint(80, 200)
            # 良率 88-99%
            qualified = int(total * random.uniform(0.88, 0.99))
            items.append(
                ProductionProcess(
                    id=pid,
                    workorder_id=wo.workorder_id,
                    process_code=code,
                    process_name=name,
                    total_qty=total,
                    qualified_qty=qualified,
                    record_date=wo.start_date + timedelta(days=random.randint(0, 10)),
                    operator=f"OP{random.randint(1, 20):03d}",
                )
            )
            pid += 1
    return items


def gen_inspections(workorders: list[ProductionWorkorder], products: list[str]) -> list[QualityInspection]:
    """生成质量检验。"""
    items = []
    for i in range(200):
        wo = random.choice(workorders) if workorders else None
        inspected = random.randint(50, 200)
        passed = int(inspected * random.uniform(0.88, 0.99))
        result = "合格" if passed == inspected else "不合格"
        items.append(
            QualityInspection(
                inspection_id=f"QI{20260000 + i}",
                workorder_id=wo.workorder_id if wo else None,
                product_code=random.choice(products),
                batch_no=f"B{20260000 + i // 10}",
                inspected_qty=inspected,
                passed_qty=passed,
                inspection_date=date.today() - timedelta(days=random.randint(0, 89)),
                inspector=f"QC{random.randint(1, 10):02d}",
                result=result,
            )
        )
    return items


def gen_defects(inspections: list[QualityInspection], products: list[str]) -> list[QualityDefect]:
    """生成质量缺陷。"""
    items = []
    for i in range(300):
        insp = random.choice(inspections)
        items.append(
            QualityDefect(
                defect_id=f"QD{20260000 + i}",
                inspection_id=insp.inspection_id,
                product_code=insp.product_code,
                defect_type=random.choice(DEFECT_TYPES),
                defect_qty=random.randint(1, 20),
                severity=random.choices(["轻微", "严重", "致命"], weights=[7, 2, 1])[0],
                defect_date=insp.inspection_date,
                cause=random.choice(DEFECT_REASONS),
            )
        )
    return items


def gen_equipment(lines: list[str]) -> list[Equipment]:
    """生成设备主数据。"""
    items = []
    for i in range(30):
        items.append(
            Equipment(
                equipment_code=f"EQ{2000 + i}",
                equipment_name=f"{random.choice(EQUIPMENT_TYPES)}-{i:02d}",
                equipment_type=random.choice(EQUIPMENT_TYPES),
                line_code=random.choice(lines),
                status=random.choices(["运行中", "运行中", "运行中", "维护中", "停机"], weights=[8, 1, 1])[0],
                install_date=date.today() - timedelta(days=random.randint(100, 1500)),
            )
        )
    return items


def gen_downtime(equipments: list[Equipment]) -> list[EquipmentDowntime]:
    """生成设备停机。"""
    items = []
    pid = 0
    for _ in range(200):
        eq = random.choice(equipments)
        # 停机时间集中在工作时间
        start_hour = random.randint(8, 16)
        minutes = random.randint(10, 240)
        items.append(
            EquipmentDowntime(
                id=pid,
                equipment_code=eq.equipment_code,
                downtime_date=date.today() - timedelta(days=random.randint(0, 89)),
                start_time=f"{start_hour:02d}:{random.randint(0, 59):02d}",
                end_time=f"{start_hour + minutes // 60:02d}:{(start_hour * 60 + minutes) % 60:02d}",
                downtime_minutes=minutes,
                reason=random.choice(DOWN_REASONS),
                impact_qty=random.randint(0, 200),
            )
        )
        pid += 1
    return items


def gen_warehouses() -> list[Warehouse]:
    """生成仓库。"""
    return [
        Warehouse(warehouse_code=code, warehouse_name=name, location=loc, capacity=random.choice([5000, 10000, 20000]))
        for code, name, loc in WAREHOUSES
    ]


def gen_materials(n: int = 50) -> list[Material]:
    """生成物料主数据。"""
    items = []
    for i in range(n):
        cat = random.choice(MATERIAL_CATEGORIES)
        items.append(
            Material(
                material_code=f"M{5000 + i}",
                material_name=f"{cat}-物料{i:03d}",
                category=cat,
                spec=f"规格-{random.choice(['A', 'B', 'C'])}",
                unit=random.choice(["件", "kg", "米", "卷"]),
                safety_stock=random.choice([50, 100, 200, 500]),
            )
        )
    return items


def gen_inventory(materials: list[str], warehouses: list[str], days: int = 30) -> list[InventoryBalance]:
    """生成库存余额（物料 × 仓库 × 30 天）。"""
    items = []
    pid = 0
    for mat in materials:
        for wh in warehouses:
            for d in _date_range(days):
                in_q = random.randint(0, 200)
                out_q = random.randint(0, 200)
                items.append(
                    InventoryBalance(
                        id=pid,
                        material_code=mat,
                        warehouse_code=wh,
                        balance_date=d,
                        balance_qty=random.randint(50, 2000),
                        in_qty=in_q,
                        out_qty=out_q,
                    )
                )
                pid += 1
    return items


def main() -> int:
    """主入口。"""
    parser = argparse.ArgumentParser(description="生成 A07 样例数据")
    parser.add_argument("--reset", action="store_true", help="先清空所有表再生成")
    parser.add_argument("--rows", type=int, default=100, help="工单生成数量")
    args = parser.parse_args()

    log.info("seed.start", reset=args.reset, rows=args.rows)

    init_db()  # 确保表已建

    with SessionLocal() as db:
        if args.reset:
            log.info("seed.reset_all_tables")
            # 注意顺序：先清从表，再清主表
            for model in [
                EquipmentDowntime, QualityDefect, QualityInspection,
                ProductionProcess, ProductionWorkorder,
                InventoryBalance, Material, Warehouse,
                Equipment, DimLine, DimProduct,
            ]:
                db.execute(delete(model))
            db.commit()

        # 1. 维度
        products = gen_dim_products(20)
        lines = gen_dim_lines()
        warehouses = gen_warehouses()
        materials = gen_materials(50)
        equipments = gen_equipment([code for code, _ in LINE_WORKSHOP])

        db.add_all(products + lines + warehouses + materials + equipments)
        db.flush()

        product_codes = [p.product_code for p in products]
        line_codes = [l.line_code for l in lines]
        material_codes = [m.material_code for m in materials]
        warehouse_codes = [w.warehouse_code for w in warehouses]

        # 2. 业务表
        workorders = gen_workorders(args.rows, product_codes, line_codes)
        processes = gen_process(workorders)
        inspections = gen_inspections(workorders, product_codes)
        defects = gen_defects(inspections, product_codes)
        downtime = gen_downtime(equipments)
        inventory = gen_inventory(material_codes, warehouse_codes, days=30)

        db.add_all(workorders + processes + inspections + defects + downtime + inventory)
        db.commit()

        log.info(
            "seed.done",
            products=len(products),
            lines=len(lines),
            workorders=len(workorders),
            processes=len(processes),
            inspections=len(inspections),
            defects=len(defects),
            equipments=len(equipments),
            downtime=len(downtime),
            materials=len(materials),
            warehouses=len(warehouses),
            inventory=len(inventory),
        )

    log.info("seed.exit_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
