"""
@file: prm.py
@author: Claude
@update: 2026.3.3
"""
import math
import random
import heapq
import numpy as np
from typing import Union, Dict, List, Tuple

from python_motion_planning.common import BaseMap, Node, TYPES, Grid
from python_motion_planning.path_planner import BasePathPlanner

class PRM(BasePathPlanner):
    """
    Class for PRM (Probabilistic Roadmap Method) path planner.

    PRM is a classical sampling-based path planning method proposed by Stanford
    University research team in 1996. It consists of two phases:
    1. Learning Phase: Randomly sample nodes in the space and connect them with
       a fast local planner to build a probabilistic roadmap.
    2. Query Phase: Search for a feasible path on the roadmap using graph search.

    Args:
        *args: see the parent class.
        sample_num: Number of random samples to generate (default: 500).
        k_neighbors: Number of nearest neighbors to connect (default: 10).
        max_edge_len: Maximum edge length for connections (default: 30.0).
        *kwargs: see the parent class.

    References:
        [1] Kavraki, L. E., Svestka, P., Latombe, J. C., & Overmars, M. H. (1996).
            Probabilistic roadmaps for path planning in high-dimensional
            configuration spaces. IEEE transactions on Robotics and Automation.

    Examples:
        >>> map_ = Grid(bounds=[[0, 15], [0, 15]])
        >>> planner = PRM(map_=map_, start=(5, 5), goal=(10, 10))
        >>> path, path_info = planner.plan()
        >>> print(path_info['success'])
        True
    """
    def __init__(self, *args,
                 sample_num: int = 500,
                 k_neighbors: int = 10,
                 max_edge_len: float = 30.0,
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Number of samples to generate
        self.sample_num = sample_num
        # Number of nearest neighbors to connect
        self.k_neighbors = k_neighbors
        # Maximum edge length
        self.max_edge_len = max_edge_len
        # Environment bounds from the map
        self.bounds = self.map_.bounds
        # Roadmap graph
        self.roadmap = {}

    def __str__(self) -> str:
        return "Probabilistic Roadmap Method (PRM)"

    def plan(self) -> Union[list, dict]:
        """
        PRM path planning algorithm implementation.

        Returns:
            path: A list containing the path waypoints
            path_info: A dictionary containing path information
        """
        # Learning Phase: Build roadmap
        self._build_roadmap()

        # Add start and goal to roadmap
        self._add_node_to_roadmap(self.start)
        self._add_node_to_roadmap(self.goal)

        # Query Phase: Search for path using A*
        path, cost = self._search_path()

        if path:
            return path, {
                "success": True,
                "start": self.start,
                "goal": self.goal,
                "length": len(path),
                "cost": cost,
                "expand": self.roadmap,
            }
        else:
            self.failed_info[1]["expand"] = self.roadmap
            return self.failed_info

    def _build_roadmap(self) -> None:
        """
        Build the probabilistic roadmap by sampling nodes and connecting them.
        """
        # Generate random samples
        samples = [self.start, self.goal]

        for _ in range(self.sample_num):
            sample = self._generate_random_node()
            # Skip if in collision or out of bounds
            if not self.map_.within_bounds(sample) or not self.map_.is_expandable(sample):
                continue
            samples.append(sample)

        # Build roadmap graph
        for sample in samples:
            node = Node(sample, None, 0, 0)
            self.roadmap[sample] = {
                'node': node,
                'neighbors': []
            }

        # Connect nodes to their k nearest neighbors
        for sample in samples:
            neighbors = self._get_k_nearest_neighbors(sample, samples)
            for neighbor in neighbors:
                # Check distance constraint
                dist = self.get_cost(sample, neighbor)
                if dist > self.max_edge_len:
                    continue

                # Check if edge is collision-free
                if not self.map_.in_collision(sample, neighbor):
                    # Add bidirectional edge
                    if neighbor not in self.roadmap[sample]['neighbors']:
                        self.roadmap[sample]['neighbors'].append(neighbor)
                    if sample not in self.roadmap[neighbor]['neighbors']:
                        self.roadmap[neighbor]['neighbors'].append(sample)

    def _add_node_to_roadmap(self, point: Tuple) -> None:
        """
        Add a node (start or goal) to the roadmap and connect it to neighbors.

        Args:
            point: Point to add to roadmap
        """
        if point not in self.roadmap:
            node = Node(point, None, 0, 0)
            self.roadmap[point] = {
                'node': node,
                'neighbors': []
            }

            # Connect to k nearest neighbors
            samples = list(self.roadmap.keys())
            neighbors = self._get_k_nearest_neighbors(point, samples)

            for neighbor in neighbors:
                if neighbor == point:
                    continue

                dist = self.get_cost(point, neighbor)
                if dist > self.max_edge_len:
                    continue

                if not self.map_.in_collision(point, neighbor):
                    if neighbor not in self.roadmap[point]['neighbors']:
                        self.roadmap[point]['neighbors'].append(neighbor)
                    if point not in self.roadmap[neighbor]['neighbors']:
                        self.roadmap[neighbor]['neighbors'].append(point)

    def _generate_random_node(self) -> Tuple:
        """
        Generate a random node within map bounds.

        Returns:
            point: Generated random point
        """
        point = []
        for d in range(self.map_.dim):
            d_min, d_max = self.bounds[d]
            point.append(random.randint(int(d_min), int(d_max)))
        return tuple(point)

    def _get_k_nearest_neighbors(self, point: Tuple,
                                  samples: List[Tuple]) -> List[Tuple]:
        """
        Find k nearest neighbors to a point.

        Args:
            point: Query point
            samples: List of sample points

        Returns:
            neighbors: List of k nearest neighbor points
        """
        # Calculate distances to all samples
        distances = []
        for sample in samples:
            if sample != point:
                dist = self.get_cost(point, sample)
                distances.append((dist, sample))

        # Sort by distance and return k nearest
        distances.sort(key=lambda x: x[0])
        k = min(self.k_neighbors, len(distances))
        return [sample for _, sample in distances[:k]]

    def _search_path(self) -> Tuple[List[Tuple], float]:
        """
        Search for a path from start to goal using A* on the roadmap.

        Returns:
            path: List of waypoints from start to goal
            cost: Total cost of the path
        """
        # A* search on the roadmap
        open_list = []
        closed_set = set()

        # Dictionary to store g values (cost from start)
        g_values = {self.start: 0}
        # Dictionary to store parent nodes
        parents = {self.start: None}

        # Add start node to open list
        h = self.get_heuristic(self.start)
        heapq.heappush(open_list, (h, self.start))

        while open_list:
            # Get node with lowest f value
            _, current = heapq.heappop(open_list)

            # Check if reached goal
            if current == self.goal:
                # Reconstruct path
                path = []
                cost = g_values[self.goal]
                while current is not None:
                    path.append(current)
                    current = parents[current]
                return path[::-1], cost

            # Skip if already processed
            if current in closed_set:
                continue

            closed_set.add(current)

            # Expand neighbors
            if current in self.roadmap:
                for neighbor in self.roadmap[current]['neighbors']:
                    if neighbor in closed_set:
                        continue

                    # Calculate tentative g value
                    tentative_g = g_values[current] + self.get_cost(current, neighbor)

                    # Update if better path found
                    if neighbor not in g_values or tentative_g < g_values[neighbor]:
                        g_values[neighbor] = tentative_g
                        parents[neighbor] = current
                        f = tentative_g + self.get_heuristic(neighbor)
                        heapq.heappush(open_list, (f, neighbor))

        # No path found
        return [], 0
