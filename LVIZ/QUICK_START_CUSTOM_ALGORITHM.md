# 🚀 自定义算法快速入门

只需 **3 步**，在 LVIZ 平台运行你的路径规划算法！

---

## 第一步：创建算法文件

复制模板并重命名：

```bash
cd LVIZ
cp custom_algorithm_template.py my_algorithm.py
```

---

## 第二步：实现算法函数

编辑 `my_algorithm.py`，修改 `generate_path()` 函数：

```python
def generate_path(terrain_data: dict, polygon: list, params: dict) -> dict:
    """
    你的算法实现

    terrain_data: 地形数据 (elevation 矩阵, width, height, min/max 高程)
    polygon: 飞行区域多边形 [(x,y), ...]
    params: 规划参数 (min_altitude, coverage_width, overlap_rate)

    返回: {path: [...], statistics: {...}}
    """

    # 1. 提取数据
    elevation = terrain_data['elevation']  # numpy array
    width = terrain_data['width']
    height = terrain_data['height']

    # 2. 实现你的算法
    path = []
    # ... 你的代码 ...

    # 3. 返回结果
    return {
        'path': path,  # [{'x': x, 'y': y, 'altitude': alt, 'distance': dist}, ...]
        'statistics': {
            'total_distance': 总航程,
            'waypoint_count': 航点数,
            # ... 更多统计
        }
    }
```

---

## 第三步：启动并测试

### 启动后端服务器

```bash
python render_server.py
```

看到这个输出表示成功：
```
[OK] Matplotlib render server: http://localhost:5001
     Waiting for /render-3d requests ...
```

### 在前端调用

#### 方法 A：通过现有 RUN 菜单（推荐）

编辑 `render_server.py` 第 112 行，修改脚本路径：

```python
script_path = data.get('scriptPath', 'my_algorithm.py')  # 改为你的文件
```

然后：
1. 浏览器打开 http://localhost:3012
2. FILE → Open TIF File (导入高程图)
3. 在 Main Display Area 绘制多边形
4. RUN → Full Coverage (会调用你的算法)

#### 方法 B：添加新菜单项（更灵活）

在 `src/App.tsx` 中添加：

```typescript
const handleRunMyAlgorithm = async () => {
  if (!terrainData || !confirmedPolygon) {
    message.warning('请先导入 TIF 并框选区域');
    return;
  }

  message.loading({ content: '执行算法中...', key: 'algo', duration: 0 });

  try {
    const canvas = document.getElementById('main-display-canvas') as HTMLCanvasElement;
    const scaleX = terrainData.width / canvas.width;
    const scaleY = terrainData.height / canvas.height;

    const polygonTerrain = confirmedPolygon.map(p => [p.x * scaleX, p.y * scaleY]);

    const response = await fetch('/run-custom', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scriptPath: 'my_algorithm.py',  // 你的算法文件
        width: terrainData.width,
        height: terrainData.height,
        elevationData: Array.from(terrainData.elevationData),
        minElevation: terrainData.minElevation,
        maxElevation: terrainData.maxElevation,
        polygon: polygonTerrain,
        params: {
          minAltitude: coverageParams.minAltitude,
          coverageWidth: coverageParams.coverageWidth,
          overlapRate: coverageParams.overlapRate,
        }
      })
    });

    const result = await response.json();
    if (result.error) throw new Error(result.error);

    setPathData(result);
    message.success({ content: '算法执行成功！', key: 'algo' });
  } catch (error) {
    message.error({ content: `错误: ${error.message}`, key: 'algo' });
  }
};

// 添加到 RUN 菜单
const runMenuItems: MenuProps['items'] = [
  { key: 'full-coverage', label: 'Full Coverage', onClick: handleRunFullCoverage },
  { key: 'my-algo', label: '我的算法', onClick: handleRunMyAlgorithm },  // 新增
  { key: 'octree', label: 'Octree Planning', onClick: handleRunOctree },
];
```

---

## ✅ 完成！

现在你的算法已经集成到 LVIZ 平台了！

---

## 📊 输出格式说明

### 路径点格式

每个路径点包含：

```python
{
    'x': 123.45,        # X 坐标（地形像素，≈米）
    'y': 67.89,         # Y 坐标（地形像素，≈米）
    'altitude': 150.2,  # 飞行高度（米，绝对高度）
    'distance': 234.5   # 累计飞行距离（米）
}
```

### 统计信息（必需字段）

```python
{
    'total_distance': 1234.5,      # 总航程（米）
    'waypoint_count': 150,         # 航点数
    'coverage_area_m2': 50000.0,   # 覆盖面积（平方米）
    'estimated_time': 123.4,       # 预计时间（秒）
}
```

### 统计信息（可选字段）

```python
{
    'total_lines': 10,             # 航线数
    'line_spacing': 50.0,          # 航线间距（米）
    'plan_min_alt': 120.5,         # 最低飞行高度
    'plan_max_alt': 180.3,         # 最高飞行高度
    'algorithm': 'My Algorithm',   # 算法名称
    'execution_time': 0.5,         # 算法执行时间（秒）
    # ... 任何你想展示的统计数据
}
```

---

## 💡 常用算法模式

### 模式 1: 全覆盖扫描

```python
# 牛耕式往返扫描
for y in range(y1, y2, line_spacing):
    row_points = [点列表]
    if direction == -1:
        row_points.reverse()
    path.extend(row_points)
    direction *= -1
```

### 模式 2: 点对点导航

```python
# A* 或 Dijkstra
path = astar_search(start, goal, elevation, obstacles)
```

### 模式 3: 随机采样

```python
# RRT / RRT*
tree = build_rrt(start, goal, obstacles, max_iterations)
path = extract_path(tree, goal)
```

### 模式 4: 优化路径

```python
# 遗传算法 / 粒子群算法
best_path = optimize_path(waypoints, terrain, constraints)
```

---

## 🐛 调试提示

### 打印调试信息

在算法中添加 print：

```python
def generate_path(terrain_data, polygon, params):
    print(f"地形尺寸: {terrain_data['width']}x{terrain_data['height']}")
    print(f"多边形顶点数: {len(polygon)}")
    print(f"参数: {params}")

    # ... 算法实现 ...

    print(f"生成路径点数: {len(path)}")
    print(f"总航程: {total_distance:.1f}m")

    return result
```

在 `render_server.py` 终端中会看到这些输出。

### 可视化调试

返回额外的调试信息：

```python
return {
    'path': path,
    'statistics': {
        ...
        'debug_info': {
            'explored_nodes': 1234,
            'max_queue_size': 567,
            'pruned_nodes': 89,
        }
    }
}
```

在前端 Console 中查看 `console.log(result.statistics.debug_info)`

---

## 🎯 示例场景

### 场景 1: 农业植保无人机

```python
params = {
    'min_altitude': 10,      # 低空飞行 10m
    'coverage_width': 15,    # 喷洒宽度 15m
    'overlap_rate': 0.3,     # 30% 重叠确保无遗漏
}
```

### 场景 2: 地形测绘

```python
params = {
    'min_altitude': 100,     # 高空 100m
    'coverage_width': 80,    # 相机覆盖 80m
    'overlap_rate': 0.6,     # 60% 重叠用于立体重建
}
```

### 场景 3: 山地搜救

```python
params = {
    'min_altitude': 50,      # 离地 50m
    'max_slope': 25,         # 最大坡度 25°
    'terrain_following': True,  # 仿地飞行
}
```

---

## 📚 参考资源

- **已有示例**: `custom_algorithm_template.py` (牛耕式扫描)
- **A* 示例**: `algorithms/astar_example.py` (已创建)
- **详细文档**: `HOW_TO_ADD_CUSTOM_ALGORITHM.md`
- **后端服务器**: `render_server.py`

---

## ❓ 常见问题

**Q: 算法运行但没显示路径？**
- 检查返回的 `path` 格式是否正确
- 确保坐标在地形范围内 (0 ≤ x < width, 0 ≤ y < height)

**Q: 如何添加自定义参数？**
- 在前端 ControlPanel 添加输入框
- 通过 `params` 字典传递给算法
- 在算法中使用 `params.get('my_param', default_value)`

**Q: 如何处理大数据？**
- 算法中对数据降采样
- 使用空间索引加速查询（如 KD-Tree）
- 优化循环和数据结构

**Q: 如何返回中间状态？**
- 可以在 `statistics` 中添加任意字段
- 前端会在 Control Panel 显示统计信息

---

**祝开发顺利！** 🎉

如有问题，请查看完整文档 `HOW_TO_ADD_CUSTOM_ALGORITHM.md`
