"""
2D 栅格地图实现
基于 example 框架的 Grid 类
@author: Based on example framework
@date: 2026-02-28
"""
from typing import Tuple, List
import numpy as np
from scipy import ndimage

from .base_map import BaseMap
from .map_types import MapTypes


class Grid2D(BaseMap):
    """
    2D 栅格地图类

    Args:
        bounds: 世界坐标范围 [[x_min, x_max], [y_min, y_max]]
        resolution: 栅格分辨率（米/格），默认 1.0
        type_map: 初始类型图，shape 需匹配计算出的栅格尺寸
        inflation_radius: 障碍膨胀半径（格），默认 0

    Examples:
        >>> map_2d = Grid2D(bounds=[[0, 100], [0, 50]], resolution=1.0)
        >>> map_2d.shape
        (100, 50)
        >>> map_2d.add_obstacle([10, 10], [20, 20])
        >>> map_2d.inflate_obstacles(radius=2.0)
    """

    def __init__(self,
                 bounds: np.ndarray = [[0, 100], [0, 50]],
                 resolution: float = 1.0,
                 type_map: np.ndarray = None,
                 inflation_radius: float = 0.0) -> None:
        super().__init__(bounds, resolution, dtype=np.int32)

        # 计算栅格尺寸
        self._shape = tuple([
            int((self.bounds[i, 1] - self.bounds[i, 0]) / self.resolution)
            for i in range(self.dim)
        ])

        # 初始化类型图
        if type_map is None:
            self._type_map = np.zeros(self._shape, dtype=np.int8)
        else:
            if type_map.shape != self._shape:
                raise ValueError(f"type_map 的形状必须是 {self._shape}，而不是 {type_map.shape}")
            self._type_map = np.asarray(type_map, dtype=np.int8)

        # 初始化 ESDF（欧几里得符号距离场）
        self._esdf = np.zeros(self._shape, dtype=np.float32)

        # 障碍膨胀
        if inflation_radius >= 1.0:
            self.inflate_obstacles(inflation_radius)

    @property
    def shape(self) -> Tuple[int, int]:
        """返回栅格地图尺寸"""
        return self._shape

    @property
    def type_map(self) -> np.ndarray:
        """返回类型图"""
        return self._type_map

    @property
    def esdf(self) -> np.ndarray:
        """返回欧几里得符号距离场"""
        return self._esdf

    def map_to_world(self, point: Tuple[int, int]) -> Tuple[float, float]:
        """
        地图坐标 -> 世界坐标
        point: (i, j) 栅格索引
        return: (x, y) 世界坐标（米）
        """
        if len(point) != self.dim:
            raise ValueError("点的维度与地图维度不匹配")
        return tuple(
            (point[i] + 0.5) * self.resolution + float(self.bounds[i, 0])
            for i in range(self.dim)
        )

    def world_to_map(self, point: Tuple[float, float]) -> Tuple[int, int]:
        """
        世界坐标 -> 地图坐标
        point: (x, y) 世界坐标（米）
        return: (i, j) 栅格索引
        """
        if len(point) != self.dim:
            raise ValueError("点的维度与地图维度不匹配")
        return tuple(
            int(round((point[i] - float(self.bounds[i, 0])) / self.resolution - 0.5))
            for i in range(self.dim)
        )

    def is_valid(self, point: Tuple[int, int]) -> bool:
        """检查点是否在地图范围内"""
        return all(0 <= point[i] < self.shape[i] for i in range(self.dim))

    def is_free(self, point: Tuple[int, int]) -> bool:
        """检查点是否可通行（非障碍物且非膨胀区）"""
        if not self.is_valid(point):
            return False
        return (self._type_map[point] != MapTypes.OBSTACLE and
                self._type_map[point] != MapTypes.INFLATION)

    def in_collision(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> bool:
        """检查两点连线是否与障碍物碰撞"""
        if not self.is_free(p1) or not self.is_free(p2):
            return True

        # Bresenham 直线算法检查路径
        line_points = self._bresenham_line(p1, p2)
        for point in line_points:
            if not self.is_free(point):
                return True
        return False

    def get_neighbors(self, point: Tuple[int, int], diagonal: bool = True) -> List[Tuple[int, int]]:
        """
        获取邻居节点
        diagonal: 是否包含对角邻居
        """
        neighbors = []
        if diagonal:
            # 8 邻域
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    neighbor = (point[0] + di, point[1] + dj)
                    if self.is_valid(neighbor) and self.is_free(neighbor):
                        neighbors.append(neighbor)
        else:
            # 4 邻域（上下左右）
            for di, dj in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                neighbor = (point[0] + di, point[1] + dj)
                if self.is_valid(neighbor) and self.is_free(neighbor):
                    neighbors.append(neighbor)
        return neighbors

    def add_obstacle(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> None:
        """添加矩形障碍物区域 [p1, p2]"""
        i_min, i_max = min(p1[0], p2[0]), max(p1[0], p2[0])
        j_min, j_max = min(p1[1], p2[1]), max(p1[1], p2[1])
        self._type_map[i_min:i_max+1, j_min:j_max+1] = MapTypes.OBSTACLE

    def fill_boundary_with_obstacles(self) -> None:
        """将地图边界填充为障碍物"""
        self._type_map[0, :] = MapTypes.OBSTACLE
        self._type_map[-1, :] = MapTypes.OBSTACLE
        self._type_map[:, 0] = MapTypes.OBSTACLE
        self._type_map[:, -1] = MapTypes.OBSTACLE

    def update_esdf(self) -> None:
        """更新欧几里得符号距离场（ESDF）"""
        obstacle_mask = (self._type_map == MapTypes.OBSTACLE)
        free_mask = ~obstacle_mask

        # 到障碍物的距离
        dist_outside = ndimage.distance_transform_edt(free_mask, sampling=self.resolution)
        # 障碍物内部距离
        dist_inside = ndimage.distance_transform_edt(obstacle_mask, sampling=self.resolution)

        self._esdf = dist_outside.astype(np.float32)
        self._esdf[obstacle_mask] = -dist_inside[obstacle_mask]

    def inflate_obstacles(self, radius: float) -> None:
        """
        障碍物膨胀
        将障碍物周围 radius 米内的区域标记为 INFLATION
        """
        self.update_esdf()
        mask = (self._esdf <= radius) & (self._type_map == MapTypes.FREE)
        self._type_map[mask] = MapTypes.INFLATION

    def _bresenham_line(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Bresenham 直线算法
        返回从 p1 到 p2 的栅格路径
        """
        x0, y0 = p1
        x1, y1 = p2
        points = []

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        x, y = x0, y0
        while True:
            points.append((x, y))
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

        return points

    def save(self, filepath: str) -> None:
        """保存地图到文件"""
        np.save(filepath, {
            'type_map': self._type_map,
            'bounds': self._bounds,
            'resolution': self._resolution
        })

    @classmethod
    def load(cls, filepath: str) -> 'Grid2D':
        """从文件加载地图"""
        data = np.load(filepath, allow_pickle=True).item()
        return cls(
            bounds=data['bounds'],
            resolution=data['resolution'],
            type_map=data['type_map']
        )
