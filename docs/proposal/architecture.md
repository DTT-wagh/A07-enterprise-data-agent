# 系统架构与模块图

> 📌 用于 PPT "系统架构" 章节 + 详细方案文档"总体设计"章节
> 🎯 提供 6 类图：系统架构 / 功能模块 / 用户旅程 / 数据流 / Agent 工作流 / ML 训练流程

---

## 一、系统架构图（三层 + 外部服务）

```mermaid
flowchart TB
    subgraph 客户端
        U[业务人员]
    end

    subgraph 前端 [前端 Vue3 + ECharts]
        UI[UI 界面]
        CHAT[聊天问析]
        CHART[图表组件]
        KG[知识图谱可视化]
    end

    subgraph 后端 [后端 FastAPI + LangChain]
        API[FastAPI 路由]
        AGENT[LangChain Agent]
        TOOLS[8 大工具]
        ML[ML 引擎]
        SQL[SQL 执行器]
        KNOW[业务知识服务]
        SCHEMA[数据资源服务]
    end

    subgraph 数据层
        PG[(PostgreSQL<br/>4 域 15 表 + 维度)]
    end

    subgraph 外部服务
        DS[DeepSeek<br/>主 LLM]
        QW[Qwen<br/>备 LLM]
    end

    U --> UI
    UI --> CHAT
    UI --> CHART
    UI --> KG
    CHAT --> API
    API --> AGENT
    AGENT --> TOOLS
    TOOLS --> SQL
    TOOLS --> ML
    TOOLS --> KNOW
    TOOLS --> SCHEMA
    SQL --> PG
    SCHEMA --> PG
    KNOW --> PG
    ML --> PG
    AGENT --> DS
    AGENT -.fallback.-> QW

    style AGENT fill:#FFE0B2
    style PG fill:#C8E6C9
    style DS fill:#B3E5FC
    style QW fill:#B3E5FC
```

---

## 二、功能模块图（5 大能力 + 1 个平台）

```mermaid
flowchart LR
    subgraph 平台 [企业数据底座智能问析 Agent 平台]
        direction TB

        subgraph 能力1 [① 业务知识管理]
            K1[业务对象]
            K2[业务指标]
            K3[业务规则]
            K4[分析主题]
        end

        subgraph 能力2 [② 数据资源理解]
            S1[表结构]
            S2[字段说明]
            S3[样例数据]
            S4[表间关系]
        end

        subgraph 能力3 [③ 自然语言智能分析]
            N1[意图识别]
            N2[NL2SQL]
            N3[SQL 安全执行]
            N4[业务解读]
        end

        subgraph 能力4 [④ SQL/脚本生成与执行 + ML]
            M1[SQL 生成]
            M2[脚本生成]
            M3[ML 6 大算法]
            M4[模型训练/推理]
        end

        subgraph 能力5 [⑤ 分析结果展示]
            V1[表格]
            V2[图表]
            V3[知识图谱]
            V4[报告生成]
        end

        subgraph 基础 [平台基础]
            B1[LangChain Agent]
            B2[双 LLM 兜底]
            B3[用户管理]
            B4[审计日志]
        end
    end

    K1 --> B1
    S1 --> B1
    N1 --> B1
    M1 --> B1
    V1 --> B1
    B1 --> B2
    B1 --> B3
    B1 --> B4

    style B1 fill:#FF6B35,color:#fff
    style B2 fill:#FFA726,color:#fff
```

---

## 三、用户旅程图（业务人员视角）

```mermaid
journey
    title 业务人员使用本平台的典型旅程
    section 注册登录
      打开应用: 3: 业务人员
      选择身份: 3: 业务人员
    section 提出问题
      输入自然语言: 5: 业务人员
      等待系统理解: 4: 系统
    section 查看结果
      查看表格: 5: 业务人员
      查看图表: 5: 业务人员
      阅读业务解读: 5: 业务人员
    section 进一步追问
      切换时间范围: 4: 业务人员
      切换维度: 4: 业务人员
      追问业务原因: 5: 业务人员
    section 沉淀复用
      收藏问句: 4: 业务人员
      导出报告: 5: 业务人员
      分享同事: 4: 业务人员
```

---

## 四、核心业务流程图（用户提问→结果展示）

```mermaid
sequenceDiagram
    actor U as 业务人员
    participant FE as 前端
    participant BE as FastAPI
    participant A as LangChain Agent
    participant T as 工具集
    participant DB as PostgreSQL
    participant LLM as DeepSeek/Qwen

    U->>FE: 输入自然语言问题
    FE->>BE: POST /api/v1/chat/message
    BE->>A: invoke(messages)
    A->>LLM: 意图识别 + 工具选择
    LLM-->>A: 选中的工具 + 参数

    loop 工具调用（可能多次）
        A->>T: 调用工具 (e.g. execute_sql)
        T->>DB: 安全 SQL 查询
        DB-->>T: 返回数据
        T-->>A: 工具结果
        A->>LLM: 反思 + 下一步决策
        LLM-->>A: 下一步动作
    end

    A->>LLM: 生成业务解读
    LLM-->>A: 文字结论
    A-->>BE: 最终结果 (data + chart + text)
    BE-->>FE: 流式返回 (SSE)
    FE-->>U: 表格 + 图表 + 解读
    U->>FE: 进一步追问（可选）
```

---

## 五、Agent 工作流图（ReAct 范式）

```mermaid
flowchart TB
    Q[用户问题] --> T[Thought<br/>理解意图]
    T --> A[Action<br/>选择工具]
    A --> OBS[Observation<br/>观察结果]
    OBS -->|未完成| T
    OBS -->|已完成| FINAL[Final Answer<br/>业务解读]

    subgraph 工具池
        T1[list_tables]
        T2[get_table_schema]
        T3[get_sample_data]
        T4[execute_sql]
        T5[compute_metric]
        T6[search_business_knowledge]
        T7[train_model]
        T8[predict]
    end

    A --> 工具池
    工具池 --> OBS

    FINAL --> OUT[结构化输出<br/>表格 + 图表 + 文字]

    style FINAL fill:#66BB6A,color:#fff
    style OUT fill:#42A5F5,color:#fff
```

---

## 六、数据流图（端到端）

```mermaid
flowchart LR
    subgraph 输入
        Q[自然语言问句]
        K[业务知识]
        S[Schema 元数据]
    end

    subgraph 处理
        P[Prompt 拼接<br/>问题 + 业务知识 + Schema]
        L[LLM 推理]
        SQL[生成 SQL]
        EXE[SQL 执行]
        INT[业务解读 LLM]
    end

    subgraph 输出
        TBL[表格]
        CHT[图表]
        TXT[文字结论]
        RPT[Markdown 报告]
    end

    Q --> P
    K --> P
    S --> P
    P --> L
    L --> SQL
    SQL --> EXE
    EXE --> INT
    INT --> TBL
    INT --> CHT
    INT --> TXT
    TXT --> RPT

    style L fill:#FF6B35,color:#fff
    style INT fill:#FFA726,color:#fff
```

---

## 七、ML 训练流程图

```mermaid
flowchart TB
    REQ[业务请求<br/>找出异常停机设备] --> AG[Agent 决策]
    AG --> T1[tool: train_model<br/>algorithm=isolation_forest]
    T1 --> FE[特征工程]
    FE --> TR[训练<br/>IsolationForest]
    TR --> EV[评估<br/>silhouette_score]
    EV --> SAVE[模型保存<br/>joblib + metrics.json]
    SAVE --> PRED[tool: predict<br/>预测异常]
    PRED --> OUT[输出异常设备 Top5<br/>+ 时间分布图]

    style TR fill:#AB47BC,color:#fff
    style OUT fill:#66BB6A,color:#fff
```

---

## 八、目录结构图（项目骨架）

```
A07-enterprise-data-agent/
├── backend/                        # 后端
│   ├── app/
│   │   ├── main.py                 # FastAPI 入口
│   │   ├── core/                   # 配置/日志/安全
│   │   ├── api/v1/                 # 路由
│   │   │   ├── chat.py
│   │   │   ├── knowledge.py
│   │   │   ├── schema.py
│   │   │   └── analytics.py
│   │   ├── services/               # 业务逻辑
│   │   │   ├── agent.py            # LangChain Agent
│   │   │   ├── sql_executor.py
│   │   │   ├── nl2sql.py
│   │   │   ├── ml_engine.py
│   │   │   └── knowledge.py
│   │   ├── models/                 # SQLAlchemy 模型
│   │   ├── schemas/                # Pydantic
│   │   └── db/                     # 连接/迁移
│   ├── tests/
│   ├── pyproject.toml
│   └── .env.example
├── frontend/                       # 前端
│   ├── src/
│   │   ├── views/
│   │   │   ├── Dashboard.vue       # 主页
│   │   │   ├── Knowledge.vue       # 业务知识
│   │   │   ├── DataSchema.vue      # 数据资源
│   │   │   ├── Chat.vue            # 智能问析
│   │   │   ├── Analytics.vue       # ML 建模
│   │   │   └── KnowledgeGraph.vue  # 知识图谱
│   │   ├── components/
│   │   │   ├── common/
│   │   │   ├── charts/             # ECharts 封装
│   │   │   └── chat/
│   │   ├── stores/                 # Pinia
│   │   ├── api/
│   │   ├── router/
│   │   ├── styles/
│   │   └── constants/
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
├── docs/                           # 文档
│   ├── schedule.md                 # 排期
│   ├── team-roles.md
│   ├── llm-setup.md
│   ├── collaboration/cross-platform.md
│   ├── data-dictionary.md          # 数据字典
│   ├── business-knowledge.md       # 业务知识
│   └── proposal/                   # 比赛材料
│       ├── topic-rationale.md
│       ├── features-highlights.md
│       ├── tech-stack.md
│       └── architecture.md         # 本文件
├── scripts/                        # 跨平台脚本
│   ├── dev.sh
│   ├── dev.ps1
│   └── _common.py
├── .github/workflows/ci.yml        # CI 三平台
├── .env.example
├── .gitattributes
├── .editorconfig
└── README.md
```

---

## 九、模块依赖关系

```mermaid
flowchart TB
    subgraph 核心
        Agent[LangChain Agent]
    end

    subgraph 业务服务
        Know[业务知识]
        Schema[数据资源]
        NL2SQL[NL2SQL]
        ML[ML 引擎]
    end

    subgraph 基础设施
        Config[配置管理]
        Logger[日志]
        Security[安全/只读 SQL]
    end

    subgraph 外部
        DB[(PostgreSQL)]
        LLM[DeepSeek/Qwen]
    end

    Agent --> NL2SQL
    Agent --> Know
    Agent --> ML
    Agent --> Schema
    NL2SQL --> Security
    NL2SQL --> DB
    Know --> DB
    Schema --> DB
    ML --> DB
    Agent --> LLM
    Know --> Config
    Schema --> Config
    ML --> Config
    Security --> Config
    Security --> Logger
```

---

## 十、部署架构图（演示环境）

```mermaid
flowchart LR
    subgraph 用户电脑 [现场用户电脑]
        B[浏览器]
    end

    subgraph 演示机 [演示机（Docker 一键启动）]
        FE[前端<br/>Nginx/Vite preview<br/>:5173]
        BE[后端<br/>FastAPI + uvicorn<br/>:8000]
        PG[(PostgreSQL<br/>:5432)]
    end

    subgraph 外部 LLM
        DS[DeepSeek API]
        QW[Qwen API]
    end

    B --> FE
    FE -->|HTTP| BE
    BE -->|SQL| PG
    BE -->|HTTPS| DS
    BE -.fallback.-> QW

    style PG fill:#C8E6C9
    style DS fill:#B3E5FC
```

---

## 十一、状态机图（一次问句处理）

```mermaid
stateDiagram-v2
    [*] --> 接收
    接收 --> 理解: 解析自然语言
    理解 --> 工具调度: 选定 1-3 个工具
    工具调度 --> 执行: 参数填充 + 安全校验
    执行 --> 反思: 是否完成？
    反思 --> 工具调度: 否
    反思 --> 解读: 是
    解读 --> 展示: 生成结论
    展示 --> [*]: 返回前端

    执行 --> 失败: SQL 错误 / 工具异常
    失败 --> 重试: 反思重写
    重试 --> 工具调度
    失败 --> 兜底: 3 次失败
    兜底 --> 展示: 预生成结果
```

---

## 十二、关键交互时序图（自然语言问数）

```mermaid
sequenceDiagram
    actor U as 用户
    participant FE as 前端
    participant BE as 后端
    participant AG as Agent
    participant T as 工具
    participant DB as DB

    U->>FE: 1. 输入"分析各工序良率"
    FE->>BE: 2. POST /chat/message
    BE->>AG: 3. invoke
    AG->>AG: 4. 意图识别 (LLM)
    AG->>T: 5. list_tables
    T->>DB: SELECT table_name
    DB-->>T: tables
    T-->>AG: result
    AG->>T: 6. get_schema(production_process)
    T->>DB: SELECT column info
    DB-->>T: schema
    T-->>AG: schema
    AG->>AG: 7. 生成 SQL (LLM)
    AG->>T: 8. execute_sql
    T->>DB: SELECT ... GROUP BY process_code
    DB-->>T: rows
    T-->>AG: data
    AG->>AG: 9. 业务解读 (LLM)
    AG-->>BE: 10. {table, chart, text}
    BE-->>FE: 11. SSE 流式返回
    FE-->>U: 12. 表格 + 柱状图 + 文字
```

---

## 十三、能力雷达图（比赛要求覆盖度）

```mermaid
graph LR
    subgraph 命题要求
        R1[业务知识组织] -->|5/5| S1[✅ 业务知识图谱]
        R2[数据资源理解] -->|5/5| S2[✅ 数据门户 + 图谱]
        R3[自然语言分析] -->|5/5| S3[✅ NL2SQL + 解读]
        R4[Agent 闭环] -->|5/5| S4[✅ 端到端 ReAct]
        R5[系统展示] -->|5/5| S5[✅ ECharts 7 类]
        R6[工程可用性] -->|4/5| S6[⚠️ 完整但时间紧]
        R7[应用价值] -->|5/5| S7[✅ 制造业真实场景]
    end

    style S1 fill:#66BB6A,color:#fff
    style S2 fill:#66BB6A,color:#fff
    style S3 fill:#66BB6A,color:#fff
    style S4 fill:#66BB6A,color:#fff
    style S5 fill:#66BB6A,color:#fff
    style S6 fill:#FFA726,color:#fff
    style S7 fill:#66BB6A,color:#fff
```

---

## 十四、文件清单

| 类别 | 文件 |
|------|------|
| 业务亮点 | [features-highlights.md](features-highlights.md) |
| 选题原因 | [topic-rationale.md](topic-rationale.md) |
| 技术栈 | [tech-stack.md](tech-stack.md) |
| 跨平台规范 | [../collaboration/cross-platform.md](../collaboration/cross-platform.md) |
| 排期 | [../schedule.md](../schedule.md) |
| 角色 | [../team-roles.md](../team-roles.md) |
| LLM 配置 | [../llm-setup.md](../llm-setup.md) |

---

> **使用建议**：
> - PPT 答辩：**图 1（系统架构）+ 图 3（用户旅程）+ 图 5（Agent 工作流）+ 图 13（雷达图）**
> - 详细方案文档：全部图按章节穿插
> - GitHub README：图 1 + 图 5 + 图 10（部署架构）
