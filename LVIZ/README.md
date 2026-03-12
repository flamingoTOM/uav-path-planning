# LVIZ 可视化平台

基于 Momenta 品牌设计系统的 DSM 高程图可视化平台。

## 功能特性

- ✨ **可拖拽布局**：支持自由调整各模块大小和位置
- 📊 **3D 可视化**：基于 Three.js 和 React Three Fiber 的高性能 3D 渲染
- 🗺️ **DSM 高程图支持**：支持导入 .tif/.tiff 格式的高程图文件
- 🎨 **Momenta 品牌设计**：遵循 Momenta 视觉规范和色彩系统
- 📐 **固定比例俯视图**：2D 俯视图保持正确的地理比例
- ⚙️ **实时参数调节**：支持渲染质量、视场角、色彩映射等参数实时调整
- 💾 **多格式导出**：支持导出 PNG、GLB、STL 等多种格式

## 布局结构

```
[ 1 - 3D信息 ][    4 - 中央视图    ][ 5 - 控制面板 ]
[ 2 - 俯视图 ][    4 - 中央视图    ][ 5 - 控制面板 ]
[     3 - 预留区域              ][ 5 - 控制面板 ]
```

### 区域说明

1. **区域 1 - 3D 信息面板**：显示高程范围、网格信息、中心坐标等实时数据
2. **区域 2 - 俯视图**：固定比例的 2D 俯视图，带坐标网格
3. **区域 3 - 预留区域**：可扩展功能模块
4. **区域 4 - 中央视图**：主 3D 渲染视图，支持交互操作
5. **区域 5 - 控制面板**：文件管理、渲染质量、可视化选项、色彩映射等控制

## 技术栈

- **框架**：React 18 + TypeScript
- **UI 组件**：Ant Design 5.x
- **3D 渲染**：Three.js + React Three Fiber + Drei
- **布局**：React Grid Layout
- **构建工具**：Vite
- **地理数据**：GeoTIFF

## 快速开始

### 安装依赖

```bash
npm install
# 或
yarn install
```

### 启动开发服务器

```bash
npm run dev
# 或
yarn dev
```

访问 `http://localhost:3000` 查看应用。

### 构建生产版本

```bash
npm run build
# 或
yarn build
```

构建产物位于 `dist/` 目录。

### 预览生产构建

```bash
npm run preview
# 或
yarn preview
```

## 使用指南

### 导入高程图

1. 点击右侧控制面板的 **"导入 .TIF 高程图"** 按钮
2. 选择 `.tif` 或 `.tiff` 格式的 DSM 高程图文件
3. 文件上传成功后，3D 视图和俯视图会自动更新

### 调整渲染质量

在控制面板的 **"渲染质量"** 部分：

- **质量预设**：选择低/中/高/超高质量预设
- **像素比例**：调整渲染分辨率 (0.5x - 3x)
- **视场角 (FOV)**：调整相机视野范围 (30° - 90°)

### 可视化选项

- **线框模式**：切换显示网格线框
- **阴影**：启用/禁用阴影渲染
- **抗锯齿**：启用/禁用抗锯齿效果

### 色彩映射

选择不同的颜色方案来可视化高程数据：

- **地形**：适合地形可视化的自然色彩
- **热力图**：红黄蓝渐变，突出高程差异
- **灰度**：单色灰度映射
- **彩虹**：全光谱彩虹色

可自定义最小值和最大值范围。

### 导出数据

支持导出以下格式：

- **PNG**：导出当前 3D 视图的截图
- **GLB**：导出 3D 模型（GLB 格式）
- **STL**：导出 3D 模型（STL 格式，适合 3D 打印）

### 拖拽调整布局

- **拖动标题栏**：移动模块位置
- **拖动右下角手柄**：调整模块大小
- 所有模块支持自由布局，不会重叠

## 项目结构

```
LVIZ/
├── public/
│   ├── index.html          # HTML 模板
│   └── favicon.ico         # Momenta favicon
├── src/
│   ├── assets/             # 静态资源
│   ├── components/         # React 组件
│   │   ├── Info3DPanel.tsx       # 3D 信息面板
│   │   ├── TopViewPanel.tsx      # 俯视图面板
│   │   ├── CenterPanel.tsx       # 中央 3D 视图
│   │   ├── ControlPanel.tsx      # 控制面板
│   │   └── ReservedPanel.tsx     # 预留面板
│   ├── styles/             # 样式文件
│   │   └── index.css       # 全局样式
│   ├── App.tsx             # 主应用组件
│   ├── main.tsx            # 应用入口
│   └── theme.ts            # Momenta 主题配置
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## Momenta 品牌规范

本项目严格遵循 Momenta 品牌设计规范：

### 主要颜色

- **Momenta Blue**: `#0066FF` - 主品牌色
- **Tech Black**: `#1A1A2E` - 主文本色
- **Success Green**: `#00C853` - 成功/在线状态
- **Warning Yellow**: `#FFB800` - 警告状态
- **Error Red**: `#FF3B3B` - 错误状态

### 字体

- **主字体**: Inter
- **代码字体**: JetBrains Mono

### 设计原则

- **智能 (Intelligent)**: 技术驱动的美学
- **可信赖 (Trustworthy)**: 稳定可靠的专业外观
- **前瞻性 (Forward-thinking)**: 创新的尖端技术感
- **专业 (Professional)**: 企业级精致界面

## 开发注意事项

### 添加新组件

1. 在 `src/components/` 目录创建新组件
2. 使用 Ant Design 组件和 Momenta 主题 tokens
3. 通过 `theme.useToken()` 获取主题变量
4. 遵循 Momenta 色彩和排版规范

### 集成 GeoTIFF

使用 `geotiff` 库解析 .tif 文件：

```typescript
import { fromFile } from 'geotiff';

const tiff = await fromFile(file);
const image = await tiff.getImage();
const data = await image.readRasters();
```

### 性能优化

- 使用 `React.memo` 优化组件渲染
- 3D 场景使用 `Suspense` 懒加载
- 大数据集使用 Web Workers 处理
- 根据设备性能动态调整渲染质量

## 浏览器支持

- Chrome/Edge >= 90
- Firefox >= 88
- Safari >= 14
- 需要支持 WebGL 2.0

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系 Momenta 团队。
