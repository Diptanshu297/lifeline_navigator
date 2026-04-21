
FROM node:20-alpine AS frontend-builder
WORKDIR /build

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
ENV VITE_API_URL=""
RUN npm run build


FROM python:3.11-slim


RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libgeos-dev libgdal-dev curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app


COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir scikit-learn


RUN python -c "import uvicorn; import fastapi; print('uvicorn:', uvicorn.__version__); print('fastapi:', fastapi.__version__)"


COPY backend/ ./


COPY --from=frontend-builder /build/dist ./static

RUN mkdir -p /app/data && \
    useradd -m -u 1000 user && \
    chown -R user:user /app

USER user
ENV PYTHONUNBUFFERED=1 \
    PATH=/usr/local/bin:$PATH

EXPOSE 7860

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]