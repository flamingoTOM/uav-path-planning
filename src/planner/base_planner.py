"""
路径规划器抽象基类
@author: Based on example framework
@date: 2026-02-28
"""
from abc import ABC, abstractmethod
from typing import Tuple, List, Dict, Any
import time


class BasePlanner(ABC):
    """
    路径规划器抽象基类

    所有规划算法都应继承此类

    Args:
        map_: 地图对象
        start: 起点坐标
        goal: 终点坐标（对于覆盖规划可能为 None）
    """

    def __init__(self, map_, start: Tuple, goal: Tuple = None):
        self.map = map_
        self.start = start
        self.goal = goal
        self.path = []
        self.planning_time = 0.0

    @abstractmethod
    def plan(self) -> Tuple[List[Tuple], Dict[str, Any]]:
        """
        执行路径规划

        Returns:
            path: 规划的路径点列表
            info: 规划信息字典，包含：
                - cost: 路径代价
                - time: 规划时间
                - expand: 扩展节点数
                - coverage: 覆盖率（对于覆盖规划）
                - 其他算法相关信息
        """
        pass

    def _check_inputs(self) -> bool:
        """检查输入参数有效性"""
        if self.start is None:
            raise ValueError("起点不能为空")
        if not self.map.is_valid(self.start):
            raise ValueError(f"起点 {self.start} 不在地图范围内")
        if not self.map.is_free(self.start):
            raise ValueError(f"起点 {self.start} 不可通行")

        if self.goal is not None:
            if not self.map.is_valid(self.goal):
                raise ValueError(f"终点 {self.goal} 不在地图范围内")
            if not self.map.is_free(self.goal):
                raise ValueError(f"终点 {self.goal} 不可通行")
        return True

    def get_path_length(self, path: List[Tuple] = None) -> float:
        """计算路径长度"""
        if path is None:
            path = self.path
        if len(path) < 2:
            return 0.0

        length = 0.0
        for i in range(len(path) - 1):
            p1_world = self.map.map_to_world(path[i])
            p2_world = self.map.map_to_world(path[i + 1])
            length += np.linalg.norm(np.array(p2_world) - np.array(p1_world))
        return length

    def calculate_coverage(self, path: List[Tuple]) -> Dict[str, float]:
        """
        计算覆盖率指标

        Returns:
            coverage_info: 包含覆盖率、重复率等信息的字典
        """
        covered_cells = set(path)
        total_free_cells = np.sum(self.map.type_map == MapTypes.FREE)

        coverage_rate = len(covered_cells) / total_free_cells if total_free_cells > 0 else 0.0
        repeat_rate = (len(path) - len(covered_cells)) / len(path) if len(path) > 0 else 0.0

        return {
            "coverage_rate": coverage_rate,
            "repeat_rate": repeat_rate,
            "covered_cells": len(covered_cells),
            "total_free_cells": total_free_cells,
            "path_length_cells": len(path)
        }
