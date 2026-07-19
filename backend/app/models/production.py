"""
生产域：工单 + 工序产量。
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import TimestampMixin


class ProductionWorkorder(Base, TimestampMixin):
    """生产工单。"""

    __tablename__ = "production_workorder"

    workorder_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    product_code: Mapped[str] = mapped_column(
        String(32), ForeignKey("dim_product.product_code"), index=True
    )
    line_code: Mapped[str] = mapped_column(
        String(32), ForeignKey("dim_line.line_code"), index=True
    )
    plan_qty: Mapped[int] = mapped_column(Integer, comment="计划数量")
    actual_qty: Mapped[int] = mapped_column(Integer, default=0, comment="实际数量")
    start_date: Mapped[date] = mapped_column(Date, index=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        String(16), default="进行中", index=True, comment="状态：进行中/已完成/已取消"
    )


class ProductionProcess(Base, TimestampMixin):
    """工序产量。"""

    __tablename__ = "production_process"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workorder_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("production_workorder.workorder_id"), index=True
    )
    process_code: Mapped[str] = mapped_column(String(32), index=True)
    process_name: Mapped[str] = mapped_column(String(64))
    total_qty: Mapped[int] = mapped_column(Integer, comment="投入数量")
    qualified_qty: Mapped[int] = mapped_column(Integer, comment="合格数量")
    record_date: Mapped[date] = mapped_column(Date, index=True)
    operator: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    __table_args__ = (
        Index("ix_process_workorder_process", "workorder_id", "process_code"),
    )
