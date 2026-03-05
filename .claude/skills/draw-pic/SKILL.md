---
name: draw-pic
description: 根据用户描述的算法名称生成 UAV 路径规划算法的可视化示意图或动画，支持多种路径规划算法（A*, Dijkstra, RRT 等）。
---

# Draw Algorithm Picture

这个 Skill 用于生成 UAV 路径规划算法的可视化示意图或动画。

## 🔒 不可变约束（CRITICAL - NEVER CHANGE）

### 约束 1: 地图大小（固定）
```python
# ⚠️ 永远不能修改这个地图大小
map_ = Grid(bounds=[[0, 101], [0, 51]])
```

### 约束 2: 标题文本标注格式（固定）
```python
# ⚠️ 永远不能修改这个代码结构，只能修改算法名称字符串
vis.ax.text(
    0.5, 1.08,
    "Dijkstra",  # ← 只能改这里的算法名称
    transform=vis.ax.transAxes,
    ha="center", va="top",
    fontsize=20,
    zorder=10000
)
```

**禁止修改的参数：**
- `0.5, 1.08` - 位置坐标
- `transform=vis.ax.transAxes` - 坐标系
- `ha="center", va="top"` - 对齐方式
- `fontsize=20` - 字体大小
- `zorder=10000` - 图层顺序

## 支持的算法

- **AStar** (A*): A* 算法
- **Dijkstra**: Dijkstra 算法
- **ThetaStar** (Theta*): Theta* 算法
- **JPS**: Jump Point Search
- **RRT**: 快速随机树
- **RRTStar** (RRT*): RRT* 算法

## Instructions

### 创建可视化脚本模板

在 `test/` 目录下创建脚本，**必须遵守不可变约束**：

```python
import random
random.seed(0)
import numpy as np
np.random.seed(0)
import sys
sys.path.append("C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/example")
from python_motion_planning.common import *
from python_motion_planning.path_planner import *

# 1. 创建地图 - ⚠️ 不可变约束
map_ = Grid(bounds=[[0, 101], [0, 51]])  # 永远不能修改
map_.fill_boundary_with_obstacles()

# 2. 添加障碍物（可自定义）
map_.type_map[10:21, 25] = TYPES.OBSTACLE
map_.type_map[20, :25] = TYPES.OBSTACLE
map_.inflate_obstacles(radius=2)

# 3. 设置起点和终点（可自定义）
start = (5, 5)
goal = (70, 40)
map_.type_map[start] = TYPES.START
map_.type_map[goal] = TYPES.GOAL

# 4. 创建规划器
planner = AStar(map_=map_, start=start, goal=goal)
path, path_info = planner.plan()

# 5. 可视化
map_.fill_expands(path_info["expand"])
vis = Visualizer("Algorithm Visualizer")
vis.plot_grid_map(map_)
vis.plot_path(path)

# 6. 添加标注 - ⚠️ 不可变约束（只改算法名称）
vis.ax.text(
    0.5, 1.08,
    "A*",  # ← 只能改这里
    transform=vis.ax.transAxes,
    ha="center", va="top",
    fontsize=20,
    zorder=10000
)

# 7. 保存
output_path = "C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/pic/a_star.png"
vis.fig.savefig(output_path, dpi=300, bbox_inches='tight')
vis.close()
```

## 可以修改 vs 不可修改

### ✅ 允许修改
- 障碍物布局和数量
- 起点和终点坐标
- 膨胀半径
- 输出文件名
- 额外的可视化元素

### ❌ 绝对不能修改
- 地图大小：`bounds=[[0, 101], [0, 51]]`
- 标题格式：固定的 `vis.ax.text()` 结构
- 标题位置：`0.5, 1.08`
- 标题参数：`transform`, `ha`, `va`, `fontsize`, `zorder`

## Examples

### 示例 1: 生成 A* 图
用户：`/draw-pic 生成 A*`

- 地图大小：`[[0, 101], [0, 51]]` ✓
- 标题文本：`"A*"` ✓

### 示例 2: 生成 Dijkstra 图
用户：`/draw-pic Dijkstra`

- 地图大小：`[[0, 101], [0, 51]]` ✓
- 标题文本：`"Dijkstra"` ✓

### 示例 3: 自定义障碍物
用户：`/draw-pic A*，3个矩形障碍物`

- 地图大小保持：`[[0, 101], [0, 51]]` ✓
- 自定义障碍物 ✓
- 标题文本：`"A*"` ✓
