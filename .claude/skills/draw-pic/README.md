# Draw-Pic 技能

路径规划算法可视化工具，基于 `example/main.py` 地图架构。

## 快速开始

```bash
# 测试单个算法
python .claude/skills/draw-pic/pyscripts/test_algorithm.py -a a_star

# 对比多个算法
python .claude/skills/draw-pic/pyscripts/compare_algorithms.py

# 批量测试
python .claude/skills/draw-pic/pyscripts/batch_test.py

# 随机碰撞覆盖法
python .claude/skills/draw-pic/pyscripts/random_bounce_algorithm.py -n 10
```

## 目录结构

```
draw-pic/
├── SKILL.md                          # 完整技能文档
├── README.md                         # 本文件
├── pyscripts/                        # Python 脚本
│   ├── config.py                     # 配置文件
│   ├── draw_pic_utils.py             # 核心工具类
│   ├── test_algorithm.py             # 单算法测试
│   ├── compare_algorithms.py         # 多算法对比
│   ├── batch_test.py                 # 批量测试
│   ├── random_bounce_algorithm.py    # 随机碰撞覆盖法
│   └── __init__.py
└── subskills/                        # 子技能
    ├── 自定义地图生成.md
    ├── 性能基准测试.md
    ├── 随机碰撞覆盖法.md
    ├── custom_map_example.py
    └── performance_benchmark.py
```

## 支持的算法

**图搜索算法：**
- A* - 启发式最优路径
- Dijkstra - 保证最优路径
- Theta* - 任意角度路径规划

**采样搜索算法：**
- RRT - 快速探索随机树
- RRT* - 渐进最优版本

**覆盖算法：**
- 随机碰撞覆盖法

## 输出位置

所有图片保存到：`ws/pic/`

## 依赖安装

```bash
pip install gymnasium osqp
```

## 配置

编辑 `pyscripts/config.py` 修改默认配置。

## 文档

- **SKILL.md** - 完整使用文档
- **subskills/** - 子技能说明
- **pyscripts/README.md** - 脚本参考
