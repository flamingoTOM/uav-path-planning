# 如何在 LVIZ 平台运行自己的算法

本指南详细说明如何将你的路径规划算法集成到 LVIZ 可视化平台。

---

## 📋 目录

1. [快速开始](#快速开始)
2. [架构说明](#架构说明)
3. [编写算法](#编写算法)
4. [算法接口规范](#算法接口规范)
5. [示例算法](#示例算法)
6. [前端调用](#前端调用)
7. [调试技巧](#调试技巧)

---

## 🚀 快速开始

### 第一步：复制算法模板

```bash
cd LVIZ
cp custom_algorithm_template.py my_algorithm.py
```

### 第二步：编写你的算法

在 `my_algorithm.py` 中实现 `generate_path()` 函数。

### 第三步：启动服务器

```bash
# 启动 Python 后端服务
python render_server.py
```

### 第四步：在前端调用

在 RUN 菜单中选择你的算法，或通过代码调用。

---

## 🏗️ 架构说明

### 系统架构

```
┌─────────────────────────────────────────────────────────┐
│  前端 (React + TypeScript)                              │
│  http://localhost:3012                                  │
│                                                         │
│  • 用户交互界面                                          │
│  • 数据可视化                                            │
│  • 多边形框选                                            │
└────────────────┬────────────────────────────────────────┘
                 │ HTTP POST
                 │ /run-custom
                 ▼
┌─────────────────────────────────────────────────────────┐
│  后端 (Python + Flask/HTTP Server)                      │
│  http://localhost:5001                                  │
│                                                         │
│  • /render-3d   → Matplotlib 3D 渲染                    │
│  • /run-custom  → 执行自定义算法                         │
└────────────────┬────────────────────────────────────────┘
                 │ 动态加载
                 ▼
┌─────────────────────────────────────────────────────────┐
│  你的算法模块 (my_algorithm.py)                          │
│                                                         │
│  def generate_path(terrain_data, polygon, params):     │
│      # 你的算法实现                                      │
│      return result                                     │
└─────────────────────────────────────────────────────────┘
```

### 数据流

```
用户导入 TIF → 前端解析 → 用户框选区域 → 调用算法 API
    ↓
后端接收请求 → 动态加载你的算法 → 执行 generate_path()
    ↓
返回路径数据 → 前端可视化 → 显示路径 + 统计 + 图表
```

---

## 💻 编写算法

### 文件位置

将你的算法文件放在 LVIZ 目录下：

```
LVIZ/
├── render_server.py              # 后端服务器（已存在）
├── custom_algorithm_template.py  # 算法模板（已存在）
├── my_algorithm.py               # 你的算法
├── algorithms/                   # 算法集合目录（可选）
│   ├── astar.py
│   ├── rrt.py
│   └── genetic.py
```

### 基本模板

```python
# my_algorithm.py
import numpy as np
import math

def point_in_polygon(px: float, py: float, polygon) -> bool:
    """射线法判断点是否在多边形内"""
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def generate_path(terrain_data: dict, polygon: list, params: dict) -> dict:
    """
    你的路径规划算法主函数

    Args:
        terrain_data: 地形数据字典
        polygon: 多边形顶点列表 [(x0,y0), (x1,y1), ...]
        params: 规划参数字典

    Returns:
        result: 包含 path 和 statistics 的字典
    """

    # 1. 提取地形数据
    elevation = terrain_data['elevation']  # numpy array (height, width)
    width = terrain_data['width']
    height = terrain_data['height']
    min_elev = terrain_data['min_elevation']
    max_elev = terrain_data['max_elevation']

    # 2. 提取参数
    min_altitude = float(params.get('min_altitude', 50))    # 飞行高度
    coverage_width = float(params.get('coverage_width', 50)) # 覆盖宽度
    overlap_rate = float(params.get('overlap_rate', 0.2))   # 重叠率

    # 3. 计算多边形包围盒
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    x1, y1 = int(max(0, min(xs))), int(max(0, min(ys)))
    x2, y2 = int(min(width-1, max(xs))), int(min(height-1, max(ys)))

    # 4. 实现你的算法
    path = []
    total_distance = 0.0

    # ========== 在这里实现你的算法 ==========

    # 示例：简单的网格扫描
    line_spacing = max(1, int(coverage_width * (1 - overlap_rate)))

    for y in range(y1, y2 + 1, line_spacing):
        for x in range(x1, x2 + 1):
            # 检查点是否在多边形内
            if point_in_polygon(x + 0.5, y + 0.5, polygon):
                # 获取地形高度
                idx = min(y * width + x, elevation.size - 1)
                terrain_alt = float(elevation.flat[idx])
                if math.isnan(terrain_alt):
                    terrain_alt = min_elev

                # 计算飞行高度
                altitude = terrain_alt + min_altitude

                # 计算距离
                if path:
                    prev = path[-1]
                    dx = x - prev['x']
                    dy = y - prev['y']
                    total_distance += math.sqrt(dx*dx + dy*dy)

                # 添加航点
                path.append({
                    'x': float(x),
                    'y': float(y),
                    'altitude': altitude,
                    'distance': total_distance
                })

    # ==========================================

    # 5. 计算统计信息
    # 计算多边形面积（鞋带公式）
    poly_area = 0.0
    n = len(polygon)
    for i in range(n):
        j = (i + 1) % n
        poly_area += polygon[i][0] * polygon[j][1] - polygon[j][0] * polygon[i][1]
    coverage_area_m2 = abs(poly_area) / 2.0

    # 航线数
    total_lines = max(1, (y2 - y1) // line_spacing)

    # 飞行时间（假设巡航速度 10 m/s）
    estimated_time = total_distance / 10.0

    # 最低/最高飞行高度
    altitudes = [p['altitude'] for p in path]
    plan_min_alt = min(altitudes) if altitudes else min_altitude
    plan_max_alt = max(altitudes) if altitudes else min_altitude

    # 6. 返回结果
    return {
        'path': path,
        'statistics': {
            'total_distance': total_distance,
            'total_lines': total_lines,
            'coverage_area_m2': coverage_area_m2,
            'estimated_time': estimated_time,
            'waypoint_count': len(path),
            'line_spacing': float(line_spacing),
            'plan_min_alt': plan_min_alt,
            'plan_max_alt': plan_max_alt,
        }
    }
```

---

## 📝 算法接口规范

### 函数签名

```python
def generate_path(
    terrain_data: dict,
    polygon: list,
    params: dict
) -> dict:
```

### 输入参数

#### `terrain_data` (dict)

| 字段 | 类型 | 说明 |
|------|------|------|
| `elevation` | np.ndarray | 高程矩阵，shape (height, width) |
| `width` | int | 地形宽度（像素 ≈ 米）|
| `height` | int | 地形高度（像素 ≈ 米）|
| `min_elevation` | float | 最低高程（米）|
| `max_elevation` | float | 最高高程（米）|

**坐标系统**: 左上角为原点 (0,0)，X 向右，Y 向下

#### `polygon` (list)

多边形顶点列表，地形坐标系：
```python
[(x0, y0), (x1, y1), (x2, y2), ...]
```

**注意**:
- 坐标单位为地形像素（通常 1 像素 ≈ 1 米）
- 已经从 canvas 坐标转换为地形坐标

#### `params` (dict)

规划参数：

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `min_altitude` | float | 离地高度（米）| 50 |
| `coverage_width` | float | 覆盖宽度（米）| 50 |
| `overlap_rate` | float | 重叠率 (0-1) | 0.2 |

**你可以添加自定义参数！**

### 返回值

```python
{
    'path': [
        {
            'x': float,          # X 坐标（地形像素）
            'y': float,          # Y 坐标（地形像素）
            'altitude': float,   # 飞行高度（米）
            'distance': float    # 累计距离（米）
        },
        ...
    ],
    'statistics': {
        'total_distance': float,    # 总航程（米）
        'total_lines': int,         # 航线数
        'coverage_area_m2': float,  # 覆盖面积（平方米）
        'estimated_time': float,    # 预计时间（秒）
        'waypoint_count': int,      # 航点数
        'line_spacing': float,      # 航线间距（米）
        'plan_min_alt': float,      # 最低飞行高度
        'plan_max_alt': float,      # 最高飞行高度
        # ... 你可以添加更多统计字段
    }
}
```

---

## 🎯 示例算法

### 示例 1: A* 路径规划

```python
# algorithms/astar.py
import numpy as np
import heapq
import math

def heuristic(a, b):
    """曼哈顿距离启发式"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(start, goal, elevation, width, height, max_slope=30):
    """
    A* 路径规划，考虑地形坡度约束

    Args:
        start: (x, y) 起点
        goal: (x, y) 终点
        elevation: 高程矩阵
        width, height: 地形尺寸
        max_slope: 最大允许坡度（度）
    """
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == goal:
            # 重构路径
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return list(reversed(path))

        # 8 个方向
        for dx, dy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
            neighbor = (current[0] + dx, current[1] + dy)

            # 边界检查
            if not (0 <= neighbor[0] < width and 0 <= neighbor[1] < height):
                continue

            # 坡度检查
            idx_cur = current[1] * width + current[0]
            idx_nei = neighbor[1] * width + neighbor[0]
            elev_cur = elevation.flat[idx_cur]
            elev_nei = elevation.flat[idx_nei]

            if math.isnan(elev_cur) or math.isnan(elev_nei):
                continue

            # 计算坡度
            distance = math.sqrt(dx*dx + dy*dy)
            slope = abs(elev_nei - elev_cur) / distance
            slope_degrees = math.degrees(math.atan(slope))

            if slope_degrees > max_slope:
                continue  # 坡度过大，跳过

            # 计算代价（距离 + 坡度惩罚）
            cost = distance * (1 + slope * 0.5)
            tentative_g = g_score[current] + cost

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []  # 未找到路径


def generate_path(terrain_data: dict, polygon: list, params: dict) -> dict:
    """
    使用 A* 算法规划路径
    """
    elevation = terrain_data['elevation']
    width = terrain_data['width']
    height = terrain_data['height']
    min_elev = terrain_data['min_elevation']

    min_altitude = float(params.get('min_altitude', 50))
    max_slope = float(params.get('max_slope', 30))  # 自定义参数

    # 获取多边形中心作为起点
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    start = (int(sum(xs)/len(xs)), int(sum(ys)/len(ys)))

    # 生成航点网格
    x1, y1 = int(min(xs)), int(min(ys))
    x2, y2 = int(max(xs)), int(max(ys))

    waypoints = []
    spacing = 20  # 航点间距
    for y in range(y1, y2, spacing):
        for x in range(x1, x2, spacing):
            if point_in_polygon(x, y, polygon):
                waypoints.append((x, y))

    # 使用 A* 连接所有航点
    full_path = []
    total_distance = 0.0
    current = start

    for waypoint in waypoints:
        segment = astar(current, waypoint, elevation, width, height, max_slope)
        if segment:
            for pt in segment:
                idx = pt[1] * width + pt[0]
                terrain_alt = float(elevation.flat[idx]) if idx < elevation.size else min_elev
                altitude = terrain_alt + min_altitude

                if full_path:
                    prev = full_path[-1]
                    dx = pt[0] - prev['x']
                    dy = pt[1] - prev['y']
                    total_distance += math.sqrt(dx*dx + dy*dy)

                full_path.append({
                    'x': float(pt[0]),
                    'y': float(pt[1]),
                    'altitude': altitude,
                    'distance': total_distance
                })

            current = waypoint

    # 计算统计
    altitudes = [p['altitude'] for p in full_path]

    return {
        'path': full_path,
        'statistics': {
            'total_distance': total_distance,
            'total_lines': len(waypoints),
            'coverage_area_m2': (x2-x1) * (y2-y1),
            'estimated_time': total_distance / 10.0,
            'waypoint_count': len(full_path),
            'line_spacing': float(spacing),
            'plan_min_alt': min(altitudes) if altitudes else 0,
            'plan_max_alt': max(altitudes) if altitudes else 0,
            'algorithm': 'A* Path Planning',  # 算法名称
        }
    }

def point_in_polygon(px: float, py: float, polygon) -> bool:
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside
```

### 示例 2: RRT 快速扩展随机树

```python
# algorithms/rrt.py
import numpy as np
import math
import random

def generate_path(terrain_data: dict, polygon: list, params: dict) -> dict:
    """
    RRT (Rapidly-exploring Random Tree) 路径规划
    """
    elevation = terrain_data['elevation']
    width = terrain_data['width']
    height = terrain_data['height']
    min_elev = terrain_data['min_elevation']

    min_altitude = float(params.get('min_altitude', 50))
    max_iterations = int(params.get('max_iterations', 1000))
    step_size = float(params.get('step_size', 5))

    # 起点和终点
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    start = (sum(xs)/len(xs), sum(ys)/len(ys))
    goal = (xs[0], ys[0])  # 或者选择多边形某个顶点

    # RRT 树
    tree = {start: None}

    for _ in range(max_iterations):
        # 随机采样
        rand_point = (
            random.uniform(min(xs), max(xs)),
            random.uniform(min(ys), max(ys))
        )

        # 找最近节点
        nearest = min(tree.keys(), key=lambda n: math.hypot(n[0]-rand_point[0], n[1]-rand_point[1]))

        # 向随机点扩展 step_size
        dist = math.hypot(rand_point[0]-nearest[0], rand_point[1]-nearest[1])
        if dist < 0.001:
            continue

        ratio = step_size / dist
        new_point = (
            nearest[0] + (rand_point[0] - nearest[0]) * ratio,
            nearest[1] + (rand_point[1] - nearest[1]) * ratio
        )

        # 碰撞检测（检查是否在多边形内）
        if not point_in_polygon(new_point[0], new_point[1], polygon):
            continue

        # 添加到树
        tree[new_point] = nearest

        # 检查是否到达目标
        if math.hypot(new_point[0]-goal[0], new_point[1]-goal[1]) < step_size:
            tree[goal] = new_point
            break

    # 回溯路径
    if goal not in tree:
        return {'path': [], 'statistics': {}}  # 未找到路径

    path_nodes = []
    current = goal
    while current is not None:
        path_nodes.append(current)
        current = tree[current]
    path_nodes.reverse()

    # 转换为标准格式
    path = []
    total_distance = 0.0

    for pt in path_nodes:
        x, y = int(pt[0]), int(pt[1])
        idx = min(y * width + x, elevation.size - 1)
        terrain_alt = float(elevation.flat[idx]) if not math.isnan(elevation.flat[idx]) else min_elev
        altitude = terrain_alt + min_altitude

        if path:
            prev = path[-1]
            dx = x - prev['x']
            dy = y - prev['y']
            total_distance += math.sqrt(dx*dx + dy*dy)

        path.append({
            'x': float(x),
            'y': float(y),
            'altitude': altitude,
            'distance': total_distance
        })

    altitudes = [p['altitude'] for p in path]

    return {
        'path': path,
        'statistics': {
            'total_distance': total_distance,
            'total_lines': 1,
            'coverage_area_m2': abs(sum(xs[i]*(ys[(i+1)%len(ys)]-ys[i-1]) for i in range(len(xs))))/2,
            'estimated_time': total_distance / 10.0,
            'waypoint_count': len(path),
            'line_spacing': 0,
            'plan_min_alt': min(altitudes) if altitudes else 0,
            'plan_max_alt': max(altitudes) if altitudes else 0,
            'algorithm': 'RRT',
        }
    }

def point_in_polygon(px: float, py: float, polygon) -> bool:
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside
```

---

## 🔌 前端调用

### 在 App.tsx 中添加自定义算法菜单

编辑 `src/App.tsx`，在 RUN 菜单中添加你的算法：

```typescript
const runMenuItems: MenuProps['items'] = [
  {
    key: 'full-coverage',
    label: 'Full Coverage',
    onClick: handleRunFullCoverage,
  },
  {
    key: 'astar',
    label: 'A* Path Planning',
    onClick: handleRunAStar,  // 新增
  },
  {
    key: 'rrt',
    label: 'RRT Planning',
    onClick: handleRunRRT,     // 新增
  },
  {
    key: 'octree',
    label: 'Octree Planning',
    onClick: handleRunOctree,
  },
];
```

### 实现调用函数

```typescript
const handleRunAStar = async () => {
  if (!terrainData) {
    message.warning('请先导入 TIF 文件');
    return;
  }

  if (!confirmedPolygon || confirmedPolygon.length < 3) {
    message.warning('请先在 Main Display Area 绘制并确认区域');
    return;
  }

  message.loading({ content: '正在执行 A* 算法...', key: 'algorithm', duration: 0 });

  try {
    // 获取 canvas 尺寸
    const canvas = document.getElementById('main-display-canvas') as HTMLCanvasElement;
    if (!canvas) throw new Error('Canvas not found');

    // 转换多边形坐标到地形坐标
    const scaleX = terrainData.width / canvas.width;
    const scaleY = terrainData.height / canvas.height;

    const polygonTerrain = confirmedPolygon.map(p => ({
      x: p.x * scaleX,
      y: p.y * scaleY
    }));

    // 调用后端算法
    const response = await fetch('/run-custom', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scriptPath: 'algorithms/astar.py',  // 算法文件路径
        width: terrainData.width,
        height: terrainData.height,
        elevationData: Array.from(terrainData.elevationData),
        minElevation: terrainData.minElevation,
        maxElevation: terrainData.maxElevation,
        polygon: polygonTerrain,
        params: {
          minAltitude: coverageParams.minAltitude,
          maxSlope: 30,  // 自定义参数
        }
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Algorithm execution failed');
    }

    const result = await response.json();
    setPathData(result);

    message.success({
      content: `A* 路径生成成功！航程: ${result.statistics.totalDistance.toFixed(0)}m`,
      key: 'algorithm',
      duration: 3,
    });
  } catch (error) {
    message.error({
      content: `算法执行失败: ${error instanceof Error ? error.message : '未知错误'}`,
      key: 'algorithm',
      duration: 5,
    });
  }
};
```

---

## 🛠️ 开发流程

### 1. 准备环境

```bash
# 安装 Python 依赖
pip install flask flask-cors numpy matplotlib
```

### 2. 创建算法文件

```bash
cd LVIZ
cp custom_algorithm_template.py algorithms/my_algorithm.py
```

### 3. 编写算法

在 `algorithms/my_algorithm.py` 中实现你的 `generate_path()` 函数。

### 4. 启动服务器

```bash
python render_server.py
```

输出应该显示：
```
[OK] Matplotlib render server: http://localhost:5001
     Waiting for /render-3d requests ...
```

### 5. 测试算法

在前端：
1. 导入 TIF 文件
2. 绘制多边形区域
3. RUN → 选择你的算法
4. 查看结果

---

## 🐛 调试技巧

### 后端调试

在 `render_server.py` 中会打印详细日志：

```
============================================================
执行算法: A*
地形尺寸: 500x400
多边形顶点数: 5
参数: {'min_altitude': 100, 'max_slope': 30}
============================================================

算法执行成功:
  - 生成路径点数: 234
  - 总航程: 1234.5m
  - 航线数: 12
  - 覆盖面积: 50000.0m²
============================================================
```

### 前端调试

打开浏览器控制台 (F12)，查看：
- 网络请求 (Network tab)
- 控制台日志 (Console tab)
- 算法执行结果

### 常见问题

**Q: 算法不执行？**
- 检查 `render_server.py` 是否运行
- 检查算法文件路径是否正确
- 查看后端控制台错误信息

**Q: 路径不显示？**
- 检查返回的 `path` 格式是否正确
- 确保坐标在地形范围内
- 查看浏览器控制台错误

**Q: 性能慢？**
- 减少路径点数量（增大采样间距）
- 优化算法复杂度
- 对大地形降采样

---

## 📊 自定义参数

你可以在前端添加自定义参数输入框，然后传递给算法：

### 前端 (ControlPanel.tsx)

```typescript
// 添加自定义参数输入
<div>
  <Text type="secondary" style={{ fontSize: 11 }}>
    最大坡度 (度)
  </Text>
  <InputNumber
    size="small"
    min={0}
    max={90}
    value={customParams.maxSlope}
    onChange={(value) => setCustomParams({ ...customParams, maxSlope: value })}
    style={{ width: '100%', marginTop: 4 }}
  />
</div>
```

### 后端 (my_algorithm.py)

```python
def generate_path(terrain_data: dict, polygon: list, params: dict) -> dict:
    # 提取自定义参数
    max_slope = float(params.get('max_slope', 30))

    # 在算法中使用
    # ...
```

---

## 📚 可用的第三方库

在算法中可以使用：

- **NumPy** - 数值计算
- **SciPy** - 科学计算（最短路径、插值等）
- **NetworkX** - 图算法
- **scikit-learn** - 机器学习
- **OpenCV** - 图像处理（需安装 `pip install opencv-python`）

示例：

```python
import numpy as np
from scipy.spatial import KDTree
from scipy.interpolate import interp1d
import networkx as nx
```

---

## 🎯 完整示例：遗传算法优化路径

```python
# algorithms/genetic.py
import numpy as np
import math
import random

def generate_path(terrain_data: dict, polygon: list, params: dict) -> dict:
    """使用遗传算法优化覆盖路径"""

    elevation = terrain_data['elevation']
    width = terrain_data['width']
    height = terrain_data['height']
    min_elev = terrain_data['min_elevation']
    min_altitude = float(params.get('min_altitude', 50))

    # 参数
    population_size = 50
    generations = 100
    mutation_rate = 0.1

    # 生成候选航点
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    x1, y1 = int(min(xs)), int(min(ys))
    x2, y2 = int(max(xs)), int(max(ys))

    waypoints = []
    for y in range(y1, y2, 20):
        for x in range(x1, x2, 20):
            if point_in_polygon(x, y, polygon):
                waypoints.append((x, y))

    n_waypoints = len(waypoints)
    if n_waypoints == 0:
        return {'path': [], 'statistics': {}}

    # 初始化种群（不同的访问顺序）
    population = [random.sample(range(n_waypoints), n_waypoints) for _ in range(population_size)]

    def fitness(order):
        """适应度函数：总路径长度（越小越好）"""
        dist = 0
        for i in range(len(order) - 1):
            p1 = waypoints[order[i]]
            p2 = waypoints[order[i+1]]
            dist += math.hypot(p2[0]-p1[0], p2[1]-p1[1])
        return -dist  # 负值，因为要最小化

    # 遗传算法主循环
    for gen in range(generations):
        # 选择
        population.sort(key=fitness, reverse=True)
        population = population[:population_size//2]

        # 交叉
        offspring = []
        while len(offspring) < population_size//2:
            p1, p2 = random.sample(population, 2)
            # 部分映射交叉 (PMX)
            cut1, cut2 = sorted(random.sample(range(n_waypoints), 2))
            child = [-1] * n_waypoints
            child[cut1:cut2] = p1[cut1:cut2]

            for i in range(n_waypoints):
                if child[i] == -1:
                    for val in p2:
                        if val not in child:
                            child[i] = val
                            break
            offspring.append(child)

        population.extend(offspring)

        # 变异
        for individual in population:
            if random.random() < mutation_rate:
                i, j = random.sample(range(n_waypoints), 2)
                individual[i], individual[j] = individual[j], individual[i]

    # 最优路径
    best_order = max(population, key=fitness)

    # 生成完整路径
    path = []
    total_distance = 0.0

    for idx in best_order:
        x, y = waypoints[idx]
        idx_elev = min(y * width + x, elevation.size - 1)
        terrain_alt = float(elevation.flat[idx_elev]) if not math.isnan(elevation.flat[idx_elev]) else min_elev
        altitude = terrain_alt + min_altitude

        if path:
            prev = path[-1]
            dx = x - prev['x']
            dy = y - prev['y']
            total_distance += math.sqrt(dx*dx + dy*dy)

        path.append({
            'x': float(x),
            'y': float(y),
            'altitude': altitude,
            'distance': total_distance
        })

    altitudes = [p['altitude'] for p in path]

    return {
        'path': path,
        'statistics': {
            'total_distance': total_distance,
            'total_lines': n_waypoints,
            'coverage_area_m2': abs(sum(xs[i]*(ys[(i+1)%len(ys)]-ys[i-1]) for i in range(len(xs))))/2,
            'estimated_time': total_distance / 10.0,
            'waypoint_count': len(path),
            'line_spacing': 20.0,
            'plan_min_alt': min(altitudes) if altitudes else 0,
            'plan_max_alt': max(altitudes) if altitudes else 0,
            'algorithm': f'Genetic Algorithm (Gen: {generations})',
        }
    }

def point_in_polygon(px: float, py: float, polygon) -> bool:
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside
```

---

## 📖 完整集成步骤

### 步骤总结

```
1. 复制模板
   cp custom_algorithm_template.py algorithms/my_algorithm.py

2. 实现算法
   编辑 algorithms/my_algorithm.py
   实现 generate_path() 函数

3. 启动后端
   python render_server.py

4. 前端添加菜单
   编辑 src/App.tsx
   添加 RUN 菜单项和处理函数

5. 测试
   导入 TIF → 框选区域 → RUN → 你的算法
```

---

## 📦 项目结构

```
LVIZ/
├── render_server.py              # Python 后端服务器
├── custom_algorithm_template.py  # 算法模板
├── algorithms/                   # 你的算法目录
│   ├── astar.py                 # A* 算法
│   ├── rrt.py                   # RRT 算法
│   ├── genetic.py               # 遗传算法
│   └── my_algorithm.py          # 你的算法
├── src/
│   └── App.tsx                  # 前端主应用
└── ...
```

---

## ✅ 检查清单

编写算法前请确认：

- [ ] 已安装 Python 依赖 (numpy, matplotlib, flask)
- [ ] 已复制算法模板
- [ ] 理解输入输出格式
- [ ] 熟悉坐标系统（左上角原点）
- [ ] 准备测试数据（TIF 文件）

---

## 🎉 现在开始编写你的算法！

如需帮助，请参考：
- `custom_algorithm_template.py` - 基础模板
- 本文档的示例代码
- `render_server.py` - 后端实现细节

祝开发顺利！🚀
