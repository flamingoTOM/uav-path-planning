# 快速入门指南

## 🚀 5 分钟快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt

# 或安装开发环境
pip install -e .
```

### 2. 运行第一个示例

```bash
cd scripts
python example_usage.py
```

这将创建一个简单的 2D 地图并可视化。

## 📖 基础教程

### 创建地图

```python
from src.map import MapTypes
from src.map.grid_2d import Grid2D

# 创建 2D 栅格地图
map_2d = Grid2D(
    bounds=[[0, 100], [0, 50]],  # 100m x 50m
    resolution=1.0               # 1米/格
)

# 添加障碍物
map_2d.add_obstacle((10, 10), (20, 20))
map_2d.fill_boundary_with_obstacles()

# 障碍物膨胀（安全缓冲）
map_2d.inflate_obstacles(radius=2.0)

# 设置起点和终点
start = (5, 5)
goal = (90, 45)
map_2d.type_map[start] = MapTypes.START
map_2d.type_map[goal] = MapTypes.GOAL
```

### 坐标转换

```python
# Map 坐标 -> World 坐标
world_point = map_2d.map_to_world((50, 25))
print(f"World: {world_point}")  # (50.5, 25.5)

# World 坐标 -> Map 坐标
map_point = map_2d.world_to_map((50.5, 25.5))
print(f"Map: {map_point}")  # (50, 25)
```

### 地图查询

```python
# 检查点是否在范围内
is_valid = map_2d.is_valid((50, 25))

# 检查点是否可通行
is_free = map_2d.is_free((50, 25))

# 检查路径是否碰撞
has_collision = map_2d.in_collision((10, 10), (90, 40))

# 获取邻居节点
neighbors = map_2d.get_neighbors((50, 25), diagonal=True)
```

### 保存和加载地图

```python
# 保存地图
map_2d.save('../data/maps/my_map.npy')

# 加载地图
loaded_map = Grid2D.load('../data/maps/my_map.npy')
```

## 🧪 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行地图测试
pytest tests/test_map.py -v

# 查看测试覆盖率
pytest tests/ --cov=src --cov-report=term
```

## 📝 开发新算法示例

### 创建新的覆盖规划算法

1. 在 `src/planner/coverage/` 创建新文件：

```python
# src/planner/coverage/my_coverage.py
from ..base_planner import BasePlanner
from typing import Tuple, List, Dict, Any
import time

class MyCoveragePlanner(BasePlanner):
    """我的覆盖规划算法"""

    def __init__(self, map_, start, **kwargs):
        super().__init__(map_, start, goal=None)
        self.max_iterations = kwargs.get('max_iterations', 10000)

    def plan(self) -> Tuple[List[Tuple], Dict[str, Any]]:
        """执行规划"""
        start_time = time.time()
        path = []

        # TODO: 实现你的算法逻辑
        # ...

        planning_time = time.time() - start_time
        coverage_info = self.calculate_coverage(path)

        info = {
            'cost': self.get_path_length(path),
            'time': planning_time,
            **coverage_info
        }

        return path, info
```

2. 在 `src/planner/coverage/__init__.py` 中导出：

```python
from .my_coverage import MyCoveragePlanner

__all__ = ['MyCoveragePlanner']
```

3. 创建测试脚本：

```python
# scripts/test_my_coverage.py
from src.map.grid_2d import Grid2D
from src.planner.coverage.my_coverage import MyCoveragePlanner

map_2d = Grid2D(bounds=[[0, 50], [0, 50]], resolution=1.0)
planner = MyCoveragePlanner(map_2d, start=(5, 5))
path, info = planner.plan()

print(f"覆盖率: {info['coverage_rate']:.2%}")
print(f"路径长度: {info['cost']:.2f} 米")
```

## 🎯 常用配置

### 修改地图配置

编辑 `data/config/map_config.yaml`:

```yaml
grid_2d:
  bounds:
    x: [0, 200]  # 修改为 200m
    y: [0, 100]  # 修改为 100m
  resolution: 0.5  # 提高分辨率
  inflation_radius: 3.0  # 增大膨胀半径
```

### 修改规划器配置

编辑 `data/config/planner_config.yaml`:

```yaml
boustrophedon:
  line_spacing: 10.0  # 修改航线间距
  turn_radius: 15.0   # 修改转弯半径
```

### 修改无人机参数

编辑 `data/config/uav_params.yaml`:

```yaml
fixed_wing:
  cruise_speed: 20.0  # 修改巡航速度
  min_turn_radius: 30.0  # 修改最小转弯半径
```

## 🐛 常见问题

### Q: 坐标转换不正确？
A: 确保理解 Map 坐标（整数索引）和 World 坐标（物理位置）的区别。使用 `map_to_world()` 和 `world_to_map()` 进行转换。

### Q: 路径规划失败？
A: 检查：
1. 起点和终点是否在地图范围内
2. 起点和终点是否可通行
3. 是否存在可行路径

### Q: 障碍物膨胀不生效？
A: 调用 `inflate_obstacles()` 前确保障碍物已添加到 type_map。

### Q: 如何调试算法？
A: 使用 `map.fill_expands()` 标记扩展节点，然后可视化查看算法搜索过程。

## 📚 学习资源

1. **项目文档**:
   - `README.md` - 项目总览
   - `ARCHITECTURE.md` - 架构详解
   - 本文件 - 快速入门

2. **代码示例**:
   - `scripts/example_usage.py` - 基础使用
   - `example/main.py` - Example 框架示例
   - `tests/test_map.py` - 单元测试示例

3. **论文材料**:
   - `paper/begin.md` - 开题报告
   - `paper/paper.md` - 论文大纲

## 💡 提示

- 使用 `pytest` 进行测试驱动开发
- 使用 YAML 配置文件管理参数，避免硬编码
- 所有坐标转换使用地图类提供的方法
- 遵循 Example 框架的设计模式
- 保持代码简洁，添加适当注释
