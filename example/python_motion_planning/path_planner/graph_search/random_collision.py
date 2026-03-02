"""
@file: random_collision.py
@author: Claude
@update: 2026.03.02
"""
from typing import Union
import random
import numpy as np

from python_motion_planning.common import BaseMap, Grid, Node, TYPES
from python_motion_planning.path_planner import BasePathPlanner

class RandomCollision(BasePathPlanner):
    """
    随机碰撞算法 (Random Collision Algorithm)

    用于全覆盖路径规划的简单算法。机器人沿直线前进，遇到障碍物时随机改变到任意方向。

    Args:
        map_: 地图对象
        start: 起点坐标
        goal: 目标点坐标（用于计算覆盖区域）
        max_steps: 最大步数（默认3000）
        max_collisions: 最大碰撞次数（默认16）

    Examples:
        >>> map_ = Grid(bounds=[[0, 101], [0, 51]])
        >>> planner = RandomCollision(map_=map_, start=(10, 25), goal=(90, 25))
        >>> path, path_info = planner.plan()
    """
    def __init__(self, map_: BaseMap, start: tuple, goal: tuple, max_steps: int = 3000, max_collisions: int = 16) -> None:
        super().__init__(map_, start, goal)
        self.max_steps = max_steps
        self.max_collisions = max_collisions

    def __str__(self) -> str:
        return "Random Collision"

    def is_valid(self, point: tuple) -> bool:
        """检查点是否有效"""
        if not self.map_.within_bounds(point):
            return False
        return self.map_.type_map[point] != TYPES.OBSTACLE

    def get_next_point(self, current: tuple, angle: float, distance: int = 3) -> tuple:
        """根据当前位置和角度计算下一个网格点（可以移动多个单位）"""
        x, y = current
        dx = np.cos(angle) * distance
        dy = np.sin(angle) * distance
        # 移动多个网格单位
        next_x = int(round(x + dx))
        next_y = int(round(y + dy))
        return (next_x, next_y)

    def get_random_angle(self) -> float:
        """生成随机角度（0到2π）"""
        return random.uniform(0, 2 * np.pi)

    def plan(self) -> Union[list, dict]:
        """
        执行随机碰撞覆盖规划

        Returns:
            path: 覆盖路径点列表
            path_info: 包含覆盖信息的字典
        """
        path = [self.start]
        visited = {self.start: Node(self.start, None, 0, 0)}
        current = self.start
        current_angle = self.get_random_angle()
        current_distance = random.randint(2, 5)
        collision_count = 0

        for step in range(self.max_steps):
            # 检查是否达到碰撞次数限制
            if collision_count >= self.max_collisions:
                break

            # 尝试沿当前角度前进
            next_point = self.get_next_point(current, current_angle, distance=current_distance)

            # 检查是否可以前进
            if self.is_valid(next_point) and next_point != current:
                current = next_point
                path.append(current)

                # 记录访问的节点
                if current not in visited:
                    parent = path[-2] if len(path) >= 2 else None
                    visited[current] = Node(current, parent, len(path), 0)
            else:
                # 碰撞！随机选择任意新角度和新距离
                collision_count += 1

                # 尝试找到一个有效的随机角度和距离
                max_attempts = 100
                for _ in range(max_attempts):
                    current_angle = self.get_random_angle()
                    current_distance = random.randint(2, 5)
                    next_point = self.get_next_point(current, current_angle, distance=current_distance)
                    if self.is_valid(next_point) and next_point != current:
                        break
                else:
                    # 找不到有效方向，停止
                    break

        # 计算路径长度
        length = 0
        cost = 0
        for i in range(1, len(path)):
            length += self.map_.get_distance(path[i-1], path[i])
            cost += self.get_cost(path[i-1], path[i])

        return path, {
            "success": True,
            "start": self.start,
            "goal": self.goal,
            "length": length,
            "cost": cost,
            "expand": visited
        }
