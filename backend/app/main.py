"""
FastAPI 应用入口。

启动：
    uvicorn app.main:app --reload --port 8000
    或
    python -m app.main
"""
from __future__ import annotations

import sys
from pathlib import Path

# 允许 `python -m app.main` 直接运行
if __name__ in ("__main__", "app.main"):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from contextlib import asynccontextmanager  # noqa: E402

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import ORJSONResponse  # noqa: E402

from app.api.v1 import chat, health  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.core.logging import get_logger, setup_logging  # noqa: E402

setup_logging()
log = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """应用生命周期。"""
    log.info(
        "app.startup",
        version=settings.app_version,
        env=settings.app_env,
        host=settings.app_host,
        port=settings.app_port,
        llm_primary_configured=bool(settings.llm_api_key),
        llm_fallback_configured=bool(settings.fallback_llm_api_key),
    )
    yield
    log.info("app.shutdown")


def create_app() -> FastAPI:
    """创建 FastAPI 应用。"""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "A07 企业数据底座智能问析 Agent — "
            "面向制造业业务人员的自然语言数据分析平台。"
        ),
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.app_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 路由
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(chat.router, prefix="/api/v1")

    # 根路径
    @app.get("/", tags=["root"])
    async def root() -> dict:
        return {
            "app": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/api/v1/health",
        }

    return app


app = create_app()


def run() -> None:
    """直接运行入口。"""
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
        log_level=settings.app_log_level.lower(),
    )


if __name__ == "__main__":
    run()
