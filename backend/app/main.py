"""
LifeLine Navigator — FastAPI Backend v5
Real-time ambulance routing using ACO on real Bangalore OSMnx road network.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .aco import ACO
from .graph_manager import graph_manager
from .hospitals import EMERGENCY_DESCRIPTIONS, EMERGENCY_ELIGIBILITY, HOSPITALS
from .models import (
    DijkstraComparison, GraphInfo, HospitalListResponse,
    HospitalResult, RouteRequest, RouteResponse,
)

logging.basicConfig(level=logging.INFO,
                    format="%(levelname)s  %(name)s  %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading Bangalore road graph …")
    graph_manager.load()
    for h in HOSPITALS.values():
        h["_node"] = graph_manager.nearest_node(h["lat"], h["lon"])
    logger.info("Hospital nodes mapped.")
    yield


app = FastAPI(
    title="LifeLine Navigator API",
    description="Real-time ambulance routing using ACO on real Bangalore OSM road network.",
    version="5.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


def _cap_penalty(hid: str) -> float:
    h = HOSPITALS.get(hid, {})
    return 1.0 + (h.get("capacity_pct", 50) / 100.0) * 0.5


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "service": "LifeLine Navigator API v5"}


@app.get("/api/graph", response_model=GraphInfo, tags=["Graph"])
async def graph_info():
    info = graph_manager.graph_info()
    return GraphInfo(**info, source="OpenStreetMap via OSMnx")


@app.get("/api/hospitals", response_model=HospitalListResponse, tags=["Hospitals"])
async def list_hospitals():
    hospitals = [
        {k: v for k, v in h.items() if not k.startswith("_")}
        for h in HOSPITALS.values()
    ]
    return HospitalListResponse(
        hospitals=hospitals,
        emergency_types=EMERGENCY_ELIGIBILITY,
        descriptions=EMERGENCY_DESCRIPTIONS,
    )


@app.post("/api/route", response_model=RouteResponse, tags=["Routing"])
async def find_route(req: RouteRequest):
    # 1. Source node
    try:
        source_node = graph_manager.nearest_node(req.start_lat, req.start_lon)
    except Exception as e:
        raise HTTPException(400, f"Could not locate start position: {e}")

    # 2. Eligible hospitals
    etype    = req.emergency_type
    eligible = EMERGENCY_ELIGIBILITY.get(etype, [])
    target_map = {
        hid: HOSPITALS[hid]["_node"]
        for hid in eligible if hid in HOSPITALS
    }
    if not target_map:
        raise HTTPException(400, f"No hospitals for emergency type '{etype}'")

    # 3. Capacity penalties
    cap_penalties = {
        HOSPITALS[hid]["_node"]: _cap_penalty(hid) for hid in target_map
    }

    # 4. Dijkstra comparison (runs on full graph — always finds a route)
    dijk_hid, dijk_cost, _ = graph_manager.dijkstra_path(source_node, target_map)
    dijk_hospital = HOSPITALS.get(dijk_hid or "", {})

    if not dijk_hid:
        raise HTTPException(
            404,
            "No route found to any hospital. "
            "Try clicking a location closer to the city centre."
        )

    # 5. ACO (runs on focused subgraph)
    p = req.aco_params
    aco = ACO(
        gm=graph_manager, alpha=p.alpha, beta=p.beta, rho=p.rho,
        Q=p.Q, tau_min=p.tau_min, tau_max=p.tau_max, elite_ants=p.elite_ants,
    )
    aco_result = aco.run(
        source       = source_node,
        targets      = set(target_map.values()),
        cap_penalty  = cap_penalties,
        n_ants       = p.ants,
        n_iterations = p.iterations,
    )

    # 6. If ACO failed to find route, fall back to Dijkstra path
    if not aco_result.best_path or aco_result.best_cost == float("inf"):
        logger.warning("ACO found no path — using Dijkstra fallback")
        _, dijk_fallback_cost, dijk_fallback_path = graph_manager.dijkstra_path(
            source_node, target_map
        )
        aco_result.best_path = dijk_fallback_path
        aco_result.best_cost = dijk_fallback_cost / 60.0 if dijk_fallback_cost else dijk_cost
        aco_result.best_dest = target_map.get(dijk_hid, -1)
        aco_result.convergence_data = [aco_result.best_cost] * p.iterations
        aco_result.converged_at = 1

    # 7. Map best dest → hospital id
    node_to_hid = {v: k for k, v in target_map.items()}
    chosen_hid  = node_to_hid.get(aco_result.best_dest, dijk_hid)
    chosen_h    = HOSPITALS[chosen_hid]

    # 8. Build per-hospital result list
    all_hosp_results = [
        HospitalResult(
            id=hid, name=HOSPITALS[hid]["name"],
            lat=HOSPITALS[hid]["lat"], lon=HOSPITALS[hid]["lon"],
            specialties=HOSPITALS[hid]["specialties"],
            capacity_pct=HOSPITALS[hid]["capacity_pct"],
            beds=HOSPITALS[hid]["beds"], icu_beds=HOSPITALS[hid]["icu_beds"],
            is_chosen=(hid == chosen_hid),
        )
        for hid in eligible if hid in HOSPITALS
    ]

    time_saved = max(0.0, dijk_cost - aco_result.best_cost)
    saved_pct  = (time_saved / dijk_cost * 100) if dijk_cost > 0 else 0.0

    return RouteResponse(
        aco_travel_time_min  = round(aco_result.best_cost, 2),
        aco_path             = graph_manager.path_coords(aco_result.best_path),
        aco_hops             = len(aco_result.best_path) - 1,
        chosen_hospital      = HospitalResult(
            id=chosen_hid, name=chosen_h["name"],
            lat=chosen_h["lat"], lon=chosen_h["lon"],
            specialties=chosen_h["specialties"],
            capacity_pct=chosen_h["capacity_pct"],
            beds=chosen_h["beds"], icu_beds=chosen_h["icu_beds"],
            is_chosen=True,
        ),
        converged_at_iter    = aco_result.converged_at,
        convergence_data     = [round(c, 2) for c in aco_result.convergence_data],
        dijkstra             = DijkstraComparison(
            travel_time_min = round(dijk_cost, 2),
            hospital_id     = dijk_hid,
            hospital_name   = dijk_hospital.get("name", ""),
            path_length     = 0,
        ),
        time_saved_min       = round(time_saved, 2),
        time_saved_pct       = round(saved_pct, 1),
        all_hospitals        = all_hosp_results,
        graph_nodes_explored = aco_result.nodes_explored,
        total_ants_deployed  = aco_result.total_ants,
    )