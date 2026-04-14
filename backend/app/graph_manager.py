"""
Graph Manager — loads real Bangalore road network from OpenStreetMap via OSMnx.
Caches the graph as a pickle file to avoid repeated downloads.

Fix note: We bypass ox.add_edge_speeds() because osmnx 2.1.0 crashes on Indian
OSM data where many edges have NaN (not a string) in the maxspeed field.
We instead compute travel time directly from highway type, which is more
reliable for Bangalore roads anyway.
"""
from __future__ import annotations

import logging
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import networkx as nx

logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────
BANGALORE_CENTER = (12.9716, 77.5946)
GRAPH_RADIUS_M   = 12_000
CACHE_PATH       = Path(__file__).parent.parent / "data" / "bangalore_graph.pkl"
NETWORK_TYPE     = "drive"

# Speed by OSM highway type (km/h) — tuned for Bangalore road conditions
SPEED_KPH: Dict[str, float] = {
    "motorway":       80.0,
    "motorway_link":  60.0,
    "trunk":          60.0,
    "trunk_link":     50.0,
    "primary":        50.0,
    "primary_link":   40.0,
    "secondary":      40.0,
    "secondary_link": 30.0,
    "tertiary":       30.0,
    "tertiary_link":  25.0,
    "residential":    25.0,
    "unclassified":   20.0,
    "service":        15.0,
    "living_street":  10.0,
    "road":           25.0,
}
DEFAULT_SPEED_KPH = 25.0


class GraphManager:
    """Singleton that holds the OSMnx MultiDiGraph for Bangalore."""

    _instance: Optional["GraphManager"] = None
    G: Optional[nx.MultiDiGraph] = None

    def __new__(cls) -> "GraphManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ── Public API ────────────────────────────────────────────────────────────

    def load(self) -> None:
        """Load graph from cache or download from OSM."""
        if self.G is not None:
            return
        if CACHE_PATH.exists():
            logger.info("Loading graph from cache: %s", CACHE_PATH)
            self._load_cache()
        else:
            logger.info("Downloading Bangalore road network from OpenStreetMap …")
            self._download_and_cache()
        logger.info(
            "Graph ready — %d nodes, %d edges",
            self.G.number_of_nodes(),
            self.G.number_of_edges(),
        )

    def nearest_node(self, lat: float, lon: float) -> int:
        """Return the graph node ID nearest to (lat, lon)."""
        import osmnx as ox
        return ox.nearest_nodes(self.G, lon, lat)

    def node_coords(self, node_id: int) -> Tuple[float, float]:
        """Return (lat, lon) for a node ID."""
        data = self.G.nodes[node_id]
        return float(data["y"]), float(data["x"])

    def path_coords(self, path: List[int]) -> List[Dict[str, float]]:
        """Convert list of node IDs to list of {lat, lon} dicts."""
        return [
            {"lat": float(self.G.nodes[n]["y"]), "lon": float(self.G.nodes[n]["x"])}
            for n in path
        ]

    def edge_travel_time(self, u: int, v: int) -> float:
        """Travel time in minutes for edge (u, v). Uses best parallel edge."""
        edges = self.G[u][v]
        best = min(
            (e.get("travel_time", self._compute_travel_time(e)) for e in edges.values()),
            default=2.0,
        )
        return best / 60.0  # seconds → minutes

    def successors_unvisited(self, node: int, visited: set) -> List[int]:
        return [n for n in self.G.successors(node) if n not in visited]

    def graph_info(self) -> Dict:
        return {
            "nodes":      self.G.number_of_nodes(),
            "edges":      self.G.number_of_edges(),
            "area_km2":   round(3.14159 * (GRAPH_RADIUS_M / 1000) ** 2, 1),
            "center_lat": BANGALORE_CENTER[0],
            "center_lon": BANGALORE_CENTER[1],
            "cached":     CACHE_PATH.exists(),
        }

    # ── Private helpers ───────────────────────────────────────────────────────

    def _download_and_cache(self) -> None:
        import osmnx as ox

        G = ox.graph_from_point(
            BANGALORE_CENTER,
            dist=GRAPH_RADIUS_M,
            network_type=NETWORK_TYPE,
            simplify=True,
        )

        # ── Bypass ox.add_edge_speeds() — crashes on Indian OSM data ──
        # Many Bangalore roads have NaN or non-string maxspeed values.
        # We compute travel_time directly from highway type instead.
        logger.info("Computing edge travel times from highway type …")
        G = self._add_travel_times_safe(G)

        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_PATH, "wb") as f:
            pickle.dump(G, f, protocol=pickle.HIGHEST_PROTOCOL)
        logger.info("Graph cached to %s", CACHE_PATH)
        self.G = G

    def _add_travel_times_safe(self, G: nx.MultiDiGraph) -> nx.MultiDiGraph:
        """
        Add speed_kph and travel_time (seconds) to every edge.
        Uses highway tag → speed lookup. Never crashes on NaN maxspeed.
        """
        for u, v, k, data in G.edges(data=True, keys=True):
            speed = self._edge_speed_kph(data)
            length = float(data.get("length", 50.0))       # metres
            travel_time = length / (speed / 3.6)            # seconds
            G[u][v][k]["speed_kph"]    = speed
            G[u][v][k]["travel_time"]  = travel_time
        return G

    def _edge_speed_kph(self, edge_data: dict) -> float:
        """Get speed for an edge. Tries maxspeed first, falls back to highway type."""
        # Try maxspeed (OSM tag) — but it may be NaN, list, or garbage
        maxspeed = edge_data.get("maxspeed")
        if maxspeed is not None:
            try:
                if isinstance(maxspeed, list):
                    maxspeed = maxspeed[0]
                val = float(str(maxspeed).split()[0])
                if 5 <= val <= 130:
                    return val
            except (ValueError, TypeError):
                pass  # fall through to highway type lookup

        # Fall back to highway type
        highway = edge_data.get("highway", "road")
        if isinstance(highway, list):
            highway = highway[0]
        return SPEED_KPH.get(str(highway), DEFAULT_SPEED_KPH)

    def _compute_travel_time(self, edge_data: dict) -> float:
        """Compute travel time in seconds for an edge without pre-computed value."""
        length = float(edge_data.get("length", 50.0))
        speed  = self._edge_speed_kph(edge_data)
        return length / (speed / 3.6)

    def _load_cache(self) -> None:
        with open(CACHE_PATH, "rb") as f:
            self.G = pickle.load(f)


# Module-level singleton
graph_manager = GraphManager()