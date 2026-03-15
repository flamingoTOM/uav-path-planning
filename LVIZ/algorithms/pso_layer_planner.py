# -*- coding: utf-8 -*-
"""
PSO 分层覆盖路径规划算法
适用于 LVIZ 可视化平台

步骤：
1. 按等高线（分位数）将地形分解为 N 个高程层
2. 对每层用 PSO 优化牛耕扫描角度，规划覆盖路径
3. 相邻层之间用 Theta* 算法连接
"""

import numpy as np
import math
import heapq
from typing import List, Tuple, Dict, Optional


# ==================== 工具函数 ====================

def point_in_polygon(px: float, py: float, polygon: list) -> bool:
    """射线法判断点 (px, py) 是否在多边形内"""
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


def build_poly_mask(polygon: list, width: int, height: int) -> np.ndarray:
    """
    构建布尔掩码：多边形内部 = True，外部 = False
    坐标系：mask[y, x]，x=列，y=行
    """
    mask = np.zeros((height, width), dtype=bool)
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    x1, y1 = max(0, int(min(xs))), max(0, int(min(ys)))
    x2, y2 = min(width - 1, int(max(xs)) + 1), min(height - 1, int(max(ys)) + 1)

    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            if point_in_polygon(x + 0.5, y + 0.5, polygon):
                mask[y, x] = True
    return mask


# ==================== Step 1: 等高线层分解 ====================

def decompose_layers(elevation: np.ndarray,
                     poly_mask: np.ndarray,
                     num_layers: int = 5) -> List[Dict]:
    """
    按高程分位数将地形分解为 N 个层

    Returns:
        按中位高程升序排列的层列表，每层为 dict：
        {layer_id, elev_low, elev_high, mask (bool H×W), median_elev}
    """
    elev_vals = elevation[poly_mask]
    elev_vals = elev_vals[~np.isnan(elev_vals)]

    if len(elev_vals) == 0:
        return []

    # 分位数边界，避免平坦区域出现空层
    boundaries = np.percentile(elev_vals, np.linspace(0, 100, num_layers + 1))

    layers = []
    for i in range(num_layers):
        low = boundaries[i]
        high = boundaries[i + 1]

        if i == num_layers - 1:
            # 最后一层包含最大值（闭区间）
            layer_mask = (poly_mask
                          & (~np.isnan(elevation))
                          & (elevation >= low)
                          & (elevation <= high))
        else:
            layer_mask = (poly_mask
                          & (~np.isnan(elevation))
                          & (elevation >= low)
                          & (elevation < high))

        if not np.any(layer_mask):
            continue

        median_elev = float(np.median(elevation[layer_mask]))
        layers.append({
            'layer_id': i,
            'elev_low': float(low),
            'elev_high': float(high),
            'mask': layer_mask,
            'median_elev': median_elev,
        })

    # 按中位高程升序排列
    layers.sort(key=lambda l: l['median_elev'])

    # 重新分配连续 layer_id
    for idx, layer in enumerate(layers):
        layer['layer_id'] = idx

    return layers


# ==================== Step 2: PSO 覆盖路径规划 ====================

def generate_boustrophedon_from_particle(particle: np.ndarray,
                                          mask: np.ndarray,
                                          line_spacing: float) -> List[Tuple[int, int]]:
    """
    根据 PSO 粒子生成牛耕（Boustrophedon）路径

    粒子编码：
      particle[0] = sweep_angle ∈ [0, π]  —— 扫描条带方向角
      particle[1] = phase_offset ∈ [0, 1] —— 条带相位偏移
      particle[2] 保留（未使用）

    Returns:
        [(x, y), ...] 路径航点列表（取各条带端点）
    """
    sweep_angle = float(particle[0])
    phase_offset = float(particle[1])

    ys_arr, xs_arr = np.where(mask)
    if len(xs_arr) == 0:
        return []

    # 旋转坐标变换
    cos_a = math.cos(sweep_angle)
    sin_a = math.sin(sweep_angle)
    us = xs_arr * cos_a + ys_arr * sin_a   # 沿扫描方向
    vs = -xs_arr * sin_a + ys_arr * cos_a  # 垂直扫描方向

    v_min = float(vs.min())
    v_max = float(vs.max())
    v_range = v_max - v_min

    if v_range < 1.0:
        # 层太薄，直接返回端点
        return [(int(xs_arr[0]), int(ys_arr[0]))]

    # 生成条带中线（加入相位偏移以探索不同起始对齐）
    phase = phase_offset * line_spacing
    v = v_min + (phase % line_spacing)
    # 确保第一条带能覆盖 v_min 附近
    while v > v_min + line_spacing / 2:
        v -= line_spacing

    strip_centers = []
    while v <= v_max + line_spacing / 2:
        if v >= v_min - line_spacing / 2:
            strip_centers.append(v)
        v += line_spacing

    if not strip_centers:
        return []

    half_sp = line_spacing / 2.0
    path: List[Tuple[int, int]] = []

    for strip_idx, v_center in enumerate(strip_centers):
        in_strip = np.abs(vs - v_center) < half_sp
        if not np.any(in_strip):
            continue

        strip_us = us[in_strip]
        strip_xs = xs_arr[in_strip]
        strip_ys = ys_arr[in_strip]

        # 按 u 坐标排序（奇偶行交替 → 蛇形）
        sort_idx = np.argsort(strip_us)
        if strip_idx % 2 == 1:
            sort_idx = sort_idx[::-1]

        sxs = strip_xs[sort_idx]
        sys_ = strip_ys[sort_idx]

        # 仅取两端点（代表条带起止航点）
        path.append((int(sxs[0]), int(sys_[0])))
        if len(sxs) > 1:
            path.append((int(sxs[-1]), int(sys_[-1])))

    return path


def _compute_fitness(path: List[Tuple[int, int]],
                     mask: np.ndarray,
                     line_spacing: float) -> float:
    """
    计算路径适应度：
      fitness = coverage_ratio * 1000 - path_length * 0.01 - turns * 2
    """
    if not path:
        return -1000.0

    # 路径总长度
    path_length = 0.0
    for i in range(1, len(path)):
        dx = path[i][0] - path[i - 1][0]
        dy = path[i][1] - path[i - 1][1]
        path_length += math.sqrt(dx * dx + dy * dy)

    # 转弯计数（夹角 > 45° 视为转弯）
    turns = 0
    if len(path) >= 3:
        for i in range(1, len(path) - 1):
            dx1 = path[i][0] - path[i - 1][0]
            dy1 = path[i][1] - path[i - 1][1]
            dx2 = path[i + 1][0] - path[i][0]
            dy2 = path[i + 1][1] - path[i][1]
            len1 = math.sqrt(dx1 * dx1 + dy1 * dy1)
            len2 = math.sqrt(dx2 * dx2 + dy2 * dy2)
            if len1 > 0 and len2 > 0:
                cos_a = max(-1.0, min(1.0, (dx1 * dx2 + dy1 * dy2) / (len1 * len2)))
                if math.degrees(math.acos(cos_a)) > 45:
                    turns += 1

    # 覆盖率估算：实际条带数 / 理论所需条带数
    ys_arr, xs_arr = np.where(mask)
    if len(xs_arr) == 0:
        coverage_ratio = 0.0
    else:
        y_range = float(ys_arr.max() - ys_arr.min())
        x_range = float(xs_arr.max() - xs_arr.min())
        max_dim = max(y_range, x_range, 1.0)
        strips_needed = max_dim / line_spacing
        strips_covered = len(path) // 2  # 每两个点代表一条带
        coverage_ratio = min(1.0, strips_covered / max(1.0, strips_needed))

    return coverage_ratio * 1000.0 - path_length * 0.01 - turns * 2.0


def pso_plan_layer(layer: Dict,
                   line_spacing: float,
                   n_particles: int = 20,
                   n_iter: int = 30) -> List[Tuple[int, int]]:
    """
    用 PSO 优化牛耕扫描角度，为单层规划覆盖路径

    粒子编码：[sweep_angle ∈ [0,π], phase_offset ∈ [0,1], _ ∈ [0,1]]
    PSO 参数：w=0.7, c1=c2=1.5
    """
    mask = layer['mask']

    # 参数边界
    lb = np.array([0.0, 0.0, 0.0])
    ub = np.array([math.pi, 1.0, 1.0])

    rng = np.random.RandomState(42)

    # 初始化粒子位置与速度
    positions = lb + rng.rand(n_particles, 3) * (ub - lb)
    velocities = np.zeros((n_particles, 3))

    # 计算初始适应度
    pbest_pos = positions.copy()
    pbest_fit = np.array([
        _compute_fitness(
            generate_boustrophedon_from_particle(positions[i], mask, line_spacing),
            mask, line_spacing
        )
        for i in range(n_particles)
    ])

    gbest_idx = int(np.argmax(pbest_fit))
    gbest_pos = pbest_pos[gbest_idx].copy()
    gbest_fit = float(pbest_fit[gbest_idx])

    w, c1, c2 = 0.7, 1.5, 1.5

    # PSO 主循环
    for _ in range(n_iter):
        r1 = rng.rand(n_particles, 3)
        r2 = rng.rand(n_particles, 3)

        velocities = (w * velocities
                      + c1 * r1 * (pbest_pos - positions)
                      + c2 * r2 * (gbest_pos - positions))
        positions = np.clip(positions + velocities, lb, ub)

        for i in range(n_particles):
            path = generate_boustrophedon_from_particle(positions[i], mask, line_spacing)
            fit = _compute_fitness(path, mask, line_spacing)

            if fit > pbest_fit[i]:
                pbest_fit[i] = fit
                pbest_pos[i] = positions[i].copy()

            if fit > gbest_fit:
                gbest_fit = fit
                gbest_pos = positions[i].copy()

    # 使用全局最优粒子生成路径
    best_path = generate_boustrophedon_from_particle(gbest_pos, mask, line_spacing)

    # Fallback：PSO 返回空路径时使用水平扫描（angle=0）
    if not best_path:
        fallback = np.array([0.0, 0.0, 0.0])
        best_path = generate_boustrophedon_from_particle(fallback, mask, line_spacing)

    return best_path


# ==================== Step 3: Theta* 层间连接 ====================

def _los_check(p1: Tuple[int, int], p2: Tuple[int, int],
               poly_mask: np.ndarray, height: int, width: int) -> bool:
    """Bresenham 直线算法检查 p1→p2 视线是否完全在多边形内"""
    x1, y1 = int(p1[0]), int(p1[1])
    x2, y2 = int(p2[0]), int(p2[1])
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1
    err = dx - dy
    cx, cy = x1, y1

    while True:
        if not (0 <= cy < height and 0 <= cx < width):
            return False
        if not poly_mask[cy, cx]:
            return False
        if cx == x2 and cy == y2:
            return True
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            cx += sx
        if e2 < dx:
            err += dx
            cy += sy


def theta_star_connect(start_xy: Tuple[int, int],
                       goal_xy: Tuple[int, int],
                       poly_mask: np.ndarray,
                       width: int,
                       height: int) -> List[Tuple[int, int]]:
    """
    Theta* 连接两点（路径必须在多边形内）

    Fallback：搜索失败时返回直连 [start_xy, goal_xy]
    """
    sx, sy = int(start_xy[0]), int(start_xy[1])
    gx, gy = int(goal_xy[0]), int(goal_xy[1])

    # 边界 & 掩码检查
    if not (0 <= sy < height and 0 <= sx < width):
        return [start_xy, goal_xy]
    if not (0 <= gy < height and 0 <= gx < width):
        return [start_xy, goal_xy]

    # 如果直接视线通畅，直连即可
    if _los_check((sx, sy), (gx, gy), poly_mask, height, width):
        return [(sx, sy), (gx, gy)]

    start = (sx, sy)
    goal = (gx, gy)

    open_set: List = []
    heapq.heappush(open_set, (0.0, start))

    came_from: Dict[Tuple, Tuple] = {start: start}
    g_score: Dict[Tuple, float] = {start: 0.0}
    visited: set = set()

    def heuristic(a, b):
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),           (0, 1),
                  (1, -1),  (1, 0),  (1, 1)]

    max_iter = width * height
    iters = 0

    while open_set and iters < max_iter:
        iters += 1
        _, current = heapq.heappop(open_set)

        if current in visited:
            continue
        visited.add(current)

        # 到达目标附近
        if abs(current[0] - goal[0]) <= 1 and abs(current[1] - goal[1]) <= 1:
            # 重构路径
            path = []
            node = current
            depth = 0
            while depth < max_iter:
                path.append(node)
                parent = came_from.get(node, node)
                if parent == node:
                    break
                node = parent
                depth += 1
            path.reverse()
            return [(p[0], p[1]) for p in path]

        for dx, dy in directions:
            nx, ny = current[0] + dx, current[1] + dy
            neighbor = (nx, ny)

            if not (0 <= ny < height and 0 <= nx < width):
                continue
            if not poly_mask[ny, nx]:
                continue
            if neighbor in visited:
                continue

            # Theta*: 尝试从当前节点的父节点直接连接邻居（视线检查）
            parent = came_from.get(current, current)
            if _los_check(parent, neighbor, poly_mask, height, width):
                px, py = parent
                new_g = g_score[parent] + math.sqrt((nx - px) ** 2 + (ny - py) ** 2)
                if neighbor not in g_score or new_g < g_score[neighbor]:
                    g_score[neighbor] = new_g
                    came_from[neighbor] = parent
                    f = new_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f, neighbor))
            else:
                move_cost = math.sqrt(dx * dx + dy * dy)
                new_g = g_score[current] + move_cost
                if neighbor not in g_score or new_g < g_score[neighbor]:
                    g_score[neighbor] = new_g
                    came_from[neighbor] = current
                    f = new_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f, neighbor))

    # Fallback: 直连
    return [start_xy, goal_xy]


def find_nearest_valid(xy: Tuple[int, int],
                       mask: np.ndarray,
                       width: int,
                       height: int) -> Optional[Tuple[int, int]]:
    """在掩码中找到距离 xy 最近的有效像素"""
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    x, y = int(xy[0]), int(xy[1])
    dists = (xs - x) ** 2 + (ys - y) ** 2
    idx = int(np.argmin(dists))
    return (int(xs[idx]), int(ys[idx]))


# ==================== 主接口 ====================

def generate_path(terrain_data: dict, polygon: list, params: dict) -> dict:
    """
    PSO 分层覆盖路径规划主函数（LVIZ 接口）

    terrain_data:
        elevation: np.ndarray (H, W)
        width, height: int
        min_elevation, max_elevation: float

    polygon:
        [(x, y), ...] 飞行区域顶点，像素坐标

    params:
        min_altitude: float   飞行离地高度（m），默认 50
        coverage_width: float 覆盖宽度（m），默认 20
        overlap_rate: float   重叠率 [0,1]，默认 0.2
        num_layers: int       分层数，默认 5

    Returns:
        {
          'path': [{'x', 'y', 'altitude', 'distance'}, ...],
          'statistics': {...},
          '_layers': [...],          # 内部数据供测试脚本使用
          '_layer_paths': [...],
          '_connection_paths': [...],
        }
    """
    elevation: np.ndarray = terrain_data['elevation']
    width: int = terrain_data['width']
    height: int = terrain_data['height']
    min_elev: float = terrain_data['min_elevation']

    min_altitude = float(params.get('min_altitude', 50.0))
    coverage_width = float(params.get('coverage_width', 20.0))
    overlap_rate = float(params.get('overlap_rate', 0.2))
    num_layers = int(params.get('num_layers', 5))

    # 条带间距 = 覆盖宽度 × (1 - 重叠率)
    line_spacing = max(3.0, coverage_width * (1.0 - overlap_rate))

    # 构建多边形掩码
    poly_mask = build_poly_mask(polygon, width, height)
    if not np.any(poly_mask):
        return {'path': [], 'statistics': {}}

    # ---------- Step 1: 层分解 ----------
    layers = decompose_layers(elevation, poly_mask, num_layers)
    if not layers:
        return {'path': [], 'statistics': {}}

    # ---------- Step 2 + 3: 逐层 PSO 规划 + Theta* 连接 ----------
    all_waypoints: List[Tuple[int, int, int]] = []   # (x, y, layer_id)
    layer_paths: List[Tuple[int, List]] = []          # (layer_id, [(x,y),...])
    connection_paths: List[List] = []

    prev_last_xy: Optional[Tuple[int, int]] = None

    for layer in layers:
        # PSO 规划
        lpath = pso_plan_layer(layer, line_spacing)

        if not lpath:
            # 退化：取层内第一个有效像素
            ys_arr, xs_arr = np.where(layer['mask'])
            if len(xs_arr) > 0:
                lpath = [(int(xs_arr[0]), int(ys_arr[0]))]
            else:
                continue

        lid = layer['layer_id']
        layer_paths.append((lid, lpath))

        # Theta* 连接上一层末尾到本层入口
        if prev_last_xy is not None:
            nearest = find_nearest_valid(prev_last_xy, layer['mask'], width, height)
            if nearest is None:
                nearest = lpath[0]

            conn = theta_star_connect(prev_last_xy, nearest, poly_mask, width, height)
            connection_paths.append(conn)

            # 添加连接路径（跳过起点，避免重复）
            for xy in conn[1:]:
                all_waypoints.append((xy[0], xy[1], -1))

        # 添加层路径点
        for xy in lpath:
            all_waypoints.append((xy[0], xy[1], lid))

        prev_last_xy = lpath[-1]

    if not all_waypoints:
        return {'path': [], 'statistics': {}}

    # ---------- 构建最终路径 ----------
    path = []
    total_distance = 0.0

    for wx, wy, _ in all_waypoints:
        x = max(0, min(width - 1, int(wx)))
        y = max(0, min(height - 1, int(wy)))

        elev_val = float(elevation[y, x])
        if math.isnan(elev_val):
            elev_val = min_elev
        altitude = elev_val + min_altitude

        if path:
            prev = path[-1]
            dx = x - prev['x']
            dy = y - prev['y']
            total_distance += math.sqrt(dx * dx + dy * dy)

        path.append({
            'x': float(x),
            'y': float(y),
            'altitude': altitude,
            'distance': total_distance,
        })

    # ---------- 统计 ----------
    altitudes = [p['altitude'] for p in path]

    poly_area = 0.0
    n = len(polygon)
    for i in range(n):
        j = (i + 1) % n
        poly_area += polygon[i][0] * polygon[j][1] - polygon[j][0] * polygon[i][1]
    coverage_area_m2 = abs(poly_area) / 2.0

    total_lines = sum(len(lp) // 2 for _, lp in layer_paths)

    return {
        'path': path,
        'statistics': {
            'total_distance': total_distance,
            'total_lines': total_lines,
            'coverage_area_m2': coverage_area_m2,
            'estimated_time': total_distance / 10.0,
            'waypoint_count': len(path),
            'line_spacing': float(line_spacing),
            'plan_min_alt': min(altitudes) if altitudes else 0.0,
            'plan_max_alt': max(altitudes) if altitudes else 0.0,
            'algorithm': (
                f'PSO Layered Coverage '
                f'(layers={len(layers)}, spacing={line_spacing:.1f}m)'
            ),
        },
    }
