import random
random.seed(0)
import numpy as np
np.random.seed(0)
import sys
sys.path.append("C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/example")
from python_motion_planning.common import *
from python_motion_planning.path_planner import *

# 创建地图
map_ = Grid(bounds=[[0, 101], [0, 51]])
map_.fill_boundary_with_obstacles()

# 添加障碍物
map_.type_map[10:21, 25] = TYPES.OBSTACLE
map_.type_map[20, :25] = TYPES.OBSTACLE
map_.type_map[35, 15:] = TYPES.OBSTACLE
map_.type_map[70, :16] = TYPES.OBSTACLE
map_.type_map[55, 29:] = TYPES.OBSTACLE
map_.type_map[55:85, 29] = TYPES.OBSTACLE
map_.inflate_obstacles(radius=2)

# 设置起点和终点
start = (5, 5)
goal = (70, 40)
map_.type_map[start] = TYPES.START
map_.type_map[goal] = TYPES.GOAL

print("正在使用 RRT 算法规划路径...")
print(f"起点: {start}, 终点: {goal}")

# 创建规划器并规划路径
planner = RRT(map_=map_, start=start, goal=goal)
path, path_info = planner.plan()

print(f"路径规划完成！")
print(f"路径点数: {len(path)}")
print(f"路径成本: {path_info['cost']:.3f}")

# 可视化
vis = Visualizer("RRT Path Visualizer")
vis.plot_grid_map(map_)

# RRT 算法通常会绘制搜索树
if "expand_tree" in path_info:
    vis.plot_expand_tree(path_info["expand_tree"], node_color="#90EE90", edge_color="#90EE90",
                         node_size=3, linewidth=0.5, node_alpha=0.6, edge_alpha=0.4)

vis.plot_path(path)

# 添加文本标注
vis.ax.text(
    0.5, 1.08,
    "RRT",
    transform=vis.ax.transAxes,
    ha="center", va="top",
    fontsize=20,
    zorder=10000
)

# 保存图片
output_path = "C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/pic/rrt.png"
vis.fig.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\n成功！图片已保存至: {output_path}")

vis.close()
