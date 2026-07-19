# 技术栈选型

> 📌 用于 PPT "技术架构" 章节 + 详细方案文档"技术选型"章节
> 🎯 设计原则：**主流成熟 + 国产化合规 + 学生友好 + 跨平台**

---

## 一、选型总原则

| 原则 | 含义 |
|------|------|
| **主流成熟** | 生态完善、文档充足、社区活跃、坑少 |
| **国产化合规** | LLM 优先国产（DeepSeek/Qwen），避免 OpenAI 依赖 |
| **学生友好** | 学习曲线平缓，3 人学生团队可快速上手 |
| **跨平台** | Mac/Windows/Linux 三端一致，CI 矩阵可验证 |
| **可扩展** | 4 周内做 MVP，未来 3-6 月可演化为正式产品 |
| **可演示** | 现场演示稳定，3 层兜底保障 |

---

## 二、总体技术栈一览

```
┌─────────────────────────────────────────────────────┐
│ 前端 (Vue3 + ECharts)                                │
│   - Vue 3.4 / Vite 5 / TypeScript / Pinia            │
│   - Element Plus / ECharts 5                         │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP/JSON
┌──────────────────────┴──────────────────────────────┐
│ 后端 (FastAPI + LangChain)                            │
│   - Python 3.11+ / FastAPI / Pydantic v2             │
│   - LangChain 0.3 / LangSmith (可选)                  │
│   - SQLAlchemy 2.x / psycopg[binary] / Alembic        │
│   - scikit-learn 1.4+ / pandas / polars              │
└──────────────────────┬──────────────────────────────┘
                       │ SQL
┌──────────────────────┴──────────────────────────────┐
│ 数据 (PostgreSQL 14+)                                  │
│   - 4 大业务域 15 张表 + 3 张公共维度                  │
│   - Alembic 迁移 / 物化视图 (指标)                     │
└─────────────────────────────────────────────────────┘
                       │ API
┌─────────────────────────────────────────────────────┐
│ LLM (OpenAI 兼容协议)                                  │
│   - 主：DeepSeek (deepseek-chat)                       │
│   - 备：Qwen (qwen-turbo) / ChatGLM (备用)            │
└─────────────────────────────────────────────────────┘
```

---

## 三、后端技术选型

### 3.1 主语言：Python 3.11+

| 选项 | 选 / 不选 | 理由 |
|------|----------|------|
| **Python 3.11+** | ✅ 选 | LangChain/scikit-learn 主流语言、AI 生态最完善 |
| Java 17 | ❌ | AI 生态薄弱，Agent 框架少 |
| Node.js 20 | ❌ | ML 库支持差，团队不熟 |
| Go 1.22 | ❌ | AI 库少，学习成本高 |

### 3.2 Web 框架：FastAPI

| 选项 | 选 / 不选 | 理由 |
|------|----------|------|
| **FastAPI** | ✅ 选 | 异步性能好、OpenAPI 自动生成、Pydantic 集成、类型提示友好 |
| Django 5 | ❌ | 重、ORM 与 LangChain 集成麻烦、不够灵活 |
| Flask 3 | ❌ | 无异步、需手写 OpenAPI |
| Spring Boot | ❌ | 学习成本高、与 AI 生态割裂 |

**关键优势**：
- 自动生成 `/docs` Swagger UI，**评委可现场浏览**
- 依赖注入 + Pydantic 校验 = 减少 50% 样板代码
- 异步原生支持，LLM 流式输出简单

### 3.3 LLM 框架：LangChain 0.3

| 选项 | 选 / 不行 | 理由 |
|------|----------|------|
| **LangChain** | ✅ 选 | Agent 工具调用成熟、社区大、SQL Agent / ReAct 范式现成 |
| LlamaIndex | ❌ | 主要面向 RAG，Agent 能力弱于 LangChain |
| AutoGen | ❌ | 多 Agent 协作，但 NL2SQL 不如 LangChain 成熟 |
| 原生调用 | ❌ | 自己实现 ReAct + Tool 成本高，4 周做不完 |

**关键组件**：
- `langchain-community` - SQLDatabase, SQL Agent
- `langchain-openai` - DeepSeek/Qwen 兼容协议
- `langchain-core` - Tool / PromptTemplate / OutputParser

### 3.4 数据库驱动：psycopg[binary]

| 选项 | 选 / 不选 | 理由 |
|------|----------|------|
| **psycopg[binary]** | ✅ 选 | PG 3.x 官方驱动、预编译包跨平台、Windows 安装友好 |
| psycopg2-binary | ❌ | Windows 安装常失败、官方已不推荐 |
| asyncpg | ⚠️ 可选 | 高性能异步，但与 SQLAlchemy 集成需 async session |

**注**：Windows 上 `pip install psycopg[binary]` 一键安装，**避免团队环境差异**。

### 3.5 ORM：SQLAlchemy 2.x + Alembic

| 选项 | 选 / 不选 | 理由 |
|------|----------|------|
| **SQLAlchemy 2.x** | ✅ 选 | Python ORM 事实标准、LangChain 集成现成 |
| Tortoise ORM | ❌ | 生态小，LangChain 集成差 |
| 原生 SQL | ❌ | 失去 ORM 优势、迁移难做 |

**配合 Alembic**：版本化 schema 迁移，**避免团队成员本地数据库不一致**。

### 3.6 ML 框架：scikit-learn 1.4+

| 选项 | 选 / 不选 | 理由 |
|------|----------|------|
| **scikit-learn** | ✅ 选 | 6 大算法全部覆盖、文档全、跨平台 |
| PyTorch | ❌ | 重、4 周内只做传统 ML 即可 |
| XGBoost / LightGBM | ⚠️ 可选 | 性能更好但学习成本高 |

**集成方式**：sklearn 模型 + joblib 持久化 + LangChain Tool 封装。

### 3.7 测试：pytest + httpx

| 选项 | 选 / 不选 | 理由 |
|------|----------|------|
| **pytest** | ✅ 选 | Python 测试事实标准、插件丰富 |
| unittest | ❌ | 样板代码多 |
| nose2 | ❌ | 已停止维护 |

---

## 四、前端技术选型

### 4.1 框架：Vue 3.4（组合式 API）

| 选项 | 选 / 不选 | 理由 |
|------|----------|------|
| **Vue 3** | ✅ 选 | 组合式 API 灵活、TypeScript 友好、Element Plus 生态完善 |
| React 18 | ⚠️ 可选 | 团队如熟 React 优先，但 Vue 在国内制造业接受度更高 |
| Angular 17 | ❌ | 重、学习曲线陡 |
| Svelte | ❌ | 生态小、企业级组件少 |

**业务角色 B 选 Vue**：中文文档全 + Element Plus 中后台现成 + 团队 1 天可上手。

### 4.2 构建：Vite 5

| 选项 | 选 / 不选 | 理由 |
|------|----------|------|
| **Vite 5** | ✅ 选 | 启动快、HMR 流畅、TypeScript 原生支持 |
| Webpack 5 | ❌ | 配置复杂、启动慢 |
| Vue CLI | ❌ | 已停止维护 |

### 4.3 UI 库：Element Plus

| 选项 | 选 / 不选 | 理由 |
|------|----------|------|
| **Element Plus** | ✅ 选 | Vue3 官方推荐、企业级组件全、中文文档 |
| Ant Design Vue | ⚠️ | 风格偏 React |
| Naive UI | ⚠️ | 轻量但生态小 |
| Vuetify | ❌ | Material 风格不符（命题方要安卓观感时也可用） |

### 4.4 可视化：ECharts 5

| 选项 | 选 / 不选 | 理由 |
|------|----------|------|
| **ECharts 5** | ✅ 选 | 国产、文档中文化、7 大图表全、社区大、百度背书 |
| D3.js | ❌ | 学习曲线陡、4 周做不完 |
| Chart.js | ❌ | 图表种类少、定制弱 |
| Highcharts | ❌ | 商业授权 |

**ECharts 5 覆盖**：折线、柱状、饼、散点、热力、桑基、关系图（**知识图谱**） → 7 大类全部满足。

### 4.5 状态管理：Pinia

| 选项 | 选 / 不选 | 理由 |
|------|----------|------|
| **Pinia** | ✅ 选 | Vue3 官方推荐、TS 友好、API 简洁 |
| Vuex 4 | ❌ | 已被 Pinia 取代 |

---

## 五、数据库选型

### 5.1 主库：PostgreSQL 14+

| 选项 | 选 / 不选 | 理由 |
|------|----------|------|
| **PostgreSQL 14+** | ✅ 选 | 开源、功能强、制造业行业标准、与 SQLAlchemy 完美集成 |
| MySQL 8 | ⚠️ | 也能用，但 PG 在 JSON / 物化视图 / Window Function 更强 |
| SQLite | ⚠️ 降级 | 演示环境无 PG 时降级，**生产必须用 PG** |
| Oracle / SQL Server | ❌ | 商业授权、不跨平台 |

**安装方式**：
- macOS：`brew install postgresql@14`
- Windows：PostgreSQL Installer 或 Docker
- Linux：`apt install postgresql-14`
- **跨平台统一**：Docker（两平台一致，**比赛演示推荐**）

### 5.2 迁移工具：Alembic

- SQLAlchemy 官方迁移工具
- 团队成员本地数据库 schema 一致
- 配合 `alembic upgrade head` 一键同步

---

## 六、LLM 选型

### 6.1 主供应商：DeepSeek

| 维度 | 数据 |
|------|------|
| 模型 | `deepseek-chat`（V3）/ `deepseek-reasoner`（R1） |
| 价格 | ¥1/M tokens（V3），¥4/M tokens（R1） |
| 上下文 | 64K |
| 速度 | 50-80 tokens/s |
| 中文能力 | 优秀 |
| Tool Calling | ✅ 支持 |
| 合规 | 国产，**数据不出境** |

### 6.2 备供应商：Qwen（通义千问）

| 维度 | 数据 |
|------|------|
| 模型 | `qwen-turbo` / `qwen-plus` / `qwen-max` |
| 价格 | turbo 0.3 元/百万 tokens、plus 4 元、max 20 元 |
| 免费额度 | 100 万 tokens（turbo） |
| 上下文 | 8K-32K |
| 中文能力 | 顶级 |
| Tool Calling | ✅ 支持 |
| 合规 | 阿里云、国产 |

### 6.3 备选 2：ChatGLM（智谱）

| 维度 | 数据 |
|------|------|
| 模型 | `glm-4` / `glm-4-flash` |
| 价格 | glm-4-flash 免费 |
| 中文能力 | 优秀 |
| Tool Calling | ✅ 支持 |

### 6.4 为什么不用 OpenAI

| 风险 | 严重性 |
|------|--------|
| 数据出境合规（制造业敏感数据） | 🔴 高 |
| API 价格高（GPT-4 30 倍于 DeepSeek） | 🟡 中 |
| 服务稳定性（境外网络） | 🟡 中 |
| 国产化政策导向 | 🟡 中 |

---

## 七、DevOps / 工具链

### 7.1 包管理

| 语言 | 工具 | 理由 |
|------|------|------|
| Python | **uv** 或 pip + venv | uv 速度快、`pip install -e .` 跨平台一致 |
| Node | **pnpm** | 节省磁盘、安装快、workspaces 友好 |
| 数据库迁移 | **Alembic** | SQLAlchemy 官方 |

### 7.2 代码规范

| 工具 | 用途 |
|------|------|
| ruff | Python linting + formatting（替代 black + flake8 + isort） |
| mypy | Python 类型检查 |
| ESLint + Prettier | 前端 linting + formatting |
| EditorConfig | 编辑器统一 |

### 7.3 CI/CD

- **GitHub Actions** 三平台矩阵（macOS / Windows / Ubuntu）
- 检查项：换行符、硬编码路径、.env 入库、secrets 扫描、pytest、ESLint

### 7.4 可观测性（按时间允许选择）

- **必须**：结构化日志（structlog）、FastAPI `/health`、错误聚合（try-except + 错误码）
- **可选**：LangSmith（Agent 链路追踪）、Sentry（错误监控）、Prometheus + Grafana（指标）

---

## 八、跨平台工具链

| 工具 | 用途 | 跨平台方案 |
|------|------|-----------|
| Python 环境 | 依赖隔离 | `python -m venv` + 激活脚本 |
| Node 环境 | 前端依赖 | pnpm + `node_modules` |
| PostgreSQL | 数据库 | Docker（一致）+ 本地安装（开发） |
| Git | 版本控制 | `core.autocrlf=input` + `core.fileMode=false` |
| 启动脚本 | 一键启动 | `scripts/dev.sh` + `scripts/dev.ps1` 等价 |

详见 [docs/collaboration/cross-platform.md](../collaboration/cross-platform.md)

---

## 九、备选方案（兜底）

| 主选 | 备选 | 触发条件 |
|------|------|---------|
| PostgreSQL | SQLite | 现场无 PG 时降级（`DATABASE_URL=sqlite:///./data/a07.db`） |
| DeepSeek | Qwen / ChatGLM | API 限流或维护时切换 |
| Vue3 + ECharts | Streamlit | 时间紧张时用 Streamlit 出 demo |
| LangChain | 原生 OpenAI SDK | LangChain 学习卡壳时降级 |
| Element Plus | 自研组件 | UI 复杂度过高时自研 |

---

## 十、版本锁定

```
python==3.11
fastapi==0.115.*
langchain==0.3.*
langchain-community==0.3.*
langchain-openai==0.2.*
sqlalchemy==2.0.*
psycopg[binary]==3.2.*
pydantic==2.9.*
pydantic-settings==2.6.*
scikit-learn==1.5.*
pandas==2.2.*
joblib==1.4.*
pytest==8.3.*
ruff==0.7.*
mypy==1.13.*
```

```
node==20
vue==3.5.*
vite==5.4.*
typescript==5.6.*
pinia==2.2.*
vue-router==4.4.*
element-plus==2.8.*
echarts==5.5.*
axios==1.7.*
```

> 锁定主版本（`==`）而非次要版本（`~`），保证三平台一致。

---

## 十一、选型决策矩阵（评委可看）

| 维度 | 备选 A | 备选 B | 本项目选 | 关键理由 |
|------|--------|--------|---------|---------|
| 后端语言 | Python | Java | **Python** | AI 生态最完善 |
| 后端框架 | FastAPI | Django | **FastAPI** | 轻量、异步、自动 OpenAPI |
| Agent 框架 | LangChain | LlamaIndex | **LangChain** | SQL Agent / ReAct 现成 |
| 数据库 | PostgreSQL | MySQL | **PostgreSQL** | JSON / 物化视图 / 窗口函数 |
| 前端框架 | Vue 3 | React 18 | **Vue 3** | 中文文档、企业级组件 |
| 可视化 | ECharts 5 | D3.js | **ECharts 5** | 中文化、7 大图表、关系图 |
| LLM 主 | DeepSeek | GPT-4 | **DeepSeek** | 国产合规、价格低、中文好 |
| 包管理 | uv / pnpm | conda / npm | **uv + pnpm** | 跨平台一致 |

---

## 十二、答辩常问技术问题

### Q1：为什么 LangChain 而不是直接调 API？
- Agent 范式（ReAct / Plan-Execute）复杂，自己实现 4 周做不完
- LangChain 的 SQL Agent 已包含 schema linking + 反思重试
- 社区 90% 的踩坑都已解决

### Q2：FastAPI 性能够吗？
- 单次 LLM 调用 1-3s，框架开销可忽略
- 异步支持并发 100+ 请求
- 对演示场景绰绰有余

### Q3：为什么不选 Django？
- Django Admin 不适合展示复杂分析
- Django ORM 与 LangChain 集成不如 SQLAlchemy 灵活
- Django 较重，4 周没必要

### Q4：Vue3 + Element Plus 风格适合制造业吗？
- Element Plus 是国内中后台事实标准
- 风格偏商务、安卓观感强
- 满足"业务人员友好"的要求

### Q5：为什么不用国产数据库（如 OceanBase）？
- PostgreSQL 跨平台一致 + 团队学习成本低
- 比赛评分不要求国产数据库
- 如未来客户要求，可平滑迁移（SQLAlchemy 抽象层）
