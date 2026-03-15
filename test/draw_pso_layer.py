# -*- coding: utf-8 -*-
"""
PSO 分层覆盖路径规划 — 独立测试脚本

合成地形（101×51 高斯山丘）+ 不规则六边形，
2 子图可视化：
  左：层分解热力图
  右：完整路径（每层不同颜色，Theta* 连线红虚线）

运行：
  /d/02-APP/29-anaconda/02-app/envs/pmp/python.exe test/draw_pso_layer.py
"""

import sys
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors

# 加入 LVIZ algorithms 路径
sys.path.append("C:/Users/22982/Desktop/uav-path-planning/LVIZ/algorithms")
from pso_layer_planner import (
    generate_path, build_poly_mask, decompose_layers,
    pso_plan_layer, theta_star_connect, find_nearest_valid,
)

# ==================== 1. 合成地形 101×51 ====================
WIDTH, HEIGHT = 101, 51

elevation = np.zeros((HEIGHT, WIDTH), dtype=float)
for y in range(HEIGHT):
    for x in range(WIDTH):
        elevation[y, x] = (
            100.0
            + 300.0 * math.exp(-((x - 50) ** 2 / 400.0 + (y - 25) ** 2 / 100.0))
        )

# ==================== 2. 不规则六边形多边形 ====================
polygon = [
    (15,  5),
    (85,  5),
    (95, 25),
    (85, 45),
    (15, 45),
    ( 5, 25),
]

# ==================== 3. 规划 ====================
terrain_data = {
    'elevation': elevation,
    'width': WIDTH,
    'height': HEIGHT,
    'min_elevation': float(elevation.min()),
    'max_elevation': float(elevation.max()),
}
params = {
    'min_altitude': 50.0,
    'coverage_width': 8.0,
    'overlap_rate': 0.2,
    'num_layers': 5,
}

print("=" * 60)
print("PSO Layered Coverage Path Planning")
print("=" * 60)
print(f"Terrain: {WIDTH}×{HEIGHT} pixels")
print(f"Coverage width: {params['coverage_width']} m, "
      f"Overlap: {params['overlap_rate']:.0%}")
print(f"Layers: {params['num_layers']}")
print("Planning...")

result = generate_path(terrain_data, polygon, params)

path = result['path']
stats = result['statistics']

# 重新执行内部步骤以获取可视化所需的层细节
# （PSO 固定随机种子，结果与 generate_path() 内部完全一致）
_line_spacing = max(3.0, params['coverage_width'] * (1.0 - params['overlap_rate']))
_poly_mask = build_poly_mask(polygon, WIDTH, HEIGHT)
layers = decompose_layers(elevation, _poly_mask, num_layers=params['num_layers'])

layer_paths = []
connection_paths = []
_prev_last = None
for _layer in layers:
    _lpath = pso_plan_layer(_layer, _line_spacing)
    if not _lpath:
        _ys, _xs = np.where(_layer['mask'])
        if len(_xs) > 0:
            _lpath = [(int(_xs[0]), int(_ys[0]))]
        else:
            continue
    layer_paths.append((_layer['layer_id'], _lpath))
    if _prev_last is not None:
        _near = find_nearest_valid(_prev_last, _layer['mask'], WIDTH, HEIGHT) or _lpath[0]
        connection_paths.append(
            theta_star_connect(_prev_last, _near, _poly_mask, WIDTH, HEIGHT)
        )
    _prev_last = _lpath[-1]

print()
print(f"  Layers found      : {len(layers)}")
print(f"  Waypoints         : {stats.get('waypoint_count', 0)}")
print(f"  Total distance    : {stats.get('total_distance', 0):.1f} m")
print(f"  Coverage area     : {stats.get('coverage_area_m2', 0):.0f} m2")
print(f"  Line spacing      : {stats.get('line_spacing', 0):.1f} m")
print(f"  Altitude range    : "
      f"{stats.get('plan_min_alt', 0):.1f} ~ "
      f"{stats.get('plan_max_alt', 0):.1f} m")
print(f"  Estimated time    : {stats.get('estimated_time', 0):.1f} s")
print(f"  Algorithm         : {stats.get('algorithm', '')}")

# ==================== 4. 可视化 ====================
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.patch.set_facecolor('#f8f8f8')

n_layers = len(layers)
cmap_layers = plt.colormaps.get_cmap('tab10').resampled(max(n_layers, 1))
layer_colors = [cmap_layers(i) for i in range(n_layers)]

# ---------- 左图：层分解热力图 ----------
ax1 = axes[0]
ax1.set_facecolor('#e8e8e8')

# 1a. 灰度高程背景
ax1.imshow(elevation, cmap='gray', origin='upper',
           extent=[0, WIDTH, HEIGHT, 0], alpha=0.55, zorder=1)

# 1b. 层颜色叠加（逐层着色）
label_map = np.full((HEIGHT, WIDTH), np.nan, dtype=float)
for layer_info in layers:
    label_map[layer_info['mask']] = float(layer_info['layer_id'])

if n_layers > 0:
    masked_label = np.ma.masked_invalid(label_map)
    ax1.imshow(masked_label, cmap=cmap_layers, vmin=-0.5, vmax=n_layers - 0.5,
               origin='upper', extent=[0, WIDTH, HEIGHT, 0], alpha=0.6, zorder=2)

# 1c. 多边形轮廓
poly_xs = [p[0] for p in polygon] + [polygon[0][0]]
poly_ys = [p[1] for p in polygon] + [polygon[0][1]]
ax1.plot(poly_xs, poly_ys, 'k-', linewidth=2, zorder=5, label='Polygon')

# 1d. 高程等值线
try:
    cs = ax1.contour(elevation, levels=8, colors='white',
                     origin='upper', linewidths=0.7, alpha=0.5, zorder=3)
    ax1.clabel(cs, inline=True, fontsize=7, fmt='%.0f')
except Exception:
    pass

# 图例
legend_patches = [
    mpatches.Patch(
        color=layer_colors[l['layer_id']],
        label=f"L{l['layer_id']} {l['elev_low']:.0f}–{l['elev_high']:.0f} m"
    )
    for l in layers
]
ax1.legend(handles=legend_patches, loc='lower right', fontsize=8,
           framealpha=0.85)

ax1.set_xlim(0, WIDTH)
ax1.set_ylim(HEIGHT, 0)
ax1.set_xlabel('X (pixels)', fontsize=10)
ax1.set_ylabel('Y (pixels)', fontsize=10)
ax1.set_title('Layer Decomposition (Elevation Contours)', fontsize=12)

# ---------- 右图：完整路径 ----------
ax2 = axes[1]
ax2.set_facecolor('#e8e8e8')

# 2a. 灰度高程背景
ax2.imshow(elevation, cmap='gray', origin='upper',
           extent=[0, WIDTH, HEIGHT, 0], alpha=0.35, zorder=1)

# 2b. 多边形轮廓
ax2.plot(poly_xs, poly_ys, 'k-', linewidth=2, zorder=5)

# 2c. 各层路径（不同颜色）
layer_path_dict = dict(layer_paths)
for layer_info in layers:
    lid = layer_info['layer_id']
    if lid not in layer_path_dict:
        continue
    lp = layer_path_dict[lid]
    if len(lp) < 1:
        continue
    color = layer_colors[lid % n_layers]
    lp_xs = [p[0] for p in lp]
    lp_ys = [p[1] for p in lp]
    ax2.plot(lp_xs, lp_ys, '-o', color=color,
             markersize=4, linewidth=1.8, zorder=10,
             label=f'Layer {lid}')
    # 起点标记
    ax2.plot(lp_xs[0], lp_ys[0], 's', color=color,
             markersize=7, zorder=12, markeredgecolor='black')

# 2d. Theta* 连接线（红色虚线）
conn_plotted = False
for conn in connection_paths:
    if len(conn) >= 2:
        cx = [p[0] for p in conn]
        cy = [p[1] for p in conn]
        ax2.plot(cx, cy, 'r--', linewidth=1.5, alpha=0.85, zorder=8,
                 label='Theta* connection' if not conn_plotted else '_')
        conn_plotted = True

# 2e. 整体路径轮廓（淡灰）
if path:
    all_xs = [p['x'] for p in path]
    all_ys = [p['y'] for p in path]
    ax2.plot(all_xs, all_ys, '-', color='#aaaaaa',
             linewidth=0.7, alpha=0.4, zorder=6)

ax2.legend(loc='lower right', fontsize=8, framealpha=0.85)

# 2f. 统计文本框
stats_text = (
    f"Waypoints : {stats.get('waypoint_count', 0)}\n"
    f"Distance  : {stats.get('total_distance', 0):.0f} m\n"
    f"Layers    : {n_layers}\n"
    f"Spacing   : {stats.get('line_spacing', 0):.1f} m\n"
    f"Est. time : {stats.get('estimated_time', 0):.0f} s"
)
ax2.text(0.02, 0.98, stats_text, transform=ax2.transAxes,
         verticalalignment='top', fontsize=9,
         fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85),
         zorder=20)

ax2.set_xlim(0, WIDTH)
ax2.set_ylim(HEIGHT, 0)
ax2.set_xlabel('X (pixels)', fontsize=10)
ax2.set_ylabel('Y (pixels)', fontsize=10)
ax2.set_title('Coverage Path (PSO Optimized Boustrophedon)', fontsize=12)

# ==================== 5. 总标题 ====================
fig.text(0.5, 1.02,
         "PSO Layered Coverage Path Planning",
         ha='center', va='top',
         fontsize=18, fontweight='bold')

plt.tight_layout()

output_path = "C:/Users/22982/Desktop/uav-path-planning/pic/pso_layer.png"
plt.savefig(output_path, dpi=150, bbox_inches='tight',
            facecolor=fig.get_facecolor())
print()
print(f"Saved → {output_path}")
plt.close()

print()
print("=" * 60)
print("Done.")
print("=" * 60)
