"""
@file: geometry.py
@author: Wu Maojia
@update: 2025.10.3
"""
from typing import List, Tuple
import math

import numpy as np

class Geometry:
    """
    几何工具类(静态方法集合)
    不需要创建对象:Geometry.dist(...) 这样直接用
    """

    @staticmethod
    def dist(p1: tuple, p2: tuple, type: str = 'Euclidean') -> float:
        if len(p1) != len(p2):
            raise ValueError(" 维度不一致 ")
        
        if type == 'Euclidean':     #欧式距离     sqrt((x1-x2)^2 + (y1-y2)^2)
            return math.sqrt(sum((a - b)** 2 for a, b in zip(p1, p2)))
        
        elif type == 'Manhattan':   #曼哈顿距离   |x1-x2| + |y1-y2|
            return sum(abs(a - b) for a, b in zip(p1, p2))
        else:
            raise ValueError("Invalid distance type")

    # @staticmethod
    # def angle(v1: tuple, v2: tuple) -> float:
    #     """
    #     Calculate the angle between two vectors

    #     Args:
    #         v1: First vector
    #         v2: Second vector

    #     Returns:
    #         angle_rad: Angle in rad between the two vectors
    #     """
    #     if len(v1) != len(v2):
    #         raise ValueError("Dimension mismatch")
        
    #     dot_product = sum(a * b for a, b in zip(v1, v2))
    #     v1_norm = math.sqrt(sum(a**2 for a in v1))
    #     v2_norm = math.sqrt(sum(b**2 for b in v2))
        
    #     if  v1_norm == 0 or v2_norm == 0:
    #         raise ValueError("Zero vector cannot calculate angle")

    #     cos_theta = dot_product / (v1_norm * v2_norm)

    #     cos_theta = min(1.0, max(-1.0, cos_theta))

    #     angle_rad = math.acos(cos_theta)
        
    #     return angle_rad

    @staticmethod
    def regularize_orient(orient: np.ndarray) -> np.ndarray:     #将角度规范化到区间 (-pi, pi] 内
        return np.mod(orient + np.pi, 2 * np.pi) - np.pi
        
    @staticmethod
    def add_orient_to_2d_path(path: List[Tuple[float, float]]) -> List[Tuple[float, float, float]]:
        """
        给一个二维路径（x, y 点序列）补充“朝向角 orient”，变成二维位姿序列 (x, y, theta)。

        朝向角的定义：
            每个点的 orient = 从当前点指向下一个点的方向角（弧度）
            orient = atan2(dy, dx)

        参数：
            path: 二维路径点列表，例如 [(x1,y1), (x2,y2), ...]

        返回：
            path_with_orient: 带朝向的路径，例如 [(x1,y1,theta1), (x2,y2,theta2), ...]
        """
        if len(path) < 2:
            return [(x, y, 0.0) for x, y in path]
        
        path_with_orient = []
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            
            dx = x2 - x1
            dy = y2 - y1
            
            orient = math.atan2(dy, dx)
            
            path_with_orient.append((x1, y1, orient))
        
        # last pose
        last_x, last_y = path[-1]
        path_with_orient.append((last_x, last_y, path_with_orient[-1][2]))
        
        return path_with_orient