"""
@file: jps.py
@author: Claude
@update: 2026.03.02
"""
from typing import Union, Tuple, Optional
import heapq

from python_motion_planning.common import BaseMap, Grid, Node, TYPES
from python_motion_planning.path_planner.graph_search.a_star import AStar

class JPS(AStar):
    """
    JPS (Jump Point Search) 路径规划器类。

    这是一个简化的 JPS 实现，基于 A* 但通过跳点来减少扩展节点数。
    在遇到障碍物时会探索所有可行方向，确保能找到路径。

    Args:
        *args: 传递给父类 AStar 的参数。
        **kwargs: 传递给父类 AStar 的参数。

    References:
        [1] Harabor, D., & Grastien, A. (2011). Online Graph Pruning for Pathfinding on Grid Maps.

    Examples:
        >>> map_ = Grid(bounds=[[0, 15], [0, 15]])
        >>> planner = JPS(map_=map_, start=(5, 5), goal=(10, 10))
        >>> path, path_info = planner.plan()
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return "JPS"

    def is_walkable(self, x: int, y: int) -> bool:
        """
        检查点是否可行走（在地图范围内且不是障碍物）。

        Args:
            x: X 坐标
            y: Y 坐标

        Returns:
            bool: 点是否可行走
        """
        point = (x, y)
        if not self.map_.within_bounds(point):
            return False
        return self.map_.type_map[point] != TYPES.OBSTACLE

    def jump(self, x: int, y: int, dx: int, dy: int, max_steps: int = 1000) -> Optional[Tuple[int, int]]:
        """
        从 (x, y) 沿着 (dx, dy) 方向跳跃，寻找跳点。

        Args:
            x: 当前 X 坐标
            y: Y 坐标
            dx: X 方向增量 (-1, 0, 1)
            dy: Y 方向增量 (-1, 0, 1)
            max_steps: 最大跳跃步数

        Returns:
            Optional[Tuple[int, int]]: 跳点坐标，如果没有找到返回 None
        """
        for _ in range(max_steps):
            nx, ny = x + dx, y + dy

            # 如果下一个点不可行走，返回 None
            if not self.is_walkable(nx, ny):
                return None

            # 如果到达目标，返回该点
            if (nx, ny) == self.goal:
                return (nx, ny)

            # 对角线移动
            if dx != 0 and dy != 0:
                # 检查是否有强制邻居
                if (self.is_walkable(nx - dx, ny) and not self.is_walkable(nx - dx, y)) or \
                   (self.is_walkable(nx, ny - dy) and not self.is_walkable(x, ny - dy)):
                    return (nx, ny)

                # 在水平和垂直方向上寻找跳点
                if self.jump(nx, ny, dx, 0, max_steps // 2) is not None or \
                   self.jump(nx, ny, 0, dy, max_steps // 2) is not None:
                    return (nx, ny)

            # 水平或垂直移动
            else:
                if dx != 0:  # 水平移动
                    # 检查上下两侧的强制邻居
                    if (self.is_walkable(nx, ny + 1) and not self.is_walkable(x, y + 1)) or \
                       (self.is_walkable(nx, ny - 1) and not self.is_walkable(x, y - 1)):
                        return (nx, ny)
                else:  # 垂直移动
                    # 检查左右两侧的强制邻居
                    if (self.is_walkable(nx + 1, ny) and not self.is_walkable(x + 1, y)) or \
                       (self.is_walkable(nx - 1, ny) and not self.is_walkable(x - 1, y)):
                        return (nx, ny)

            # 继续跳跃
            x, y = nx, ny

        return None

    def find_neighbors(self, node: Node) -> list:
        """
        寻找当前节点的跳点邻居。
        这是一个简化版本，在找不到沿父方向的跳点时会探索所有方向。

        Args:
            node: 当前节点

        Returns:
            list: 跳点邻居列表（元组坐标）
        """
        x, y = node.current
        neighbors = []

        # 所有8个方向
        all_directions = [
            (0, 1), (1, 0), (0, -1), (-1, 0),  # 直线
            (1, 1), (1, -1), (-1, 1), (-1, -1)  # 对角线
        ]

        # 如果是起点，搜索所有方向
        if node.parent is None:
            for dx, dy in all_directions:
                jump_point = self.jump(x, y, dx, dy)
                if jump_point is not None:
                    neighbors.append(jump_point)
            return neighbors

        # 根据父节点确定优先方向
        px, py = node.parent
        dx_parent = x - px
        dy_parent = y - py

        # 归一化方向
        if dx_parent != 0:
            dx_parent = dx_parent // abs(dx_parent)
        if dy_parent != 0:
            dy_parent = dy_parent // abs(dy_parent)

        # 优先搜索方向（基于父方向的自然邻居和强制邻居）
        priority_directions = []

        # 对角线移动
        if dx_parent != 0 and dy_parent != 0:
            # 对角线、水平、垂直方向
            priority_directions = [
                (dx_parent, dy_parent),
                (dx_parent, 0),
                (0, dy_parent)
            ]

            # 强制邻居方向
            if not self.is_walkable(x - dx_parent, y):
                priority_directions.append((-dx_parent, dy_parent))
            if not self.is_walkable(x, y - dy_parent):
                priority_directions.append((dx_parent, -dy_parent))

        # 直线移动
        elif dx_parent != 0:  # 水平
            priority_directions.append((dx_parent, 0))
            # 强制邻居
            if not self.is_walkable(x, y + 1):
                priority_directions.append((dx_parent, 1))
            if not self.is_walkable(x, y - 1):
                priority_directions.append((dx_parent, -1))

        else:  # dy_parent != 0，垂直
            priority_directions.append((0, dy_parent))
            # 强制邻居
            if not self.is_walkable(x + 1, y):
                priority_directions.append((1, dy_parent))
            if not self.is_walkable(x - 1, y):
                priority_directions.append((-1, dy_parent))

        # 首先尝试优先方向
        for dx, dy in priority_directions:
            if self.is_walkable(x + dx, y + dy):
                jump_point = self.jump(x, y, dx, dy)
                if jump_point is not None:
                    neighbors.append(jump_point)

        # 如果优先方向没找到足够的邻居，尝试所有方向（确保能找到路径）
        if len(neighbors) == 0:
            for dx, dy in all_directions:
                if (dx, dy) not in priority_directions:
                    if self.is_walkable(x + dx, y + dy):
                        jump_point = self.jump(x, y, dx, dy)
                        if jump_point is not None:
                            neighbors.append(jump_point)

        return neighbors

    def plan(self) -> Union[list, dict]:
        """
        执行 JPS 路径规划。

        Returns:
            path: 路径点列表
            path_info: 路径信息字典
        """
        # OPEN list (priority queue) and CLOSED list (hash table)
        OPEN = []
        start_node = Node(self.start, None, 0, self.get_heuristic(self.start))
        heapq.heappush(OPEN, start_node)
        CLOSED = dict()

        while OPEN:
            node = heapq.heappop(OPEN)

            # exists in CLOSED list
            if node.current in CLOSED:
                continue

            # add to CLOSED
            CLOSED[node.current] = node

            # goal found
            if node.current == self.goal:
                path, length, cost = self.extract_path(CLOSED)
                return path, {
                    "success": True,
                    "start": self.start,
                    "goal": self.goal,
                    "length": length,
                    "cost": cost,
                    "expand": CLOSED
                }

            # find jump point neighbors
            neighbors = self.find_neighbors(node)

            for neighbor in neighbors:
                # exists in CLOSED list
                if neighbor in CLOSED:
                    continue

                # calculate g and h values
                g_new = node.g + self.get_cost(node.current, neighbor)
                h_new = self.get_heuristic(neighbor)

                # create new node and add to OPEN
                node_n = Node(neighbor, node.current, g_new, h_new)
                heapq.heappush(OPEN, node_n)

        self.failed_info[1]["expand"] = CLOSED
        return self.failed_info
