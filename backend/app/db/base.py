"""
SQLAlchemy 声明式基类。

所有 ORM 模型继承此 Base。
跨平台：使用 SQLAlchemy 2.x 风格。
"""
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """所有模型的基类。"""

    pass
