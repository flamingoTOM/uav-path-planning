# Draw-Pic 子技能

高级功能和扩展示例。

## 可用子技能

### 1. 自定义地图生成
**脚本：** `custom_map_example.py`
**文档：** `自定义地图生成.md`

创建不同模式的地图：
- 迷宫地图
- 窄通道地图
- 螺旋地图

**使用：**
```bash
python custom_map_example.py
```

### 2. 性能基准测试
**脚本：** `performance_benchmark.py`
**文档：** `性能基准测试.md`

统计分析算法性能：
- 多次运行统计
- 时间、成本、路径长度分析
- 对比报告生成

**使用：**
```bash
python performance_benchmark.py --iterations 20
```

### 3. 随机碰撞覆盖法
**脚本：** `../pyscripts/random_bounce_algorithm.py`
**文档：** `随机碰撞覆盖法.md`

实现全覆盖路径规划算法：
- 随机碰撞策略
- 覆盖过程可视化
- 适用于论文示意图

**使用：**
```bash
python ../pyscripts/random_bounce_algorithm.py --bounces 10
```

## 创建自定义子技能

模板示例：

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# 导入核心工具
pyscripts_dir = Path(__file__).parent.parent / 'pyscripts'
sys.path.insert(0, str(pyscripts_dir))

from draw_pic_utils import MapBuilder, AlgorithmTester, Visualizer

def main():
    # 构建自定义地图
    builder = MapBuilder(width=120, height=80)
    builder.add_obstacle_line(x=60, y=(10, 70))
    map_obj = builder.build(start=(10, 40), goal=(110, 40))

    # 测试算法
    tester = AlgorithmTester(map_obj)
    result = tester.test_algorithm('a_star')

    # 可视化
    viz = Visualizer()
    viz.plot_result(result, save_path='pic/my_custom.png')

if __name__ == '__main__':
    main()
```

## 子技能开发建议

1. **命名规范** - 使用描述性的中文或英文文件名
2. **文档同步** - 为每个脚本创建对应的 .md 说明文档
3. **输出一致** - 所有图片统一输出到 `pic/` 目录
4. **参数化** - 使用 argparse 提供命令行接口
5. **代码复用** - 充分利用 `draw_pic_utils` 中的工具类

## 扩展方向

- 动画生成 - 算法执行过程动画
- 多起点终点 - 批量测试不同配置
- 障碍物密度研究 - 分析障碍物影响
- 启发式对比 - 测试不同启发式函数
- 路径平滑 - 后处理路径优化
- 3D 可视化 - 三维路径展示
