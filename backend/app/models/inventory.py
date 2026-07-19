"""
库存域：仓库 + 物料 + 库存余额。
"""
from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import Date, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import TimestampMixin


class Warehouse(Base, TimestampMixin):
    """仓库。"""

    __tablename__ = "warehouse"

    warehouse_code: Mapped[str] = mapped_column(String(32), primary_key=True)
    warehouse_name: Mapped[str] = mapped_column(String(128), nullable=False)
    location: Mapped[str] = mapped_column(String(128), default="")
    capacity: Mapped[int] = mapped_column(Integer, default=10000)


class Material(Base, TimestampMixin):
    """物料主数据。"""

    __tablename__ = "material"

    material_code: Mapped[str] = mapped_column(String(32), primary_key=True)
    material_name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(32), index=True)
    spec: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    unit: Mapped[str] = mapped_column(String(16), default="件")
    safety_stock: Mapped[int] = mapped_column(Integer, default=100, comment="安全库存")


class InventoryBalance(Base, TimestampMixin):
    """库存余额。"""

    __tablename__ = "inventory_balance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    material_code: Mapped[str] = mapped_column(
        String(32), ForeignKey("material.material_code"), index=True
    )
    warehouse_code: Mapped[str] = mapped_column(
        String(32), ForeignKey("warehouse.warehouse_code"), index=True
    )
    balance_date: Mapped[date] = mapped_column(Date, index=True)
    balance_qty: Mapped[int] = mapped_column(Integer, comment="结存数量")
    in_qty: Mapped[int] = mapped_column(Integer, default=0, comment="当日入库")
    out_qty: Mapped[int] = mapped_column(Integer, default=0, comment="当日出库")

    __table_args__ = (
        Index("ix_balance_material_warehouse_date", "material_code", "warehouse_code", "balance_date"),
    )
