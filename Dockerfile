# syntax=docker/dockerfile:1.6
# ═══════════════════════════════════════════════════════════════════════════
# BrainScan AI — multi-stage Dockerfile
# Builds a slim image (~1.5 GB) with PyTorch CPU + FastAPI
# ═══════════════════════════════════════════════════════════════════════════

ARG PYTHON_VERSION=3.11

# ───────────────────────────────────────────────────────────── builder ──
FROM python:${PYTHON_VERSION}-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /build

# System deps for opencv-python
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install Python deps into a dedicated location
RUN pip install --user -r requirements.txt

# ──────────────────────────────────────────────────────────── runtime ──
FROM python:${PYTHON_VERSION}-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

# Runtime libs only (no compilers)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /root/.local /root/.local

WORKDIR /app

# Copy only what's needed at runtime (not data/, logs/, results/, venv/)
COPY api/        ./api/
COPY src/        ./src/
COPY interface/  ./interface/
COPY models/     ./models/
COPY config.json runtime.txt ./

EXPOSE 8000

# Liveness probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run as non-root (best practice)
RUN useradd --create-home --shell /bin/bash brainscan && \
    chown -R brainscan:brainscan /app
USER brainscan

CMD ["python", "-m", "uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
