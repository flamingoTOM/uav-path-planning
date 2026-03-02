import random
random.seed(0)
import numpy as np
np.random.seed(0)
from python_motion_planning.common import *
from python_motion_planning.path_planner import *
from python_motion_planning.controller import *

##########################           地图           ###############################
map_ = Grid(bounds=[[0, 101], [0, 51]])
map_.fill_boundary_with_obstacles()    #把地图最外圈封成障碍，防止路径贴边出界
map_.type_map[10:21, 25] = TYPES.OBSTACLE
map_.type_map[20, :25] = TYPES.OBSTACLE
map_.type_map[35, 15:] = TYPES.OBSTACLE
map_.type_map[70, :16] = TYPES.OBSTACLE
map_.type_map[55, 29:] = TYPES.OBSTACLE
map_.type_map[55:85, 29] = TYPES.OBSTACLE
map_.inflate_obstacles(radius=2)
start = (5, 5)
goal = (70, 40)
map_.type_map[start] = TYPES.START
map_.type_map[goal] = TYPES.GOAL
##################################################################################



planner = AStar(map_=map_, start=start, goal=goal)
path, path_info = planner.plan()
print(path)
print(path_info)

map_.fill_expands(path_info["expand"])  # 将规划过程中扩展的节点（搜索树中的节点）在地图上标记出来，用于可视化

vis = Visualizer("Path Visualizer")
vis.plot_grid_map(map_)
vis.plot_path(path)


cost = path_info["cost"]
vis.ax.text(
    0.36, 1.2,
    f"      A_Star\nCost: {cost:.3f}",
    transform=vis.ax.transAxes,
    ha="left", va="top",
    fontsize=20,
    zorder=10000
)

vis.show()
vis.close()