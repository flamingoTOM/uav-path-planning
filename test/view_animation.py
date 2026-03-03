"""
查看生成的 A* 算法动画
"""
import os
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

gif_path = "C:/Users/xiaoyu.liu/Desktop/my_project/uav-path-planning/gif/astar_animation.gif"

if not os.path.exists(gif_path):
    print(f"错误：找不到文件 {gif_path}")
    exit(1)

print(f"正在加载动画: {gif_path}")

# 使用 PIL 打开 GIF
img = Image.open(gif_path)

# 获取 GIF 信息
frame_count = 0
try:
    while True:
        frame_count += 1
        img.seek(frame_count)
except EOFError:
    pass

print(f"\nGIF 信息:")
print(f"  - 文件大小: {os.path.getsize(gif_path) / (1024*1024):.2f} MB")
print(f"  - 图片尺寸: {img.size[0]} x {img.size[1]} 像素")
print(f"  - 总帧数: {frame_count}")
print(f"  - 模式: {img.mode}")

# 显示 GIF
print(f"\n正在使用 matplotlib 显示动画...")
print("关闭窗口以退出。")

fig, ax = plt.subplots(figsize=(10, 6))
ax.axis('off')

img.seek(0)
im = ax.imshow(img)

def update(frame):
    img.seek(frame % frame_count)
    im.set_array(img.convert('RGB'))
    return [im]

ani = FuncAnimation(fig, update, frames=frame_count, interval=200, blit=True, repeat=True)
plt.tight_layout()
plt.show()
