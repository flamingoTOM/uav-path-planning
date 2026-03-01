# Draw-Pic 脚本说明

路径规划算法测试和可视化脚本集合。

## 核心脚本

### test_algorithm.py
测试单个算法并生成可视化。

```bash
# 测试 A* 算法
python test_algorithm.py --algorithm a_star

# 自定义起点终点
python test_algorithm.py -a dijkstra --start "(10,10)" --goal "(80,40)"

# 指定输出文件
python test_algorithm.py -a theta_star --output my_test.png

# 只显示不保存
python test_algorithm.py -a a_star --no-save --show
```

### compare_algorithms.py
对比多个算法。

```bash
# 对比默认算法
python compare_algorithms.py

# 指定算法
python compare_algorithms.py --algorithms a_star dijkstra theta_star

# 改变布局
python compare_algorithms.py --layout horizontal

# 自定义输出
python compare_algorithms.py --output my_comparison.png
```

### batch_test.py
批量测试所有算法。

```bash
# 测试所有算法
python batch_test.py

# 测试指定算法
python batch_test.py --algorithms a_star dijkstra

# 仅生成对比图
python batch_test.py --skip-individual

# 仅生成单独图
python batch_test.py --skip-comparison
```

### random_bounce_algorithm.py
随机碰撞覆盖法可视化。

```bash
# 基本用法
python random_bounce_algorithm.py --bounces 10

# 自定义地图尺寸
python random_bounce_algorithm.py -n 20 --width 150 --height 80

# 指定输出
python random_bounce_algorithm.py -n 15 --output bounce.png
```

## Python API 使用

```python
from draw_pic_utils import MapBuilder, AlgorithmTester, Visualizer

# 构建地图
builder = MapBuilder(width=101, height=51)
builder.add_default_obstacles()
map_obj = builder.build(start=(5, 5), goal=(70, 40))

# 测试算法
tester = AlgorithmTester(map_obj)
result = tester.test_algorithm('a_star')

# 可视化
viz = Visualizer()
viz.plot_result(result, save_path='pic/test.png')
```

## 配置文件

编辑 `config.py` 修改：
- 默认地图尺寸和配置
- 默认障碍物
- 可用算法列表
- 可视化设置
- 输出目录

## 输出

所有图片保存到 `/pic` 目录，带时间戳防止覆盖。

## 工具类

### MapBuilder
地图构建器，支持：
- `add_default_obstacles()` - 添加默认障碍物
- `add_obstacle_line()` - 添加线性障碍物
- `add_obstacle_rectangle()` - 添加矩形障碍物
- `build()` - 构建地图对象

### AlgorithmTester
算法测试器，支持：
- `test_algorithm(name)` - 测试单个算法
- `test_multiple_algorithms(names)` - 测试多个算法

### Visualizer
可视化工具，支持：
- `plot_result(result)` - 单个结果可视化
- `plot_comparison(results)` - 多个结果对比
