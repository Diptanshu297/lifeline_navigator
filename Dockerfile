# ──────────────────────────────────────────────────────────────
# LifeLine Navigator — Hugging Face Spaces Dockerfile
# Single container: builds React frontend, serves via FastAPI
# Listens on port 7860 (HF Spaces convention)
# ──────────────────────────────────────────────────────────────

# ── Stage 1: Build React frontend ────────────────────────────
FROM node:20-alpine AS frontend-builder
WORKDIR /build

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
# Same-origin deploy — API is on the same URL
ENV VITE_API_URL=""
RUN npm run build

# ── Stage 2: FastAPI + static frontend ───────────────────────
FROM python:3.11-slim

# System dependencies for osmnx / scipy / shapely
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libgeos-dev libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Hugging Face Spaces requires a non-root user with UID 1000
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

WORKDIR /home/user/app

# Python deps
COPY --chown=user backend/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt \
    && pip install --user --no-cache-dir scikit-learn

# App code
COPY --chown=user backend/ ./

# Built React assets → served as static files
COPY --chown=user --from=frontend-builder /build/dist ./static

# Graph cache directory (persisted via HF Spaces storage)
RUN mkdir -p /home/user/app/data

EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]