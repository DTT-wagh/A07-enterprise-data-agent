"""
数据库连接与会话。

跨平台：
- 支持 PostgreSQL（生产、推荐）
- 支持 SQLite（演示、降级、自动建库）
"""
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.logging import get_logger

log = get_logger(__name__)


def _make_engine_url() -> str:
    """根据 DATABASE_URL 构造引擎 URL，SQLite 时自动建目录。"""
    url = settings.database_url
    if url.startswith("sqlite:///"):
        path_str = url.replace("sqlite:///", "", 1)
        path = Path(path_str)
        if not path.is_absolute():
            # 相对路径：相对项目根
            path = settings.project_root / path_str
        path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{path}"
    return url


def _engine_kwargs() -> dict:
    """根据数据库类型返回不同的 engine kwargs。"""
    url = _make_engine_url()
    if url.startswith("sqlite"):
        return {
            "connect_args": {"check_same_thread": False},
            "echo": settings.database_echo,
        }
    return {
        "pool_size": settings.database_pool_size,
        "max_overflow": settings.database_max_overflow,
        "pool_pre_ping": True,
        "echo": settings.database_echo,
    }


_engine: Engine = create_engine(_make_engine_url(), **_engine_kwargs())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


# SQLite 外键约束默认关闭，需要显式开启
@event.listens_for(_engine, "connect")
def _enable_sqlite_fk(dbapi_connection, _connection_record):  # type: ignore[no-untyped-def]
    if _engine.url.get_backend_name().startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_engine() -> Engine:
    """获取全局 Engine。"""
    return _engine


def get_db() -> Iterator[Session]:
    """FastAPI 依赖：每个请求一个 Session。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """创建所有表（仅用于演示 / 首次启动）。

    生产环境应使用 Alembic 迁移。
    """
    # 导入所有模型以注册到 Base.metadata
    from app.models import (  # noqa: F401
        dim,
        equipment,
        inventory,
        production,
        quality,
    )

    log.info("db.init_start", url=str(_engine.url).split("@")[-1])
    Base.metadata.create_all(bind=_engine)
    log.info("db.init_done", tables=len(Base.metadata.tables))
