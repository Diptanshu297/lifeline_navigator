"""
ACO with MMAS on a focused subgraph extracted from the full Bangalore road network.
Works on ~500-3000 node subgraphs, not the full 134k graph.
"""
from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

import networkx as nx

logger = logging.getLogger(__name__)


@dataclass
class AntPath:
    nodes: List[int]
    cost:  float
    dest:  int


@dataclass
class ACOResult:
    best_path:        List[int]
    best_cost:        float
    best_dest:        int
    converged_at:     int
    convergence_data: List[float]
    nodes_explored:   int
    total_ants:       int
    elapsed_sec:      float


class ACO:
    def __init__(self, gm, alpha=1.0, beta=2.0, rho=0.15,
                 Q=100.0, tau_min=0.01, tau_max=5.0, elite_ants=3):
        self.gm         = gm
        self.alpha      = alpha
        self.beta       = beta
        self.rho        = rho
        self.Q          = Q
        self.tau_min    = tau_min
        self.tau_max    = tau_max
        self.elite_ants = elite_ants
        self._pheromone: Dict[Tuple[int, int], float] = {}

    def run(self, source: int, targets: Set[int], cap_penalty: Dict[int, float],
            n_ants: int = 20, n_iterations: int = 40) -> ACOResult:

        t0 = time.perf_counter()

        # ── Build focused subgraph ─────────────────────────────────────────
        logger.info("Building routing subgraph …")
        sub_G = self.gm.subgraph_for_routing(source, targets)
        n_sub = sub_G.number_of_nodes()
        logger.info("Subgraph: %d nodes, %d edges", n_sub, sub_G.number_of_edges())

        # Verify source and at least one target exist in subgraph
        reachable_targets = targets & set(sub_G.nodes)
        if source not in sub_G.nodes or not reachable_targets:
            logger.warning("Source or targets not in subgraph — falling back to Dijkstra only")
            return self._empty_result(n_ants * n_iterations, time.perf_counter() - t0)

        self._init_pheromone(sub_G)

        best_path:  Optional[List[int]] = None
        best_cost   = float("inf")
        best_dest:  Optional[int] = None
        converged_at = 1
        convergence: List[float] = []
        nodes_explored = 0
        # max_steps scales with subgraph size — always enough to traverse it
        max_steps = max(800, n_sub * 2)

        for iteration in range(1, n_iterations + 1):
            results: List[AntPath] = []

            for _ in range(n_ants):
                path = self._ant_walk(source, reachable_targets,
                                     cap_penalty, sub_G, max_steps)
                if path is not None:
                    results.append(path)
                    nodes_explored += len(path.nodes)

            self._evaporate()

            for r in results:
                self._deposit(r)

            if best_path is not None and self.elite_ants > 0:
                self._deposit_elite(best_path, best_cost)

            if results:
                iter_best = min(results, key=lambda r: r.cost)
                if iter_best.cost < best_cost:
                    best_cost    = iter_best.cost
                    best_path    = iter_best.nodes
                    best_dest    = iter_best.dest
                    converged_at = iteration

            convergence.append(best_cost if best_cost < float("inf") else 0.0)

        elapsed = time.perf_counter() - t0
        logger.info("ACO done %.2fs — best %.2f min at iter %d",
                    elapsed, best_cost, converged_at)

        return ACOResult(
            best_path        = best_path or [],
            best_cost        = best_cost,
            best_dest        = best_dest or -1,
            converged_at     = converged_at,
            convergence_data = convergence,
            nodes_explored   = nodes_explored,
            total_ants       = n_ants * n_iterations,
            elapsed_sec      = elapsed,
        )

    # ── Private ───────────────────────────────────────────────────────────────

    def _init_pheromone(self, G: nx.MultiDiGraph):
        tau0 = (self.tau_min + self.tau_max) / 2
        self._pheromone = {(u, v): tau0 for u, v, _ in G.edges(data=True)}

    def _ant_walk(self, source, targets, cap_penalty,
                  G: nx.MultiDiGraph, max_steps: int) -> Optional[AntPath]:
        current  = source
        path     = [source]
        visited: Set[int] = {source}
        cost     = 0.0

        for _ in range(max_steps):
            if current in targets:
                return AntPath(nodes=path, cost=cost, dest=current)

            neighbors = [n for n in G.successors(current) if n not in visited]
            if not neighbors:
                return None

            # Shortcut: jump directly to target if it's a neighbour
            t_neighbors = [n for n in neighbors if n in targets]
            if t_neighbors:
                nxt = t_neighbors[0]
                cost += self.gm.edge_travel_time(current, nxt, G) * cap_penalty.get(nxt, 1.0)
                path.append(nxt)
                return AntPath(nodes=path, cost=cost, dest=nxt)

            nxt = self._select_next(current, neighbors, cap_penalty, G)
            cost += self.gm.edge_travel_time(current, nxt, G) * cap_penalty.get(nxt, 1.0)
            path.append(nxt)
            visited.add(nxt)
            current = nxt

        if current in targets:
            return AntPath(nodes=path, cost=cost, dest=current)
        return None

    def _select_next(self, current, neighbors, cap_penalty, G) -> int:
        scores: List[float] = []
        for n in neighbors:
            tau = self._pheromone.get((current, n), self.tau_min)
            t   = self.gm.edge_travel_time(current, n, G)
            p   = cap_penalty.get(n, 1.0)
            eta = 1.0 / (t * p) if t * p > 0 else 1.0
            scores.append((tau ** self.alpha) * (eta ** self.beta))

        total = sum(scores)
        if total == 0:
            return random.choice(neighbors)
        r = random.random() * total
        for node, score in zip(neighbors, scores):
            r -= score
            if r <= 0:
                return node
        return neighbors[-1]

    def _evaporate(self):
        for key in self._pheromone:
            self._pheromone[key] = max(
                self.tau_min, (1.0 - self.rho) * self._pheromone[key])

    def _deposit(self, path: AntPath):
        if path.cost <= 0:
            return
        delta = self.Q / path.cost
        for i in range(len(path.nodes) - 1):
            u, v = path.nodes[i], path.nodes[i + 1]
            if (u, v) in self._pheromone:
                self._pheromone[(u, v)] = min(
                    self.tau_max, self._pheromone[(u, v)] + delta)

    def _deposit_elite(self, path: List[int], cost: float):
        if cost <= 0:
            return
        delta = self.elite_ants * self.Q / cost
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            if (u, v) in self._pheromone:
                self._pheromone[(u, v)] = min(
                    self.tau_max, self._pheromone[(u, v)] + delta)

    @staticmethod
    def _empty_result(total_ants: int, elapsed: float) -> ACOResult:
        return ACOResult(
            best_path=[], best_cost=float("inf"), best_dest=-1,
            converged_at=0, convergence_data=[], nodes_explored=0,
            total_ants=total_ants, elapsed_sec=elapsed,
        )