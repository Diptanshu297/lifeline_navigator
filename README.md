---
title: LifeLine Navigator
emoji: 🚑
colorFrom: red
colorTo: blue
sdk: docker
app_port: 7860
pinned: true
license: mit
short_description: ACO ambulance routing on real Bangalore roads
---

# 🚑 LifeLine Navigator

**Intelligent Ambulance Route Optimization using Ant Colony Optimization (ACO)**

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61dafb?logo=react)](https://react.dev)
[![OpenStreetMap](https://img.shields.io/badge/Map-OpenStreetMap-7EBC6F?logo=openstreetmap)](https://openstreetmap.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> *"Optimizing Every Second to Save a Life"*

LifeLine Navigator is a full-stack emergency dispatch system that routes ambulances through **real Bangalore streets** (OpenStreetMap data) using a custom ACO algorithm. It adapts to live traffic, matches patients to specialist hospitals, and outperforms static Dijkstra routing by **18–47%** under dynamic traffic conditions.

## 🖥️ Live Demo

Deployed on Hugging Face Spaces — visit this Space's URL to use the app.

API docs: append `/docs` to the Space URL.

## ✨ Features

- 🗺️ **Real road network** — 134,153 node Bangalore graph from OpenStreetMap via OSMnx
- 🏥 **25 hospitals** — all major Bangalore hospitals with specialties and live capacity
- 🐜 **ACO + MMAS** — Max-Min Ant System with elite ant reinforcement
- 🚑 **Emergency routing** — Cardiac / Trauma / Neuro / General matched to eligible hospitals
- 📊 **Capacity penalties** — full hospitals get higher effective cost
- ⏱️ **Physics-grounded ETA** — real minutes via road-type speed limits
- 🔄 **vs Dijkstra** — every route compared against optimal in real time
- 📈 **Live convergence chart** — pheromone reinforcement visualized

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Python 3.11 |
| Routing | OSMnx + NetworkX |
| Frontend | React 18 + Vite + Leaflet |
| Charts | Recharts |
| Deployment | Docker + Hugging Face Spaces |

## 🚀 Local Development

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/preload_graph.py       # One-time: downloads Bangalore graph
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev                           # → http://localhost:5173
```

## 📡 API

- `GET  /api/health`     — health check
- `GET  /api/graph`      — graph metadata
- `GET  /api/hospitals`  — hospital list + eligibility
- `POST /api/route`      — compute ACO route
- `GET  /docs`           — Swagger UI

## 👥 Team

| Name | Roll No | Contribution |
|------|---------|-------------|
| Markab Debbarma | 245859090 | Problem design, market analysis, deployment |
| Diptanshu Datta | 245819186 | ACO algorithm, graph model, API backend |
| Challa Ekansh Rao | 245819066 | Frontend, results analysis, Docker |

**Guide:** Dr. Sowmya R — Dept. of Electronics & Communication Engineering  
**Course:** Design & Analysis of Algorithms Lab — 2026

## 📄 License

MIT © 2026 Markab Debbarma, Diptanshu Datta, Challa Ekansh Rao