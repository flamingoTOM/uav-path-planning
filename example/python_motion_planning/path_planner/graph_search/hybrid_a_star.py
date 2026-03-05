"""
@file: hybrid_a_star.py
@author: Claude
@update: 2026.3.6
"""
from typing import Union
import heapq
import math

import numpy as np

from python_motion_planning.common import BaseMap, Grid, Node, TYPES
from python_motion_planning.path_planner import BasePathPlanner


class HybridAStar(BasePathPlanner):
    """
    Hybrid A* 路径规划器类。

    将 A* 扩展到连续 (x, y, theta) 状态空间，采用类车辆运动学模型。
    通过离散化状态进行访问状态检测，同时保持连续的运动轨迹。

    Args:
        map_: Grid 地图对象。
        start: 起点坐标 (x, y)，格点坐标系。
        goal: 终点坐标 (x, y)，格点坐标系。
        step_size: 每步仿真的弧长（格点单位），默认 3.0。
        n_steers: 离散转向角数量，默认 5。
        max_steer: 最大转向角（弧度），默认 0.6。
        xy_resolution: 状态离散化的空间分辨率，默认 2.0。
        theta_resolution: 状态离散化的角度分辨率（度），默认 15.0。
        wheel_base: 轴距（格点单位），默认 3.5。

    References:
        [1] Practical Search Techniques in Path Planning for Autonomous Driving
    """

    def __init__(self,
                 *args,
                 step_size: float = 3.0,
                 n_steers: int = 5,
                 max_steer: float = 0.6,
                 xy_resolution: float = 2.0,
                 theta_resolution: float = 15.0,
                 wheel_base: float = 3.5,
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.step_size = step_size
        self.n_steers = n_steers
        self.max_steer = max_steer
        self.xy_resolution = xy_resolution
        self.theta_resolution = math.radians(theta_resolution)
        self.wheel_base = wheel_base
        self.n_substeps = 5

    def __str__(self) -> str:
        return "Hybrid A*"

    def _discretize(self, x: float, y: float, theta: float) -> tuple:
        """将连续状态离散化为哈希键。"""
        xd = round(x / self.xy_resolution)
        yd = round(y / self.xy_resolution)
        n_bins = round(2 * math.pi / self.theta_resolution)
        td = round(theta / self.theta_resolution) % n_bins
        return (xd, yd, td)

    def _get_heuristic(self, x: float, y: float) -> float:
        """到目标点的欧氏距离启发值。"""
        gx, gy = float(self.goal[0]), float(self.goal[1])
        return math.hypot(x - gx, y - gy)

    def _in_collision(self, x: float, y: float) -> bool:
        """检查连续坐标 (x, y) 是否与栅格地图中的障碍物碰撞。"""
        ix, iy = int(round(x)), int(round(y))
        return not self.map_.is_expandable((ix, iy))

    def _simulate_motion(self, x: float, y: float, theta: float, steer: float):
        """
        用自行车运动学模型仿真一步运动。

        Returns:
            (new_x, new_y, new_theta)，若碰撞则返回 None。
        """
        dt = self.step_size / self.n_substeps
        cx, cy, ctheta = x, y, theta

        for _ in range(self.n_substeps):
            cx += dt * math.cos(ctheta)
            cy += dt * math.sin(ctheta)
            ctheta += dt * math.tan(steer) / self.wheel_base

            if self._in_collision(cx, cy):
                return None

        ctheta = math.atan2(math.sin(ctheta), math.cos(ctheta))
        return cx, cy, ctheta

    def plan(self) -> Union[list, dict]:
        """
        执行 Hybrid A* 路径规划。

        算法流程：
        1. 以起点和朝向目标的初始航向初始化搜索。
        2. 使用优先队列（最小堆），按 f = g + h 排序。
        3. 每次扩展时，遍历所有离散转向角，仿真运动学模型。
        4. 通过状态离散化避免重复访问相同格区。
        5. 当距目标点距离小于阈值时，回溯路径。

        Returns:
            path: 路径点列表（格点坐标）。
            path_info: 包含规划结果的字典。
        """
        sx, sy = float(self.start[0]), float(self.start[1])
        gx, gy = float(self.goal[0]), float(self.goal[1])

        init_theta = math.atan2(gy - sy, gx - sx)
        steers = np.linspace(-self.max_steer, self.max_steer, self.n_steers)

        start_key = self._discretize(sx, sy, init_theta)

        # states: key -> (x, y, theta, g, parent_key)
        states = {start_key: (sx, sy, init_theta, 0.0, None)}

        h0 = self._get_heuristic(sx, sy)
        counter = 0
        OPEN = [(h0, counter, start_key)]
        CLOSED = set()

        # For visualization: grid cell -> Node
        expand_cells = {}
        goal_key = None
        goal_tolerance = max(self.step_size * 1.5, self.xy_resolution * 2)

        while OPEN:
            _, _, key = heapq.heappop(OPEN)

            if key in CLOSED:
                continue
            CLOSED.add(key)

            x, y, theta, g, parent_key = states[key]

            # Record expanded cell for visualization
            grid_pt = (int(round(x)), int(round(y)))
            if grid_pt not in expand_cells:
                parent_grid = None
                if parent_key is not None:
                    px, py = states[parent_key][0], states[parent_key][1]
                    parent_grid = (int(round(px)), int(round(py)))
                expand_cells[grid_pt] = Node(
                    grid_pt, parent_grid, g, self._get_heuristic(x, y)
                )

            # Goal check
            if math.hypot(x - gx, y - gy) <= goal_tolerance:
                goal_key = key
                # Add goal cell to expand
                goal_grid = (int(round(gx)), int(round(gy)))
                if goal_grid not in expand_cells:
                    expand_cells[goal_grid] = Node(goal_grid, grid_pt, g, 0.0)
                break

            # Expand with discrete steering angles
            for steer in steers:
                result = self._simulate_motion(x, y, theta, steer)
                if result is None:
                    continue

                nx, ny, ntheta = result
                nkey = self._discretize(nx, ny, ntheta)

                if nkey in CLOSED:
                    continue

                ng = g + self.step_size
                nh = self._get_heuristic(nx, ny)
                nf = ng + nh

                if nkey not in states or ng < states[nkey][3]:
                    states[nkey] = (nx, ny, ntheta, ng, key)
                    counter += 1
                    heapq.heappush(OPEN, (nf, counter, nkey))

        if goal_key is None:
            self.failed_info[1]["expand"] = expand_cells
            return self.failed_info

        # Backtrack path
        path = []
        k = goal_key
        while k is not None:
            x, y, theta, g, pk = states[k]
            path.append((int(round(x)), int(round(y))))
            k = pk

        # Append actual goal point
        goal_pt = (int(round(gx)), int(round(gy)))
        if path[0] != goal_pt:
            path.insert(0, goal_pt)
        path = path[::-1]

        # Deduplicate while preserving order
        seen = set()
        deduped = []
        for pt in path:
            if pt not in seen:
                seen.add(pt)
                deduped.append(pt)

        length = sum(
            math.hypot(deduped[i + 1][0] - deduped[i][0],
                       deduped[i + 1][1] - deduped[i][1])
            for i in range(len(deduped) - 1)
        )

        return deduped, {
            "success": True,
            "start": self.start,
            "goal": self.goal,
            "length": length,
            "cost": length,
            "expand": expand_cells,
        }
