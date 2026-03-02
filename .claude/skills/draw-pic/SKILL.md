---
name: draw-pic
description: 根据用户描述的算法名称生成 UAV 路径规划算法的可视化示意图，支持多种路径规划算法（A*, Dijkstra, RRT 等）。
---

# Draw Algorithm Picture

这个 Skill 用于生成 UAV 路径规划算法的可视化示意图。用户只需提供算法名称，skill 会自动生成包含地图、障碍物、路径和搜索过程的可视化图片。

## 功能特性

- 基于 example/main.py 的架构模板
- 支持多种路径规划算法
- 自动生成地图和障碍物布局
- 可视化搜索过程（展开的节点）
- 标注算法名称和路径成本
- 图片自动保存到 `uav-path-planning/pic/` 目录

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

**基本用法：**
- "画一个 A* 算法示意图"
- "生成 RRT 的可视化"
- "展示 Dijkstra 算法的搜索过程"

**自定义用法：**
- "用 A* 算法，起点 (10, 10)，终点 (80, 40)"
- "生成 RRT 图，地图大小 150x80"

**批量生成：**
- "生成所有算法的示意图"
- "对比 A* 和 Dijkstra"
