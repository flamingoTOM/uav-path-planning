# -*- coding: utf-8 -*-
"""
全覆盖路径规划 (Full Coverage Path Planning) — 分区蛇形扫描
地图：回字形障碍（x=15..85, y=15..35 矩形框）

路径分 4 个区域顺序覆盖，全程连续无跨障碍跳跃：
  Zone A  左侧条带  x=1..14,  y=1..49
  Zone B  中间下方  x=16..84, y=1..14
  Zone C  右侧条带  x=86..99, y=1..49
  Zone D  中间上方  x=84..16, y=36..49 (反向扫描)
"""

# ===================================================================
#  CONFIG  ← 用户可修改
# ===================================================================
START      = (2, 2)
COVERAGE_W = 3        # 单次扫描覆盖宽度（像素）
OVERLAP_R  = 0.2      # 目标重叠率
# ===================================================================

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math

W, H = 101, 51

# ------------------------------------------------------------------
# 1. 地图
# ------------------------------------------------------------------
obs = np.zeros((W, H), dtype=bool)
obs[0, :] = obs[W-1, :] = True
obs[:, 0] = obs[:, H-1] = True
OX1, OX2, OY1, OY2 = 15, 85, 15, 35
obs[OX1:OX2+1, OY1] = True
obs[OX1:OX2+1, OY2] = True
obs[OX1, OY1:OY2+1] = True
obs[OX2, OY1:OY2+1] = True
free = ~obs

# ------------------------------------------------------------------
# 2. 洪水填充（可达性）
# ------------------------------------------------------------------
sx, sy = START
reach = np.zeros((W, H), dtype=bool)
stack = [(sx, sy)]
while stack:
    cx, cy = stack.pop()
    if cx < 0 or cx >= W or cy < 0 or cy >= H:
        continue
    if obs[cx, cy] or reach[cx, cy]:
        continue
    reach[cx, cy] = True
    stack += [(cx+1,cy),(cx-1,cy),(cx,cy+1),(cx,cy-1)]

# ------------------------------------------------------------------
# 3. 分区蛇形路径规划
# ------------------------------------------------------------------
step   = max(1, int(COVERAGE_W * (1.0 - OVERLAP_R)))
half_w = COVERAGE_W // 2

xs_A = list(range(1,  15, step))       # 左侧  x=1..14
xs_B = list(range(16, 85, step))       # 中下  x=16..84
xs_C = list(range(86, 100, step))      # 右侧  x=86..99
xs_D = list(range(84, 15, -step))      # 中上  x=84..16 (反向)

path = [(sx, sy)]


def sweep_col(x, y_min, y_max, dir_y):
    """扫描列 x 的 y=y_min..y_max，dir_y=1 从下往上，-1 从上往下。
    返回翻转后的新 dir_y。"""
    ys = [y for y in range(y_min, y_max+1) if reach[x, y]]
    if not ys:
        return -dir_y
    ys_s = sorted(ys, reverse=(dir_y == -1))
    # 移动到该列起点
    if path[-1] != (x, ys_s[0]):
        path.append((x, ys_s[0]))
    for y in ys_s:
        if path[-1] != (x, y):
            path.append((x, y))
    return -dir_y


def go_to(tx, ty):
    """L 形路由：先改 y，再改 x（两步均在可达区域内）"""
    cx, cy = path[-1]
    if cy != ty:
        path.append((cx, ty))
    if cx != tx:
        path.append((tx, ty))


# Zone A：左侧条带（全高）
d = 1
for x in xs_A:
    d = sweep_col(x, 1, 49, d)

# 过渡 A→B：去到 (16, 1)
go_to(16, 1)

# Zone B：中间下方
d = 1
for x in xs_B:
    d = sweep_col(x, 1, 14, d)

# 过渡 B→C：横向到 x=86（y 不变）
cx, cy = path[-1]
go_to(86, cy)

# Zone C：右侧条带（全高）
d = 1
for x in xs_C:
    d = sweep_col(x, 1, 49, d)

# 过渡 C→D：去到 (84, 36)
go_to(84, 36)

# Zone D：中间上方（反向，从 x=84 向 x=16）
d = 1
for x in xs_D:
    d = sweep_col(x, 36, 49, d)

# ------------------------------------------------------------------
# 4. 覆盖统计
# ------------------------------------------------------------------
coverage_count = np.zeros((W, H), dtype=int)

def add_coverage(sweep_xs, y_min, y_max):
    for x in sweep_xs:
        for y in range(y_min, y_max+1):
            if not reach[x, y]:
                continue
            for dx in range(-half_w, half_w+1):
                cx2 = x + dx
                if 0 <= cx2 < W and reach[cx2, y]:
                    coverage_count[cx2, y] += 1

add_coverage(xs_A, 1, 49)
add_coverage(xs_B, 1, 14)
add_coverage(xs_C, 1, 49)
add_coverage(xs_D, 36, 49)

n_reach   = int(reach.sum())
n_covered = int((coverage_count > 0).sum())
n_overlap = int((coverage_count > 1).sum())
cov_rate  = n_covered / n_reach * 100 if n_reach else 0
ov_rate   = n_overlap / n_covered * 100 if n_covered else 0

path_length = sum(
    math.sqrt((path[i+1][0]-path[i][0])**2 + (path[i+1][1]-path[i][1])**2)
    for i in range(len(path)-1)
)

print("=" * 58)
print("Full Coverage Path Planning  —  Zone Boustrophedon")
print("=" * 58)
print(f"  Start          : {START}")
print(f"  Coverage width : {COVERAGE_W} px  step={step}")
print(f"  Reachable      : {n_reach}")
print(f"  Covered        : {n_covered}  ({cov_rate:.1f}%)")
print(f"  Overlap cells  : {n_overlap}  ({ov_rate:.1f}%)")
print(f"  Waypoints      : {len(path)}")
print(f"  Path length    : {path_length:.1f} px")
print("=" * 58)

# ------------------------------------------------------------------
# 5. 可视化
# ------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(13, 7.5))
fig.patch.set_facecolor('#f2f2f2')
ax.set_facecolor('#ffffff')

# 颜色图
rgb = np.ones((H, W, 3), dtype=float)
for x in range(W):
    for y in range(H):
        if obs[x, y]:
            rgb[y, x] = [0.08, 0.08, 0.08]
        elif not reach[x, y] and free[x, y]:
            rgb[y, x] = [0.08, 0.08, 0.08]      # 内部黑色填充
        elif coverage_count[x, y] > 1:
            rgb[y, x] = [0.40, 0.40, 0.40]      # 深灰：重叠
        elif coverage_count[x, y] == 1:
            rgb[y, x] = [0.77, 0.77, 0.77]      # 浅灰：单次覆盖

ax.imshow(rgb, origin='lower', extent=[0, W, 0, H],
          zorder=1, interpolation='nearest', aspect='auto')

# 路径：红色粗实线，一条连续线
all_px = [p[0] for p in path]
all_py = [p[1] for p in path]
ax.plot(all_px, all_py, '-', color='#E53935',
        linewidth=3.5, solid_capstyle='round',
        solid_joinstyle='round', zorder=50)

# 起点
ax.plot(sx, sy, 'o', color='white', markersize=6, zorder=51)

ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.set_xlabel('X (pixels)', fontsize=10)
ax.set_ylabel('Y (pixels)', fontsize=10)

# 固定格式标题
ax.text(
    0.5, 1.08,
    "Full Coverage Path Planning",
    transform=ax.transAxes,
    ha="center", va="top",
    fontsize=20,
    zorder=10000
)

plt.tight_layout()
output_path = "C:/Users/22982/Desktop/uav-path-planning/pic/coverage_ring.png"
plt.savefig(output_path, dpi=200, bbox_inches='tight',
            facecolor=fig.get_facecolor())
print(f"Saved -> {output_path}")
plt.close()
