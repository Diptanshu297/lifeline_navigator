#!/usr/bin/env python3
"""
Preload and cache the Bangalore road graph.
Run this once before starting the server, or on first Docker build.

Usage:
    python scripts/preload_graph.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.graph_manager import graph_manager

if __name__ == "__main__":
    print("Downloading Bangalore road network from OpenStreetMap …")
    print("This may take 2–5 minutes on first run. Result will be cached.")
    graph_manager.load()
    info = graph_manager.graph_info()
    print(f"\nGraph ready:")
    print(f"  Nodes : {info['nodes']:,}")
    print(f"  Edges : {info['edges']:,}")
    print(f"  Area  : {info['area_km2']} km²")
    print(f"  Cached: {info['cached']}")
    print("\nDone. Start the server with: uvicorn app.main:app --reload")
