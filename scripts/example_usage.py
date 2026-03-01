"""
项目使用示例
演示如何使用统一的地图格式和规划框架
"""
import sys
sys.path.append('..')

import numpy as np
import matplotlib.pyplot as plt
from src.map import MapTypes
from src.map.grid_2d import Grid2D


def create_simple_map():
    """创建一个简单的测试地图"""
    print("创建 2D 栅格地图...")
    map_2d = Grid2D(bounds=[[0, 100], [0, 50]], resolution=1.0)

    # 填充边界
    map_2d.fill_boundary_with_obstacles()

    # 添加一些障碍物
    map_2d.add_obstacle((10, 10), (20, 15))
    map_2d.add_obstacle((30, 25), (40, 35))
    map_2d.add_obstacle((60, 5), (70, 15))
    map_2d.add_obstacle((50, 35), (55, 45))

    # 障碍物膨胀
    map_2d.inflate_obstacles(radius=2.0)

    # 设置起点和终点
    start = (5, 5)
    goal = (90, 45)
    map_2d.type_map[start] = MapTypes.START
    map_2d.type_map[goal] = MapTypes.GOAL

    print(f"地图尺寸: {map_2d.shape}")
    print(f"世界坐标范围: {map_2d.bounds}")
    print(f"分辨率: {map_2d.resolution} 米/格")

    return map_2d, start, goal


def visualize_map(map_2d, start, goal):
    """可视化地图"""
    print("\n可视化地图...")

    # 创建颜色映射
    color_map = {
        MapTypes.FREE: [1.0, 1.0, 1.0],      # 白色
        MapTypes.OBSTACLE: [0.2, 0.2, 0.2],  # 深灰
        MapTypes.INFLATION: [0.8, 0.8, 0.8], # 浅灰
        MapTypes.START: [0.2, 0.8, 0.2],     # 绿色
        MapTypes.GOAL: [0.8, 0.2, 0.2],      # 红色
    }

    # 创建 RGB 图像
    img = np.zeros((*map_2d.shape, 3))
    for type_val, color in color_map.items():
        mask = (map_2d.type_map == type_val)
        img[mask] = color

    # 绘制
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(img.transpose(1, 0, 2), origin='lower', extent=[
        map_2d.bounds[0, 0], map_2d.bounds[0, 1],
        map_2d.bounds[1, 0], map_2d.bounds[1, 1]
    ])

    # 标注起点和终点
    start_world = map_2d.map_to_world(start)
    goal_world = map_2d.map_to_world(goal)
    ax.plot(start_world[0], start_world[1], 'go', markersize=15, label='起点')
    ax.plot(goal_world[0], goal_world[1], 'rs', markersize=15, label='终点')

    ax.set_xlabel('X (m)', fontsize=12)
    ax.set_ylabel('Y (m)', fontsize=12)
    ax.set_title('2D 栅格地图示例', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('../pic/example_map.png', dpi=150)
    print("地图已保存至: ../pic/example_map.png")
    plt.show()


def test_coordinate_conversion(map_2d):
    """测试坐标转换"""
    print("\n测试坐标转换...")

    # Map -> World -> Map
    map_point = (50, 25)
    world_point = map_2d.map_to_world(map_point)
    map_point_back = map_2d.world_to_map(world_point)

    print(f"地图坐标: {map_point}")
    print(f"世界坐标: {world_point}")
    print(f"转换回地图坐标: {map_point_back}")
    assert map_point == map_point_back, "坐标转换不一致！"
    print("✓ 坐标转换测试通过")


def main():
    """主函数"""
    print("="*60)
    print("无人机路径规划项目 - 使用示例")
    print("="*60)

    # 创建地图
    map_2d, start, goal = create_simple_map()

    # 测试坐标转换
    test_coordinate_conversion(map_2d)

    # 可视化
    visualize_map(map_2d, start, goal)

    print("\n" + "="*60)
    print("示例运行完成！")
    print("="*60)


if __name__ == "__main__":
    main()
