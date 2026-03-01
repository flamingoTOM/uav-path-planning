"""
地图类型定义
统一的地图格点类型枚举
@author: Based on example framework
@date: 2026-02-28
"""


class MapTypes:
    """
    统一的地图类型定义
    用于标记栅格地图中每个格点的状态
    """
    FREE = 0         # 可通行区域
    OBSTACLE = 1     # 障碍物
    START = 2        # 起点
    GOAL = 3         # 终点
    INFLATION = 4    # 膨胀区（安全缓冲）
    EXPAND = 5       # 已搜索区域
    COVERED = 6      # 已覆盖区域
    PATH = 7         # 规划路径
    CUSTOM = 8       # 自定义区域

    @classmethod
    def get_name(cls, type_value: int) -> str:
        """获取类型名称"""
        type_names = {
            0: "FREE",
            1: "OBSTACLE",
            2: "START",
            3: "GOAL",
            4: "INFLATION",
            5: "EXPAND",
            6: "COVERED",
            7: "PATH",
            8: "CUSTOM"
        }
        return type_names.get(type_value, "UNKNOWN")
