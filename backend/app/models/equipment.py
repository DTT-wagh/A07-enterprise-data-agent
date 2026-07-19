"""
设备域：设备主数据 + 停机。
"""
from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import Date, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import TimestampMixin


class Equipment(Base, TimestampMixin):
    """设备主数据。"""

    __tablename__ = "equipment"

    equipment_code: Mapped[str] = mapped_column(String(32), primary_key=True)
    equipment_name: Mapped[str] = mapped_column(String(128), nullable=False)
    equipment_type: Mapped[str] = mapped_column(String(32), index=True)
    line_code: Mapped[Optional[str]] = mapped_column(
        String(32), ForeignKey("dim_line.line_code"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(16), default="运行中", index=True, comment="运行中/停机/维护中/已报废"
    )
    install_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)


class EquipmentDowntime(Base, TimestampMixin):
    """设备停机记录。"""

    __tablename__ = "equipment_downtime"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipment_code: Mapped[str] = mapped_column(
        String(32), ForeignKey("equipment.equipment_code"), index=True
    )
    downtime_date: Mapped[date] = mapped_column(Date, index=True)
    start_time: Mapped[str] = mapped_column(String(8), comment="HH:MM")
    end_time: Mapped[str] = mapped_column(String(8), comment="HH:MM")
    downtime_minutes: Mapped[int] = mapped_column(Integer, comment="停机分钟")
    reason: Mapped[str] = mapped_column(String(64), index=True)
    impact_qty: Mapped[int] = mapped_column(Integer, default=0, comment="影响产量")

    __table_args__ = (
        Index("ix_downtime_equipment_date", "equipment_code", "downtime_date"),
    )
