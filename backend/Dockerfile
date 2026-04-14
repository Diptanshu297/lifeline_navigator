FROM python:3.11-slim

WORKDIR /app

# System deps needed by osmnx / scipy
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libgeos-dev libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create data directory for graph cache
RUN mkdir -p /app/data

# Pre-download graph on build (comment out to skip — graph downloads on first request instead)
# RUN python scripts/preload_graph.py

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
