---
name: draw-pic
description: 根据用户描述的算法名称生成 UAV 路径规划算法的可视化示意图或动画，支持多种路径规划算法（A*, Dijkstra, RRT 等）。
---

# Draw Algorithm Picture

这个 Skill 用于生成 UAV 路径规划算法的可视化示意图或动画。用户只需提供算法名称，skill 会自动生成包含地图、障碍物、路径和搜索过程的可视化图片或 GIF 动画。

## 功能特性

- 基于 example/main.py 的架构模板
- 支持多种路径规划算法
- 自动生成地图和障碍物布局
- 可视化搜索过程（展开的节点）
- 标注算法名称和路径成本
- **静态图片**：保存到 `uav-path-planning/pic/` 目录
- **动画 GIF**：保存到 `uav-path-planning/gif/` 目录，展示搜索过程

## 支持的算法

### 图搜索算法 (Graph Search)
- **AStar** (A*): 启发式搜索算法，使用距离启发函数
- **Dijkstra**: 经典最短路径算法
- **ThetaStar** (Theta*): A* 的变体，支持任意角度路径
- **JPS**: Jump Point Search，A* 的优化版本，通过跳点减少搜索节点
- **RandomCollision**: 随机碰撞算法，沿任意角度直线前进，碰撞后随机转向

### 采样搜索算法 (Sample Search)
- **RRT**: 快速随机树算法
- **RRTStar** (RRT*): RRT 的优化版本，保证渐进最优

## Instructions

### 步骤 1: 获取用户输入
询问用户想要可视化哪个算法。如果用户没有明确指定，可以提供算法列表让用户选择。

### 步骤 2: 创建可视化脚本
在 `uav-path-planning/test/` 目录下创建 Python 脚本，使用以下模板结构：

```python
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

# 2. 添加障碍物（可以使用示例布局或自定义）
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
planner = AlgorithmClass(map_=map_, start=start, goal=goal)
path, path_info = planner.plan()

# 5. 可视化
map_.fill_expands(path_info["expand"])
vis = Visualizer("Algorithm Visualizer")
vis.plot_grid_map(map_)
vis.plot_path(path)

# 6. 添加标注
vis.ax.text(
    0.5, 1.08,
    "AlgorithmName",
    transform=vis.ax.transAxes,
    ha="center", va="top",
    fontsize=20,
    zorder=10000
)

# 7. 保存图片
output_path = "C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/pic/algorithm_name.png"
vis.save(output_path)
vis.close()
print(f"图片已保存至: {output_path}")
```

### 步骤 3: 算法名称映射
根据用户输入的算法名称，映射到对应的类：

| 用户输入 | 类名 | 说明 |
|---------|------|------|
| A* / AStar / a_star | AStar | A* 算法 |
| Dijkstra / dijkstra | Dijkstra | Dijkstra 算法 |
| Theta* / ThetaStar / theta_star | ThetaStar | Theta* 算法 |
| JPS / jps / jump_point_search | JPS | Jump Point Search 算法 |
| RandomCollision / random_collision | RandomCollision | 随机碰撞覆盖算法 |
| RRT / rrt | RRT | 快速随机树 |
| RRT* / RRTStar / rrt_star | RRTStar | RRT* 算法 |

### 步骤 4: 生成并执行脚本
1. 根据算法名称替换模板中的 `AlgorithmClass` 和 `AlgorithmName`
2. 设置合适的输出文件名（如 `a_star.png`, `dijkstra.png`）
3. 执行 Python 脚本生成图片
4. 向用户报告图片保存位置

### 步骤 5: 处理错误
如果算法名称不在支持列表中，提示用户可用的算法选项。

### 步骤 6 (可选): 生成动画 GIF
如果用户需要动画演示，使用以下模板创建动画脚本：

```python
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

# 2. 添加障碍物（同静态图片）
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

# 4. 创建带历史记录的规划器
class AStarWithHistory(AStar):
    def __init__(self, *args, frame_skip=87, **kwargs):
        super().__init__(*args, **kwargs)
        self.history = []
        self.frame_skip = frame_skip
        self.step_count = 0

    def plan(self):
        import heapq
        OPEN = []
        start_node = Node(self.start, None, 0, self.get_heuristic(self.start))
        heapq.heappush(OPEN, start_node)
        CLOSED = dict()
        self.history.append({self.start: start_node})

        while OPEN:
            node = heapq.heappop(OPEN)
            if not self.map_.is_expandable(node.current, node.parent):
                continue
            if node.current in CLOSED:
                continue

            CLOSED[node.current] = node
            if self.step_count % self.frame_skip == 0:
                self.history.append(dict(CLOSED))
            self.step_count += 1

            if node.current == self.goal:
                if self.history[-1] != CLOSED:
                    self.history.append(dict(CLOSED))
                path, length, cost = self.extract_path(CLOSED)
                return path, {
                    "success": True, "start": self.start, "goal": self.goal,
                    "length": length, "cost": cost, "expand": CLOSED
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

# 5. 运行算法
planner = AStarWithHistory(map_=map_, start=start, goal=goal, frame_skip=87)
path, path_info = planner.plan()

# 添加停留帧（3秒 = 15帧 @ 5fps）
hold_frames = 15
for _ in range(hold_frames):
    planner.history.append(planner.history[-1])

# 6. 创建动画
fig = plt.figure("Algorithm Animation", figsize=(10, 6), dpi=80)
ax = fig.add_subplot()

# 颜色映射
cmap_dict = {
    TYPES.FREE: "#ffffff", TYPES.OBSTACLE: "#000000",
    TYPES.START: "#ff0000", TYPES.GOAL: "#1155cc",
    TYPES.INFLATION: "#add8e6", TYPES.EXPAND: "#cccccc",
    TYPES.CUSTOM: "#bbbbbb",
}
cmap = mcolors.ListedColormap([info for info in cmap_dict.values()])
norm = mcolors.BoundaryNorm([i for i in range(len(cmap_dict) + 1)], len(cmap_dict))

# 预计算路径（世界坐标）
path_world = np.array([map_.map_to_world(p) for p in path])

def update(frame):
    ax.clear()
    temp_map = map_.type_map.array.copy()

    # 填充当前帧的扩展节点
    if frame < len(planner.history):
        current_expand = planner.history[frame]
        for coord in current_expand.keys():
            if coord != start and coord != goal:
                if temp_map[coord] == TYPES.FREE:
                    temp_map[coord] = TYPES.EXPAND

    # 绘制地图
    ax.imshow(np.transpose(temp_map), cmap=cmap, norm=norm,
              origin='lower', interpolation='nearest',
              extent=[*map_.bounds[0], *map_.bounds[1]])

    # 显示路径（当搜索完成时）
    expanded_count = len(planner.history[frame]) if frame < len(planner.history) else 0
    if expanded_count == len(path_info['expand']) and path_info['success']:
        ax.plot(path_world[:, 0], path_world[:, 1],
                color='#ff0000', linewidth=2.5, label='Path', zorder=50)
        ax.legend(loc='upper right', fontsize=10)

    # 显示标题
    ax.set_title("A*", fontsize=20, pad=10, fontweight='bold')
    ax.set_xlabel("X", fontsize=10)
    ax.set_ylabel("Y", fontsize=10)
    return []

# 7. 保存动画
fps = 5
ani = animation.FuncAnimation(fig, update, frames=len(planner.history),
                             interval=1000//fps, blit=False, repeat=True)

output_path = "C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/gif/astar_animation.gif"
writer = animation.PillowWriter(fps=fps, bitrate=1800)
ani.save(output_path, writer=writer, dpi=80)
plt.close()
print(f"动画已保存至: {output_path}")
```

**动画参数说明：**
- `frame_skip`: 控制帧数，值越大动画越快（推荐 65-100）
  - 寻路 6 秒：`frame_skip=87`
  - 寻路 8 秒：`frame_skip=65`
- `hold_frames`: 路径显示后停留时间
  - 3 秒停留：`hold_frames=15` (@ 5fps)
  - 4 秒停留：`hold_frames=20` (@ 5fps)
- `fps`: 帧率，推荐 5 FPS
- `dpi`: 分辨率，推荐 80

## Examples

### 示例 1: 生成 A* 算法示意图
**用户输入：** "生成 A* 算法的示意图"

**操作：**
1. 识别算法名称为 "A*"
2. 创建脚本 `test/draw_a_star.py`
3. 使用 `AStar` 类
4. 保存图片到 `pic/a_star.png`
5. 执行脚本并返回结果

### 示例 2: 生成 RRT 算法示意图
**用户输入：** "画一个 RRT 的路径规划图"

**操作：**
1. 识别算法名称为 "RRT"
2. 创建脚本 `test/draw_rrt.py`
3. 使用 `RRT` 类
4. 保存图片到 `pic/rrt.png`
5. 执行脚本并返回结果

### 示例 3: 生成 RandomCollision 算法示意图
**用户输入：** "生成随机碰撞算法的示意图"

**操作：**
1. 识别算法名称为 "RandomCollision"
2. 创建脚本 `test/draw_random_collision.py`
3. 使用 `RandomCollision` 类
4. 保存图片到 `pic/random_collision.png`
5. 执行脚本并返回结果

### 示例 4: 批量生成多个算法
**用户输入：** "生成 Dijkstra 和 Theta* 的对比图"

**操作：**
1. 为每个算法分别创建脚本
2. 生成 `pic/dijkstra.png` 和 `pic/theta_star.png`
3. 向用户展示两张图片的路径

### 示例 5: 生成 A* 算法动画
**用户输入：** "创建 A* 算法动画，放在 /gif 目录"

**操作：**
1. 识别算法名称为 "A*"
2. 创建 `/gif` 目录（如果不存在）
3. 创建动画脚本 `test/draw_astar_animation.py`
4. 使用 `AStarWithHistory` 类记录搜索过程
5. 配置动画参数：
   - 寻路时间约 6-8 秒
   - 路径显示后停留 3 秒
   - 标题显示算法名称（简洁版）
6. 保存 GIF 到 `gif/astar_animation.gif`
7. 向用户报告动画文件位置和参数信息

### 示例 6: 自定义动画时长
**用户输入：** "生成 A* 动画，寻路 6 秒，找到路后停留 3 秒"

**操作：**
1. 根据时长计算 `frame_skip` 参数（6 秒 ≈ frame_skip=87）
2. 设置 `hold_frames=15` (3 秒 @ 5fps)
3. 生成并保存动画
4. 报告实际时长和文件大小

## 自定义选项

### 地图配置
用户可以自定义：
- 地图大小: `bounds=[[0, x], [0, y]]`
- 起点位置: `start = (x, y)`
- 终点位置: `goal = (x, y)`
- 障碍物布局: 通过 `map_.type_map[...]` 设置

### 可视化配置
- 图片标题
- 文本标注位置
- 输出文件名

## Best Practices

1. **算法名称规范化**: 自动识别不同格式的算法名称（大小写、下划线、空格等）
2. **文件命名**: 使用小写+下划线格式（如 `a_star.png`, `rrt_star.png`）
3. **路径管理**: 始终使用绝对路径，避免路径问题
4. **错误处理**: 如果算法执行失败，提供清晰的错误信息
5. **清理测试文件**: 可以询问用户是否保留生成的测试脚本

## Quick Reference

**静态图片生成：**
- "画一个 A* 算法示意图"
- "生成 RRT 的可视化"
- "展示 Dijkstra 算法的搜索过程"

**动画生成：**
- "创建 A* 算法动画，放在 /gif 目录"
- "生成 A* 动画，寻路 6 秒，停留 3 秒"
- "生成 RRT 算法的动画演示"

**自定义用法：**
- "用 A* 算法，起点 (10, 10)，终点 (80, 40)"
- "生成 RRT 图，地图大小 150x80"
- "生成动画，寻路 8 秒，路径显示 4 秒"

**批量生成：**
- "生成所有算法的示意图"
- "对比 A* 和 Dijkstra"

**动画参数快速参考：**
- 寻路 6 秒：`frame_skip=87`
- 寻路 8 秒：`frame_skip=65`
- 停留 3 秒：`hold_frames=15`
- 停留 4 秒：`hold_frames=20`
