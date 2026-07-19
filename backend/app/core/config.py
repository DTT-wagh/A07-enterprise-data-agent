"""
跨平台配置：pydantic-settings + pathlib

所有路径走 Path；所有可调参数走环境变量（.env 注入）。
**禁止**硬编码绝对路径。
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# 项目根目录解析：跨平台 + 不依赖环境变量
def _project_root() -> Path:
    """解析项目根目录。

    优先级：
        1. 环境变量 PROJECT_ROOT
        2. 当前工作目录向上找 pyproject.toml
        3. 本文件所在目录向上 3 级（backend/app/core → 项目根）
    """
    import os

    env = os.environ.get("PROJECT_ROOT")
    if env:
        return Path(env).expanduser().resolve()

    cwd = Path.cwd().resolve()
    for parent in [cwd, *cwd.parents]:
        if (parent / "pyproject.toml").exists():
            return parent

    # 兜底：基于本文件位置
    return Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """全局配置（单例）。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ===== 应用元信息 =====
    app_name: str = "A07 Enterprise Data Agent"
    app_version: str = "0.1.0"
    app_env: Literal["development", "staging", "production"] = "development"

    # ===== 服务 =====
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = True
    app_log_level: str = "INFO"

    # CORS：跨平台前端开发地址
    app_cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
        ]
    )

    # ===== 安全 =====
    app_secret_key: str = "change-me-in-production"

    # ===== 数据库 =====
    database_url: str = "sqlite:///./data/a07.db"
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10

    @field_validator("database_url")
    @classmethod
    def _ensure_sqlite_relative(cls, v: str) -> str:
        """SQLite 路径转绝对路径（基于项目根）。"""
        if v.startswith("sqlite:///"):
            rel = v.replace("sqlite:///", "", 1)
            if not Path(rel).is_absolute():
                abs_path = (_project_root() / rel).resolve()
                abs_path.parent.mkdir(parents=True, exist_ok=True)
                return f"sqlite:///{abs_path}"
        return v

    # ===== LLM 主供应商 =====
    llm_api_key: str = ""
    llm_base_url: str = "https://api.deepseek.com/v1"
    llm_model: str = "deepseek-chat"
    llm_timeout: int = 30
    llm_max_retries: int = 2

    # ===== LLM 备用供应商 =====
    fallback_llm_api_key: str = ""
    fallback_llm_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    fallback_llm_model: str = "qwen-turbo"

    # ===== 数据路径（运行时计算，禁止硬编码） =====
    @property
    def project_root(self) -> Path:
        return _project_root()

    @property
    def data_dir(self) -> Path:
        d = self.project_root / "data"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def model_dir(self) -> Path:
        d = self.data_dir / "models"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def experiment_dir(self) -> Path:
        d = self.data_dir / "experiments"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def seed_dir(self) -> Path:
        d = self.project_root / "backend" / "app" / "db" / "seed"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def init_sql(self) -> Path:
        return self.project_root / "backend" / "app" / "db" / "init.sql"

    # ===== SQL 安全 =====
    sql_max_rows: int = 1000
    sql_timeout_seconds: int = 30
    # 允许的 SQL 类型（只读）
    sql_allowed_starts: tuple[str, ...] = ("SELECT", "WITH")

    # ===== ML =====
    ml_default_test_size: float = 0.2
    ml_default_random_state: int = 42


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """获取单例配置。"""
    return Settings()


settings = get_settings()
