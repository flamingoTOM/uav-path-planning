"""
6x6 网格强化学习路径规划 Demo
使用 Q-learning 算法从左下角寻找到右上角的最优路径
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class GridWorld:
    """6x6 网格世界环境"""

    def __init__(self, size=6):
        self.size = size
        self.start_state = (5, 0)  # 左下角 (row, col)
        self.goal_state = (0, 5)   # 右上角
        self.current_state = self.start_state

        # 定义动作：上、下、左、右
        self.actions = {
            0: (-1, 0),  # 上
            1: (1, 0),   # 下
            2: (0, -1),  # 左
            3: (0, 1)    # 右
        }
        self.action_names = ['上', '下', '左', '右']

    def reset(self):
        """重置环境到起始状态"""
        self.current_state = self.start_state
        return self.current_state

    def step(self, action):
        """执行动作，返回下一个状态、奖励、是否结束"""
        row, col = self.current_state
        d_row, d_col = self.actions[action]

        # 计算新位置
        new_row = max(0, min(self.size - 1, row + d_row))
        new_col = max(0, min(self.size - 1, col + d_col))

        self.current_state = (new_row, new_col)

        # 奖励函数设计
        if self.current_state == self.goal_state:
            reward = 100  # 到达目标，高奖励
            done = True
        elif (new_row, new_col) == (row, col):
            reward = -1  # 撞墙，小惩罚
            done = False
        else:
            reward = -1  # 每走一步的代价
            done = False

        return self.current_state, reward, done

    def get_state_index(self, state):
        """将二维状态转换为一维索引"""
        row, col = state
        return row * self.size + col


class QLearningAgent:
    """Q-learning 智能体"""

    def __init__(self, n_states, n_actions, learning_rate=0.1,
                 discount_factor=0.95, epsilon=1.0, epsilon_decay=0.995,
                 epsilon_min=0.01):
        self.n_states = n_states
        self.n_actions = n_actions
        self.lr = learning_rate  # 学习率
        self.gamma = discount_factor  # 折扣因子
        self.epsilon = epsilon  # 探索率
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min

        # 初始化 Q 表：状态 x 动作
        self.q_table = np.zeros((n_states, n_actions))

    def choose_action(self, state_index, training=True):
        """选择动作：ε-贪婪策略"""
        if training and np.random.random() < self.epsilon:
            # 探索：随机选择动作
            return np.random.randint(self.n_actions)
        else:
            # 利用：选择 Q 值最大的动作
            return np.argmax(self.q_table[state_index])

    def update_q_table(self, state, action, reward, next_state):
        """更新 Q 表"""
        # Q-learning 更新公式
        current_q = self.q_table[state, action]
        max_next_q = np.max(self.q_table[next_state])
        new_q = current_q + self.lr * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state, action] = new_q

    def decay_epsilon(self):
        """衰减探索率"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)


def train_agent(env, agent, n_episodes=500, max_steps=100):
    """训练智能体"""
    rewards_history = []
    steps_history = []
    epsilon_history = []
    success_history = []

    print("开始训练...")
    print(f"总回合数: {n_episodes}")
    print("-" * 50)

    for episode in range(n_episodes):
        state = env.reset()
        state_index = env.get_state_index(state)
        total_reward = 0
        steps = 0
        success = False

        for step in range(max_steps):
            # 选择动作
            action = agent.choose_action(state_index, training=True)

            # 执行动作
            next_state, reward, done = env.step(action)
            next_state_index = env.get_state_index(next_state)

            # 更新 Q 表
            agent.update_q_table(state_index, action, reward, next_state_index)

            total_reward += reward
            steps += 1
            state_index = next_state_index

            if done:
                success = True
                break

        # 衰减探索率
        agent.decay_epsilon()

        # 记录训练数据
        rewards_history.append(total_reward)
        steps_history.append(steps)
        epsilon_history.append(agent.epsilon)
        success_history.append(1 if success else 0)

        # 打印进度
        if (episode + 1) % 50 == 0:
            avg_reward = np.mean(rewards_history[-50:])
            avg_steps = np.mean(steps_history[-50:])
            success_rate = np.mean(success_history[-50:]) * 100
            print(f"回合 {episode + 1}/{n_episodes} | "
                  f"平均奖励: {avg_reward:.2f} | "
                  f"平均步数: {avg_steps:.2f} | "
                  f"成功率: {success_rate:.0f}% | "
                  f"ε: {agent.epsilon:.3f}")

    print("-" * 50)
    print("训练完成！")

    return rewards_history, steps_history, epsilon_history, success_history


def get_optimal_path(env, agent):
    """获取训练后的最优路径"""
    path = []
    state = env.reset()
    path.append(state)

    max_steps = 50
    for _ in range(max_steps):
        state_index = env.get_state_index(state)
        action = agent.choose_action(state_index, training=False)
        state, _, done = env.step(action)
        path.append(state)

        if done:
            break

    return path


def visualize_training_process(rewards, steps, epsilon, success, save_dir):
    """可视化训练过程"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    # 1. 每回合的奖励
    axes[0, 0].plot(rewards, alpha=0.3, color='blue', linewidth=0.5)
    axes[0, 0].plot(np.convolve(rewards, np.ones(50)/50, mode='valid'),
                    color='red', linewidth=2, label='50回合移动平均')
    axes[0, 0].set_xlabel('训练回合', fontsize=12)
    axes[0, 0].set_ylabel('总奖励', fontsize=12)
    axes[0, 0].set_title('训练过程 - 奖励变化', fontsize=14, fontweight='bold')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # 2. 每回合的步数
    axes[0, 1].plot(steps, alpha=0.3, color='green', linewidth=0.5)
    axes[0, 1].plot(np.convolve(steps, np.ones(50)/50, mode='valid'),
                    color='darkgreen', linewidth=2, label='50回合移动平均')
    axes[0, 1].set_xlabel('训练回合', fontsize=12)
    axes[0, 1].set_ylabel('步数', fontsize=12)
    axes[0, 1].set_title('训练过程 - 步数变化', fontsize=14, fontweight='bold')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # 3. 探索率衰减
    axes[1, 0].plot(epsilon, color='purple', linewidth=2)
    axes[1, 0].set_xlabel('训练回合', fontsize=12)
    axes[1, 0].set_ylabel('探索率 (ε)', fontsize=12)
    axes[1, 0].set_title('探索率衰减曲线', fontsize=14, fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3)

    # 4. 成功率
    success_rate = np.convolve(success, np.ones(50)/50, mode='valid') * 100
    axes[1, 1].plot(success_rate, color='orange', linewidth=2)
    axes[1, 1].set_xlabel('训练回合', fontsize=12)
    axes[1, 1].set_ylabel('成功率 (%)', fontsize=12)
    axes[1, 1].set_title('训练过程 - 成功率变化 (50回合滑动窗口)',
                        fontsize=14, fontweight='bold')
    axes[1, 1].set_ylim([0, 105])
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'training_process.png'),
                dpi=300, bbox_inches='tight')
    print(f"训练过程图已保存: {save_dir}/training_process.png")
    plt.close()


def visualize_grid_and_path(env, path, save_dir):
    """可视化网格和最优路径"""
    fig, ax = plt.subplots(figsize=(10, 10))

    # 绘制网格
    for i in range(env.size + 1):
        ax.plot([0, env.size], [i, i], 'k-', linewidth=1)
        ax.plot([i, i], [0, env.size], 'k-', linewidth=1)

    # 标记起点（绿色）
    start_row, start_col = env.start_state
    start_rect = patches.Rectangle((start_col, env.size - start_row - 1), 1, 1,
                                   linewidth=2, edgecolor='green',
                                   facecolor='lightgreen', alpha=0.7)
    ax.add_patch(start_rect)
    ax.text(start_col + 0.5, env.size - start_row - 0.5, 'S',
           fontsize=20, ha='center', va='center', fontweight='bold')

    # 标记终点（红色）
    goal_row, goal_col = env.goal_state
    goal_rect = patches.Rectangle((goal_col, env.size - goal_row - 1), 1, 1,
                                  linewidth=2, edgecolor='red',
                                  facecolor='lightcoral', alpha=0.7)
    ax.add_patch(goal_rect)
    ax.text(goal_col + 0.5, env.size - goal_row - 0.5, 'G',
           fontsize=20, ha='center', va='center', fontweight='bold')

    # 绘制路径
    if len(path) > 1:
        path_x = [col + 0.5 for row, col in path]
        path_y = [env.size - row - 0.5 for row, col in path]
        ax.plot(path_x, path_y, 'b-', linewidth=3, marker='o',
               markersize=10, label=f'最优路径 (步数: {len(path)-1})')

        # 添加箭头显示方向
        for i in range(len(path) - 1):
            dx = path_x[i + 1] - path_x[i]
            dy = path_y[i + 1] - path_y[i]
            ax.arrow(path_x[i], path_y[i], dx * 0.6, dy * 0.6,
                    head_width=0.15, head_length=0.1, fc='blue', ec='blue',
                    alpha=0.6, linewidth=2)

    ax.set_xlim([0, env.size])
    ax.set_ylim([0, env.size])
    ax.set_aspect('equal')
    ax.set_xlabel('列 (X)', fontsize=14)
    ax.set_ylabel('行 (Y)', fontsize=14)
    ax.set_title('Q-learning 最优路径 (6×6 网格)', fontsize=16, fontweight='bold')
    ax.legend(loc='upper left', fontsize=12)

    # 设置刻度
    ax.set_xticks(range(env.size + 1))
    ax.set_yticks(range(env.size + 1))

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'optimal_path.png'),
                dpi=300, bbox_inches='tight')
    print(f"最优路径图已保存: {save_dir}/optimal_path.png")
    plt.close()


def visualize_q_table(env, agent, save_dir):
    """可视化 Q 表（展示每个状态的最优动作）"""
    fig, ax = plt.subplots(figsize=(12, 10))

    # 绘制网格
    for i in range(env.size + 1):
        ax.plot([0, env.size], [i, i], 'k-', linewidth=1)
        ax.plot([i, i], [0, env.size], 'k-', linewidth=1)

    # 箭头方向映射
    arrow_map = {
        0: (0, 0.3),    # 上
        1: (0, -0.3),   # 下
        2: (-0.3, 0),   # 左
        3: (0.3, 0)     # 右
    }

    # 在每个格子中绘制最优动作
    for row in range(env.size):
        for col in range(env.size):
            state_index = env.get_state_index((row, col))

            # 跳过起点和终点
            if (row, col) == env.start_state or (row, col) == env.goal_state:
                continue

            # 获取最优动作
            best_action = np.argmax(agent.q_table[state_index])
            q_value = agent.q_table[state_index, best_action]

            # 绘制箭头
            x = col + 0.5
            y = env.size - row - 0.5
            dx, dy = arrow_map[best_action]

            ax.arrow(x, y, dx, dy, head_width=0.2, head_length=0.15,
                    fc='blue', ec='blue', alpha=0.7, linewidth=2)

            # 显示 Q 值
            ax.text(x, y - 0.35, f'{q_value:.1f}',
                   fontsize=8, ha='center', va='top', color='darkblue')

    # 标记起点和终点
    start_row, start_col = env.start_state
    start_rect = patches.Rectangle((start_col, env.size - start_row - 1), 1, 1,
                                   linewidth=2, edgecolor='green',
                                   facecolor='lightgreen', alpha=0.7)
    ax.add_patch(start_rect)
    ax.text(start_col + 0.5, env.size - start_row - 0.5, 'S',
           fontsize=20, ha='center', va='center', fontweight='bold')

    goal_row, goal_col = env.goal_state
    goal_rect = patches.Rectangle((goal_col, env.size - goal_row - 1), 1, 1,
                                  linewidth=2, edgecolor='red',
                                  facecolor='lightcoral', alpha=0.7)
    ax.add_patch(goal_rect)
    ax.text(goal_col + 0.5, env.size - goal_row - 0.5, 'G',
           fontsize=20, ha='center', va='center', fontweight='bold')

    ax.set_xlim([0, env.size])
    ax.set_ylim([0, env.size])
    ax.set_aspect('equal')
    ax.set_xlabel('列 (X)', fontsize=14)
    ax.set_ylabel('行 (Y)', fontsize=14)
    ax.set_title('Q 表可视化 - 每个状态的最优动作和 Q 值',
                fontsize=16, fontweight='bold')

    # 添加图例
    legend_elements = [
        patches.FancyArrow(0, 0, 0.3, 0, width=0.1,
                          facecolor='blue', edgecolor='blue', alpha=0.7)
    ]
    ax.legend(legend_elements, ['最优动作方向'],
             loc='upper left', fontsize=12)

    ax.set_xticks(range(env.size + 1))
    ax.set_yticks(range(env.size + 1))

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'q_table_visualization.png'),
                dpi=300, bbox_inches='tight')
    print(f"Q表可视化图已保存: {save_dir}/q_table_visualization.png")
    plt.close()


def main():
    """主函数"""
    # 创建保存目录
    save_dir = 'pic'
    os.makedirs(save_dir, exist_ok=True)

    # 创建环境和智能体
    env = GridWorld(size=6)
    n_states = env.size * env.size
    n_actions = len(env.actions)

    agent = QLearningAgent(
        n_states=n_states,
        n_actions=n_actions,
        learning_rate=0.1,
        discount_factor=0.95,
        epsilon=1.0,
        epsilon_decay=0.995,
        epsilon_min=0.01
    )

    print("=" * 50)
    print("6×6 网格强化学习路径规划")
    print("=" * 50)
    print(f"起点: {env.start_state} (左下角)")
    print(f"终点: {env.goal_state} (右上角)")
    print(f"状态空间大小: {n_states}")
    print(f"动作空间大小: {n_actions}")
    print("=" * 50)
    print()

    # 训练智能体
    rewards, steps, epsilon, success = train_agent(env, agent, n_episodes=500)

    print()
    print("=" * 50)
    print("训练结果统计")
    print("=" * 50)
    print(f"最后100回合平均奖励: {np.mean(rewards[-100:]):.2f}")
    print(f"最后100回合平均步数: {np.mean(steps[-100:]):.2f}")
    print(f"最后100回合成功率: {np.mean(success[-100:]) * 100:.1f}%")
    print("=" * 50)
    print()

    # 获取最优路径
    optimal_path = get_optimal_path(env, agent)
    print("最优路径:")
    for i, state in enumerate(optimal_path):
        print(f"步骤 {i}: {state}")
    print(f"总步数: {len(optimal_path) - 1}")
    print()

    # 生成可视化图表
    print("生成可视化图表...")
    visualize_training_process(rewards, steps, epsilon, success, save_dir)
    visualize_grid_and_path(env, optimal_path, save_dir)
    visualize_q_table(env, agent, save_dir)

    print()
    print("=" * 50)
    print("所有图表已生成完成！")
    print(f"图片保存位置: {save_dir}/")
    print("=" * 50)


if __name__ == "__main__":
    main()
