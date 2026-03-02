"""
算法可视化脚本生成器
根据算法名称生成对应的可视化脚本
"""
import os
import sys

# 算法名称映射
ALGORITHM_MAP = {
    'a*': 'AStar',
    'astar': 'AStar',
    'a_star': 'AStar',
    'dijkstra': 'Dijkstra',
    'theta*': 'ThetaStar',
    'thetastar': 'ThetaStar',
    'theta_star': 'ThetaStar',
    'rrt': 'RRT',
    'rrt*': 'RRTStar',
    'rrtstar': 'RRTStar',
    'rrt_star': 'RRTStar',
}

def normalize_algorithm_name(user_input):
    """将用户输入的算法名称规范化为类名"""
    normalized = user_input.lower().strip().replace(' ', '_')
    return ALGORITHM_MAP.get(normalized, None)

def get_file_safe_name(algorithm_name):
    """获取文件安全的算法名称"""
    return algorithm_name.lower().replace('*', '_star').replace(' ', '_')

def generate_script_template(algorithm_class, algorithm_display_name, start=(5, 5), goal=(70, 40)):
    """生成可视化脚本模板"""
    template = f"""import random
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
start = {start}
goal = {goal}
map_.type_map[start] = TYPES.START
map_.type_map[goal] = TYPES.GOAL

# 创建规划器并规划路径
planner = {algorithm_class}(map_=map_, start=start, goal=goal)
path, path_info = planner.plan()

print(f"路径点数: {{len(path)}}")
print(f"路径信息: {{path_info}}")

# 填充扩展节点用于可视化
map_.fill_expands(path_info["expand"])

# 可视化
vis = Visualizer("{algorithm_display_name} Path Planner")
vis.plot_grid_map(map_)
vis.plot_path(path)

# 添加文本标注
cost = path_info["cost"]
vis.ax.text(
    0.36, 1.2,
    f"      {algorithm_display_name}\\nCost: {{cost:.3f}}",
    transform=vis.ax.transAxes,
    ha="left", va="top",
    fontsize=20,
    zorder=10000
)

# 保存图片
output_path = "C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/pic/{get_file_safe_name(algorithm_display_name)}.png"
vis.save(output_path)
print(f"图片已保存至: {{output_path}}")

vis.close()
"""
    return template

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python generate_visualization.py <algorithm_name> [start_x] [start_y] [goal_x] [goal_y]")
        print("\n支持的算法:")
        for key in sorted(set(ALGORITHM_MAP.values())):
            print(f"  - {key}")
        sys.exit(1)

    user_input = sys.argv[1]
    algorithm_class = normalize_algorithm_name(user_input)

    if algorithm_class is None:
        print(f"错误: 不支持的算法 '{user_input}'")
        print("\n支持的算法:")
        for key in sorted(set(ALGORITHM_MAP.values())):
            print(f"  - {key}")
        sys.exit(1)

    # 获取自定义起点和终点（如果提供）
    start = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) >= 4 else (5, 5)
    goal = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) >= 6 else (70, 40)

    # 生成脚本
    script_content = generate_script_template(algorithm_class, user_input, start, goal)

    # 保存脚本
    safe_name = get_file_safe_name(user_input)
    script_path = f"C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/test/draw_{safe_name}.py"

    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)

    print(f"脚本已生成: {script_path}")
    print(f"执行命令: python {script_path}")

    # 自动执行脚本
    os.system(f'python "{script_path}"')

if __name__ == "__main__":
    main()
