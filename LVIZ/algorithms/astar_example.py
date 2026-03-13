# -*- coding: utf-8 -*-
"""
A* 路径规划算法示例
适用于 LVIZ 可视化平台

特点：
- 考虑地形坡度约束
- 避障能力
- 最短路径优化
"""

import numpy as np
import heapq
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


def heuristic(a, b):
    """欧几里得距离启发式函数"""
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)


def astar_search(start, goal, elevation, width, height, polygon, max_slope_degrees=35):
    """
    A* 搜索算法

    Args:
        start: (x, y) 起点
        goal: (x, y) 终点
        elevation: 高程矩阵
        width, height: 地形尺寸
        polygon: 多边形边界
        max_slope_degrees: 最大允许坡度（度）

    Returns:
        路径点列表 [(x, y), ...]，如果未找到则返回空列表
    """
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    # 8 个方向
    directions = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

    while open_set:
        current = heapq.heappop(open_set)[1]

        # 到达目标
        if abs(current[0] - goal[0]) < 2 and abs(current[1] - goal[1]) < 2:
            # 重构路径
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return list(reversed(path))

        # 遍历邻居
        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)

            # 边界检查
            if not (0 <= neighbor[0] < width and 0 <= neighbor[1] < height):
                continue

            # 多边形内检查
            if not point_in_polygon(neighbor[0] + 0.5, neighbor[1] + 0.5, polygon):
                continue

            # 获取高程
            idx_cur = int(current[1]) * width + int(current[0])
            idx_nei = int(neighbor[1]) * width + int(neighbor[0])

            if idx_cur >= elevation.size or idx_nei >= elevation.size:
                continue

            elev_cur = float(elevation.flat[idx_cur])
            elev_nei = float(elevation.flat[idx_nei])

            if math.isnan(elev_cur) or math.isnan(elev_nei):
                continue

            # 坡度检查
            distance = math.sqrt(dx*dx + dy*dy)
            elev_diff = abs(elev_nei - elev_cur)
            slope_radians = math.atan2(elev_diff, distance)
            slope_degrees = math.degrees(slope_radians)

            if slope_degrees > max_slope_degrees:
                continue  # 坡度过大，不可通行

            # 计算代价（距离 + 坡度惩罚）
            slope_penalty = 1 + (slope_degrees / max_slope_degrees) * 0.5
            cost = distance * slope_penalty

            tentative_g = g_score[current] + cost

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []  # 未找到路径


def generate_path(terrain_data: dict, polygon: list, params: dict) -> dict:
    """
    主函数：使用 A* 算法规划覆盖路径

    策略：
    1. 在多边形内生成均匀分布的航点网格
    2. 使用 A* 连接所有航点
    3. 考虑地形坡度约束
    """

    elevation = terrain_data['elevation']
    width = terrain_data['width']
    height = terrain_data['height']
    min_elev = terrain_data['min_elevation']

    min_altitude = float(params.get('min_altitude', 50))
    coverage_width = float(params.get('coverage_width', 50))
    max_slope = float(params.get('max_slope', 35))  # 自定义参数

    # 获取多边形包围盒
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    x1, y1 = int(max(0, min(xs))), int(max(0, min(ys)))
    x2, y2 = int(min(width-1, max(xs))), int(min(height-1, max(ys)))

    # 生成航点网格
    spacing = max(5, int(coverage_width * 0.8))
    waypoints = []

    for y in range(y1, y2 + 1, spacing):
        for x in range(x1, x2 + 1, spacing):
            if point_in_polygon(x + 0.5, y + 0.5, polygon):
                waypoints.append((x, y))

    if not waypoints:
        return {'path': [], 'statistics': {}}

    # 使用 A* 连接所有航点
    full_path_nodes = []
    current = waypoints[0]

    for waypoint in waypoints[1:]:
        segment = astar_search(current, waypoint, elevation, width, height, polygon, max_slope)
        if segment:
            full_path_nodes.extend(segment[:-1])  # 避免重复点
            current = waypoint
        else:
            # 如果 A* 失败，直接连线
            full_path_nodes.append(waypoint)
            current = waypoint

    full_path_nodes.append(current)

    # 转换为标准格式
    path = []
    total_distance = 0.0

    for node in full_path_nodes:
        x, y = int(node[0]), int(node[1])
        idx = min(y * width + x, elevation.size - 1)
        terrain_alt = float(elevation.flat[idx])
        if math.isnan(terrain_alt):
            terrain_alt = min_elev

        altitude = terrain_alt + min_altitude

        if path:
            prev = path[-1]
            dx = x - prev['x']
            dy = y - prev['y']
            total_distance += math.sqrt(dx*dx + dy*dy)

        path.append({
            'x': float(x),
            'y': float(y),
            'altitude': altitude,
            'distance': total_distance
        })

    # 计算统计
    altitudes = [p['altitude'] for p in path]

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
            'total_lines': len(waypoints),
            'coverage_area_m2': coverage_area_m2,
            'estimated_time': total_distance / 10.0,
            'waypoint_count': len(path),
            'line_spacing': float(spacing),
            'plan_min_alt': min(altitudes) if altitudes else 0,
            'plan_max_alt': max(altitudes) if altitudes else 0,
            'algorithm': f'A* Planning (Max Slope: {max_slope}°)',
        }
    }
