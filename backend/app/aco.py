"""
Ant Colony Optimization (ACO) with MMAS on real OSMnx road network.

Key upgrades vs basic ACO:
  - MMAS: pheromone clamped to [τ_min, τ_max] prevents stagnation
  - Elite ants: reinforce global best path each iteration
  - Multi-target: ants walk toward any eligible hospital (set of targets)
  - Hospital capacity penalty: full hospitals get higher effective cost
  - Time-of-day factor: optional traffic multiplier
"""
from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from .graph_manager import GraphManager

logger = logging.getLogger(__name__)


@dataclass
class AntPath:
    nodes:  List[int]
    cost:   float          # total travel time in minutes
    dest:   int            # destination hospital node


@dataclass
class ACOResult:
    best_path:         List[int]
    best_cost:         float           # minutes
    best_dest:         int
    converged_at:      int
    convergence_data:  List[float]     # best cost after each iteration
    nodes_explored:    int
    total_ants:        int
    elapsed_sec:       float


class ACO:
    """
    Ant Colony Optimization for emergency vehicle routing.

    Parameters
    ----------
    gm          : GraphManager — loaded road network
    alpha       : pheromone exponent (exploitation)
    beta        : heuristic exponent (exploration)
    rho         : evaporation rate
    Q           : pheromone deposit constant
    tau_min     : MMAS lower bound
    tau_max     : MMAS upper bound
    elite_ants  : number of extra elite reinforcements of global best per iteration
    """

    def __init__(
        self,
        gm:         GraphManager,
        alpha:      float = 1.0,
        beta:       float = 2.0,
        rho:        float = 0.15,
        Q:          float = 100.0,
        tau_min:    float = 0.01,
        tau_max:    float = 5.0,
        elite_ants: int   = 3,
    ) -> None:
        self.gm         = gm
        self.alpha      = alpha
        self.beta       = beta
        self.rho        = rho
        self.Q          = Q
        self.tau_min    = tau_min
        self.tau_max    = tau_max
        self.elite_ants = elite_ants

        # Pheromone matrix: {(u, v): float}
        self._pheromone: Dict[Tuple[int, int], float] = {}

    # ── Public ────────────────────────────────────────────────────────────────

    def run(
        self,
        source:         int,
        targets:        Set[int],
        cap_penalty:    Dict[int, float],
        n_ants:         int   = 20,
        n_iterations:   int   = 40,
    ) -> ACOResult:
        """
        Run ACO from source node toward any node in targets.

        cap_penalty maps hospital node_id → capacity penalty multiplier (≥ 1.0).
        """
        t0 = time.perf_counter()
        self._init_pheromone()

        best_path:   Optional[List[int]] = None
        best_cost:   float               = float("inf")
        best_dest:   Optional[int]       = None
        converged_at = 1
        convergence: List[float]         = []
        nodes_explored = 0

        for iteration in range(1, n_iterations + 1):
            results: List[AntPath] = []

            for _ in range(n_ants):
                path = self._ant_walk(source, targets, cap_penalty)
                if path is not None:
                    results.append(path)
                    nodes_explored += len(path.nodes)

            # Evaporate
            self._evaporate()

            # Deposit
            for r in results:
                self._deposit(r)

            # Elite reinforcement on global best
            if best_path is not None and self.elite_ants > 0:
                self._deposit_elite(best_path, best_cost)

            # Update global best
            if results:
                iter_best = min(results, key=lambda r: r.cost)
                if iter_best.cost < best_cost:
                    best_cost  = iter_best.cost
                    best_path  = iter_best.nodes
                    best_dest  = iter_best.dest
                    converged_at = iteration

            convergence.append(best_cost if best_cost < float("inf") else 0.0)

        elapsed = time.perf_counter() - t0
        logger.info(
            "ACO done in %.2fs — best cost %.2f min at iter %d",
            elapsed, best_cost, converged_at,
        )

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

    def _init_pheromone(self) -> None:
        """Initialise uniform pheromone on all edges."""
        tau0 = (self.tau_min + self.tau_max) / 2
        self._pheromone = {
            (u, v): tau0
            for u, v, _ in self.gm.G.edges(data=True)
        }

    def _ant_walk(
        self,
        source:      int,
        targets:     Set[int],
        cap_penalty: Dict[int, float],
    ) -> Optional[AntPath]:
        """Single ant constructs a path from source to any target."""
        current  = source
        path     = [source]
        visited: Set[int] = {source}
        cost     = 0.0
        max_steps = min(500, len(self.gm.G.nodes) // 2)

        for _ in range(max_steps):
            if current in targets:
                return AntPath(nodes=path, cost=cost, dest=current)

            neighbors = self.gm.successors_unvisited(current, visited)
            if not neighbors:
                return None

            next_node = self._select_next(current, neighbors, cap_penalty)
            edge_cost = self.gm.edge_travel_time(current, next_node)
            # Apply hospital capacity penalty at destination nodes
            penalty   = cap_penalty.get(next_node, 1.0)
            cost     += edge_cost * penalty

            path.append(next_node)
            visited.add(next_node)
            current = next_node

        # Check if we ended at a target
        if current in targets:
            return AntPath(nodes=path, cost=cost, dest=current)
        return None

    def _select_next(
        self,
        current:     int,
        neighbors:   List[int],
        cap_penalty: Dict[int, float],
    ) -> int:
        """Roulette-wheel selection using pheromone × heuristic."""
        scores: List[float] = []
        for n in neighbors:
            tau = self._pheromone.get((current, n), self.tau_min)
            t   = self.gm.edge_travel_time(current, n)
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

    def _evaporate(self) -> None:
        """Apply MMAS evaporation: τ ← max(τ_min, (1−ρ)·τ)."""
        for key in self._pheromone:
            self._pheromone[key] = max(
                self.tau_min,
                (1.0 - self.rho) * self._pheromone[key],
            )

    def _deposit(self, path: AntPath) -> None:
        """Deposit pheromone: Δτ = Q / L_a, clamped to τ_max."""
        if path.cost <= 0:
            return
        delta = self.Q / path.cost
        for i in range(len(path.nodes) - 1):
            u, v = path.nodes[i], path.nodes[i + 1]
            if (u, v) in self._pheromone:
                self._pheromone[(u, v)] = min(
                    self.tau_max,
                    self._pheromone[(u, v)] + delta,
                )

    def _deposit_elite(self, path: List[int], cost: float) -> None:
        """Elite ants deposit extra on the global best path."""
        if cost <= 0:
            return
        delta = self.elite_ants * self.Q / cost
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            if (u, v) in self._pheromone:
                self._pheromone[(u, v)] = min(
                    self.tau_max,
                    self._pheromone[(u, v)] + delta,
                )
