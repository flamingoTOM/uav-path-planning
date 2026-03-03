"""
生成 A* 算法动画（优化版）
展示逐步搜索过程，通过跳帧和优化设置加快生成速度
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

# 4. 修改 AStar 算法以记录扩展过程
class AStarWithHistory(AStar):
    def __init__(self, *args, frame_skip=3, **kwargs):
        super().__init__(*args, **kwargs)
        self.history = []  # 记录选定步骤的扩展节点
        self.frame_skip = frame_skip  # 跳帧：每 N 步记录一次
        self.step_count = 0

    def plan(self):
        """执行 A* 规划并记录关键步骤"""
        import heapq

        OPEN = []
        start_node = Node(self.start, None, 0, self.get_heuristic(self.start))
        heapq.heappush(OPEN, start_node)
        CLOSED = dict()

        # 记录初始状态
        self.history.append({self.start: start_node})

        while OPEN:
            node = heapq.heappop(OPEN)

            if not self.map_.is_expandable(node.current, node.parent):
                continue

            if node.current in CLOSED:
                continue

            # 添加到 CLOSED
            CLOSED[node.current] = node

            # 每隔 frame_skip 步记录一次
            if self.step_count % self.frame_skip == 0:
                self.history.append(dict(CLOSED))
            self.step_count += 1

            # 找到目标
            if node.current == self.goal:
                # 确保最后一帧被记录
                if self.history[-1] != CLOSED:
                    self.history.append(dict(CLOSED))

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
print("正在运行 A* 算法...")
planner = AStarWithHistory(map_=map_, start=start, goal=goal, frame_skip=87)
path, path_info = planner.plan()

print(f"路径规划成功！")
print(f"路径长度: {path_info['length']:.2f}")
print(f"总扩展节点数: {len(path_info['expand'])}")
original_frame_count = len(planner.history)
print(f"搜索过程帧数: {original_frame_count}")

# 在最后添加停留帧（3秒 = 15帧 @ 5fps）
hold_frames = 15
for _ in range(hold_frames):
    planner.history.append(planner.history[-1])
print(f"停留帧数: {hold_frames}")
print(f"总帧数: {len(planner.history)} (搜索 {original_frame_count} + 停留 {hold_frames})")

# 6. 创建动画
fig = plt.figure("A* Algorithm Animation", figsize=(10, 6), dpi=80)
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

# 预计算路径（世界坐标）
path_world = np.array([map_.map_to_world(p) for p in path])

def update(frame):
    """更新每一帧"""
    ax.clear()

    # 创建临时地图副本用于显示当前帧
    temp_map = map_.type_map.array.copy()

    # 填充当前帧的扩展节点
    if frame < len(planner.history):
        current_expand = planner.history[frame]
        for coord in current_expand.keys():
            if coord != start and coord != goal:
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

    # 计算当前扩展节点数
    expanded_count = len(planner.history[frame]) if frame < len(planner.history) else 0

    # 当搜索完成（包括停留帧）时，绘制完整路径
    if expanded_count == len(path_info['expand']) and path_info['success']:
        ax.plot(path_world[:, 0], path_world[:, 1],
                color='#ff0000', linewidth=2.5, label='Path', zorder=50)
        ax.legend(loc='upper right', fontsize=10)

    # 显示标题
    ax.set_title(
        "A*",
        fontsize=20, pad=10, fontweight='bold'
    )

    ax.set_xlabel("X", fontsize=10)
    ax.set_ylabel("Y", fontsize=10)

    return []

# 7. 创建动画
fps = 5  # 降低帧率以加快生成速度
interval = 1000 // fps

print(f"\n正在创建动画...")
ani = animation.FuncAnimation(
    fig,
    update,
    frames=len(planner.history),
    interval=interval,
    blit=False,  # 关闭 blit 以提高兼容性
    repeat=True
)

# 8. 保存动画为 GIF
output_path = "C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/gif/astar_animation.gif"
print(f"正在保存动画到: {output_path}")
print("这可能需要 30-60 秒，请耐心等待...")

# 使用 PillowWriter 保存 GIF
writer = animation.PillowWriter(fps=fps, bitrate=1800)
ani.save(output_path, writer=writer, dpi=80)

print(f"\n[OK] 动画已成功保存！")
print(f"文件位置: {output_path}")
print(f"\n动画信息:")
print(f"  - 总帧数: {len(planner.history)} (搜索 {original_frame_count} + 停留 {hold_frames})")
print(f"  - 帧率: {fps} FPS")
search_time = original_frame_count / fps
hold_time = hold_frames / fps
total_time = len(planner.history) / fps
print(f"  - 时长: {total_time:.1f} 秒 (搜索 {search_time:.1f}s + 停留 {hold_time:.1f}s)")
print(f"  - 扩展节点总数: {len(path_info['expand'])}")
print(f"  - 路径长度: {path_info['length']:.2f}")

plt.close()
print("\n完成！")
