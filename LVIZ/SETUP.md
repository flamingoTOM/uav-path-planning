# LVIZ 可视化平台 - 快速配置指南

## 📦 安装步骤

### 1. 进入项目目录

```bash
cd LVIZ
```

### 2. 安装依赖

使用 npm:
```bash
npm install
```

或使用 yarn:
```bash
yarn install
```

或使用 pnpm:
```bash
pnpm install
```

### 3. 启动开发服务器

```bash
npm run dev
```

服务器将在 `http://localhost:3000` 启动，浏览器会自动打开。

## 🎨 项目特性

### ✅ 已实现功能

- [x] 可拖拽的网格布局系统
- [x] Momenta 品牌主题（亮色模式）
- [x] 5 个功能面板（3D 信息、俯视图、预留区域、中央 3D 视图、控制面板）
- [x] 3D 场景渲染（Three.js + React Three Fiber）
- [x] 文件上传接口（支持 .tif 文件）
- [x] 渲染质量控制
- [x] 可视化选项（线框、阴影、抗锯齿）
- [x] 色彩映射设置
- [x] 导出功能按钮（PNG/GLB/STL）
- [x] 响应式布局
- [x] Momenta Logo (SVG)

### 🚧 待实现功能

#### 高优先级
- [ ] GeoTIFF 文件解析和加载
- [ ] 3D 地形网格生成（基于高程数据）
- [ ] 俯视图的实际高程数据渲染
- [ ] 深色模式主题切换功能连接
- [ ] 实际的导出功能实现

#### 中优先级
- [ ] 3D 信息面板的数据绑定
- [ ] 色彩映射的实际应用
- [ ] 渲染质量设置的实时生效
- [ ] 视图重置功能
- [ ] 相机位置和角度的保存/恢复

#### 低优先级
- [ ] 多文件管理
- [ ] 历史记录功能
- [ ] 测量工具（距离、面积）
- [ ] 截面分析工具
- [ ] 数据统计面板

## 🔧 核心技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18.2.0 | UI 框架 |
| TypeScript | 5.3.3 | 类型系统 |
| Ant Design | 5.12.0 | UI 组件库 |
| Three.js | 0.160.0 | 3D 渲染引擎 |
| @react-three/fiber | 8.15.0 | React Three.js 封装 |
| @react-three/drei | 9.92.0 | Three.js 辅助组件 |
| react-grid-layout | 1.4.4 | 可拖拽布局 |
| geotiff | 2.0.7 | GeoTIFF 解析 |
| Vite | 5.0.8 | 构建工具 |

## 📂 项目结构说明

```
LVIZ/
├── public/                 # 静态资源
│   └── logo.svg           # Momenta Logo (favicon)
├── src/
│   ├── assets/            # 源代码资源
│   │   └── logo.svg       # Momenta Logo (UI 使用)
│   ├── components/        # React 组件
│   │   ├── Info3DPanel.tsx       # 左上：3D 信息面板
│   │   ├── TopViewPanel.tsx      # 左中：俯视图面板
│   │   ├── ReservedPanel.tsx     # 左下：预留面板
│   │   ├── CenterPanel.tsx       # 中央：3D 视图面板
│   │   └── ControlPanel.tsx      # 右侧：控制面板
│   ├── styles/
│   │   └── index.css      # 全局样式和布局样式
│   ├── App.tsx            # 主应用组件
│   ├── main.tsx           # 入口文件
│   └── theme.ts           # Momenta 主题配置
├── index.html             # HTML 模板
├── vite.config.ts         # Vite 配置
├── tsconfig.json          # TypeScript 配置
├── package.json           # 依赖管理
├── README.md              # 项目文档
└── SETUP.md               # 本文件 - 配置指南
```

## 🎯 下一步开发建议

### 1. 实现 GeoTIFF 加载 (高优先级)

在 `src/components/ControlPanel.tsx` 中实现实际的 TIF 文件解析：

```typescript
import { fromBlob } from 'geotiff';

const handleFileUpload = async (file: File) => {
  const tiff = await fromBlob(file);
  const image = await tiff.getImage();
  const rasters = await image.readRasters();
  const width = image.getWidth();
  const height = image.getHeight();

  // 将高程数据传递给 3D 视图
  onTerrainDataLoaded({
    width,
    height,
    elevationData: rasters[0], // 第一个波段是高程数据
  });
};
```

### 2. 生成 3D 地形网格

在 `src/components/CenterPanel.tsx` 中根据高程数据生成地形：

```typescript
const generateTerrainGeometry = (width: number, height: number, elevationData: Float32Array) => {
  const geometry = new THREE.PlaneGeometry(
    width,
    height,
    width - 1,
    height - 1
  );

  const vertices = geometry.attributes.position.array;
  for (let i = 0; i < elevationData.length; i++) {
    vertices[i * 3 + 2] = elevationData[i]; // Z 坐标 = 高程
  }

  geometry.computeVertexNormals();
  return geometry;
};
```

### 3. 实现深色模式切换

在 `App.tsx` 中使用 `ConfigProvider` 切换主题：

```typescript
import { ConfigProvider } from 'antd';
import { momentaLightTheme, momentaDarkTheme } from './theme';

<ConfigProvider theme={isDarkMode ? momentaDarkTheme : momentaLightTheme}>
  {/* 应用内容 */}
</ConfigProvider>
```

### 4. 连接渲染设置

将 `ControlPanel` 中的设置传递给 `CenterPanel`：

```typescript
// 在 App.tsx 中管理状态
const [renderSettings, setRenderSettings] = useState<RenderSettings>({...});

// 传递给子组件
<ControlPanel onSettingsChange={setRenderSettings} />
<CenterPanel settings={renderSettings} />
```

## 🐛 已知问题

1. **深色模式切换无效**: Switch 组件未连接到 ConfigProvider
2. **导出按钮无功能**: 需要实现截图和模型导出逻辑
3. **渲染设置未生效**: ControlPanel 的设置未传递到 3D 场景
4. **示例数据**: 当前使用占位数据，需要连接实际的 GeoTIFF 数据

## 📚 相关文档

- [Ant Design 文档](https://ant.design/)
- [React Three Fiber 文档](https://docs.pmnd.rs/react-three-fiber)
- [Three.js 文档](https://threejs.org/docs/)
- [GeoTIFF.js 文档](https://geotiffjs.github.io/)
- [React Grid Layout 文档](https://github.com/react-grid-layout/react-grid-layout)

## 💡 提示

### 性能优化

- 对于大型 GeoTIFF 文件，考虑使用 Web Workers 进行解析
- 实现 LOD (Level of Detail) 以优化大地形的渲染
- 使用 React.memo 和 useMemo 优化组件渲染
- 启用 Three.js 的 frustum culling 和 occlusion culling

### 调试技巧

- 使用 `<Stats />` 组件监控 FPS
- 在 Chrome DevTools 中使用 Performance 面板分析性能
- 使用 `console.time()` 和 `console.timeEnd()` 测量代码执行时间
- 启用 React DevTools Profiler 分析组件渲染

### 样式定制

所有 Momenta 品牌色彩和样式都在 `src/theme.ts` 中定义，修改时请遵循 Momenta 设计规范。

## ✨ 特别说明

这个项目已经搭建好了完整的架构和 UI 框架，使用了 Momenta 官方的品牌设计系统。核心的数据处理和 3D 渲染逻辑需要根据实际的 DSM 数据格式进行定制开发。

祝开发顺利！🚀
