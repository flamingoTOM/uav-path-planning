import random
random.seed(0)
import numpy as np
np.random.seed(0)
import sys
sys.path.append("C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/example")
from python_motion_planning.common import *
from python_motion_planning.path_planner import *

##########################           地图           ###############################
map_ = Grid(bounds=[[0, 101], [0, 51]])
map_.fill_boundary_with_obstacles()
start = (5, 5)
goal = (70, 40)
map_.type_map[start] = TYPES.START
##################################################################################



planner = RandomCollision(map_=map_, start=start, goal=goal)
path, path_info = planner.plan()
print(f"Path points: {len(path)}")
print(f"Cost: {path_info['cost']:.3f}")

vis = Visualizer("Path Visualizer")
vis.plot_grid_map(map_)
vis.plot_path(path)


vis.ax.text(
    0.5, 1.08,
    "RandomCollision",
    transform=vis.ax.transAxes,
    ha="center", va="top",
    fontsize=20,
    zorder=10000
)

output_path = "C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/pic/random_collision.png"
vis.fig.savefig(output_path, dpi=300, bbox_inches='tight')
vis.close()
print(f"Saved: {output_path}")
