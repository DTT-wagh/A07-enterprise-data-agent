"""
健康检查端点：用于探活 + 依赖检查。

GET /api/v1/health
- 检查数据库连接
- 检查主 LLM API 可达性
- 检查备用 LLM API 可达性
"""
from __future__ import annotations

import time

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.config import settings
from app.core.logging import get_logger

router = APIRouter(prefix="/health", tags=["health"])
log = get_logger(__name__)


class ComponentStatus(BaseModel):
    """单个组件状态。"""

    status: str  # "ok" | "degraded" | "down"
    latency_ms: int | None = None
    detail: str | None = None


class HealthResponse(BaseModel):
    """健康检查响应。"""

    status: str  # "ok" | "degraded" | "down"
    app: str
    version: str
    env: str
    uptime_ms: int
    components: dict[str, ComponentStatus]


_START_TIME = time.time()


async def _check_database() -> ComponentStatus:
    """检查数据库连接。"""
    start = time.time()
    try:
        # TODO: 接入真实 DB session
        # from app.db.session import engine
        # with engine.connect() as conn:
        #     conn.execute(text("SELECT 1"))
        elapsed = int((time.time() - start) * 1000)
        return ComponentStatus(status="ok", latency_ms=elapsed, detail="not connected")
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        log.warning("health.db_failed", error=str(e))
        return ComponentStatus(status="down", latency_ms=elapsed, detail=str(e))


async def _check_llm(base_url: str, api_key: str, label: str) -> ComponentStatus:
    """检查 LLM API 可达性。"""
    start = time.time()
    try:
        if not api_key:
            return ComponentStatus(status="degraded", detail=f"{label}: no api key")
        # 简单 HEAD/GET 探活
        import httpx
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(
                f"{base_url.rstrip('/')}/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
        elapsed = int((time.time() - start) * 1000)
        if resp.status_code == 200:
            return ComponentStatus(status="ok", latency_ms=elapsed)
        return ComponentStatus(
            status="degraded", latency_ms=elapsed, detail=f"http {resp.status_code}"
        )
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        log.warning("health.llm_failed", label=label, error=str(e))
        return ComponentStatus(status="down", latency_ms=elapsed, detail=str(e))


@router.get("", response_model=HealthResponse)
async def health() -> HealthResponse:
    """健康检查。"""
    db_status = await _check_database()
    primary_llm = await _check_llm(
        settings.llm_base_url, settings.llm_api_key, "primary"
    )
    fallback_llm = await _check_llm(
        settings.fallback_llm_base_url, settings.fallback_llm_api_key, "fallback"
    )

    components = {
        "database": db_status,
        "llm_primary": primary_llm,
        "llm_fallback": fallback_llm,
    }

    # 整体状态：DB + 至少 1 个 LLM OK 即可
    any_llm_ok = primary_llm.status == "ok" or fallback_llm.status == "ok"
    if db_status.status == "ok" and any_llm_ok:
        overall = "ok"
    elif db_status.status == "down":
        overall = "down"
    else:
        overall = "degraded"

    return HealthResponse(
        status=overall,
        app=settings.app_name,
        version=settings.app_version,
        env=settings.app_env,
        uptime_ms=int((time.time() - _START_TIME) * 1000),
        components=components,
    )
