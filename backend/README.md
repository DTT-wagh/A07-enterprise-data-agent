# A07 Backend

> FastAPI + LangChain 后端 — 企业数据底座智能问析 Agent

## 当前进度（M1 骨架）

- [x] FastAPI 入口
- [x] 结构化日志（structlog）
- [x] 跨平台配置（pydantic-settings + pathlib）
- [x] 健康检查端点
- [x] 聊天端点骨架
- [x] 双 LLM 工厂（DeepSeek + Qwen fallback）
- [ ] 数据库接入（SQLAlchemy + Alembic）
- [ ] LangChain Agent 接入
- [ ] 业务知识 API
- [ ] 数据资源 API
- [ ] ML 引擎

## 快速开始

```bash
# 1. 创建虚拟环境（跨平台）
cd backend
python3 -m venv .venv

# macOS / Linux
source .venv/bin/activate
# Windows PowerShell
# .\.venv\Scripts\Activate.ps1

# 2. 安装依赖
pip install -e ".[dev]"

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 填入 LLM_API_KEY 等

# 4. 启动
uvicorn app.main:app --reload --port 8000
# 或
python -m app.main
```

## 端点

| 路径 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 应用信息 |
| `/docs` | GET | Swagger UI（自动生成） |
| `/redoc` | GET | ReDoc |
| `/api/v1/health` | GET | 健康检查 |
| `/api/v1/chat/message` | POST | 自然语言问析 |

## 目录

```
backend/
├── app/
│   ├── main.py              # 入口
│   ├── core/                # 配置 / 日志
│   ├── api/v1/              # 路由
│   ├── services/            # 业务（LLM 工厂、Agent、ML）
│   ├── models/              # SQLAlchemy（待）
│   ├── schemas/             # Pydantic（待）
│   └── db/                  # 数据库 / 迁移（待）
├── tests/                   # 测试（待）
├── pyproject.toml
└── .env.example
```

## 跨平台规范

- **路径**：`pathlib.Path` 强制
- **环境变量**：`.env` 注入，禁止硬编码
- **用户目录**：`Path.home()`，禁止 `/Users/xxx` 或 `C:\Users\xxx`
- 详细规范见 [`docs/collaboration/cross-platform.md`](../docs/collaboration/cross-platform.md)

## 测试

```bash
pytest -q
ruff check .
mypy app/
```
