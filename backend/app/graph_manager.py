"""
Graph Manager — loads real Bangalore road network from OpenStreetMap via OSMnx.

Key improvement: Multi-hop subgraph expansion scales with distance.
Short routes get tight subgraphs; long routes get wider ones so ACO
has room to explore alternative paths.
"""
from __future__ import annotations

import logging
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import networkx as nx

logger = logging.getLogger(__name__)

BANGALORE_CENTER = (12.9716, 77.5946)
GRAPH_RADIUS_M   = 12_000
CACHE_PATH       = Path(__file__).parent.parent / "data" / "bangalore_graph.pkl"
NETWORK_TYPE     = "drive"

SPEED_KPH: Dict[str, float] = {
    "motorway":       80.0, "motorway_link":  60.0,
    "trunk":          60.0, "trunk_link":     50.0,
    "primary":        50.0, "primary_link":   40.0,
    "secondary":      40.0, "secondary_link": 30.0,
    "tertiary":       30.0, "tertiary_link":  25.0,
    "residential":    25.0, "unclassified":   20.0,
    "service":        15.0, "living_street":  10.0,
    "road":           25.0,
}
DEFAULT_SPEED_KPH = 25.0


def _weight_fn(u, v, d):
    return min((e.get("travel_time", 60.0) for e in d.values()), default=60.0)


class GraphManager:
    _instance: Optional["GraphManager"] = None
    G: Optional[nx.MultiDiGraph] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ── Public API ────────────────────────────────────────────────────────────

    def load(self) -> None:
        if self.G is not None:
            return
        if CACHE_PATH.exists():
            logger.info("Loading graph from cache: %s", CACHE_PATH)
            self._load_cache()
        else:
            logger.info("Downloading Bangalore road network from OpenStreetMap …")
            self._download_and_cache()
        logger.info("Graph ready — %d nodes, %d edges",
                    self.G.number_of_nodes(), self.G.number_of_edges())

    def nearest_node(self, lat: float, lon: float) -> int:
        import osmnx as ox
        return ox.nearest_nodes(self.G, lon, lat)

    def node_coords(self, node_id: int) -> Tuple[float, float]:
        d = self.G.nodes[node_id]
        return float(d["y"]), float(d["x"])

    def path_coords(self, path: List[int]) -> List[Dict[str, float]]:
        return [{"lat": float(self.G.nodes[n]["y"]),
                 "lon": float(self.G.nodes[n]["x"])} for n in path]

    def edge_travel_time(self, u: int, v: int, G: nx.MultiDiGraph = None) -> float:
        g = G if G is not None else self.G
        edges = g[u][v]
        best = min(
            (e.get("travel_time", self._compute_travel_time(e)) for e in edges.values()),
            default=2.0,
        )
        return best / 60.0

    def successors_unvisited(self, node: int, visited: set,
                              G: nx.MultiDiGraph = None) -> List[int]:
        g = G if G is not None else self.G
        return [n for n in g.successors(node) if n not in visited]

    def graph_info(self) -> Dict:
        return {
            "nodes":      self.G.number_of_nodes(),
            "edges":      self.G.number_of_edges(),
            "area_km2":   round(3.14159 * (GRAPH_RADIUS_M / 1000) ** 2, 1),
            "center_lat": BANGALORE_CENTER[0],
            "center_lon": BANGALORE_CENTER[1],
            "cached":     CACHE_PATH.exists(),
        }

    def subgraph_for_routing(self, source: int,
                              targets: Set[int]) -> nx.MultiDiGraph:
        """
        Build a routing subgraph wide enough to allow ACO exploration.

        Strategy:
          1. Find Dijkstra shortest path to EACH target (not just the closest).
             All paths combined = "route corridor" spanning the city.
          2. Expand radius proportional to corridor length — wider corridor
             for longer routes so ants have room to explore alternatives.
          3. Cap subgraph size to keep ACO tractable.
        """
        core: Set[int] = {source}

        # 1. Collect shortest paths to every reachable target
        path_lengths: List[int] = []
        for target in targets:
            try:
                path = nx.shortest_path(self.G, source, target, weight=_weight_fn)
                core.update(path)
                path_lengths.append(len(path))
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                continue

        if not path_lengths:
            # Source is isolated — return empty subgraph with source + targets
            logger.warning("No Dijkstra path found from source to any target")
            ego = nx.ego_graph(self.G, source, radius=50, undirected=True)
            core |= set(ego.nodes)
            core |= targets
            return self.G.subgraph(core).copy()

        # 2. Expansion radius scales with longest path
        # Short route (20 hops)  → radius 2 (small subgraph, fast ACO)
        # Medium route (100 hops) → radius 3
        # Long route  (500 hops) → radius 4
        max_path_len = max(path_lengths)
        if   max_path_len < 30:   radius = 2
        elif max_path_len < 100:  radius = 2
        elif max_path_len < 300:  radius = 3
        else:                     radius = 3   # cap at 3 to keep subgraph bounded

        logger.info("Corridor length %d hops → expansion radius %d",
                    max_path_len, radius)

        # 3. BFS expansion around every core node
        expanded: Set[int] = set(core)
        frontier = set(core)
        for _ in range(radius):
            next_frontier: Set[int] = set()
            for node in frontier:
                # Add both predecessors and successors for bidirectional coverage
                next_frontier.update(self.G.successors(node))
                next_frontier.update(self.G.predecessors(node))
            next_frontier -= expanded  # only genuinely new nodes
            expanded.update(next_frontier)
            frontier = next_frontier

            # Safety cap — keep subgraph tractable for ACO
            if len(expanded) > 8000:
                logger.info("Subgraph reached cap at 8000 nodes (radius used: partial)")
                break

        # Always include all targets so ACO has something to aim for
        expanded.update(targets)

        sub = self.G.subgraph(expanded).copy()

        # 4. Connectivity sanity check — ensure at least one target is reachable
        reachable_targets = targets & set(sub.nodes)
        if not reachable_targets or source not in sub.nodes:
            logger.warning("Subgraph disconnected — falling back to full graph")
            return self.G

        # Verify source can actually reach at least one target in subgraph
        try:
            for t in reachable_targets:
                if nx.has_path(sub, source, t):
                    break
            else:
                logger.warning("No reachable target in subgraph — using full graph")
                return self.G
        except nx.NodeNotFound:
            return self.G

        logger.info("Subgraph built — %d nodes, %d edges (from %d core nodes, radius %d)",
                    sub.number_of_nodes(), sub.number_of_edges(), len(core), radius)
        return sub

    def dijkstra_path(self, source: int,
                      targets: Dict[str, int]) -> Tuple[str, float, List[int]]:
        best_id, best_cost, best_path = None, float("inf"), []
        for hid, tnode in targets.items():
            try:
                cost, path = nx.single_source_dijkstra(
                    self.G, source, tnode, weight=_weight_fn, cutoff=180 * 60,
                )
                cost_min = cost / 60.0
                if cost_min < best_cost:
                    best_cost, best_id, best_path = cost_min, hid, path
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                continue
        return best_id, best_cost, best_path

    # ── Private ───────────────────────────────────────────────────────────────

    def _download_and_cache(self) -> None:
        import osmnx as ox
        G = ox.graph_from_point(BANGALORE_CENTER, dist=GRAPH_RADIUS_M,
                                network_type=NETWORK_TYPE, simplify=True)
        logger.info("Computing edge travel times …")
        G = self._add_travel_times_safe(G)
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_PATH, "wb") as f:
            pickle.dump(G, f, protocol=pickle.HIGHEST_PROTOCOL)
        logger.info("Graph cached to %s", CACHE_PATH)
        self.G = G

    def _add_travel_times_safe(self, G: nx.MultiDiGraph) -> nx.MultiDiGraph:
        for u, v, k, data in G.edges(data=True, keys=True):
            speed  = self._edge_speed_kph(data)
            length = float(data.get("length", 50.0))
            G[u][v][k]["speed_kph"]   = speed
            G[u][v][k]["travel_time"] = length / (speed / 3.6)
        return G

    def _edge_speed_kph(self, data: dict) -> float:
        maxspeed = data.get("maxspeed")
        if maxspeed is not None:
            try:
                if isinstance(maxspeed, list):
                    maxspeed = maxspeed[0]
                val = float(str(maxspeed).split()[0])
                if 5 <= val <= 130:
                    return val
            except (ValueError, TypeError):
                pass
        highway = data.get("highway", "road")
        if isinstance(highway, list):
            highway = highway[0]
        return SPEED_KPH.get(str(highway), DEFAULT_SPEED_KPH)

    def _compute_travel_time(self, data: dict) -> float:
        length = float(data.get("length", 50.0))
        speed  = self._edge_speed_kph(data)
        return length / (speed / 3.6)

    def _load_cache(self) -> None:
        with open(CACHE_PATH, "rb") as f:
            self.G = pickle.load(f)


graph_manager = GraphManager()