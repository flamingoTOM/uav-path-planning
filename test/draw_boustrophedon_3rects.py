"""
牛耕分解算法可视化
地图包含3个矩形障碍物
"""

import random
random.seed(0)
import numpy as np
np.random.seed(0)
import sys
sys.path.append("C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/example")
from python_motion_planning.common import *


# ==================== 牛耕分解算法 ====================

class BoustrophedonCell:
    """表示一个牛耕分解后的单元"""
    def __init__(self, cell_id: int):
        self.id = cell_id
        self.min_col = float('inf')
        self.max_col = float('-inf')
        self.columns = {}
        self.positions = set()

    def add_column(self, col: int, free_segments: list):
        if not free_segments:
            return
        self.columns[col] = free_segments
        self.min_col = min(self.min_col, col)
        self.max_col = max(self.max_col, col)
        for row_start, row_end in free_segments:
            for row in range(row_start, row_end + 1):
                self.positions.add((row, col))


def get_free_segments_in_column(map_: Grid, col: int) -> list:
    """获取指定列中的所有自由行段"""
    segments = []
    in_segment = False
    segment_start = None

    for row in range(map_.shape[0]):
        pos = (row, col)
        cell_type = map_.type_map[pos]
        is_free = (cell_type != TYPES.OBSTACLE and cell_type != TYPES.INFLATION)

        if is_free and not in_segment:
            in_segment = True
            segment_start = row
        elif not is_free and in_segment:
            segments.append((segment_start, row - 1))
            in_segment = False

    if in_segment:
        segments.append((segment_start, map_.shape[0] - 1))

    return segments


def has_topology_change(prev_segments: list, curr_segments: list) -> bool:
    """检测相邻两列是否发生拓扑变化"""
    if len(prev_segments) != len(curr_segments):
        return True
    if len(prev_segments) == 0:
        return False
    for curr_start, curr_end in curr_segments:
        has_overlap = False
        for prev_start, prev_end in prev_segments:
            if not (curr_end < prev_start or curr_start > prev_end):
                has_overlap = True
                break
        if not has_overlap:
            return True
    return False


def boustrophedon_decomposition(map_: Grid) -> tuple:
    """执行牛耕分解，返回单元列表和关键列列表"""
    cells = []
    critical_cols = []  # 记录拓扑变化的列
    current_cell = None
    prev_segments = []

    for col in range(map_.shape[1]):
        curr_segments = get_free_segments_in_column(map_, col)

        if col == 0 or has_topology_change(prev_segments, curr_segments):
            if current_cell is not None:
                cells.append(current_cell)
            current_cell = BoustrophedonCell(len(cells))
            # 记录关键列（跳过第一列边界）
            if col > 1:
                critical_cols.append(col)

        if current_cell is not None:
            current_cell.add_column(col, curr_segments)

        prev_segments = curr_segments

    if current_cell is not None:
        cells.append(current_cell)

    return cells, critical_cols


# ==================== 主程序 ====================

# 1. 创建地图 - ⚠️ 不可变约束
map_ = Grid(bounds=[[0, 101], [0, 51]])  # 永远不能修改
map_.fill_boundary_with_obstacles()

# 2. 创建两个正六边形障碍物

def create_hexagon(center: tuple, radius: float) -> list:
    """生成正六边形顶点"""
    vertices = []
    for i in range(6):
        angle = i * (np.pi / 3)
        row = center[0] + radius * np.sin(angle)
        col = center[1] + radius * np.cos(angle)
        vertices.append((int(round(row)), int(round(col))))
    return vertices

def fill_hexagon(map_: Grid, vertices: list):
    """填充六边形障碍物"""
    rows = [v[0] for v in vertices]
    cols = [v[1] for v in vertices]
    min_row, max_row = min(rows), max(rows)
    min_col, max_col = min(cols), max(cols)

    for row in range(min_row, max_row + 1):
        intersections = []
        for i in range(len(vertices)):
            v1 = vertices[i]
            v2 = vertices[(i + 1) % len(vertices)]
            y1, y2 = v1[0], v2[0]
            x1, x2 = v1[1], v2[1]

            if y1 == y2:
                continue
            if min(y1, y2) <= row < max(y1, y2):
                t = (row - y1) / (y2 - y1)
                col = x1 + t * (x2 - x1)
                intersections.append(int(round(col)))

        intersections.sort()
        for i in range(0, len(intersections), 2):
            if i + 1 < len(intersections):
                col_start = intersections[i]
                col_end = intersections[i + 1]
                for col in range(col_start, col_end + 1):
                    if map_.within_bounds((row, col)):
                        map_.type_map[row, col] = TYPES.OBSTACLE

# 地图大小是 (101, 51)，即 row: 0-100, col: 0-50
# 地图显示：X轴=row(0-100), Y轴=col(0-50)
# row 中轴约在 50，左右分布需要改变 row 坐标
radius = 8

# 左侧六边形：row 约 30，col 在中间
hexagon1_center = (30, 25)
hexagon1_vertices = create_hexagon(hexagon1_center, radius)
fill_hexagon(map_, hexagon1_vertices)

# 右侧六边形：row 约 70，col 在中间
hexagon2_center = (70, 25)
hexagon2_vertices = create_hexagon(hexagon2_center, radius)
fill_hexagon(map_, hexagon2_vertices)

map_.inflate_obstacles(radius=0)

print("=" * 70)
print("Boustrophedon Decomposition with 2 Hexagon Obstacles")
print("=" * 70)
print(f"Map size: {map_.shape}")
print(f"Hexagon 1: center={hexagon1_center}, radius={radius}")
print(f"Hexagon 2: center={hexagon2_center}, radius={radius}")
print()

# 4. 执行牛耕分解
print("Executing Boustrophedon Decomposition...")
cells, critical_cols = boustrophedon_decomposition(map_)
print(f"Decomposed into {len(cells)} cells")
print(f"Critical columns (topology changes): {critical_cols}")
print()

# 5. 为单元着色
decomp_map = Grid(bounds=map_.bounds, resolution=map_.resolution)
decomp_map.type_map.update(map_.type_map.array.copy())

color_types = [7, 8, 9, 10, 11, 12, TYPES.CUSTOM]
for i, cell in enumerate(cells):
    color_id = color_types[i % len(color_types)]
    for pos in cell.positions:
        if decomp_map.type_map[pos] == TYPES.FREE:
            decomp_map.type_map[pos] = color_id

# 6. 可视化
vis = Visualizer("Boustrophedon Decomposition")
vis.plot_grid_map(decomp_map)

# 绘制关键线（红色虚线标记拓扑变化位置）
print(f"Drawing {len(critical_cols)} critical lines at columns: {critical_cols}")

for col in critical_cols:
    # 正确的坐标转换：(row, col) -> (world_y, world_x)
    world_x = col * map_.resolution + map_.bounds[0][0]
    print(f"  Drawing line at col={col}, world_x={world_x}")
    # 画一条从底部到顶部的红色粗虚线
    vis.ax.axvline(x=world_x, color='red', linestyle='--',
                  linewidth=4, alpha=1.0, zorder=1000)

# 添加图例说明红线含义
vis.ax.plot([], [], color='red', linestyle='--', linewidth=4, label='Critical Lines (Topology Changes)')
vis.ax.legend(loc='upper right', fontsize=12)

# 标注单元编号
for cell in cells:
    positions = list(cell.positions)
    if positions:
        rows = [p[0] for p in positions]
        cols = [p[1] for p in positions]
        center_row = int(np.mean(rows))
        center_col = int(np.mean(cols))
        center_world = map_.map_to_world((center_row, center_col))

        vis.ax.text(center_world[0], center_world[1],
                   f"C{cell.id}",
                   ha='center', va='center',
                   fontsize=14, fontweight='bold',
                   color='blue', zorder=200,
                   bbox=dict(boxstyle='round', facecolor='white',
                            alpha=0.8, edgecolor='blue', linewidth=2))

# 7. 添加标注 - ⚠️ 不可变约束（只改算法名称）
vis.ax.text(
    0.5, 1.08,
    "Boustrophedon Decomposition",  # ← 只能改这里
    transform=vis.ax.transAxes,
    ha="center", va="top",
    fontsize=20,
    zorder=10000
)

# 8. 保存图片
output_path = "C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/pic/boustrophedon_decomposition.png"
vis.fig.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Image saved to: {output_path}")
vis.close()

print()
print("=" * 70)
print("Visualization completed!")
print(f"Total cells: {len(cells)}")
print(f"Output: {output_path}")
print("=" * 70)
