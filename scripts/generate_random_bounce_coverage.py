"""
生成随机碰撞覆盖法示意图（简洁版）
只展示边框、路径、碰撞点、起点和终点
"""
import sys
sys.path.append('..')

import numpy as np
import matplotlib.pyplot as plt
from src.map import MapTypes
from src.map.grid_2d import Grid2D


def create_simple_map():
    """创建简单地图（只有边界）"""
    print("创建地图...")
    map_2d = Grid2D(bounds=[[0, 60], [0, 40]], resolution=1.0)

    # 只填充边界障碍物
    map_2d.fill_boundary_with_obstacles()

    # 边界膨胀
    map_2d.inflate_obstacles(radius=2.0)

    return map_2d


def simulate_random_bounce(map_2d, start_pos, target_bounces=10, step_size=2.5):
    """
    模拟随机碰撞覆盖，直到达到目标碰撞次数

    Args:
        map_2d: 地图对象
        start_pos: 起始位置 (x, y) 世界坐标
        target_bounces: 目标碰撞次数
        step_size: 每步移动距离

    Returns:
        path: 路径点列表
        bounce_points: 碰撞点列表
    """
    print(f"模拟随机碰撞覆盖（目标碰撞{target_bounces}次）...")

    path = [start_pos]
    bounce_points = []

    # 初始方向（随机）
    direction = np.random.uniform(0, 2 * np.pi)

    current_pos = np.array(start_pos, dtype=float)

    max_steps = 3000  # 防止无限循环
    step_count = 0

    safe_margin = 3.0  # 安全边距

    while len(bounce_points) < target_bounces and step_count < max_steps:
        step_count += 1

        # 计算下一个位置
        next_pos = current_pos + step_size * np.array([np.cos(direction), np.sin(direction)])

        # 边界检查（包含膨胀层）
        hit_boundary = False

        if next_pos[0] < map_2d.bounds[0, 0] + safe_margin:
            # 碰到左边界
            bounce_points.append(tuple(current_pos))
            hit_boundary = True
        elif next_pos[0] > map_2d.bounds[0, 1] - safe_margin:
            # 碰到右边界
            bounce_points.append(tuple(current_pos))
            hit_boundary = True
        elif next_pos[1] < map_2d.bounds[1, 0] + safe_margin:
            # 碰到下边界
            bounce_points.append(tuple(current_pos))
            hit_boundary = True
        elif next_pos[1] > map_2d.bounds[1, 1] - safe_margin:
            # 碰到上边界
            bounce_points.append(tuple(current_pos))
            hit_boundary = True

        if hit_boundary:
            # 随机转向（在0-360度范围内随机选择新方向）
            direction = np.random.uniform(0, 2 * np.pi)
            continue

        # 移动到下一个位置
        current_pos = next_pos
        path.append(tuple(current_pos))

    print(f"生成了 {len(path)} 个路径点，{len(bounce_points)} 个碰撞点")
    return path, bounce_points


def visualize_simple_coverage(map_2d, path, bounce_points):
    """可视化简洁版覆盖路径"""
    print("生成可视化...")

    fig, ax = plt.subplots(figsize=(12, 8))

    # 绘制白色背景
    ax.add_patch(plt.Rectangle(
        (map_2d.bounds[0, 0], map_2d.bounds[1, 0]),
        map_2d.bounds[0, 1] - map_2d.bounds[0, 0],
        map_2d.bounds[1, 1] - map_2d.bounds[1, 0],
        facecolor='white', edgecolor='none'
    ))

    # 绘制膨胀层（浅灰色）
    inflation_width = 2.0
    ax.add_patch(plt.Rectangle(
        (map_2d.bounds[0, 0], map_2d.bounds[1, 0]),
        map_2d.bounds[0, 1] - map_2d.bounds[0, 0],
        inflation_width,
        facecolor='#CCCCCC', edgecolor='none', label='Inflation Zone'
    ))
    ax.add_patch(plt.Rectangle(
        (map_2d.bounds[0, 0], map_2d.bounds[1, 1] - inflation_width),
        map_2d.bounds[0, 1] - map_2d.bounds[0, 0],
        inflation_width,
        facecolor='#CCCCCC', edgecolor='none'
    ))
    ax.add_patch(plt.Rectangle(
        (map_2d.bounds[0, 0], map_2d.bounds[1, 0]),
        inflation_width,
        map_2d.bounds[1, 1] - map_2d.bounds[1, 0],
        facecolor='#CCCCCC', edgecolor='none'
    ))
    ax.add_patch(plt.Rectangle(
        (map_2d.bounds[0, 1] - inflation_width, map_2d.bounds[1, 0]),
        inflation_width,
        map_2d.bounds[1, 1] - map_2d.bounds[1, 0],
        facecolor='#CCCCCC', edgecolor='none'
    ))

    # 绘制边界框
    ax.add_patch(plt.Rectangle(
        (map_2d.bounds[0, 0], map_2d.bounds[1, 0]),
        map_2d.bounds[0, 1] - map_2d.bounds[0, 0],
        map_2d.bounds[1, 1] - map_2d.bounds[1, 0],
        fill=False, edgecolor='black', linewidth=3
    ))

    # 绘制路径（红色）
    if len(path) > 1:
        path_array = np.array(path)
        ax.plot(path_array[:, 0], path_array[:, 1],
               color='red', linewidth=2, label='Coverage Path', zorder=3)

    # 绘制碰撞点（深红色叉号）
    if bounce_points:
        bounce_array = np.array(bounce_points)
        ax.scatter(bounce_array[:, 0], bounce_array[:, 1],
                  c='darkred', s=120, marker='x', linewidths=3,
                  label='Bounce Points', zorder=5)

    # 标记起点（绿色圆点）
    ax.plot(path[0][0], path[0][1], 'o', color='green', markersize=12,
           markeredgewidth=2, markeredgecolor='darkgreen',
           label='Start', zorder=6)

    # 标记终点（蓝色方块）
    ax.plot(path[-1][0], path[-1][1], 's', color='blue', markersize=12,
           markeredgewidth=2, markeredgecolor='darkblue',
           label='End', zorder=6)

    # 设置坐标轴
    ax.set_xlim(map_2d.bounds[0, 0] - 2, map_2d.bounds[0, 1] + 2)
    ax.set_ylim(map_2d.bounds[1, 0] - 2, map_2d.bounds[1, 1] + 2)
    ax.set_xlabel('X (m)', fontsize=13)
    ax.set_ylabel('Y (m)', fontsize=13)
    ax.set_title('Random Bounce Coverage Method', fontsize=15, fontweight='bold', pad=15)
    ax.set_aspect('equal')
    ax.legend(loc='upper right', fontsize=11, framealpha=0.95)

    plt.tight_layout()

    # 保存图片
    output_path = '../pic/random_bounce_coverage.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"示意图已保存至: {output_path}")

    plt.close()


def main():
    """主函数"""
    print("="*60)
    print("随机碰撞覆盖法示意图生成器（简洁版）")
    print("="*60)

    # 设置随机种子
    np.random.seed(42)

    # 创建地图
    map_2d = create_simple_map()

    # 模拟随机碰撞覆盖（10次碰撞）
    start_pos = (30.0, 20.0)  # 从中心位置开始
    path, bounce_points = simulate_random_bounce(
        map_2d, start_pos, target_bounces=10, step_size=2.5
    )

    # 可视化
    visualize_simple_coverage(map_2d, path, bounce_points)

    print("\n" + "="*60)
    print("生成完成！")
    print("="*60)


if __name__ == "__main__":
    main()
