"""
LLM 工厂：双供应商 + 自动 fallback

主用 DeepSeek，失败/限流时自动切到 Qwen。
所有 LLM 调用都通过本模块，禁止直接 import langchain_openai。
"""
from __future__ import annotations

from typing import Any

from langchain_openai import ChatOpenAI
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings
from app.core.logging import get_logger

log = get_logger(__name__)


def get_primary_llm(timeout: int | None = None) -> ChatOpenAI:
    """获取主用 LLM。"""
    return ChatOpenAI(
        model=settings.llm_model,
        openai_api_key=settings.llm_api_key,
        openai_api_base=settings.llm_base_url,
        timeout=timeout or settings.llm_timeout,
        max_retries=settings.llm_max_retries,
    )


def get_fallback_llm(timeout: int | None = None) -> ChatOpenAI:
    """获取备用 LLM。"""
    return ChatOpenAI(
        model=settings.fallback_llm_model,
        openai_api_key=settings.fallback_llm_api_key,
        openai_api_base=settings.fallback_llm_base_url,
        timeout=timeout or settings.llm_timeout,
        max_retries=settings.llm_max_retries,
    )


def is_fallback_configured() -> bool:
    """备用 LLM 是否已配置。"""
    return bool(settings.fallback_llm_api_key)


def is_primary_configured() -> bool:
    """主用 LLM 是否已配置。"""
    return bool(settings.llm_api_key)


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    reraise=True,
)
def _invoke_with_retry(llm: ChatOpenAI, payload: Any, label: str) -> Any:
    """带重试的 LLM 调用。"""
    log.info("llm.invoke_start", provider=label, model=llm.model_name)
    try:
        result = llm.invoke(payload)
        log.info("llm.invoke_success", provider=label, model=llm.model_name)
        return result
    except Exception as e:
        log.warning("llm.invoke_failed", provider=label, error=str(e))
        raise


def chat_with_fallback(messages: list[dict[str, str]]) -> Any:
    """主用失败时自动切换备用。

    Args:
        messages: [{"role": "user", "content": "..."}, ...]
    """
    if not is_primary_configured() and not is_fallback_configured():
        raise RuntimeError("No LLM configured. Set LLM_API_KEY or FALLBACK_LLM_API_KEY.")

    # 尝试主用
    if is_primary_configured():
        try:
            return _invoke_with_retry(
                get_primary_llm(), messages, label="primary"
            )
        except Exception as primary_err:
            log.warning(
                "llm.primary_failed_try_fallback", error=str(primary_err)
            )

    # 降级到备用
    if is_fallback_configured():
        return _invoke_with_retry(
            get_fallback_llm(), messages, label="fallback"
        )

    raise RuntimeError("Primary LLM failed and no fallback configured.")
