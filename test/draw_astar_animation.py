"""
生成 A* 算法动画
展示逐步搜索过程
"""
import random
random.seed(0)
import numpy as np
np.random.seed(0)
import sys
sys.path.append("C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/example")
from python_motion_planning.common import *
from python_motion_planning.path_planner import *
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import colors as mcolors

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

# 4. 修改 AStar 算法以记录每一步的扩展过程
class AStarWithHistory(AStar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.history = []  # 记录每一步的扩展节点

    def plan(self):
        """执行 A* 规划并记录每一步"""
        import heapq

        OPEN = []
        start_node = Node(self.start, None, 0, self.get_heuristic(self.start))
        heapq.heappush(OPEN, start_node)
        CLOSED = dict()

        while OPEN:
            node = heapq.heappop(OPEN)

            if not self.map_.is_expandable(node.current, node.parent):
                continue

            if node.current in CLOSED:
                continue

            # 记录当前步骤的扩展节点
            CLOSED[node.current] = node
            self.history.append(dict(CLOSED))  # 深拷贝当前状态

            # 找到目标
            if node.current == self.goal:
                path, length, cost = self.extract_path(CLOSED)
                return path, {
                    "success": True,
                    "start": self.start,
                    "goal": self.goal,
                    "length": length,
                    "cost": cost,
                    "expand": CLOSED
                }

            for node_n in self.map_.get_neighbors(node):
                if node_n.current in CLOSED:
                    continue

                node_n.g = node.g + self.get_cost(node.current, node_n.current)
                node_n.h = self.get_heuristic(node_n.current)

                if node_n.current == self.goal:
                    heapq.heappush(OPEN, node_n)
                    break

                heapq.heappush(OPEN, node_n)

        self.failed_info[1]["expand"] = CLOSED
        return self.failed_info

# 5. 创建规划器并规划路径
planner = AStarWithHistory(map_=map_, start=start, goal=goal)
path, path_info = planner.plan()

print(f"路径规划成功！")
print(f"路径长度: {path_info['length']:.2f}")
print(f"扩展节点数: {len(path_info['expand'])}")
print(f"动画总帧数: {len(planner.history)}")

# 6. 创建动画
fig = plt.figure("A* Algorithm Animation", figsize=(12, 8))
ax = fig.add_subplot()

# 颜色映射
cmap_dict = {
    TYPES.FREE: "#ffffff",
    TYPES.OBSTACLE: "#000000",
    TYPES.START: "#ff0000",
    TYPES.GOAL: "#1155cc",
    TYPES.INFLATION: "#add8e6",
    TYPES.EXPAND: "#cccccc",
    TYPES.CUSTOM: "#bbbbbb",
}
cmap = mcolors.ListedColormap([info for info in cmap_dict.values()])
norm = mcolors.BoundaryNorm([i for i in range(len(cmap_dict) + 1)], len(cmap_dict))

def init():
    """初始化动画"""
    ax.clear()
    # 绘制基础地图
    ax.imshow(
        np.transpose(map_.type_map.array),
        cmap=cmap,
        norm=norm,
        origin='lower',
        interpolation='nearest',
        extent=[*map_.bounds[0], *map_.bounds[1]],
    )
    ax.set_title("A* Algorithm Animation - Initialization", fontsize=16)
    return []

def update(frame):
    """更新每一帧"""
    ax.clear()

    # 创建临时地图副本用于显示当前帧
    temp_map = map_.type_map.array.copy()

    # 填充当前帧的扩展节点
    if frame < len(planner.history):
        current_expand = planner.history[frame]
        for coord in current_expand.keys():
            if temp_map[coord] == TYPES.FREE:
                temp_map[coord] = TYPES.EXPAND

    # 绘制地图
    ax.imshow(
        np.transpose(temp_map),
        cmap=cmap,
        norm=norm,
        origin='lower',
        interpolation='nearest',
        extent=[*map_.bounds[0], *map_.bounds[1]],
    )

    # 如果已找到路径，绘制路径
    if frame == len(planner.history) - 1 and path_info['success']:
        path_array = np.array(path)
        # 转换为世界坐标
        path_world = [map_.map_to_world(p) for p in path]
        path_world = np.array(path_world)
        ax.plot(path_world[:, 0], path_world[:, 1],
                color='#ff0000', linewidth=3, label='Path', zorder=50)
        ax.legend(loc='upper right')

    # 显示当前帧信息
    expanded_count = len(planner.history[frame]) if frame < len(planner.history) else 0
    ax.set_title(
        f"A* Algorithm Animation\nFrame: {frame + 1}/{len(planner.history)} | "
        f"Expanded Nodes: {expanded_count}",
        fontsize=14
    )

    return []

# 7. 创建动画
# 控制帧率：每秒显示的帧数
fps = 10  # 每秒10帧
interval = 1000 // fps  # 毫秒

ani = animation.FuncAnimation(
    fig,
    update,
    init_func=init,
    frames=len(planner.history),
    interval=interval,
    blit=True,
    repeat=True
)

# 8. 保存动画为 GIF
output_path = "C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/gif/astar_animation.gif"
print(f"\n正在保存动画到: {output_path}")
print("这可能需要一些时间，请耐心等待...")

# 使用 PillowWriter 保存 GIF
writer = animation.PillowWriter(fps=fps)
ani.save(output_path, writer=writer)

print(f"动画已成功保存！")
print(f"文件位置: {output_path}")
print(f"动画参数:")
print(f"  - 总帧数: {len(planner.history)}")
print(f"  - 帧率: {fps} FPS")
print(f"  - 时长: {len(planner.history) / fps:.1f} 秒")

plt.close()
