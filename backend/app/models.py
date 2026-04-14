"""
API request/response models using Pydantic v2.
"""
from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ── Request models ────────────────────────────────────────────────────────────

class ACOParams(BaseModel):
    iterations:  int   = Field(default=40,   ge=5,   le=200, description="Number of ACO iterations")
    ants:        int   = Field(default=20,   ge=5,   le=100, description="Ants per iteration")
    alpha:       float = Field(default=1.0,  ge=0.1, le=5.0, description="Pheromone exponent α")
    beta:        float = Field(default=2.0,  ge=0.1, le=5.0, description="Heuristic exponent β")
    rho:         float = Field(default=0.15, ge=0.01,le=0.9, description="Evaporation rate ρ")
    Q:           float = Field(default=100.0,ge=1.0, le=1000.0, description="Pheromone deposit constant")
    tau_min:     float = Field(default=0.01, ge=0.001,le=1.0, description="MMAS lower pheromone bound")
    tau_max:     float = Field(default=5.0,  ge=1.0, le=50.0,  description="MMAS upper pheromone bound")
    elite_ants:  int   = Field(default=3,    ge=0,   le=10,  description="Extra elite ant reinforcements")


class RouteRequest(BaseModel):
    start_lat:      float = Field(..., ge=12.5, le=13.5,  description="Ambulance start latitude")
    start_lon:      float = Field(..., ge=77.0, le=78.0,  description="Ambulance start longitude")
    emergency_type: str   = Field(..., pattern="^(cardiac|trauma|neuro|general)$")
    aco_params:     ACOParams = Field(default_factory=ACOParams)

    model_config = {
        "json_schema_extra": {
            "example": {
                "start_lat": 12.9716,
                "start_lon": 77.5946,
                "emergency_type": "cardiac",
                "aco_params": {
                    "iterations": 40,
                    "ants": 20,
                    "alpha": 1.0,
                    "beta": 2.0,
                    "rho": 0.15,
                }
            }
        }
    }


# ── Response models ───────────────────────────────────────────────────────────

class Coordinate(BaseModel):
    lat: float
    lon: float


class HospitalResult(BaseModel):
    id:             str
    name:           str
    lat:            float
    lon:            float
    specialties:    List[str]
    capacity_pct:   int
    beds:           int
    icu_beds:       int
    travel_time_min: Optional[float] = None
    is_chosen:      bool = False


class RouteStep(BaseModel):
    node_id:    int
    lat:        float
    lon:        float
    road_name:  Optional[str] = None
    speed_kph:  Optional[float] = None


class DijkstraComparison(BaseModel):
    travel_time_min: float
    hospital_id:     str
    hospital_name:   str
    path_length:     int


class RouteResponse(BaseModel):
    # Main ACO result
    aco_travel_time_min:  float
    aco_path:             List[Coordinate]
    aco_hops:             int
    chosen_hospital:      HospitalResult
    converged_at_iter:    int
    convergence_data:     List[float]   # best cost per iteration

    # Dijkstra comparison
    dijkstra:             DijkstraComparison

    # Savings
    time_saved_min:       float
    time_saved_pct:       float

    # All eligible hospitals with their costs
    all_hospitals:        List[HospitalResult]

    # Meta
    graph_nodes_explored: int
    total_ants_deployed:  int


class GraphInfo(BaseModel):
    nodes:          int
    edges:          int
    area_km2:       float
    center_lat:     float
    center_lon:     float
    cached:         bool
    source:         str = "OpenStreetMap via OSMnx"


class HospitalListResponse(BaseModel):
    hospitals:          List[Dict[str, Any]]
    emergency_types:    Dict[str, List[str]]
    descriptions:       Dict[str, str]
