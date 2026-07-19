"""
公共维度：产品、产线。
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import TimestampMixin


class DimProduct(Base, TimestampMixin):
    """产品维度。"""

    __tablename__ = "dim_product"

    product_code: Mapped[str] = mapped_column(String(32), primary_key=True)
    product_name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    spec: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    unit: Mapped[str] = mapped_column(String(16), default="件")


class DimLine(Base, TimestampMixin):
    """产线维度。"""

    __tablename__ = "dim_line"

    line_code: Mapped[str] = mapped_column(String(32), primary_key=True)
    line_name: Mapped[str] = mapped_column(String(128), nullable=False)
    workshop: Mapped[str] = mapped_column(String(64), nullable=False)
    capacity_per_shift: Mapped[int] = mapped_column(default=1000, comment="每班次产能")
