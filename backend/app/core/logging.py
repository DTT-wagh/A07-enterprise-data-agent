"""
结构化日志：structlog

输出 JSON（生产）/ Rich（开发），统一跨平台格式。
"""
from __future__ import annotations

import logging
import sys

import structlog
from structlog.types import EventDict, Processor

from app.core.config import settings


def _add_app_context(_, __, event_dict: EventDict) -> EventDict:
    """注入应用元信息。"""
    event_dict.setdefault("app", settings.app_name)
    event_dict.setdefault("version", settings.app_version)
    event_dict.setdefault("env", settings.app_env)
    return event_dict


def setup_logging() -> None:
    """初始化日志。

    生产：JSON 格式
    开发：Rich 彩色输出
    """
    is_dev = settings.app_env == "development"

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        _add_app_context,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if is_dev:
        # 开发：Rich 彩色 + 可读格式
        processors = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    else:
        # 生产：JSON
        processors = [
            *shared_processors,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.app_log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    # 把 stdlib logging 也接管
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.app_log_level, logging.INFO),
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """获取 logger。"""
    return structlog.get_logger(name)
