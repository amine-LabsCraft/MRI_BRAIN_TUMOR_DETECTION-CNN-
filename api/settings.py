"""
Centralised settings & logger for the BrainScan API.

Values are loaded from environment variables (with .env support if
python-dotenv is available). All settings have sensible dev defaults.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

# ── .env support (optional) ──────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass


# ── Helpers ──────────────────────────────────────────────────────────────────
def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(int(default))).strip().lower() in ("1", "true", "yes", "on")


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default


def _csv(name: str, default: str) -> list[str]:
    raw = os.getenv(name, default).strip()
    return [p.strip() for p in raw.split(",") if p.strip()]


# ── Settings ─────────────────────────────────────────────────────────────────
class Settings:
    BASE_DIR:   Path = Path(__file__).resolve().parent.parent
    MODEL_PATH: Path = BASE_DIR / os.getenv(
        "BRAINSCAN_MODEL_PATH",
        "models/final_model_20251106_142153.pth",
    )

    CORS_ORIGINS: list[str] = _csv("BRAINSCAN_CORS_ORIGINS", "*")
    API_KEY:      str       = os.getenv("BRAINSCAN_API_KEY", "").strip()
    RATE_LIMIT:   int       = _int("BRAINSCAN_RATE_LIMIT", 60)
    DISABLE_RATELIMIT: bool = _bool("BRAINSCAN_DISABLE_RATELIMIT", False)
    LOG_LEVEL:    str       = os.getenv("BRAINSCAN_LOG_LEVEL", "INFO").upper()


settings = Settings()


# ── Logger ───────────────────────────────────────────────────────────────────
def get_logger(name: str = "brainscan") -> logging.Logger:
    """Return a configured logger (idempotent — safe to call multiple times)."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    level = getattr(logging, settings.LOG_LEVEL, logging.INFO)
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s  %(levelname)-7s  %(name)s  %(message)s",
        datefmt="%H:%M:%S",
    ))
    logger.addHandler(handler)
    logger.propagate = False
    return logger
