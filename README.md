# 无人机仿地飞行全覆盖路径规划与最优控制

本项目实现无人机在三维地形环境下的全覆盖路径规划和最优控制算法。

## 📁 项目结构

```
ws/
├── src/                          # 源代码目录
│   ├── map/                      # 地图模块
│   │   ├── __init__.py
│   │   ├── base_map.py          # 地图抽象基类
│   │   ├── grid_2d.py           # 2D 栅格地图
│   │   ├── grid_3d.py           # 3D 栅格地图（支持高度信息）
│   │   ├── terrain_map.py       # 地形地图（DEM数据）
│   │   └── map_types.py         # 地图类型定义
│   │
│   ├── planner/                  # 路径规划模块
│   │   ├── __init__.py
│   │   ├── base_planner.py      # 规划器抽象基类
│   │   ├── coverage/            # 全覆盖规划算法
│   │   │   ├── __init__.py
│   │   │   ├── random_bounce.py # 随机碰撞覆盖法
│   │   │   ├── boustrophedon.py # 牛耕式覆盖法
│   │   │   └── spiral.py        # 螺旋式覆盖法
│   │   ├── terrain_following/   # 仿地飞行路径规划
│   │   │   ├── __init__.py
│   │   │   ├── tf_coverage.py   # 仿地全覆盖规划
│   │   │   └── altitude_opt.py  # 高度优化
│   │   └── graph_search/        # 图搜索算法
│   │       ├── __init__.py
│   │       ├── a_star.py
│   │       └── dijkstra.py
│   │
│   ├── controller/               # 控制器模块
│   │   ├── __init__.py
│   │   ├── base_controller.py   # 控制器抽象基类
│   │   ├── mpc.py               # 模型预测控制
│   │   ├── pid.py               # PID 控制器
│   │   └── trajectory_tracker.py # 轨迹跟踪控制器
│   │
│   ├── trajectory/               # 轨迹处理模块
│   │   ├── __init__.py
│   │   ├── smoother.py          # 轨迹平滑
│   │   ├── b_spline.py          # B样条曲线
│   │   └── bezier.py            # 贝塞尔曲线
│   │
│   ├── uav/                      # 无人机模型模块
│   │   ├── __init__.py
│   │   ├── base_uav.py          # 无人机抽象基类
│   │   ├── dynamics.py          # 动力学模型
│   │   └── kinematics.py        # 运动学模型
│   │
│   ├── decomposition/            # 区域分解模块
│   │   ├── __init__.py
│   │   ├── terrain_decomp.py    # 基于地形的区域分解
│   │   └── priority_sort.py     # 子区域优先级排序
│   │
│   ├── utils/                    # 工具模块
│   │   ├── __init__.py
│   │   ├── geometry.py          # 几何计算工具
│   │   ├── terrain_loader.py    # 地形数据加载
│   │   └── metrics.py           # 性能评估指标
│   │
│   └── visualizer/               # 可视化模块
│       ├── __init__.py
│       ├── map_viz.py           # 地图可视化
│       ├── path_viz.py          # 路径可视化
│       └── animation.py         # 动画生成
│
├── tests/                        # 测试目录
│   ├── __init__.py
│   ├── test_map.py              # 地图模块测试
│   ├── test_planner.py          # 规划器测试
│   ├── test_controller.py       # 控制器测试
│   └── integration/             # 集成测试
│       └── test_full_pipeline.py
│
├── data/                         # 数据目录
│   ├── maps/                    # 地图数据
│   │   ├── simple_2d.npy
│   │   ├── mountain_dem.tif     # DEM地形数据
│   │   └── test_terrain.json
│   └── config/                  # 配置文件
│       ├── map_config.yaml
│       ├── planner_config.yaml
│       └── uav_params.yaml
│
├── scripts/                      # 脚本目录
│   ├── random_bounce_coverage.py # 已有：随机碰撞示意图
│   ├── run_coverage_sim.py      # 覆盖规划仿真
│   ├── run_terrain_following.py # 仿地飞行仿真
│   ├── benchmark.py             # 性能基准测试
│   └── generate_terrain.py      # 地形数据生成
│
├── pic/                          # 图片输出目录
│   └── random_bounce_coverage.png # 已有
│
├── paper/                        # 论文目录
│   ├── begin.md                 # 已有：开题报告
│   └── paper.md                 # 已有：论文大纲
│
├── pdf/                          # PDF文档目录
│   └── 刘晓煜-毕设开题报告.pdf    # 已有
│
├── example/                      # 参考示例（保持原样）
│   └── python_motion_planning/
│
├── requirements.txt              # Python依赖
├── setup.py                      # 项目安装配置
└── README.md                     # 项目说明（本文件）
```

## 🗺️ 统一地图格式

### 地图类型定义

所有地图类型统一使用整数枚举：

```python
class MapTypes:
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

### 地图数据格式

#### 2D 栅格地图
```python
{
    "type": "grid_2d",
    "bounds": [[0, 100], [0, 50]],  # [[x_min, x_max], [y_min, y_max]]
    "resolution": 1.0,               # 栅格分辨率（米/格）
    "type_map": np.ndarray,          # shape: (nx, ny), dtype: int8
    "metadata": {
        "origin": [0, 0],
        "unit": "meter"
    }
}
```

#### 3D 地形地图
```python
{
    "type": "terrain_3d",
    "bounds": [[0, 100], [0, 50], [0, 30]],  # [[x], [y], [z]]
    "resolution": 1.0,
    "height_map": np.ndarray,        # shape: (nx, ny), 高度值
    "type_map": np.ndarray,          # shape: (nx, ny), 类型标记
    "metadata": {
        "dem_source": "SRTM",
        "projection": "WGS84",
        "unit": "meter"
    }
}
```

### 坐标系统

- **Map坐标**: 整数索引 (i, j) 或 (i, j, k)，表示栅格位置
- **World坐标**: 浮点数 (x, y) 或 (x, y, z)，表示物理位置（米）
- **转换公式**:
  - `world = (map + 0.5) * resolution + bounds[:, 0]`
  - `map = round((world - bounds[:, 0]) / resolution - 0.5)`

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行示例

```bash
# 2D 覆盖规划示例
python scripts/run_coverage_sim.py --map data/maps/simple_2d.npy

# 3D 仿地飞行示例
python scripts/run_terrain_following.py --dem data/maps/mountain_dem.tif

# 运行测试
pytest tests/
```

### 3. 开发新算法

1. 在 `src/planner/coverage/` 创建新算法文件
2. 继承 `BasePlanner` 类
3. 实现 `plan()` 方法
4. 在 `tests/` 中添加单元测试
5. 在 `scripts/` 中添加仿真脚本

## 📊 算法性能评估指标

- **覆盖率**: 已覆盖面积 / 总可达面积
- **路径长度**: 总飞行距离
- **重复率**: 重复覆盖面积 / 总覆盖面积
- **飞行时间**: 估算飞行时长
- **能量消耗**: 基于动力学模型估算

## 🔧 开发规范

1. 所有地图使用统一的 `BaseMap` 接口
2. 所有规划器使用统一的 `BasePlanner` 接口
3. 坐标转换使用地图类提供的方法
4. 代码遵循 PEP 8 规范
5. 每个模块包含完整的文档字符串

## 📝 TODO

- [ ] 实现 3D 栅格地图类
- [ ] 实现地形地图加载器
- [ ] 实现牛耕式覆盖算法
- [ ] 实现仿地飞行路径规划
- [ ] 实现 MPC 控制器
- [ ] 实现轨迹平滑算法
- [ ] 完成山地仿真实验

## 📚 参考资料

- Example框架: `./example/python_motion_planning/`
- 论文文档: `./paper/`
- 可视化示例: `./pic/`
