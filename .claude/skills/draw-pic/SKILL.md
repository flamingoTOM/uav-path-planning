---
name: draw-pic
description: "路径规划算法可视化工具。基于 example/main.py 地图架构，测试和对比多种算法（A*、Dijkstra、Theta*、RRT、RRT*），输出高质量图片到 /pic 目录。"
---

# Draw-Pic 技能

## 概述

基于 `example/main.py` 的地图架构，用于验证和可视化路径规划算法的工具。

## 功能

**支持算法：**
- **图搜索：** A*、Dijkstra、Theta*
- **采样搜索：** RRT、RRT*
- **覆盖算法：** 随机碰撞覆盖法

**核心特性：**
- 自定义地图构建
- 算法性能对比
- 高质量可视化（300 DPI）
- 自动输出到 `/pic` 目录

## 使用方法

### 测试单个算法
```bash
python .claude/skills/draw-pic/pyscripts/test_algorithm.py --algorithm a_star
```

### 对比多个算法
```bash
python .claude/skills/draw-pic/pyscripts/compare_algorithms.py --algorithms a_star dijkstra
```

### 批量测试
```bash
python .claude/skills/draw-pic/pyscripts/batch_test.py
```

### 随机碰撞覆盖法
```bash
python .claude/skills/draw-pic/pyscripts/random_bounce_algorithm.py --bounces 10
```

## 命令行参数

**test_algorithm.py：**
- `--algorithm, -a`: 算法名称
- `--start`: 起点坐标，如 "(5,5)"
- `--goal`: 终点坐标，如 "(70,40)"
- `--output, -o`: 输出文件名

**compare_algorithms.py：**
- `--algorithms`: 算法列表（空格分隔）
- `--layout`: 布局方式（grid/horizontal/vertical）

**random_bounce_algorithm.py：**
- `--bounces, -n`: 碰撞次数
- `--width`: 区域宽度
- `--height`: 区域高度

## Python API

```python
from draw_pic_utils import MapBuilder, AlgorithmTester, Visualizer

# 构建地图
builder = MapBuilder()
builder.add_default_obstacles()
map_obj = builder.build()

# 测试算法
tester = AlgorithmTester(map_obj)
result = tester.test_algorithm('a_star')

# 可视化
viz = Visualizer()
viz.plot_result(result, save_path='pic/test.png')
```

## 输出格式

所有图片保存到 `/pic` 目录：
```
pic/
├── a_star_<时间戳>.png
├── dijkstra_<时间戳>.png
├── comparison_<时间戳>.png
└── random_bounce_coverage.png
```

## 性能指标

每个可视化包含：
- 路径成本
- 执行时间
- 扩展节点数（图搜索算法）
- 路径长度

## 子技能

详见 `subskills/` 目录：
- **自定义地图生成** - 迷宫、窄通道、螺旋等模式
- **性能基准测试** - 多次运行统计分析
- **算法动画生成** - 创建算法执行过程动画

## 依赖

```bash
pip install gymnasium osqp
```

## 配置

修改 `pyscripts/config.py` 调整：
- 默认地图尺寸
- 障碍物配置
- 可视化样式
- 输出目录
