# LVIZ 算法开发文档总览

欢迎使用 LVIZ 可视化平台！本文档帮助你快速集成自己的路径规划算法。

---

## 📚 文档导航

### 🚀 快速入门
**文件**: `QUICK_START_CUSTOM_ALGORITHM.md`

最快速度上手，3 步集成你的算法！适合：
- 第一次使用 LVIZ
- 想快速测试算法效果
- 了解基本工作流程

### 📖 完整指南
**文件**: `HOW_TO_ADD_CUSTOM_ALGORITHM.md`

详细的技术文档，包含：
- 架构说明
- 接口规范
- 多个示例算法（A*, RRT, 遗传算法）
- 前端集成方法
- 调试技巧

### 📝 算法模板
**文件**: `custom_algorithm_template.py`

标准算法模板，包含：
- 完整的函数签名
- 详细的参数说明
- 牛耕式扫描参考实现
- 注释和文档字符串

### 🎯 示例算法
**文件**: `algorithms/astar_example.py`

A* 路径规划完整实现：
- 考虑地形坡度约束
- 障碍物避让
- 最短路径优化
- 可直接运行测试

---

## 🏗️ 系统架构

```
┌──────────────────────────────────────────────┐
│  Web 前端 (React)                            │
│  • 地形可视化                                 │
│  • 交互式框选                                 │
│  • 参数设置                                   │
│  http://localhost:3012                      │
└────────────┬─────────────────────────────────┘
             │
             │ HTTP /run-custom
             ▼
┌──────────────────────────────────────────────┐
│  Python 后端 (Flask)                         │
│  • /render-3d → Matplotlib 3D 渲染          │
│  • /run-custom → 动态加载执行算法            │
│  http://localhost:5001                      │
└────────────┬─────────────────────────────────┘
             │
             │ 动态加载
             ▼
┌──────────────────────────────────────────────┐
│  你的算法模块                                 │
│  • my_algorithm.py                          │
│  • algorithms/astar.py                      │
│  • algorithms/rrt.py                        │
└──────────────────────────────────────────────┘
```

---

## 💻 必需的函数接口

你的算法文件必须包含：

```python
def generate_path(terrain_data: dict, polygon: list, params: dict) -> dict:
    """
    主函数：必须实现

    输入:
        terrain_data - 地形数据
        polygon - 多边形顶点 [(x,y), ...]
        params - 规划参数

    返回:
        result - {'path': [...], 'statistics': {...}}
    """
    pass
```

---

## 🎨 算法类型示例

### 全覆盖算法
- Boustrophedon (牛耕式) ✅ 已内置
- Spiral (螺旋式)
- Grid Coverage (网格覆盖)

### 点对点导航
- A* ✅ 有示例
- Dijkstra
- RRT / RRT*
- PRM (概率路图)

### 优化算法
- 遗传算法 ✅ 文档中有示例
- 粒子群优化 (PSO)
- 蚁群算法 (ACO)
- 模拟退火 (SA)

### 智能算法
- 强化学习路径规划
- 神经网络预测
- 深度学习避障

---

## 📦 可用的 Python 库

算法中可以使用任何 Python 库：

```python
import numpy as np           # 数值计算
import scipy                 # 科学计算
import networkx as nx        # 图算法
from sklearn import ...      # 机器学习
import torch                 # 深度学习
import cv2                   # 图像处理
```

只需 `pip install` 即可。

---

## 🔧 开发工具链

### 推荐开发流程

1. **独立测试**
   ```python
   # test_my_algorithm.py
   import numpy as np
   from my_algorithm import generate_path

   # 构造测试数据
   terrain_data = {
       'elevation': np.random.rand(100, 100) * 50,
       'width': 100,
       'height': 100,
       'min_elevation': 0,
       'max_elevation': 50,
   }

   polygon = [(10, 10), (90, 10), (90, 90), (10, 90)]
   params = {'min_altitude': 50}

   result = generate_path(terrain_data, polygon, params)
   print(f"生成航点数: {len(result['path'])}")
   ```

2. **集成到 LVIZ**
   - 启动 render_server.py
   - 在前端测试

3. **性能优化**
   - 使用 `cProfile` 分析性能
   - 优化瓶颈代码

### 单元测试

```python
# test_algorithms.py
import unittest
import numpy as np
from algorithms.astar import generate_path

class TestAStar(unittest.TestCase):
    def test_basic_path(self):
        terrain = {
            'elevation': np.zeros((100, 100)),
            'width': 100,
            'height': 100,
            'min_elevation': 0,
            'max_elevation': 0,
        }
        polygon = [(10,10), (90,10), (90,90), (10,90)]
        params = {'min_altitude': 50}

        result = generate_path(terrain, polygon, params)

        self.assertIsInstance(result, dict)
        self.assertIn('path', result)
        self.assertGreater(len(result['path']), 0)

if __name__ == '__main__':
    unittest.main()
```

---

## 📈 性能优化建议

### 大地形处理

```python
def generate_path(terrain_data, polygon, params):
    elevation = terrain_data['elevation']

    # 策略 1: 降采样
    if elevation.shape[0] > 1000:
        step = 2
        elevation = elevation[::step, ::step]
        # 记得调整坐标

    # 策略 2: 只处理感兴趣区域
    x1, y1, x2, y2 = get_bounding_box(polygon)
    elevation_roi = elevation[y1:y2, x1:x2]

    # 策略 3: 分块处理
    for block in divide_into_blocks(polygon):
        process_block(block)
```

### 算法复杂度

- **O(n²)** 以下: 可处理 1000x1000 地形
- **O(n³)** 以上: 建议降采样或分块

---

## 🎓 学习资源

### 路径规划算法

- [A* 算法教程](https://www.redblobgames.com/pathfinding/a-star/introduction.html)
- [RRT 算法论文](http://msl.cs.uiuc.edu/~lavalle/papers/Lav98c.pdf)
- [覆盖规划综述](https://ieeexplore.ieee.org/document/8593846)

### Python 开发

- NumPy 文档: https://numpy.org/doc/
- SciPy 文档: https://scipy.org/
- NetworkX 文档: https://networkx.org/

---

## 📞 获取帮助

### 问题排查

1. 检查后端服务器是否运行
2. 查看后端终端日志
3. 查看浏览器 Console
4. 检查文件路径是否正确

### 示例代码

查看 `algorithms/astar_example.py` 获取完整工作示例。

---

## 🎉 开始开发

选择一个文档开始：

| 如果你是... | 推荐阅读 |
|------------|---------|
| 🆕 新手 | `QUICK_START_CUSTOM_ALGORITHM.md` |
| 👨‍💻 开发者 | `HOW_TO_ADD_CUSTOM_ALGORITHM.md` |
| 🔍 寻找示例 | `algorithms/astar_example.py` |
| 📝 需要模板 | `custom_algorithm_template.py` |

**祝开发顺利！** 🚀
