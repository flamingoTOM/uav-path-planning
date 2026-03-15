# -*- coding: utf-8 -*-
"""
PSO (Particle Swarm Optimization) Path Planning
粒子群优化 - 从起点到终点的最短无碰路径规划

每个粒子编码 N_WP 个中间路径点，适应度 = 路径总长 + 障碍穿越惩罚
"""
import random
random.seed(42)
import numpy as np
np.random.seed(42)
import sys
import math
sys.path.append("C:/Users/22982/Desktop/uav-path-planning/example")
from python_motion_planning.common import *
from python_motion_planning.path_planner import *

# ==================== 1. 创建地图 ====================
map_ = Grid(bounds=[[0, 101], [0, 51]])
map_.fill_boundary_with_obstacles()

map_.type_map[10:21, 25] = TYPES.OBSTACLE
map_.type_map[20, :25]   = TYPES.OBSTACLE
map_.type_map[35, 15:]   = TYPES.OBSTACLE
map_.type_map[70, :16]   = TYPES.OBSTACLE
map_.type_map[55, 29:]   = TYPES.OBSTACLE
map_.type_map[55:85, 29] = TYPES.OBSTACLE
map_.inflate_obstacles(radius=2)

start = (5, 5)
goal  = (70, 40)
map_.type_map[start] = TYPES.START
map_.type_map[goal]  = TYPES.GOAL

# ==================== 2. PSO 路径规划 ====================
N_WP        = 5      # 中间路径点数量
N_PARTICLES = 40     # 粒子数
N_ITER      = 150    # 迭代次数
SX, SY = start
GX, GY = goal

X_MIN, X_MAX = 1.0, 99.0
Y_MIN, Y_MAX = 1.0, 49.0
DIM = 2 * N_WP
LB  = np.tile([X_MIN, Y_MIN], N_WP).astype(float)
UB  = np.tile([X_MAX, Y_MAX], N_WP).astype(float)


def is_obstacle(x, y):
    xi = int(round(max(0, min(100, x))))
    yi = int(round(max(0, min(50,  y))))
    t = map_.type_map[xi, yi]
    # 包含原始障碍物(OBSTACLE)和膨胀区域(INFLATION)
    return t == TYPES.OBSTACLE or t == TYPES.INFLATION


def segment_cost(p1, p2):
    """欧氏长度 + 障碍穿越惩罚（每个障碍采样点 +200）"""
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    length  = math.sqrt(dx * dx + dy * dy)
    # 每 0.5 像素采样一次，不遗漏 1px 薄墙
    n_samples = max(3, int(length * 2) + 2)
    penalty = 0
    for t in np.linspace(0, 1, n_samples):
        if is_obstacle(p1[0] + t * dx, p1[1] + t * dy):
            penalty += 1
    return length + penalty * 200.0


def path_fitness(particle):
    """粒子适应度：值越小路径越优"""
    pts = [(float(SX), float(SY))]
    for i in range(N_WP):
        pts.append((particle[2 * i], particle[2 * i + 1]))
    pts.append((float(GX), float(GY)))
    return sum(segment_cost(pts[k], pts[k + 1]) for k in range(len(pts) - 1))


def pso_search():
    rng = np.random.RandomState(42)

    # 初始化
    pos  = LB + rng.rand(N_PARTICLES, DIM) * (UB - LB)
    vel  = np.zeros((N_PARTICLES, DIM))
    fits = np.array([path_fitness(pos[i]) for i in range(N_PARTICLES)])

    pbest_pos = pos.copy()
    pbest_fit = fits.copy()
    gi         = int(np.argmin(pbest_fit))
    gbest_pos  = pbest_pos[gi].copy()
    gbest_fit  = float(pbest_fit[gi])

    w, c1, c2 = 0.7, 1.5, 1.5
    explored   = []

    for it in range(N_ITER):
        r1  = rng.rand(N_PARTICLES, DIM)
        r2  = rng.rand(N_PARTICLES, DIM)
        vel = (w * vel
               + c1 * r1 * (pbest_pos - pos)
               + c2 * r2 * (gbest_pos - pos))
        pos = np.clip(pos + vel, LB, UB)

        for i in range(N_PARTICLES):
            f = path_fitness(pos[i])
            if f < pbest_fit[i]:
                pbest_fit[i] = f
                pbest_pos[i] = pos[i].copy()
            if f < gbest_fit:
                gbest_fit = f
                gbest_pos = pos[i].copy()

        # 每 10 次迭代记录粒子中间点（可视化探索区域）
        if it % 10 == 0:
            for i in range(N_PARTICLES):
                for wp in range(N_WP):
                    x = int(round(pos[i, 2 * wp]))
                    y = int(round(pos[i, 2 * wp + 1]))
                    if 0 <= x <= 100 and 0 <= y <= 50:
                        explored.append((x, y))

        if it % 30 == 0:
            print(f"  iter {it:3d} | best fitness = {gbest_fit:.2f}")

    # 构造最终路径
    final_path = [(SX, SY)]
    for i in range(N_WP):
        final_path.append((int(round(gbest_pos[2 * i])),
                           int(round(gbest_pos[2 * i + 1]))))
    final_path.append((GX, GY))

    return final_path, explored, gbest_fit


print("=" * 50)
print("PSO Path Planning")
print(f"Start: {start}  Goal: {goal}")
print(f"Particles: {N_PARTICLES}  Iters: {N_ITER}  Waypoints: {N_WP}")
print("=" * 50)

path, explored, best_cost = pso_search()

path_length = sum(
    math.sqrt((path[i+1][0]-path[i][0])**2 + (path[i+1][1]-path[i][1])**2)
    for i in range(len(path)-1)
)
print(f"\nBest fitness : {best_cost:.2f}")
print(f"Path length  : {path_length:.2f}")
print(f"Path         : {path}")

# ==================== 3. 可视化 ====================
# fill_expands 需要 dict（key=位置元组, value 任意）
map_.fill_expands({pos: 1 for pos in explored})

vis = Visualizer("PSO Path Visualizer")
vis.plot_grid_map(map_)
vis.plot_path(path)

# 固定格式标题（不可变约束）
vis.ax.text(
    0.5, 1.08,
    "PSO",
    transform=vis.ax.transAxes,
    ha="center", va="top",
    fontsize=20,
    zorder=10000
)

# 统计信息小标注
info = (
    f"Particles : {N_PARTICLES}  |  Iters : {N_ITER}  |  "
    f"Waypoints : {N_WP}\n"
    f"Path length : {path_length:.1f}  |  Fitness : {best_cost:.1f}"
)
vis.ax.text(
    0.5, -0.06, info,
    transform=vis.ax.transAxes,
    ha="center", va="top",
    fontsize=9, color="#444444",
    zorder=10000
)

output_path = "C:/Users/22982/Desktop/uav-path-planning/pic/pso_path.png"
vis.fig.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\nSaved -> {output_path}")
vis.close()

print("=" * 50)
print("Done.")
print("=" * 50)
