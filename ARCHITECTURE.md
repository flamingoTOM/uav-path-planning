# 项目架构说明

## 📐 设计理念

本项目基于 `example/python_motion_planning` 框架，针对无人机仿地飞行全覆盖路径规划任务进行了专门设计和扩展。

### 核心设计原则

1. **统一接口**: 所有地图、规划器、控制器都继承统一的抽象基类
2. **模块解耦**: 各模块职责清晰，便于独立开发和测试
3. **可扩展性**: 易于添加新的算法和功能
4. **标准格式**: 统一的数据格式和坐标系统

## 🗺️ 地图系统架构

### 类层次结构

```
BaseMap (抽象基类)
├── Grid2D (2D 栅格地图)
├── Grid3D (3D 栅格地图，支持多层高度)
└── TerrainMap (地形地图，集成 DEM 数据)
```

### 统一数据格式

#### 地图类型枚举 (MapTypes)

```python
FREE = 0         # 可通行区域
OBSTACLE = 1     # 障碍物
START = 2        # 起点
GOAL = 3         # 终点
INFLATION = 4    # 膨胀区（安全缓冲）
EXPAND = 5       # 已搜索区域
COVERED = 6      # 已覆盖区域
PATH = 7         # 规划路径
CUSTOM = 8       # 自定义区域
```

#### 坐标系统

**Map 坐标**: 整数索引，表示栅格位置
- 2D: `(i, j)` - 第 i 行，第 j 列
- 3D: `(i, j, k)` - 第 i 行，第 j 列，第 k 层

**World 坐标**: 浮点数，表示物理位置（单位：米）
- 2D: `(x, y)`
- 3D: `(x, y, z)`

**转换公式**:
```python
# Map -> World
world = (map + 0.5) * resolution + bounds[:, 0]

# World -> Map
map = round((world - bounds[:, 0]) / resolution - 0.5)
```

### 地图核心功能

| 功能 | 方法 | 说明 |
|------|------|------|
| 坐标转换 | `map_to_world()`, `world_to_map()` | Map ↔ World 坐标互转 |
| 有效性检查 | `is_valid()` | 检查点是否在地图范围内 |
| 可通行性检查 | `is_free()` | 检查点是否可通行 |
| 碰撞检测 | `in_collision()` | 检查两点连线是否碰撞 |
| 邻居查询 | `get_neighbors()` | 获取相邻可通行格点 |
| 障碍物操作 | `add_obstacle()`, `fill_boundary_with_obstacles()` | 添加障碍物 |
| 障碍膨胀 | `inflate_obstacles()` | 安全缓冲区膨胀 |
| ESDF 更新 | `update_esdf()` | 更新欧几里得符号距离场 |
| 保存/加载 | `save()`, `load()` | 地图数据持久化 |

## 🛩️ 规划器系统架构

### 类层次结构

```
BasePlanner (抽象基类)
├── CoveragePlanner (覆盖规划基类)
│   ├── RandomBouncePlanner (随机碰撞覆盖)
│   ├── BoustrophedonPlanner (牛耕式覆盖)
│   └── SpiralPlanner (螺旋式覆盖)
├── TerrainFollowingPlanner (仿地飞行规划基类)
│   ├── TFCoveragePlanner (仿地全覆盖规划)
│   └── AltitudeOptimizer (高度优化规划)
└── GraphSearchPlanner (图搜索规划基类)
    ├── AStarPlanner (A* 算法)
    └── DijkstraPlanner (Dijkstra 算法)
```

### 规划器接口

所有规划器必须实现：

```python
def plan(self) -> Tuple[List[Tuple], Dict[str, Any]]:
    """
    执行路径规划

    Returns:
        path: 路径点列表 [(x1, y1), (x2, y2), ...]
        info: 规划信息字典
            - cost: 路径代价
            - time: 规划时间（秒）
            - coverage_rate: 覆盖率
            - repeat_rate: 重复率
            - expand_nodes: 扩展节点数
    """
    pass
```

### 性能评估指标

| 指标 | 计算方法 | 适用场景 |
|------|---------|---------|
| 覆盖率 | 已覆盖格点数 / 总可达格点数 | 全覆盖规划 |
| 重复率 | (总路径点数 - 唯一点数) / 总路径点数 | 全覆盖规划 |
| 路径长度 | Σ 相邻点距离 | 所有规划 |
| 规划时间 | 算法执行时间 | 所有规划 |
| 最大爬升角 | max(arctan(Δz/Δxy)) | 仿地飞行 |
| 能量消耗 | 基于动力学模型估算 | 所有规划 |

## 🎮 控制器系统架构

### 类层次结构

```
BaseController (抽象基类)
├── MPCController (模型预测控制)
├── PIDController (PID 控制器)
└── TrajectoryTracker (轨迹跟踪控制器)
```

### 控制器接口

```python
def control(self, current_state, target_state) -> control_input:
    """
    计算控制输入

    Args:
        current_state: 当前状态 (位置, 速度, 姿态)
        target_state: 目标状态

    Returns:
        control_input: 控制输入 (油门, 舵面偏角等)
    """
    pass
```

## 🔄 数据流程

### 1. 地图构建流程

```
原始数据 (DEM/点云/栅格)
    ↓
加载器 (terrain_loader.py)
    ↓
地图对象 (Grid2D/TerrainMap)
    ↓
障碍物检测与膨胀
    ↓
ESDF 计算
    ↓
可用于规划的地图
```

### 2. 路径规划流程

```
地图 + 起点/终点
    ↓
规划器 (BasePlanner)
    ↓
粗路径 (离散格点序列)
    ↓
轨迹平滑 (B-spline/Bezier)
    ↓
平滑轨迹 (连续路径点)
    ↓
控制器 (MPC/PID)
    ↓
控制指令序列
```

### 3. 仿真验证流程

```
配置文件 (YAML)
    ↓
创建地图 + 无人机模型
    ↓
执行规划算法
    ↓
轨迹跟踪控制
    ↓
性能指标统计
    ↓
可视化结果 + 报告
```

## 📦 模块依赖关系

```
utils (工具模块)
  ↑
map (地图模块)
  ↑
planner (规划模块)
  ↑
trajectory (轨迹模块)
  ↑
controller (控制模块)
  ↑
visualizer (可视化模块)
```

**依赖规则**:
- 底层模块不依赖上层模块
- 同层模块避免循环依赖
- 通过抽象接口解耦

## 🔧 开发工作流

### 添加新的覆盖规划算法

1. 在 `src/planner/coverage/` 创建新文件，如 `my_algorithm.py`
2. 继承 `BasePlanner` 类
3. 实现 `plan()` 方法
4. 在 `src/planner/coverage/__init__.py` 中导出
5. 在 `tests/` 中添加单元测试
6. 在 `scripts/` 中创建仿真脚本
7. 更新 `data/config/planner_config.yaml` 添加配置

### 添加新的地图类型

1. 在 `src/map/` 创建新文件
2. 继承 `BaseMap` 类
3. 实现所有抽象方法
4. 在 `src/map/__init__.py` 中导出
5. 添加对应的测试用例
6. 在 `data/config/map_config.yaml` 中添加配置

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_map.py -v

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html
```

## 📊 与 Example 框架的对应关系

| Example 框架 | 本项目 | 说明 |
|-------------|--------|------|
| `common/env/map/base_map.py` | `src/map/base_map.py` | 地图抽象基类 |
| `common/env/map/grid.py` | `src/map/grid_2d.py` | 2D 栅格地图 |
| `common/env/types.py` | `src/map/map_types.py` | 类型定义 |
| `path_planner/base_path_planner.py` | `src/planner/base_planner.py` | 规划器基类 |
| `path_planner/graph_search/a_star.py` | `src/planner/graph_search/a_star.py` | A* 算法 |
| `controller/` | `src/controller/` | 控制器模块 |
| `common/visualizer/` | `src/visualizer/` | 可视化模块 |

### 主要扩展

1. **新增模块**:
   - `planner/coverage/` - 全覆盖规划算法
   - `planner/terrain_following/` - 仿地飞行规划
   - `decomposition/` - 区域分解
   - `trajectory/` - 轨迹处理

2. **增强功能**:
   - 3D 地形地图支持
   - 覆盖率评估指标
   - 配置文件管理
   - 完整的测试框架

## 🚀 下一步工作

### 优先级 P0（核心功能）
- [ ] 实现 `Grid3D` 类（3D 栅格地图）
- [ ] 实现 `TerrainMap` 类（DEM 地形地图）
- [ ] 实现 `BoustrophedonPlanner`（牛耕式覆盖）
- [ ] 实现基础可视化功能

### 优先级 P1（关键算法）
- [ ] 实现 `TFCoveragePlanner`（仿地全覆盖规划）
- [ ] 实现 `MPCController`（模型预测控制）
- [ ] 实现轨迹平滑算法（B-spline）
- [ ] 实现区域分解算法

### 优先级 P2（增强功能）
- [ ] 3D 可视化（Mayavi/Plotly）
- [ ] 动画生成
- [ ] 性能基准测试
- [ ] 完整的文档和示例

## 📚 参考资源

- Example 框架源码: `./example/python_motion_planning/`
- 论文材料: `./paper/begin.md`, `./paper/paper.md`
- 可视化示例: `./pic/random_bounce_coverage.png`
- 配置示例: `./data/config/*.yaml`
