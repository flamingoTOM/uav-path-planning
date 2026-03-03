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

print("正在使用 PRM 算法规划路径...")
print(f"起点: {start}, 终点: {goal}")

# 4. 创建规划器并规划路径
planner = PRM(map_=map_, start=start, goal=goal, sample_num=500, k_neighbors=10)
path, path_info = planner.plan()

if path_info['success']:
    print(f"路径规划完成！")
    print(f"路径点数: {len(path)}")
    print(f"路径成本: {path_info['cost']:.3f}")
else:
    print("路径规划失败！")

# 5. 可视化
# 将所有采样节点标记为扩展节点
roadmap_nodes = {}
for point, data in planner.roadmap.items():
    roadmap_nodes[point] = data['node']

map_.fill_expands(roadmap_nodes)
vis = Visualizer("PRM Path Visualizer")
vis.plot_grid_map(map_)

# 绘制路线图的边（邻接关系）
for point, data in planner.roadmap.items():
    for neighbor in data['neighbors']:
        x_coords = [point[0], neighbor[0]]
        y_coords = [point[1], neighbor[1]]
        vis.ax.plot(x_coords, y_coords, 'c-', linewidth=0.5, alpha=0.3, zorder=1)

# 绘制路径
vis.plot_path(path)

# 6. 添加文本标注
vis.ax.text(
    0.5, 1.08,
    "PRM (Probabilistic Roadmap Method)",
    transform=vis.ax.transAxes,
    ha="center", va="top",
    fontsize=20,
    zorder=10000
)

# 7. 保存图片
output_path = "C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/pic/prm.png"
vis.fig.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\n成功！图片已保存至: {output_path}")

vis.close()
