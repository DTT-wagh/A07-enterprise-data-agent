"""
自然语言问析端点（骨架）。

M1 目标：端点能接收消息，返回"已收到"。
M2 目标：接入 LangChain Agent，返回真实分析结果。

POST /api/v1/chat/message
"""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.logging import get_logger

router = APIRouter(prefix="/chat", tags=["chat"])
log = get_logger(__name__)


class ChatMessage(BaseModel):
    """单条聊天消息。"""

    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    """问析请求。"""

    message: str = Field(..., min_length=1, max_length=2000, description="用户自然语言问题")
    session_id: str | None = Field(default=None, description="会话 ID（用于多轮上下文）")
    stream: bool = Field(default=False, description="是否流式返回")


class ChatResponse(BaseModel):
    """问析响应。"""

    session_id: str
    reply: str
    sql: str | None = None
    data: list[dict] | None = None
    chart: dict | None = None
    insights: list[str] | None = None
    duration_ms: int


@router.post("/message", response_model=ChatResponse)
async def chat_message(req: ChatRequest) -> ChatResponse:
    """处理一条自然语言问析请求。

    M1 阶段：返回占位响应。
    M2 阶段：接入 LangChain Agent。
    """
    import time
    import uuid

    start = time.time()
    session_id = req.session_id or str(uuid.uuid4())

    log.info(
        "chat.message_received",
        session_id=session_id,
        length=len(req.message),
        stream=req.stream,
    )

    # TODO M2: 接入 LangChain Agent
    reply = (
        f"[M1 骨架] 已收到您的消息：{req.message!r}。"
        "LangChain Agent 将在 M2 阶段接入。"
    )

    duration_ms = int((time.time() - start) * 1000)
    return ChatResponse(
        session_id=session_id,
        reply=reply,
        duration_ms=duration_ms,
    )


@router.get("/sessions/{session_id}")
async def get_session(session_id: str) -> dict:
    """获取会话历史。"""
    # TODO M3: 接入会话存储
    return {"session_id": session_id, "messages": []}
