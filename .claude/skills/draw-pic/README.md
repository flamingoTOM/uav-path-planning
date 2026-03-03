# Draw Algorithm Picture Skill

这个 skill 用于快速生成 UAV 路径规划算法的可视化示意图或动画。

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

### 静态图片
- 保存位置: `uav-path-planning/pic/` 目录
- 文件格式: PNG
- 命名格式: `<algorithm_name>.png` (如 `a_star.png`)

### 动画 GIF
- 保存位置: `uav-path-planning/gif/` 目录
- 文件格式: GIF
- 命名格式: `<algorithm_name>_animation.gif` (如 `astar_animation.gif`)
- 特点: 展示算法逐步搜索过程，路径显示后停留若干秒

### 测试脚本
- 保存在 `uav-path-planning/test/` 目录

## 架构说明

基于 `example/main.py` 的模板架构：
1. 创建地图 (Grid)
2. 添加障碍物
3. 设置起点和终点
4. 使用指定算法规划路径
5. 可视化结果（地图、路径、搜索过程）
6. 保存图片

## 示例用法

### 生成静态图片
```python
# 在 Claude Code 中
"生成 A* 算法的示意图"
"画一个 RRT 的路径规划图"
"对比 Dijkstra 和 A* 算法"
"用 Theta* 生成路径，起点 (10, 10)，终点 (80, 40)"
```

### 生成动画
```python
# 在 Claude Code 中
"/draw-pic 创建 A* 算法动画，放在 /gif 目录"
"生成 A* 动画，寻路 6 秒，找到路后停留 3 秒"
"创建 RRT 算法的动画演示"
```

## 自定义选项

如果需要自定义地图、障碍物或其他参数，可以：
1. 直接修改 `test/` 目录下生成的脚本
2. 或者使用 `scripts/draw_algorithm.py` 中的 `draw_algorithm()` 函数

## 注意事项

- 不会修改 `/example` 目录中的任何内容
- 所有生成的代码都在 `/uav-path-planning/test` 中
- 静态图片输出在 `/uav-path-planning/pic` 中
- 动画 GIF 输出在 `/uav-path-planning/gif` 中
- 动画生成可能需要 30-60 秒，请耐心等待

## 动画参数说明

生成动画时可以控制以下参数：

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `frame_skip` | 控制动画帧数，值越大动画越快 | 65-100 |
| `hold_frames` | 路径显示后停留帧数 | 15-20 (3-4秒) |
| `fps` | 帧率 | 5 FPS |
| `dpi` | 图片分辨率 | 80 |

**时长参考：**
- 寻路 6 秒：`frame_skip=87`
- 寻路 8 秒：`frame_skip=65`
- 停留 3 秒：`hold_frames=15`
- 停留 4 秒：`hold_frames=20`
