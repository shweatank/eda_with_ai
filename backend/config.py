"""
Central configuration, loaded from the `.env` file at the project root.

Nothing in this project ever hard-codes a credential: every secret is read
from the environment here, and only here.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# ai_rtl_debugger/backend/config.py -> ai_rtl_debugger/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


class Settings:
    """Plain settings object -- no magic, easy to read in a presentation."""

    # ---- Neo4j AuraDB ----
    NEO4J_URI: str = os.getenv("NEO4J_URI", "")
    NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "")
    NEO4J_DATABASE: str = os.getenv("NEO4J_DATABASE", "neo4j")

    # ---- Groq ----
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    # ---- external tools ----
    IVERILOG_BIN: str = os.getenv("IVERILOG_BIN", "iverilog")
    VVP_BIN: str = os.getenv("VVP_BIN", "vvp")
    SIM_TIMEOUT_SECONDS: int = int(os.getenv("SIM_TIMEOUT_SECONDS", "60"))

    # ---- paths ----
    VERILOG_DIR: Path = PROJECT_ROOT / "verilog"
    JOBS_DIR: Path = PROJECT_ROOT / "data" / "jobs"

    # ---- background workers ----
    MAX_WORKERS: int = 4

    @property
    def neo4j_configured(self) -> bool:
        return bool(self.NEO4J_URI and self.NEO4J_PASSWORD)

    @property
    def groq_configured(self) -> bool:
        return bool(self.GROQ_API_KEY)

    def safe_summary(self) -> dict:
        """Diagnostics that never leak a secret."""
        return {
            "neo4j_uri": self.NEO4J_URI or "(unset)",
            "neo4j_database": self.NEO4J_DATABASE,
            "neo4j_password_set": bool(self.NEO4J_PASSWORD),
            "groq_model": self.GROQ_MODEL,
            "groq_api_key_set": bool(self.GROQ_API_KEY),
            "iverilog_bin": self.IVERILOG_BIN,
            "sim_timeout_seconds": self.SIM_TIMEOUT_SECONDS,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
