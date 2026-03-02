"""
快速生成算法可视化图片的脚本
用法: python draw_algorithm.py <algorithm_name>
"""
import random
random.seed(0)
import numpy as np
np.random.seed(0)
import sys
import os

# 添加 example 路径
sys.path.append("C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/example")
from python_motion_planning.common import *
from python_motion_planning.path_planner import *

# 算法名称映射
ALGORITHM_MAP = {
    'a*': ('AStar', 'A*'),
    'astar': ('AStar', 'A*'),
    'a_star': ('AStar', 'A*'),
    'dijkstra': ('Dijkstra', 'Dijkstra'),
    'theta*': ('ThetaStar', 'Theta*'),
    'thetastar': ('ThetaStar', 'Theta*'),
    'theta_star': ('ThetaStar', 'Theta*'),
    'jps': ('JPS', 'JPS'),
    'jump_point_search': ('JPS', 'JPS'),
    'randomcollision': ('RandomCollision', 'RandomCollision'),
    'random_collision': ('RandomCollision', 'RandomCollision'),
    'rrt': ('RRT', 'RRT'),
    'rrt*': ('RRTStar', 'RRT*'),
    'rrtstar': ('RRTStar', 'RRT*'),
    'rrt_star': ('RRTStar', 'RRT*'),
}

def draw_algorithm(algorithm_name, start=(5, 5), goal=(70, 40), custom_obstacles=None):
    """
    绘制指定算法的路径规划可视化图

    参数:
        algorithm_name: 算法名称（字符串）
        start: 起点坐标，默认 (5, 5)
        goal: 终点坐标，默认 (70, 40)
        custom_obstacles: 自定义障碍物列表（可选）

    返回:
        保存的图片路径
    """
    # 规范化算法名称
    normalized = algorithm_name.lower().strip().replace(' ', '_')
    if normalized not in ALGORITHM_MAP:
        print(f"错误: 不支持的算法 '{algorithm_name}'")
        print("\n支持的算法:")
        for key in sorted(set([v[1] for v in ALGORITHM_MAP.values()])):
            print(f"  - {key}")
        return None

    algorithm_class, display_name = ALGORITHM_MAP[normalized]

    # 创建地图
    map_ = Grid(bounds=[[0, 101], [0, 51]])
    map_.fill_boundary_with_obstacles()

    # 添加障碍物
    if custom_obstacles is None:
        # 使用默认障碍物布局
        map_.type_map[10:21, 25] = TYPES.OBSTACLE
        map_.type_map[20, :25] = TYPES.OBSTACLE
        map_.type_map[35, 15:] = TYPES.OBSTACLE
        map_.type_map[70, :16] = TYPES.OBSTACLE
        map_.type_map[55, 29:] = TYPES.OBSTACLE
        map_.type_map[55:85, 29] = TYPES.OBSTACLE
        map_.inflate_obstacles(radius=2)
    else:
        # 使用自定义障碍物
        for obstacle in custom_obstacles:
            map_.type_map[obstacle] = TYPES.OBSTACLE
        map_.inflate_obstacles(radius=2)

    # 设置起点和终点
    map_.type_map[start] = TYPES.START
    map_.type_map[goal] = TYPES.GOAL

    print(f"正在使用 {display_name} 算法规划路径...")
    print(f"起点: {start}, 终点: {goal}")

    # 创建规划器并规划路径
    planner_class = globals()[algorithm_class]
    planner = planner_class(map_=map_, start=start, goal=goal)
    path, path_info = planner.plan()

    print(f"路径规划完成！")
    print(f"路径点数: {len(path)}")
    print(f"路径成本: {path_info['cost']:.3f}")

    # 填充扩展节点
    map_.fill_expands(path_info["expand"])

    # 可视化
    vis = Visualizer(f"{display_name} Path Visualizer")
    vis.plot_grid_map(map_)
    vis.plot_path(path)

    # 添加文本标注
    cost = path_info["cost"]
    vis.ax.text(
        0.36, 1.2,
        f"      {display_name}\\nCost: {cost:.3f}",
        transform=vis.ax.transAxes,
        ha="left", va="top",
        fontsize=20,
        zorder=10000
    )

    # 保存图片
    safe_name = display_name.lower().replace('*', '_star').replace(' ', '_')
    output_path = f"C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/pic/{safe_name}.png"

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    vis.fig.savefig(output_path, dpi=300, bbox_inches='tight')
    vis.close()

    print(f"\n成功！图片已保存至: {output_path}")
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python draw_algorithm.py <算法名称> [起点x] [起点y] [终点x] [终点y]")
        print("\n示例:")
        print("  python draw_algorithm.py 'A*'")
        print("  python draw_algorithm.py Dijkstra 10 10 80 40")
        print("\n支持的算法:")
        print("  - A* (AStar)")
        print("  - Dijkstra")
        print("  - Theta*")
        print("  - RRT")
        print("  - RRT*")
        sys.exit(1)

    algorithm = sys.argv[1]

    # 解析起点和终点（如果提供）
    if len(sys.argv) >= 6:
        start = (int(sys.argv[2]), int(sys.argv[3]))
        goal = (int(sys.argv[4]), int(sys.argv[5]))
        draw_algorithm(algorithm, start, goal)
    else:
        draw_algorithm(algorithm)
