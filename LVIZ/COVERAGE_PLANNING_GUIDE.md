# LVIZ 全覆盖路径规划使用指南

## 功能概述

LVIZ 现在支持完整的 UAV 全覆盖路径规划功能，包括：
- 交互式区域选择
- 仿地飞行算法
- 实时路径生成
- 飞行高度剖面图

---

## 使用流程

### 第一步：导入 TIF 高程图

1. 点击菜单栏 **FILE → Open TIF File**
2. 选择你的 .tif 高程图文件
3. 等待文件解析完成

### 第二步：选择覆盖区域

1. 在 **Main Display Area** (中央区域) 会显示俯视图
2. 用鼠标**拖动框选**要覆盖的区域
3. 松开鼠标后会出现 **Confirm** 和 **Cancel** 按钮
4. 点击 **Confirm** 确认选择
5. 右侧 Control Panel 会显示 **Selected Region** 参数面板

### 第三步：设置覆盖参数

在右侧 **Control Panel** 的 **Coverage Parameters** 中设置：

| 参数 | 说明 | 默认值 | 范围 |
|------|------|--------|------|
| **Flight Height** | 飞行高度 | 100 m | 10-500 m |
| **Coverage Width** | 单次扫描覆盖宽度 | 50 m | 5-200 m |
| **Overlap Rate** | 相邻扫描线重叠率 | 20% | 0-50% |
| **Terrain Following** | 是否仿地飞行 | 开启 | 开关 |

### 第四步：生成覆盖路径

1. 点击菜单栏 **RUN → Full Coverage**
2. 算法会自动生成覆盖路径
3. 路径会显示在 Main Display Area (红色线和点)
4. 右侧显示路径统计信息
5. 底部 Bottom Panel 显示**距离-飞行高度图**

---

## 算法说明

### 全覆盖算法 (Boustrophedon Pattern)

采用经典的"牛耕式"往返路径：

```
Start →→→→→→→→→→→ End
                ↓
      ←←←←←←←←←←←
      ↓
      →→→→→→→→→→→
                ↓
      ←←←←←←←←←←←
```

**特点**:
- 完全覆盖选定区域
- 最小转弯次数
- 路径平滑连续

### 仿地飞行模式

**启用时**:
- 飞行高度 = 地形高度 + 设定的飞行高度
- 始终保持与地面固定距离
- 适合低空摄影测量

**禁用时**:
- 飞行高度 = 固定的绝对高度
- 不跟随地形起伏
- 适合高空覆盖

### 路径参数

#### Coverage Width (覆盖宽度)
- 传感器的有效覆盖宽度
- 取决于飞行高度和相机视场角
- 越大则扫描线越少，效率越高

#### Overlap Rate (重叠率)
- 相邻扫描线的重叠比例
- 20% 重叠可确保无漏洞
- 高重叠率提高数据质量但增加飞行时间

---

## 显示说明

### Main Display Area

| 元素 | 颜色 | 说明 |
|------|------|------|
| 背景 | 彩色 | 高程数据，颜色表示高度 |
| 蓝色虚线框 | 蓝色 | 正在框选的区域 |
| 绿色实线框 | 绿色 | 已确认的区域 |
| 红色路径 | 红色 | 生成的覆盖路径 |
| 红色圆点 | 红色 | 路径航点 |

### Bottom Panel (距离-飞行高度图)

**图表说明**:
- **X 轴**: 累计飞行距离 (m)
- **Y 轴**: 飞行高度 (m)
- **蓝色曲线**: 飞行高度随距离的变化
- **浅蓝色填充**: 曲线下方区域

**用途**:
- 可视化飞行高度变化
- 检查是否有异常高度
- 评估仿地飞行效果

### Control Panel

#### Selected Region (选中区域后显示)
- **Width**: 区域宽度 (像素)
- **Height**: 区域高度 (像素)
- **Coordinates**: 区域坐标范围

#### Coverage Parameters (选中区域后显示)
- Flight Height: 飞行高度调节
- Coverage Width: 覆盖宽度调节
- Overlap Rate: 重叠率滑块
- Terrain Following: 仿地开关

#### Path Statistics (生成路径后显示)
- **Total Distance**: 总飞行距离
- **Lines**: 扫描线数量
- **Coverage**: 覆盖面积
- **Est. Time**: 预计飞行时间

---

## 快速操作指南

### 基本工作流

```
1. FILE → Open TIF File (导入高程图)
   ↓
2. 在 Main Display Area 框选区域
   ↓
3. 点击 Confirm 确认区域
   ↓
4. 调整 Coverage Parameters (可选)
   ↓
5. RUN → Full Coverage (生成路径)
   ↓
6. 查看路径和统计信息
```

### 快捷操作

- **VIEW 菜单**: 快速切换显示选项 (网格、比例尺等)
- **EDIT → Reset Settings**: 恢复默认设置
- **Clear Selection 按钮**: 清除选择重新框选

---

## 参数调优建议

### 低空详细测绘
```
Flight Height: 50 m
Coverage Width: 20 m
Overlap Rate: 30%
Terrain Following: ON
```

### 高空快速覆盖
```
Flight Height: 200 m
Coverage Width: 100 m
Overlap Rate: 10%
Terrain Following: OFF
```

### 山地仿地飞行
```
Flight Height: 80 m
Coverage Width: 40 m
Overlap Rate: 20%
Terrain Following: ON
Elevation Scale: 70-100 (查看地形起伏)
```

---

## 注意事项

1. **选择区域**: 建议选择矩形区域以获得最优路径
2. **覆盖宽度**: 应小于区域宽度，否则只会生成一条扫描线
3. **仿地飞行**: 在山区建议开启，平原可关闭
4. **重叠率**: 推荐 20%-30%，确保无盲区
5. **飞行高度**: 考虑地形最高点，避免碰撞

---

## 数据导出 (开发中)

未来将支持导出：
- 路径 KML 文件 (Google Earth)
- 路径 GPX 文件 (GPS 设备)
- 飞行剖面 CSV
- 高程图 PNG

---

## 技术细节

### 算法复杂度
- **时间复杂度**: O(n × m)，n 为宽度，m 为扫描线数
- **空间复杂度**: O(k)，k 为路径点数

### 性能
- 适用于 1000×1000 以下的区域选择
- 大区域 (>2000×2000) 可能需要几秒生成时间

### 坐标系统
- 使用像素坐标系
- 比例尺根据 TIF 文件元数据计算

---

## 常见问题

**Q: 为什么点击 RUN 没反应？**
A: 确保已导入 TIF 文件并框选了区域。

**Q: 路径生成太慢？**
A: 减小选择区域或增大覆盖宽度。

**Q: 飞行高度图不显示？**
A: 底部 Panel 需要先生成路径才会显示。

**Q: 如何重新选择区域？**
A: 点击 Main Display Area 右上角的 "Clear Selection" 按钮。

---

**更新日期**: 2026-03-12
**版本**: 1.0.0
