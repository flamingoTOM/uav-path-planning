import random
random.seed(0)
import numpy as np
np.random.seed(0)
import sys
sys.path.append("C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/example")
from python_motion_planning.common import *
from python_motion_planning.path_planner import *

# 1. 创建地图
map_ = Grid(bounds=[[0, 101], [0, 51]])
map_.fill_boundary_with_obstacles()

# 2. 添加障碍物
map_.type_map[10:21, 25] = TYPES.OBSTACLE
map_.type_map[20, :25] = TYPES.OBSTACLE
map_.type_map[35, 15:] = TYPES.OBSTACLE
map_.type_map[70, :16] = TYPES.OBSTACLE
map_.type_map[55, 29:] = TYPES.OBSTACLE
map_.type_map[55:85, 29] = TYPES.OBSTACLE
map_.inflate_obstacles(radius=2)

# 3. 设置起点和终点
start = (5, 5)
goal = (70, 40)
map_.type_map[start] = TYPES.START
map_.type_map[goal] = TYPES.GOAL

# 4. 创建规划器并规划路径
planner = ThetaStar(map_=map_, start=start, goal=goal)
path, path_info = planner.plan()

# 5. 可视化
map_.fill_expands(path_info["expand"])
vis = Visualizer("Theta* Algorithm Visualizer")
vis.plot_grid_map(map_)
vis.plot_path(path)

# 6. 添加标注
vis.ax.text(
    0.5, 1.08,
    "Theta* Algorithm",
    transform=vis.ax.transAxes,
    ha="center", va="top",
    fontsize=20,
    zorder=10000
)

# 7. 保存图片
output_path = "C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/pic/theta_star.png"
vis.fig.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\n成功！图片已保存至: {output_path}")
vis.close()
