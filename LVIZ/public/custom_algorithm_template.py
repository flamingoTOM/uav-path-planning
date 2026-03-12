# -*- coding: utf-8 -*-
"""
LVIZ 自定义路径规划算法模板
============================================================
将此文件复制并修改后，在规划参数中填写该文件路径，
LVIZ 将自动调用 generate_path() 函数执行路径规划。

接口规范
---------
函数签名：
    generate_path(terrain_data, polygon, params) -> dict

参数说明
---------
terrain_data : dict
    地形数据
    {
        "elevation": np.ndarray,   # shape (height, width)，高程值（米）
        "width": int,              # 地形宽度（像素，1px ≈ 1m）
        "height": int,             # 地形高度（像素）
        "min_elevation": float,    # 最低高程（米）
        "max_elevation": float,    # 最高高程（米）
    }

polygon : list[tuple[float, float]]
    飞行区域多边形顶点列表（地形坐标系）
    [(x0, y0), (x1, y1), ...]
    坐标单位为地形像素（≈ 米），左上角为原点

params : dict
    规划参数
    {
        "min_altitude": float,     # 防地高度（米）
        "coverage_width": float,   # 覆盖宽度（米）
        "overlap_rate": float,     # 重叠率（0~1）
    }

返回值
------
dict
    {
        "path": [                  # 路径点列表
            {"x": float, "y": float, "altitude": float, "distance": float},
            ...
        ],
        "statistics": {            # 统计信息
            "total_distance": float,      # 总航程（米）
            "total_lines": int,           # 航线数
            "coverage_area_m2": float,    # 覆盖面积（平方米）
            "estimated_time": float,      # 预计飞行时间（秒，以 10m/s 计）
            "waypoint_count": int,        # 航点总数
            "line_spacing": float,        # 航线间距（米）
        }
    }
"""

import numpy as np
import math


def point_in_polygon(px: float, py: float, polygon) -> bool:
    """射线法判断点是否在多边形内"""
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def generate_path(terrain_data: dict, polygon: list, params: dict) -> dict:
    """
    自定义路径规划 — 示例：螺旋式扫描（由外向内）

    请根据你的算法需求修改此函数。
    """
    elevation: np.ndarray = terrain_data['elevation']
    height, width = elevation.shape
    min_elev = terrain_data['min_elevation']

    min_altitude  = float(params.get('min_altitude',  50))
    coverage_width = float(params.get('coverage_width', 50))
    overlap_rate   = float(params.get('overlap_rate',   0.2))

    line_spacing = max(1, int(coverage_width * (1 - overlap_rate)))

    # ── 获取多边形包围盒 ──────────────────────────────────────────────────────
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    x1, y1 = int(max(0, min(xs))), int(max(0, min(ys)))
    x2, y2 = int(min(width - 1, max(xs))), int(min(height - 1, max(ys)))

    # ── 牛耕式扫描（参考实现，可替换为你的算法） ─────────────────────────────
    path = []
    total_distance = 0.0
    direction = 1

    for y in range(y1, y2 + 1, line_spacing):
        row_pts = []
        for x in range(x1, x2 + 1):
            if point_in_polygon(x + 0.5, y + 0.5, polygon):
                row_pts.append((x, y))

        if not row_pts:
            continue

        if direction == -1:
            row_pts.reverse()

        for (px, py) in row_pts:
            idx = min(py * width + px, elevation.size - 1)
            terrain_alt = float(elevation.flat[idx]) if not math.isnan(elevation.flat[idx]) else min_elev
            altitude = terrain_alt + min_altitude

            if path:
                prev = path[-1]
                dx = px - prev['x']
                dy = py - prev['y']
                total_distance += math.sqrt(dx * dx + dy * dy)

            path.append({'x': float(px), 'y': float(py),
                         'altitude': altitude, 'distance': total_distance})

        direction *= -1

    # ── 统计信息 ──────────────────────────────────────────────────────────────
    region_w = x2 - x1
    region_h = y2 - y1
    total_lines = max(1, region_h // line_spacing)

    poly_area = 0.0
    n = len(polygon)
    for i in range(n):
        j = (i + 1) % n
        poly_area += polygon[i][0] * polygon[j][1] - polygon[j][0] * polygon[i][1]
    coverage_area_m2 = abs(poly_area) / 2.0

    return {
        'path': path,
        'statistics': {
            'total_distance': total_distance,
            'total_lines': total_lines,
            'coverage_area_m2': coverage_area_m2,
            'estimated_time': total_distance / 10.0,
            'waypoint_count': len(path),
            'line_spacing': float(line_spacing),
            'plan_min_alt': min(p['altitude'] for p in path) if path else 0.0,
            'plan_max_alt': max(p['altitude'] for p in path) if path else 0.0,
        }
    }
