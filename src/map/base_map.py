"""
地图抽象基类
定义统一的地图接口
@author: Based on example framework
@date: 2026-02-28
"""
from abc import ABC, abstractmethod
from typing import Tuple, List
import numpy as np


class BaseMap(ABC):
    """
    路径规划地图的抽象基类

    所有地图类型（2D栅格、3D栅格、地形地图等）都应继承此类

    Args:
        bounds: 地图在世界坐标系中的范围，shape: (n, 2)，n>=2
                bounds[i, 0] 表示第 i 个维度的下界
                bounds[i, 1] 表示第 i 个维度的上界
        resolution: 地图分辨率（单位：米/格）
        dtype: 坐标的数据类型（np.int32、np.float32等）
    """

    def __init__(self,
                 bounds: np.ndarray,
                 resolution: float = 1.0,
                 dtype: np.dtype = np.int32) -> None:
        self._bounds = np.asarray(bounds, dtype=float)
        self._resolution = resolution
        self._dtype = dtype

        # 检查 bounds 格式
        if len(self._bounds.shape) != 2 or self._bounds.shape[0] < 2 or self._bounds.shape[1] != 2:
            raise ValueError(f"bounds 的形状必须是 (n, 2), n>=2，而不是 {self._bounds.shape}")

        # 检查边界有效性
        for d in range(self._bounds.shape[0]):
            if self._bounds[d, 0] >= self._bounds[d, 1]:
                raise ValueError(f"第 {d} 维的下界必须小于上界")

    @property
    def bounds(self) -> np.ndarray:
        """返回地图的世界坐标范围"""
        return self._bounds

    @property
    def resolution(self) -> float:
        """返回地图分辨率"""
        return self._resolution

    @property
    def dim(self) -> int:
        """返回地图维度"""
        return self._bounds.shape[0]

    @property
    def dtype(self) -> np.dtype:
        """返回坐标数据类型"""
        return self._dtype

    @abstractmethod
    def map_to_world(self, point: Tuple) -> Tuple:
        """将地图坐标转换为世界坐标"""
        pass

    @abstractmethod
    def world_to_map(self, point: Tuple) -> Tuple:
        """将世界坐标转换为地图坐标"""
        pass

    @abstractmethod
    def is_valid(self, point: Tuple) -> bool:
        """检查点是否在地图范围内"""
        pass

    @abstractmethod
    def is_free(self, point: Tuple) -> bool:
        """检查点是否可通行"""
        pass

    @abstractmethod
    def in_collision(self, p1: Tuple, p2: Tuple) -> bool:
        """检查两点连线是否碰撞"""
        pass

    @abstractmethod
    def get_neighbors(self, point: Tuple, diagonal: bool = True) -> List[Tuple]:
        """获取邻居节点"""
        pass
