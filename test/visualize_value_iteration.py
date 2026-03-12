import random
random.seed(0)
import numpy as np
np.random.seed(0)
import sys
sys.path.append("C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/example")
from python_motion_planning.common import *
import matplotlib.pyplot as plt

# Value Iteration 路径规划器
class ValueIterationPlanner:
    """Value Iteration 路径规划器（动态规划算法）"""

    def __init__(self, map_, start, goal, discount=0.95, threshold=0.01):
        self.map_ = map_
        self.start = start
        self.goal = goal
        self.gamma = discount  # 折扣因子
        self.threshold = threshold  # 收敛阈值

        # 动作空间：上、下、左、右
        self.actions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        # 初始化价值函数
        h, w = map_.type_map.shape
        self.value = np.zeros((h, w))
        self.policy = np.zeros((h, w), dtype=int)  # 最优策略

        # 记录访问过的状态（用于可视化）
        self.expand = {}

        # 记录训练历史
        self.delta_history = []
        self.value_snapshots = []  # 保存关键迭代的价值函数快照

    def is_valid(self, pos):
        """检查位置是否有效"""
        x, y = pos
        h, w = self.map_.type_map.shape
        if 0 <= x < h and 0 <= y < w:
            return self.map_.type_map[pos] != TYPES.OBSTACLE
        return False

    def get_reward(self, pos):
        """获取奖励"""
        if pos == self.goal:
            return 100.0
        elif not self.is_valid(pos):
            return -100.0
        else:
            return -1.0

    def get_next_state(self, state, action):
        """执行动作得到下一个状态"""
        next_state = (state[0] + action[0], state[1] + action[1])
        if not self.is_valid(next_state):
            return state  # 撞墙则保持原地
        return next_state

    def value_iteration(self):
        """Value Iteration 算法"""
        print("开始 Value Iteration 训练...")
        iteration = 0

        while True:
            iteration += 1
            delta = 0.0
            new_value = self.value.copy()

            # 更新所有状态的价值函数
            for x in range(self.value.shape[0]):
                for y in range(self.value.shape[1]):
                    state = (x, y)

                    # 跳过障碍物和目标点
                    if not self.is_valid(state) or state == self.goal:
                        continue

                    # 记录探索的状态
                    self.expand[state] = None

                    # 计算所有动作的 Q 值
                    q_values = []
                    for action in self.actions:
                        next_state = self.get_next_state(state, action)
                        reward = self.get_reward(next_state)
                        nx, ny = next_state
                        q_value = reward + self.gamma * self.value[nx, ny]
                        q_values.append(q_value)

                    # 更新价值函数（取最大 Q 值）
                    max_q = max(q_values)
                    new_value[x, y] = max_q

                    # 更新策略（选择最优动作）
                    self.policy[x, y] = np.argmax(q_values)

                    # 计算变化量
                    delta = max(delta, abs(self.value[x, y] - max_q))

            self.value = new_value

            # 记录训练历史
            self.delta_history.append(delta)

            # 保存关键迭代的快照（第1,10,30,60,100,最后一次）
            if iteration in [1, 10, 30, 60, 100] or delta < self.threshold:
                self.value_snapshots.append((iteration, self.value.copy()))

            if iteration % 10 == 0:
                print(f"  Iteration {iteration}, Delta: {delta:.6f}")

            # 检查收敛
            if delta < self.threshold:
                print(f"收敛！总迭代次数: {iteration}")
                break

            if iteration > 1000:
                print("达到最大迭代次数")
                break

        print("训练完成！")

    def extract_path(self):
        """根据最优策略提取路径"""
        path = []
        state = self.start
        visited = set()

        for step in range(500):
            path.append(state)
            visited.add(state)

            if state == self.goal:
                break

            # 根据策略选择动作
            x, y = state
            action_idx = self.policy[x, y]
            action = self.actions[action_idx]

            next_state = self.get_next_state(state, action)

            # 避免循环
            if next_state in visited:
                print(f"警告：检测到循环，在步骤 {step} 处停止")
                break

            state = next_state

        return path


def visualize_training_process(planner, map_, output_path):
    """可视化训练过程"""
    print("生成训练过程可视化...")

    # 创建图形：1行2列
    fig = plt.figure(figsize=(20, 8))

    # 左侧：Delta 收敛曲线
    ax1 = plt.subplot(1, 2, 1)
    iterations = range(1, len(planner.delta_history) + 1)
    ax1.plot(iterations, planner.delta_history, linewidth=2, color='#2E86AB')
    ax1.axhline(y=planner.threshold, color='red', linestyle='--', linewidth=2,
                label=f'Threshold = {planner.threshold}')
    ax1.set_xlabel('Iteration', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Delta (Max Value Change)', fontsize=14, fontweight='bold')
    ax1.set_title('Value Iteration Convergence', fontsize=16, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=12)
    ax1.set_yscale('log')  # 使用对数刻度更清晰

    # 右侧：价值函数热力图演变（选择关键迭代）
    num_snapshots = min(6, len(planner.value_snapshots))

    # 创建子图网格
    gs = fig.add_gridspec(2, 3, left=0.55, right=0.98, top=0.92, bottom=0.08,
                          hspace=0.3, wspace=0.3)

    for idx in range(num_snapshots):
        if idx < len(planner.value_snapshots):
            iteration, value_snapshot = planner.value_snapshots[idx]

            ax = fig.add_subplot(gs[idx // 3, idx % 3])

            # 创建遮罩版本（障碍物显示为白色）
            masked_value = value_snapshot.copy()
            for x in range(masked_value.shape[0]):
                for y in range(masked_value.shape[1]):
                    if not planner.is_valid((x, y)):
                        masked_value[x, y] = np.nan

            # 绘制热力图
            im = ax.imshow(masked_value, cmap='viridis', origin='lower',
                          interpolation='bilinear', aspect='auto')

            # 标记起点和终点
            ax.plot(planner.start[1], planner.start[0], 'r*', markersize=15)
            ax.plot(planner.goal[1], planner.goal[0], 'g*', markersize=15)

            ax.set_title(f'Iteration {iteration}', fontsize=12, fontweight='bold')
            ax.set_xlabel('X', fontsize=10)
            ax.set_ylabel('Y', fontsize=10)

            # 添加颜色条
            cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            cbar.set_label('Value', fontsize=9)

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"训练过程图已保存: {output_path}")
    plt.close()

# 1. 创建地图 - ⚠️ 不可变约束
map_ = Grid(bounds=[[0, 101], [0, 51]])  # 永远不能修改
map_.fill_boundary_with_obstacles()

# 2. 添加障碍物（标准配置）
map_.type_map[10:21, 25] = TYPES.OBSTACLE
map_.type_map[20, :25] = TYPES.OBSTACLE
map_.type_map[35, 15:] = TYPES.OBSTACLE
map_.type_map[70, :16] = TYPES.OBSTACLE
map_.type_map[55, 29:] = TYPES.OBSTACLE
map_.type_map[55:85, 29] = TYPES.OBSTACLE
map_.inflate_obstacles(radius=2)

# 3. 设置起点和终点
start = (5, 5)
goal = (70, 40)
map_.type_map[start] = TYPES.START
map_.type_map[goal] = TYPES.GOAL

# 4. 创建 Value Iteration 规划器
print("=" * 50)
print("Value Iteration 路径规划")
print("=" * 50)
planner = ValueIterationPlanner(map_=map_, start=start, goal=goal,
                               discount=0.95, threshold=0.01)

# 5. 运行 Value Iteration
planner.value_iteration()

# 6. 提取路径
path = planner.extract_path()
print(f"找到路径，长度: {len(path)}")

# 7. 可视化
map_.fill_expands(planner.expand)
vis = Visualizer("Value Iteration Path Planning")
vis.plot_grid_map(map_)
vis.plot_path(path)

# 8. 添加标注 - ⚠️ 不可变约束（只改算法名称）
vis.ax.text(
    0.5, 1.08,
    "Value Iteration",  # ← 只能改这里
    transform=vis.ax.transAxes,
    ha="center", va="top",
    fontsize=20,
    zorder=10000
)

# 9. 保存路径图
output_path = "C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/pic/value_iteration.png"
vis.fig.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"路径图已保存: {output_path}")
vis.close()

# 10. 生成训练过程可视化
training_output = "C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/pic/value_iteration_training.png"
visualize_training_process(planner, map_, training_output)

print("=" * 50)
print("可视化完成！")
print("=" * 50)
