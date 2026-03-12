#!/usr/bin/env python3
"""
全覆盖路径规划模块
支持多种算法：牛耕式（Boustrophedon）、螺旋式（Spiral）、分区式（Partition）
"""

import numpy as np
import time
from typing import List, Tuple, Dict, Optional


class CoveragePlanner:
    """全覆盖路径规划器"""

    def __init__(self, elevation_map: np.ndarray, resolution: float):
        """
        Args:
            elevation_map: 高程矩阵 [H, W]，值为海拔高度（米）
            resolution: 分辨率（米/像素）
        """
        self.elevation_map = elevation_map
        self.resolution = resolution
        self.h, self.w = elevation_map.shape

    def plan(
        self,
        polygon: List[Tuple[int, int]],
        algorithm: str,
        params: dict
    ) -> dict:
        """
        生成全覆盖路径

        Args:
            polygon: 多边形顶点列表（网格坐标）[(gx, gy), ...]
            algorithm: 算法类型 ('boustrophedon', 'spiral', 'partition')
            params: 算法参数 {
                'spacing': 覆盖间距（米）,
                'altitude': 飞行高度相对偏移（米）,
                'w_h': 爬升权重,
                'w_r': 风险权重,
                'angle': 航线角度（度，仅牛耕式）
            }

        Returns: {
            'waypoints': [[x, y, z], ...],  # 世界坐标（米）
            'waypoints_grid': [[gx, gy], ...],  # 网格坐标
            'metrics': {
                'coverage': 覆盖率 η,
                'length': 路径长度 L,
                'climb': 总爬升 H_up,
                'risk': 风险值 R,
                'cost': 综合代价 J,
                'elapsed_ms': 计算耗时（毫秒）
            },
            'debug': {  # 调试信息
                'cells': [...],  # 分解后的单元
                'sweep_lines': [...],  # 扫掠线
            }
        }
        """
        t_start = time.time()

        if algorithm == 'boustrophedon':
            result = self._plan_boustrophedon(polygon, params)
        elif algorithm == 'spiral':
            result = self._plan_spiral(polygon, params)
        elif algorithm == 'partition':
            result = self._plan_partition(polygon, params)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

        # 添加计算耗时
        elapsed_ms = round((time.time() - t_start) * 1000, 2)
        result['metrics']['elapsed_ms'] = elapsed_ms

        return result

    # ======================================================================
    #  辅助函数：多边形处理
    # ======================================================================

    def _polygon_to_mask(self, polygon: List[Tuple[int, int]]) -> np.ndarray:
        """将多边形转换为布尔掩码（True=内部，False=外部）"""
        mask = np.zeros((self.h, self.w), dtype=bool)

        # 获取包围盒
        xs = [p[0] for p in polygon]
        ys = [p[1] for p in polygon]
        min_x = max(0, min(xs))
        max_x = min(self.w - 1, max(xs))
        min_y = max(0, min(ys))
        max_y = min(self.h - 1, max(ys))

        # 射线法判断每个点是否在多边形内
        for gy in range(min_y, max_y + 1):
            for gx in range(min_x, max_x + 1):
                if self._point_in_polygon(gx, gy, polygon):
                    mask[gy, gx] = True

        return mask

    def _point_in_polygon(self, x: int, y: int, polygon: List[Tuple[int, int]]) -> bool:
        """射线法判断点是否在多边形内"""
        inside = False
        n = len(polygon)
        for i in range(n):
            xi, yi = polygon[i]
            xj, yj = polygon[(i + 1) % n]

            intersect = ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi)
            if intersect:
                inside = not inside

        return inside

    # ======================================================================
    #  算法 1：牛耕式（Boustrophedon）
    # ======================================================================

    def _plan_boustrophedon(self, polygon: List[Tuple[int, int]], params: dict) -> dict:
        """牛耕式路径规划"""
        # 1. 多边形裁剪区域
        mask = self._polygon_to_mask(polygon)

        # 2. 扫掠参数
        spacing_px = max(1, int(params['spacing'] / self.resolution))
        angle = params.get('angle', 0)  # 航线角度（度）

        # 3. 生成扫掠路径（简化版：垂直扫掠）
        waypoints_grid = []
        x_coords = sorted(set(x for x, y in polygon))
        min_x = min(x_coords)
        max_x = max(x_coords)

        # 从左到右扫掠
        direction = 1  # 1=向下，-1=向上
        for col in range(min_x, max_x + 1, spacing_px):
            # 边界检查
            if col < 0 or col >= self.w:
                continue

            # 找到该列在多边形内的所有行
            rows_in_col = []
            for row in range(self.h):
                if mask[row, col]:
                    rows_in_col.append(row)

            if not rows_in_col:
                continue

            # 生成牛耕路径
            if direction == 1:
                # 向下扫
                for row in rows_in_col:
                    waypoints_grid.append([col, row])
            else:
                # 向上扫
                for row in reversed(rows_in_col):
                    waypoints_grid.append([col, row])

            direction *= -1  # 切换方向

        # 4. 添加高度
        waypoints_3d = self._add_altitude(waypoints_grid, params['altitude'])

        # 5. 计算评价指标
        metrics = self._evaluate_path(waypoints_3d, mask, params)

        return {
            'waypoints': waypoints_3d.tolist(),
            'waypoints_grid': waypoints_grid,
            'metrics': metrics,
            'debug': {
                'cells': [],
                'sweep_lines': waypoints_grid,
            }
        }

    # ======================================================================
    #  算法 2：螺旋式（Spiral）
    # ======================================================================

    def _plan_spiral(self, polygon: List[Tuple[int, int]], params: dict) -> dict:
        """螺旋式路径规划（从外向内）"""
        mask = self._polygon_to_mask(polygon)
        spacing_px = max(1, int(params['spacing'] / self.resolution))

        # 获取包围盒
        ys, xs = np.where(mask)
        if len(xs) == 0:
            return self._empty_result()

        min_x, max_x = xs.min(), xs.max()
        min_y, max_y = ys.min(), ys.max()

        waypoints_grid = []
        visited = np.zeros_like(mask, dtype=bool)

        # 螺旋遍历
        x, y = min_x, min_y
        dx, dy = spacing_px, 0  # 初始方向：向右
        direction_changes = 0

        while True:
            # 记录当前点
            if 0 <= x < self.w and 0 <= y < self.h and mask[y, x] and not visited[y, x]:
                waypoints_grid.append([x, y])
                visited[y, x] = True

            # 尝试前进
            next_x, next_y = x + dx, y + dy

            # 检查是否需要转向
            if not (0 <= next_x < self.w and 0 <= next_y < self.h and mask[next_y, next_x]):
                # 右转
                dx, dy = -dy, dx
                direction_changes += 1

                if direction_changes > 4:  # 所有方向都无法前进
                    break

                next_x, next_y = x + dx, y + dy

            # 如果转向后仍无法前进，停止
            if not (0 <= next_x < self.w and 0 <= next_y < self.h and mask[next_y, next_x]):
                break

            x, y = next_x, next_y
            direction_changes = 0

        waypoints_3d = self._add_altitude(waypoints_grid, params['altitude'])
        metrics = self._evaluate_path(waypoints_3d, mask, params)

        return {
            'waypoints': waypoints_3d.tolist(),
            'waypoints_grid': waypoints_grid,
            'metrics': metrics,
            'debug': {'cells': [], 'sweep_lines': waypoints_grid}
        }

    # ======================================================================
    #  算法 3：分区式（Partition）
    # ======================================================================

    def _plan_partition(self, polygon: List[Tuple[int, int]], params: dict) -> dict:
        """分区式路径规划（将区域分成多个子区域，分别覆盖）"""
        mask = self._polygon_to_mask(polygon)
        spacing_px = max(1, int(params['spacing'] / self.resolution))

        # 简化实现：将区域分成上下两半
        ys, xs = np.where(mask)
        if len(ys) == 0:
            return self._empty_result()

        mid_y = (ys.min() + ys.max()) // 2

        # 上半部分：从左到右扫掠
        waypoints_grid = []
        upper_mask = mask.copy()
        upper_mask[mid_y:, :] = False

        # 下半部分：从右到左扫掠
        lower_mask = mask.copy()
        lower_mask[:mid_y, :] = False

        # 合并路径
        for m in [upper_mask, lower_mask]:
            ys, xs = np.where(m)
            if len(xs) == 0:
                continue

            min_x, max_x = xs.min(), xs.max()
            direction = 1

            for col in range(min_x, max_x + 1, spacing_px):
                # 边界检查
                if col < 0 or col >= self.w:
                    continue

                rows_in_col = [r for r in range(self.h) if m[r, col]]
                if not rows_in_col:
                    continue

                if direction == 1:
                    for row in rows_in_col:
                        waypoints_grid.append([col, row])
                else:
                    for row in reversed(rows_in_col):
                        waypoints_grid.append([col, row])

                direction *= -1

        waypoints_3d = self._add_altitude(waypoints_grid, params['altitude'])
        metrics = self._evaluate_path(waypoints_3d, mask, params)

        return {
            'waypoints': waypoints_3d.tolist(),
            'waypoints_grid': waypoints_grid,
            'metrics': metrics,
            'debug': {'cells': [], 'sweep_lines': waypoints_grid}
        }

    # ======================================================================
    #  评价指标计算
    # ======================================================================

    def _add_altitude(self, waypoints_grid: List, altitude_offset: float) -> np.ndarray:
        """为路径点添加高度（基于地形 + 偏移量）"""
        waypoints_3d = []

        for gx, gy in waypoints_grid:
            # 网格坐标 → 世界坐标（米）
            x = gx * self.resolution
            y = gy * self.resolution

            # 获取地面高程
            if 0 <= gy < self.h and 0 <= gx < self.w:
                ground_elev = self.elevation_map[gy, gx]
                if np.isnan(ground_elev):
                    ground_elev = 0.0
            else:
                ground_elev = 0.0

            # 飞行高度 = 地面 + 偏移
            z = ground_elev + altitude_offset

            waypoints_3d.append([x, y, z])

        return np.array(waypoints_3d)

    def _evaluate_path(
        self,
        waypoints: np.ndarray,
        mask: np.ndarray,
        params: dict
    ) -> dict:
        """计算评价指标"""
        if len(waypoints) == 0:
            return {
                'coverage': 0.0,
                'length': 0.0,
                'climb': 0.0,
                'risk': 0.0,
                'cost': 0.0,
            }

        # 1. 覆盖率
        covered_cells = set()
        for wx, wy, wz in waypoints:
            gx = int(wx / self.resolution)
            gy = int(wy / self.resolution)
            if 0 <= gx < self.w and 0 <= gy < self.h:
                covered_cells.add((gx, gy))

        total_cells = np.sum(mask)
        eta = len(covered_cells) / total_cells if total_cells > 0 else 0.0

        # 2. 路径长度
        L = 0.0
        for i in range(len(waypoints) - 1):
            L += np.linalg.norm(waypoints[i + 1] - waypoints[i])

        # 3. 总爬升距离
        H_up = 0.0
        for i in range(len(waypoints) - 1):
            dz = waypoints[i + 1][2] - waypoints[i][2]
            if dz > 0:
                H_up += dz

        # 4. 风险项（最小离地高度）
        min_clearance = float('inf')
        for wx, wy, wz in waypoints:
            gx = int(wx / self.resolution)
            gy = int(wy / self.resolution)
            if 0 <= gx < self.w and 0 <= gy < self.h:
                ground = self.elevation_map[gy, gx]
                if not np.isnan(ground):
                    clearance = wz - ground
                    min_clearance = min(min_clearance, clearance)

        # 风险惩罚：离地高度低于 10m 时惩罚
        R = max(0, 10 - min_clearance) if min_clearance != float('inf') else 0.0

        # 5. 综合代价
        w_h = params.get('w_h', 1.0)
        w_r = params.get('w_r', 0.5)
        J = L + w_h * H_up + w_r * R

        return {
            'coverage': round(eta, 4),
            'length': round(L, 2),
            'climb': round(H_up, 2),
            'risk': round(R, 2),
            'cost': round(J, 2),
        }

    def _empty_result(self) -> dict:
        """返回空结果"""
        return {
            'waypoints': [],
            'waypoints_grid': [],
            'metrics': {
                'coverage': 0.0,
                'length': 0.0,
                'climb': 0.0,
                'risk': 0.0,
                'cost': 0.0,
            },
            'debug': {'cells': [], 'sweep_lines': []}
        }
