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
    gcc g++ libgeos-dev libgdal-dev curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps — install system-wide (not --user)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir scikit-learn

# App code
COPY backend/ ./

# Built React frontend
COPY --from=frontend-builder /build/dist ./static

# Create data dir (for graph cache) and chown everything to HF user
RUN mkdir -p /app/data && useradd -m -u 1000 user && chown -R user:user /app
USER user

ENV PYTHONUNBUFFERED=1

EXPOSE 7860

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]