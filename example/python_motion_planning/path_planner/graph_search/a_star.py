"""
@file: a_star.py
@author: Wu Maojia
@update: 2025.10.3
"""
from typing import Union
import heapq
 
from python_motion_planning.common import BaseMap, Grid, Node, TYPES
from python_motion_planning.path_planner.graph_search.dijkstra import Dijkstra

class AStar(Dijkstra):
    """
       A* 路径规划器类。

       继承自 Dijkstra，主要区别在于：A* 在节点优先级计算中加入了启发式函数 `h(n)`，
       使得搜索更倾向于朝向目标点，从而减少搜索空间。

       Args:
           *args: 传递给父类 Dijkstra 的参数。
           *kwargs: 传递给父类 Dijkstra 的参数。

       References:
        [1] A Formal Basis for the heuristic Determination of Minimum Cost Paths

    Examples:
        >>> map_ = Grid(bounds=[[0, 15], [0, 15]])
        >>> planner = AStar(map_=map_, start=(5, 5), goal=(10, 10))
        >>> planner.plan()
        ([(5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)], {'success': True, 'start': (5, 5), 'goal': (10, 10), 'length': 7.0710678118654755, 'cost': 7.0710678118654755, 'expand': {(5, 5): Node((5, 5), None, 0, 7.0710678118654755), (6, 6): Node((6, 6), (5, 5), 1.4142135623730951, 5.656854249492381), (7, 7): Node((7, 7), (6, 6), 2.8284271247461903, 4.242640687119285), (8, 8): Node((8, 8), (7, 7), 4.242640687119286, 2.8284271247461903), (9, 9): Node((9, 9), (8, 8), 5.656854249492381, 1.4142135623730951), (10, 10): Node((10, 10), (9, 9), 7.0710678118654755, 0.0)}})

        >>> planner.map_.type_map[3:10, 6] = TYPES.OBSTACLE
        >>> planner.plan()
        ([(5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)], {'success': True, 'start': (5, 5), 'goal': (10, 10), 'length': 7.0710678118654755, 'cost': 7.0710678118654755, 'expand': {(5, 5): Node((5, 5), None, 0, 7.0710678118654755), (6, 6): Node((6, 6), (5, 5), 1.4142135623730951, 5.656854249492381), (7, 7): Node((7, 7), (6, 6), 2.8284271247461903, 4.242640687119285), (8, 8): Node((8, 8), (7, 7), 4.242640687119286, 2.8284271247461903), (9, 9): Node((9, 9), (8, 8), 5.656854249492381, 1.4142135623730951), (10, 10): Node((10, 10), (9, 9), 7.0710678118654755, 0.0)}})
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return "A*"

    def plan(self) -> Union[list, dict]:
        """
        执行 A* 路径规划。

        算法流程：
        1. 初始化 OPEN 队列（优先队列）和 CLOSED 集合。
        2. 将起始节点加入 OPEN 队列，其 `g=0`，`h=启发式值`。
        3. 循环：
            a. 从 OPEN 中弹出 f 值最小的节点。
            b. 若该节点为障碍物或已在 CLOSED 中，则跳过。
            c. 若该节点为目标点，则回溯路径并返回。
            d. 否则，遍历其所有邻居节点：
                - 若邻居已在 CLOSED 中，跳过。
                - 计算邻居的 `g` 值（从起点到邻居的实际代价）。
                - 计算邻居的 `h` 值（从邻居到目标的启发式估计代价）。
                - 若邻居是目标点，则加入 OPEN 并跳出循环。
                - 否则，将邻居加入 OPEN。
            e. 将当前节点加入 CLOSED。
        4. 若 OPEN 为空仍未找到目标，返回失败信息。

        Returns:
            path: 路径点列表，从起点到目标点的坐标序列。
            path_info: 包含规划结果的字典，包含：
                - `success`: 是否成功找到路径。
                - `start`: 起始点坐标。
                - `goal`: 目标点坐标。
                - `length`: 路径总长度（欧氏距离）。
                - `cost`: 路径总代价（与长度相同，除非使用非欧氏代价）。
                - `expand`: 所有扩展过的节点字典（用于可视化或调试）。
        """
        # OPEN list (priority queue) and CLOSED list (hash table)
        OPEN = []
        start_node = Node(self.start, None, 0, self.get_heuristic(self.start))
        heapq.heappush(OPEN, start_node)
        CLOSED = dict()

        while OPEN:
            node = heapq.heappop(OPEN)

            # obstacle found
            if not self.map_.is_expandable(node.current, node.parent):
                continue

            # exists in CLOSED list
            if node.current in CLOSED:
                continue

            # goal found
            if node.current == self.goal:
                CLOSED[node.current] = node
                path, length, cost = self.extract_path(CLOSED)
                return path, {
                    "success": True, 
                    "start": self.start, 
                    "goal": self.goal, 
                    "length": length, 
                    "cost": cost, 
                    "expand": CLOSED
                }

            for node_n in self.map_.get_neighbors(node): 
                # exists in CLOSED list
                if node_n.current in CLOSED:
                    continue

                node_n.g = node.g + self.get_cost(node.current, node_n.current)
                node_n.h = self.get_heuristic(node_n.current)

                # goal found
                if node_n.current == self.goal:
                    heapq.heappush(OPEN, node_n)
                    break
                
                # update OPEN list
                heapq.heappush(OPEN, node_n)

            CLOSED[node.current] = node

        self.failed_info[1]["expand"] = CLOSED
        return self.failed_info
