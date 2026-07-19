"""
质量域：检验 + 缺陷。
"""
from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import Date, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import TimestampMixin


class QualityInspection(Base, TimestampMixin):
    """质量检验记录。"""

    __tablename__ = "quality_inspection"

    inspection_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    workorder_id: Mapped[Optional[str]] = mapped_column(
        String(32), ForeignKey("production_workorder.workorder_id"), nullable=True
    )
    product_code: Mapped[str] = mapped_column(
        String(32), ForeignKey("dim_product.product_code"), index=True
    )
    batch_no: Mapped[str] = mapped_column(String(32), index=True)
    inspected_qty: Mapped[int] = mapped_column(Integer, comment="送检数量")
    passed_qty: Mapped[int] = mapped_column(Integer, comment="合格数量")
    inspection_date: Mapped[date] = mapped_column(Date, index=True)
    inspector: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    result: Mapped[str] = mapped_column(String(16), default="合格", index=True)

    __table_args__ = (
        Index("ix_inspection_product_date", "product_code", "inspection_date"),
    )


class QualityDefect(Base, TimestampMixin):
    """质量缺陷记录。"""

    __tablename__ = "quality_defect"

    defect_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    inspection_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("quality_inspection.inspection_id"), index=True
    )
    product_code: Mapped[str] = mapped_column(
        String(32), ForeignKey("dim_product.product_code"), index=True
    )
    defect_type: Mapped[str] = mapped_column(String(32), index=True, comment="缺陷类型")
    defect_qty: Mapped[int] = mapped_column(Integer, comment="缺陷数量")
    severity: Mapped[str] = mapped_column(
        String(16), default="轻微", comment="严重程度：轻微/严重/致命"
    )
    defect_date: Mapped[date] = mapped_column(Date, index=True)
    cause: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
