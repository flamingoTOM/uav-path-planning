"""
随机碰撞覆盖法示意图生成脚本
Random Bounce Coverage Method Visualization

描述：展示机器人在封闭区域内的随机碰撞覆盖路径规划过程
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import matplotlib
matplotlib.use('Agg')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 创建图形
fig, ax = plt.subplots(figsize=(12, 8))
fig.patch.set_facecolor('white')

# 定义工作区域边界
workspace_width = 10
workspace_height = 8
ax.add_patch(patches.Rectangle((0, 0), workspace_width, workspace_height,
                                fill=False, edgecolor='#1e293b', linewidth=2.5))

# 添加障碍物
obstacles = [
    patches.Rectangle((3, 5), 1.5, 1.2, fill=True, facecolor='#94a3b8', edgecolor='#475569', linewidth=1.5),
    patches.Rectangle((6.5, 2), 1.2, 1.8, fill=True, facecolor='#94a3b8', edgecolor='#475569', linewidth=1.5),
    patches.Circle((2, 2), 0.6, fill=True, facecolor='#94a3b8', edgecolor='#475569', linewidth=1.5)
]
for obstacle in obstacles:
    ax.add_patch(obstacle)

# 模拟随机碰撞路径
np.random.seed(42)

# 初始位置和方向
x, y = 1, 1
angle = 45  # 初始角度（度）
step_size = 0.3
path_x, path_y = [x], [y]
bounce_points_x, bounce_points_y = [], []

# 模拟移动步数
for i in range(150):
    # 计算下一步位置
    next_x = x + step_size * np.cos(np.radians(angle))
    next_y = y + step_size * np.sin(np.radians(angle))

    # 检查是否碰到边界
    bounced = False
    if next_x <= 0 or next_x >= workspace_width:
        angle = 180 - angle
        bounced = True
    if next_y <= 0 or next_y >= workspace_height:
        angle = -angle
        bounced = True

    # 简单的障碍物碰撞检测
    if 3 <= next_x <= 4.5 and 5 <= next_y <= 6.2:
        angle = angle + np.random.uniform(90, 270)
        bounced = True
    if 6.5 <= next_x <= 7.7 and 2 <= next_y <= 3.8:
        angle = angle + np.random.uniform(90, 270)
        bounced = True
    if np.sqrt((next_x - 2)**2 + (next_y - 2)**2) <= 0.6:
        angle = angle + np.random.uniform(90, 270)
        bounced = True

    # 随机扰动（体现随机性）
    if bounced:
        angle = angle + np.random.uniform(-30, 30)
        bounce_points_x.append(x)
        bounce_points_y.append(y)

    # 更新位置
    x += step_size * np.cos(np.radians(angle))
    y += step_size * np.sin(np.radians(angle))

    # 确保在边界内
    x = np.clip(x, 0, workspace_width)
    y = np.clip(y, 0, workspace_height)

    path_x.append(x)
    path_y.append(y)

# 绘制路径
# 使用渐变色表示时间顺序
for i in range(len(path_x) - 1):
    alpha = 0.3 + 0.7 * (i / len(path_x))
    color_intensity = 0.4 + 0.6 * (i / len(path_x))
    ax.plot(path_x[i:i+2], path_y[i:i+2],
            color=plt.cm.Blues(color_intensity),
            linewidth=1.5, alpha=alpha)

# 标记起点和终点
ax.plot(path_x[0], path_y[0], 'o', color='#22c55e', markersize=12,
        label='起点', zorder=10, markeredgecolor='white', markeredgewidth=2)
ax.plot(path_x[-1], path_y[-1], 's', color='#ef4444', markersize=12,
        label='终点', zorder=10, markeredgecolor='white', markeredgewidth=2)

# 标记碰撞点
ax.scatter(bounce_points_x[:20], bounce_points_y[:20],
           c='#f59e0b', s=50, alpha=0.6, marker='x',
           linewidths=2, label='碰撞转向点', zorder=5)

# 添加说明文本
ax.text(0.5, workspace_height + 0.5, '随机碰撞覆盖法示意图',
        fontsize=18, fontweight='bold', color='#1e293b')
ax.text(0.5, workspace_height + 0.2,
        '机器人遇到障碍物或边界时随机转向，重复覆盖区域',
        fontsize=12, color='#475569')

# 添加特征标注
ax.annotate('遇边界转向', xy=(0.1, 4), xytext=(0.5, 6.5),
            arrowprops=dict(arrowstyle='->', color='#f59e0b', lw=2),
            fontsize=11, color='#f59e0b', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#fef3c7', edgecolor='#f59e0b'))

ax.annotate('路径重叠区域\n(效率损失)', xy=(5, 4.5), xytext=(8.5, 6),
            arrowprops=dict(arrowstyle='->', color='#3b82f6', lw=2),
            fontsize=11, color='#3b82f6', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#dbeafe', edgecolor='#3b82f6'))

# 图例和标注
ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
ax.text(7.5, 0.5, '障碍物', fontsize=10, color='#475569',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#e2e8f0'))

# 设置坐标轴
ax.set_xlim(-0.5, workspace_width + 0.5)
ax.set_ylim(-0.5, workspace_height + 1)
ax.set_xlabel('X 坐标 (m)', fontsize=12, fontweight='bold')
ax.set_ylabel('Y 坐标 (m)', fontsize=12, fontweight='bold')
ax.set_aspect('equal')
ax.grid(True, alpha=0.2, linestyle='--')

# 移除顶部和右侧边框
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('../pic/random_bounce_coverage.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("图片已保存至: ../pic/random_bounce_coverage.png")
print(f"总路径点数: {len(path_x)}")
print(f"碰撞转向次数: {len(bounce_points_x)}")
