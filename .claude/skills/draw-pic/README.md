# Draw Algorithm Picture Skill

这个 skill 用于快速生成 UAV 路径规划算法的可视化示意图。

## 快速开始

### 方法 1: 使用 Skill（推荐）
在 Claude Code 中直接使用斜杠命令：
```
/draw-pic A*
```

### 方法 2: 直接运行脚本
```bash
python .claude/skills/draw-pic/scripts/draw_algorithm.py "A*"
```

### 方法 3: 自定义起点和终点
```bash
python .claude/skills/draw-pic/scripts/draw_algorithm.py "Dijkstra" 10 10 80 40
```

## 支持的算法

| 算法名称 | 别名 | 类型 |
|---------|------|------|
| A* | AStar, a_star | 图搜索 |
| Dijkstra | dijkstra | 图搜索 |
| Theta* | ThetaStar, theta_star | 图搜索 |
| RRT | rrt | 采样搜索 |
| RRT* | RRTStar, rrt_star | 采样搜索 |

## 输出

- 生成的图片会保存在 `uav-path-planning/pic/` 目录
- 文件命名格式: `<algorithm_name>.png` (如 `a_star.png`)
- 测试脚本保存在 `uav-path-planning/test/` 目录

## 架构说明

基于 `example/main.py` 的模板架构：
1. 创建地图 (Grid)
2. 添加障碍物
3. 设置起点和终点
4. 使用指定算法规划路径
5. 可视化结果（地图、路径、搜索过程）
6. 保存图片

## 示例用法

```python
# 在 Claude Code 中
"生成 A* 算法的示意图"
"画一个 RRT 的路径规划图"
"对比 Dijkstra 和 A* 算法"
"用 Theta* 生成路径，起点 (10, 10)，终点 (80, 40)"
```

## 自定义选项

如果需要自定义地图、障碍物或其他参数，可以：
1. 直接修改 `test/` 目录下生成的脚本
2. 或者使用 `scripts/draw_algorithm.py` 中的 `draw_algorithm()` 函数

## 注意事项

- 不会修改 `/example` 目录中的任何内容
- 所有生成的代码都在 `/uav-path-planning/test` 中
- 所有图片输出在 `/uav-path-planning/pic` 中
