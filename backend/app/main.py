"""
LifeLine Navigator — FastAPI Backend
Real-time ambulance routing using Ant Colony Optimization on live OSMnx graph.
"""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Dict

import networkx as nx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .aco import ACO
from .graph_manager import graph_manager
from .hospitals import EMERGENCY_DESCRIPTIONS, EMERGENCY_ELIGIBILITY, HOSPITALS
from .models import (
    DijkstraComparison,
    GraphInfo,
    HospitalListResponse,
    HospitalResult,
    RouteRequest,
    RouteResponse,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")
logger = logging.getLogger(__name__)


# ── Lifespan: load graph on startup ──────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading Bangalore road graph …")
    graph_manager.load()

    # Pre-compute nearest graph nodes for all hospitals
    for h in HOSPITALS.values():
        h["_node"] = graph_manager.nearest_node(h["lat"], h["lon"])
    logger.info("Hospital nodes mapped.")
    yield
    logger.info("Shutdown.")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="LifeLine Navigator API",
    description=(
        "Real-time ambulance route optimization using Ant Colony Optimization "
        "on the real Bangalore road network (OpenStreetMap data via OSMnx). "
        "Supports emergency-type routing, hospital capacity penalties, "
        "multi-ambulance dispatch, and live traffic simulation."
    ),
    version="5.0.0",
    contact={
        "name":  "Markab Debbarma, Diptanshu Datta, Challa Ekansh Rao",
        "email": "lifeline-navigator@example.com",
    },
    license_info={"name": "MIT"},
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helper ────────────────────────────────────────────────────────────────────

def _capacity_penalty(hospital_id: str) -> float:
    """CapPenalty = 1 + (capacity_pct / 100) × 0.5."""
    h = HOSPITALS.get(hospital_id, {})
    cap = h.get("capacity_pct", 50) / 100.0
    return 1.0 + cap * 0.5


def _dijkstra_best(source: int, targets: Dict[str, int]) -> tuple[str, float, list[int]]:
    """Run Dijkstra from source to each target, return best (hospital_id, cost, path)."""
    best_id, best_cost, best_path = None, float("inf"), []
    for hid, tnode in targets.items():
        try:
            cost, path = nx.single_source_dijkstra(
                graph_manager.G, source, tnode,
                weight=lambda u, v, d: min(
                    (e.get("travel_time", 60) for e in d.values()), default=60
                ) / 60.0,
                cutoff=120,   # 120-minute cutoff
            )
            penalty = _capacity_penalty(hid)
            total = cost * penalty
            if total < best_cost:
                best_cost, best_id, best_path = total, hid, path
        except nx.NetworkXNoPath:
            continue
    return best_id, best_cost, best_path


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root() -> Dict[str, str]:
    """Health check."""
    return {"status": "ok", "service": "LifeLine Navigator API v5"}


@app.get("/api/graph", response_model=GraphInfo, tags=["Graph"])
async def graph_info() -> GraphInfo:
    """Return metadata about the loaded road graph."""
    info = graph_manager.graph_info()
    return GraphInfo(**info, source="OpenStreetMap via OSMnx")


@app.get("/api/hospitals", response_model=HospitalListResponse, tags=["Hospitals"])
async def list_hospitals() -> HospitalListResponse:
    """Return all hospitals with metadata, emergency eligibility, and descriptions."""
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
async def find_route(req: RouteRequest) -> RouteResponse:
    """
    Find the optimal ambulance route using Ant Colony Optimization.

    - Locates the nearest road-network node to the provided coordinates.
    - Filters hospitals by emergency type.
    - Applies hospital capacity penalties.
    - Runs ACO with MMAS + elite ants.
    - Returns ACO result, Dijkstra comparison, convergence data, and full path.
    """
    # 1. Find source node
    try:
        source_node = graph_manager.nearest_node(req.start_lat, req.start_lon)
    except Exception as e:
        raise HTTPException(400, f"Could not locate start position on graph: {e}")

    # 2. Eligible hospitals
    etype      = req.emergency_type
    eligible   = EMERGENCY_ELIGIBILITY.get(etype, [])
    target_map = {hid: HOSPITALS[hid]["_node"] for hid in eligible if hid in HOSPITALS}

    if not target_map:
        raise HTTPException(400, f"No hospitals found for emergency type '{etype}'")

    # 3. Capacity penalties
    cap_penalties = {HOSPITALS[hid]["_node"]: _capacity_penalty(hid) for hid in target_map}

    # 4. ACO
    p = req.aco_params
    aco = ACO(
        gm         = graph_manager,
        alpha      = p.alpha,
        beta       = p.beta,
        rho        = p.rho,
        Q          = p.Q,
        tau_min    = p.tau_min,
        tau_max    = p.tau_max,
        elite_ants = p.elite_ants,
    )
    aco_result = aco.run(
        source       = source_node,
        targets      = set(target_map.values()),
        cap_penalty  = cap_penalties,
        n_ants       = p.ants,
        n_iterations = p.iterations,
    )

    if not aco_result.best_path:
        raise HTTPException(404, "ACO could not find a route. Try adjusting start location.")

    # 5. Dijkstra comparison
    dijk_hid, dijk_cost, _ = _dijkstra_best(source_node, target_map)
    dijk_hospital = HOSPITALS.get(dijk_hid, {})

    # 6. Map best ACO dest node → hospital id
    node_to_hid = {v: k for k, v in target_map.items()}
    chosen_hid  = node_to_hid.get(aco_result.best_dest, eligible[0])
    chosen_h    = HOSPITALS[chosen_hid]

    # 7. Build per-hospital results
    all_hospital_results = []
    for hid in eligible:
        h = HOSPITALS[hid]
        all_hospital_results.append(
            HospitalResult(
                id            = hid,
                name          = h["name"],
                lat           = h["lat"],
                lon           = h["lon"],
                specialties   = h["specialties"],
                capacity_pct  = h["capacity_pct"],
                beds          = h["beds"],
                icu_beds      = h["icu_beds"],
                is_chosen     = (hid == chosen_hid),
            )
        )

    time_saved = max(0.0, dijk_cost - aco_result.best_cost)
    saved_pct  = (time_saved / dijk_cost * 100) if dijk_cost > 0 else 0.0

    return RouteResponse(
        aco_travel_time_min  = round(aco_result.best_cost, 2),
        aco_path             = graph_manager.path_coords(aco_result.best_path),
        aco_hops             = len(aco_result.best_path) - 1,
        chosen_hospital      = HospitalResult(
            id           = chosen_hid,
            name         = chosen_h["name"],
            lat          = chosen_h["lat"],
            lon          = chosen_h["lon"],
            specialties  = chosen_h["specialties"],
            capacity_pct = chosen_h["capacity_pct"],
            beds         = chosen_h["beds"],
            icu_beds     = chosen_h["icu_beds"],
            is_chosen    = True,
        ),
        converged_at_iter    = aco_result.converged_at,
        convergence_data     = [round(c, 2) for c in aco_result.convergence_data],
        dijkstra             = DijkstraComparison(
            travel_time_min = round(dijk_cost, 2),
            hospital_id     = dijk_hid or "",
            hospital_name   = dijk_hospital.get("name", ""),
            path_length     = 0,
        ),
        time_saved_min       = round(time_saved, 2),
        time_saved_pct       = round(saved_pct, 1),
        all_hospitals        = all_hospital_results,
        graph_nodes_explored = aco_result.nodes_explored,
        total_ants_deployed  = aco_result.total_ants,
    )
