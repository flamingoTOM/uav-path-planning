import React, { useState, useRef } from 'react';
import {
  Layout, Typography, Dropdown, MenuProps, message, Modal,
  Form, InputNumber, Spin, Descriptions, Divider, Space, Select,
  Input, Collapse, Button, Tag,
} from 'antd';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { AimOutlined, CodeOutlined, DownloadOutlined } from '@ant-design/icons';
import TopViewPanel from './components/TopViewPanel';
import CenterPanel from './components/CenterPanel';
import ControlPanel from './components/ControlPanel';
import MainDisplayArea from './components/MainDisplayArea';
import BottomChartPanel from './components/BottomChartPanel';
import ExportModal from './components/ExportModal';
import { ErrorBoundary } from './components/ErrorBoundary';
import { fromBlob } from 'geotiff';
import { generateCoveragePath, CoverageParams } from './utils/coveragePlanner';
import logoSrc from './assets/logo.svg';

const { Header } = Layout;
const { Title, Text } = Typography;

export interface TerrainSettings {
  exaggeration: number;
  colorScheme: 'terrain' | 'heatmap' | 'grayscale' | 'rainbow' | 'viridis';
  showGrid: boolean;
  showScale: boolean;
  showCompass: boolean;
  showContours: boolean;
}

export interface RenderQuality {
  pixelRatio: number;
  antialias: boolean;
  shadows: boolean;
}

interface PolygonInfo {
  points: { x: number; y: number }[];
  canvasW: number;
  canvasH: number;
  areaMsq: number;
  perimeter: number;
  vertexCount: number;
}

// 'preselect'：点击运行后先弹"选择区域"引导步骤
type CoverageWorkflow = 'idle' | 'preselect' | 'draw' | 'calculating' | 'params' | 'planning' | 'done';

function calcPolygonInfo(
  pts: { x: number; y: number }[],
  canvasW: number,
  canvasH: number,
  terrainData: any
): Omit<PolygonInfo, 'points' | 'canvasW' | 'canvasH'> {
  if (!terrainData || pts.length < 3) return { areaMsq: 0, perimeter: 0, vertexCount: pts.length };
  const sx = terrainData.width / canvasW, sy = terrainData.height / canvasH;
  let area = 0, perimeter = 0;
  const n = pts.length;
  for (let i = 0; i < n; i++) {
    const j = (i + 1) % n;
    const xi = pts[i].x * sx, yi = pts[i].y * sy;
    const xj = pts[j].x * sx, yj = pts[j].y * sy;
    area += xi * yj - xj * yi;
    perimeter += Math.sqrt((xj - xi) ** 2 + (yj - yi) ** 2);
  }
  return { areaMsq: Math.abs(area) / 2, perimeter, vertexCount: n };
}

function fmtArea(m2: number) {
  if (m2 >= 1_000_000) return (m2 / 1_000_000).toFixed(4) + ' km²';
  if (m2 >= 10_000) return (m2 / 10_000).toFixed(2) + ' hm²';
  return m2.toFixed(1) + ' m²';
}
function fmtDist(m: number) {
  return m >= 1000 ? (m / 1000).toFixed(2) + ' km' : m.toFixed(1) + ' m';
}

const DEFAULT_PARAMS: CoverageParams = {
  minAltitude: 50, coverageWidth: 50, overlapRate: 0.2, terrainFollowing: true,
};

// 自定义算法接口说明（Python）
const CUSTOM_API_DOC = `def generate_path(terrain_data, polygon, params) -> dict:
    """
    terrain_data: {
      elevation: np.ndarray,  # (height, width)
      width: int, height: int,
      min_elevation: float, max_elevation: float
    }
    polygon: [(x, y), ...]   # 地形坐标
    params: {
      min_altitude: float,   # 防地高度(m)
      coverage_width: float, # 覆盖宽度(m)
      overlap_rate: float    # 重叠率(0-1)
    }
    return: {
      path: [{"x","y","altitude","distance"}, ...],
      statistics: {"total_distance","total_lines",
                   "coverage_area_m2","waypoint_count",...}
    }
    """`;

const App: React.FC = () => {
  const [terrainData, setTerrainData] = useState<any>(null);
  const [terrainSettings, setTerrainSettings] = useState<TerrainSettings>({
    exaggeration: 70, colorScheme: 'terrain',
    showGrid: true, showScale: true, showCompass: true, showContours: true,
  });
  const [renderQuality, setRenderQuality] = useState<RenderQuality>({
    pixelRatio: 0.5, antialias: false, shadows: false,
  });
  const [pathData, setPathData] = useState<any>(null);
  const [coverageParams, setCoverageParams] = useState<CoverageParams>(DEFAULT_PARAMS);

  // 覆盖规划工作流
  const [coverageWorkflow, setCoverageWorkflow] = useState<CoverageWorkflow>('idle');
  const [polygonInfo, setPolygonInfo] = useState<PolygonInfo | null>(null);
  const [modalParams, setModalParams] = useState<CoverageParams>(DEFAULT_PARAMS);
  const [modalAlgorithm, setModalAlgorithm] = useState<string>('boustrophedon');
  const [customScriptPath, setCustomScriptPath] = useState<string>('');

  // 导出弹窗
  const [showExport, setShowExport] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // ── 地形加载 ────────────────────────────────────────────────────────────────
  const handleFileSelect = async (file: File) => {
    message.loading({ content: '正在解析 TIF 文件…', key: 'tif', duration: 0 });
    try {
      const tiff = await fromBlob(file);
      const image = await tiff.getImage();
      const rasters = await image.readRasters();
      const width = image.getWidth(), height = image.getHeight();
      const elevationData = rasters[0] as Float32Array;
      let minElevation = Infinity, maxElevation = -Infinity;
      for (let i = 0; i < elevationData.length; i++) {
        const v = elevationData[i];
        if (!isNaN(v)) { if (v < minElevation) minElevation = v; if (v > maxElevation) maxElevation = v; }
      }
      setTerrainData({ width, height, elevationData, minElevation, maxElevation, fileName: file.name });
      setPathData(null); setPolygonInfo(null); setCoverageWorkflow('idle');
      message.success({ content: `已加载 ${file.name}（${width}×${height}）`, key: 'tif', duration: 3 });
    } catch (err) {
      message.error({ content: `解析失败：${err instanceof Error ? err.message : '未知错误'}`, key: 'tif', duration: 5 });
    }
  };

  // ── 设置 ────────────────────────────────────────────────────────────────────
  const handleSettingsChange = (s: Partial<TerrainSettings>) =>
    setTerrainSettings(p => ({ ...p, ...s }));
  const handleRenderQualityChange = (q: Partial<RenderQuality>) =>
    setRenderQuality(p => ({ ...p, ...q }));
  const handleCoverageParamsChange = (p: Partial<CoverageParams>) =>
    setCoverageParams(prev => ({ ...prev, ...p }));

  // ── 覆盖工作流 ──────────────────────────────────────────────────────────────

  /** Step 1: RUN → 全覆盖 → 弹出"选择区域"引导 */
  const handleRunFullCoverage = () => {
    if (!terrainData) { message.warning('请先导入 TIF 地形文件'); return; }
    setPolygonInfo(null); setPathData(null);
    setCoverageWorkflow('preselect');
  };

  /** Step 2: 用户确认后进入多边形绘制 */
  const handleStartDraw = () => setCoverageWorkflow('draw');

  /** Step 3: 多边形绘制完成 */
  const handlePolygonConfirmed = (pts: { x: number; y: number }[], cW: number, cH: number) => {
    setCoverageWorkflow('calculating');
    setTimeout(() => {
      const info = calcPolygonInfo(pts, cW, cH, terrainData);
      setPolygonInfo({ points: pts, canvasW: cW, canvasH: cH, ...info });
      setModalParams({ ...coverageParams, terrainFollowing: true });
      setCoverageWorkflow('params');
    }, 600);
  };

  const handlePolygonClear = () => setPolygonInfo(null);

  /** Step 4: 参数确认 → 开始规划 */
  const handleParamsConfirm = () => {
    if (!polygonInfo) return;
    setCoverageParams(modalParams);
    setCoverageWorkflow('planning');

    if (modalAlgorithm === 'custom') {
      // 调用 Python 自定义算法
      runCustomAlgorithm();
    } else {
      // 内置算法（TypeScript）
      setTimeout(() => {
        try {
          const result = generateCoveragePath(
            terrainData, polygonInfo.points, polygonInfo.canvasW, polygonInfo.canvasH, modalParams
          );
          setPathData(result);
          setCoverageWorkflow('done');
          message.success(
            `规划完成！${result.statistics.totalLines} 条航线，` +
            `${result.statistics.waypointCount} 个航点，` +
            `总航程 ${result.statistics.totalDistance.toFixed(0)} m`
          );
        } catch (err) {
          message.error(`规划失败：${err instanceof Error ? err.message : '未知错误'}`);
          setCoverageWorkflow('params');
        }
      }, 120);
    }
  };

  const runCustomAlgorithm = async () => {
    if (!polygonInfo) return;
    try {
      // 降采样
      const { width: dW, height: dH, elevationData, minElevation, maxElevation } = terrainData;
      const stepX = Math.max(1, Math.ceil(dW / 100));
      const stepY = Math.max(1, Math.ceil(dH / 100));
      const sampledW = Math.ceil(dW / stepX), sampledH = Math.ceil(dH / stepY);
      const sampled: number[] = [];
      for (let y = 0; y < dH; y += stepY)
        for (let x = 0; x < dW; x += stepX) {
          const v = elevationData[y * dW + x];
          sampled.push(isFinite(v) ? v : minElevation);
        }

      // 将 canvas polygon 坐标转为地形坐标
      const polygon = polygonInfo.points.map(p => [
        (p.x / polygonInfo.canvasW) * dW * (1 / (dW / sampledW)),
        (p.y / polygonInfo.canvasH) * dH * (1 / (dH / sampledH)),
      ]);

      const res = await fetch('/run-custom', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scriptPath: customScriptPath,
          width: sampledW, height: sampledH,
          elevationData: sampled,
          minElevation, maxElevation,
          polygon,
          params: {
            minAltitude: modalParams.minAltitude,
            coverageWidth: modalParams.coverageWidth,
            overlapRate: modalParams.overlapRate,
          },
        }),
      });

      const json = await res.json();
      if (json.error) throw new Error(json.error);

      // 将 Python 返回结果适配为前端格式
      const result = {
        path: json.path ?? [],
        altitudeProfile: {
          distances: (json.path ?? []).map((p: any) => p.distance),
          altitudes:  (json.path ?? []).map((p: any) => p.altitude),
          minAlt: Math.min(...(json.path ?? []).map((p: any) => p.altitude)),
          maxAlt: Math.max(...(json.path ?? []).map((p: any) => p.altitude)),
        },
        statistics: {
          totalDistance:   json.statistics?.total_distance   ?? 0,
          totalLines:      json.statistics?.total_lines      ?? 0,
          coverageAreaM2:  json.statistics?.coverage_area_m2 ?? 0,
          estimatedTime:   json.statistics?.estimated_time   ?? 0,
          waypointCount:   json.statistics?.waypoint_count   ?? 0,
          lineSpacing:     json.statistics?.line_spacing      ?? 0,
          planMinAlt:      json.statistics?.plan_min_alt     ?? 0,
          planMaxAlt:      json.statistics?.plan_max_alt     ?? 0,
        },
      };

      setPathData(result);
      setCoverageWorkflow('done');
      message.success(
        `自定义算法规划完成！${result.statistics.totalLines} 条航线，` +
        `${result.statistics.waypointCount} 个航点`
      );
    } catch (err: any) {
      message.error(`自定义算法执行失败：${err.message}`);
      setCoverageWorkflow('params');
    }
  };

  const handleCoverageCancel = () => { setCoverageWorkflow('idle'); setPolygonInfo(null); };

  // ── 菜单 ────────────────────────────────────────────────────────────────────

  const fileMenuItems: MenuProps['items'] = [
    { key: 'open', label: '打开 TIF 文件', onClick: () => fileInputRef.current?.click() },
    { type: 'divider' },
    {
      key: 'export',
      label: (
        <span>
          <DownloadOutlined style={{ marginRight: 6 }} />
          导出为…
        </span>
      ),
      onClick: () => setShowExport(true),
    },
  ];

  const editMenuItems: MenuProps['items'] = [{
    key: 'reset', label: '重置设置',
    onClick: () => {
      handleSettingsChange({ exaggeration: 70, colorScheme: 'terrain', showGrid: true, showScale: true, showCompass: true, showContours: true });
      handleRenderQualityChange({ pixelRatio: 0.5, antialias: false, shadows: false });
      message.success('已重置为默认设置');
    },
  }];

  const viewMenuItems: MenuProps['items'] = [
    { key: 'grid',    label: terrainSettings.showGrid    ? '✓ 显示网格'   : '显示网格',   onClick: () => handleSettingsChange({ showGrid:    !terrainSettings.showGrid    }) },
    { key: 'scale',   label: terrainSettings.showScale   ? '✓ 显示比例尺' : '显示比例尺', onClick: () => handleSettingsChange({ showScale:   !terrainSettings.showScale   }) },
    { key: 'compass', label: terrainSettings.showCompass ? '✓ 显示指北针' : '显示指北针', onClick: () => handleSettingsChange({ showCompass: !terrainSettings.showCompass }) },
    { key: 'contours',label: terrainSettings.showContours? '✓ 显示等高线' : '显示等高线', onClick: () => handleSettingsChange({ showContours:!terrainSettings.showContours}) },
    { type: 'divider' },
    { key: 'shadows',  label: renderQuality.shadows  ? '✓ 启用阴影'   : '启用阴影',   onClick: () => handleRenderQualityChange({ shadows:  !renderQuality.shadows  }) },
    { key: 'antialias',label: renderQuality.antialias ? '✓ 启用抗锯齿' : '启用抗锯齿', onClick: () => handleRenderQualityChange({ antialias: !renderQuality.antialias }) },
  ];

  const runMenuItems: MenuProps['items'] = [
    { key: 'full-coverage', label: '全覆盖', onClick: handleRunFullCoverage },
    { key: 'octree', label: '八叉树规划', onClick: () => message.info('八叉树规划（开发中）') },
  ];

  // ── 样式 ────────────────────────────────────────────────────────────────────
  const menuStyle: React.CSSProperties = {
    padding: '0 12px', height: '40px', lineHeight: '40px',
    cursor: 'pointer', transition: 'background 0.2s', fontSize: '13px',
  };
  const resH: React.CSSProperties = { height: '4px', background: '#D0D0D0', cursor: 'row-resize' };
  const resV: React.CSSProperties = { width:  '4px', background: '#D0D0D0', cursor: 'col-resize' };
  const hov = (e: React.MouseEvent<HTMLSpanElement>, on: boolean) => {
    e.currentTarget.style.background = on ? '#E8E8E8' : 'transparent';
  };

  // ── JSX ─────────────────────────────────────────────────────────────────────
  return (
    <Layout style={{ height: '100vh', background: '#F0F0F0', display: 'flex', flexDirection: 'column' }}>

      {/* 顶部菜单栏 */}
      <Header style={{
        background: '#FFFFFF', padding: '0 16px', borderBottom: '1px solid #D0D0D0',
        display: 'flex', alignItems: 'center', height: '40px', flexShrink: 0, zIndex: 1000,
      }}>
        <img src={logoSrc} alt="Logo" style={{ width: 28, height: 28, marginRight: 12 }} />
        <Title level={5} style={{ margin: 0, color: '#333', fontSize: '14px', fontWeight: 600, marginRight: 24 }}>
          LVIZ 可视化平台
        </Title>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          {(
            [['文件', fileMenuItems], ['编辑', editMenuItems], ['视图', viewMenuItems], ['运行', runMenuItems]] as const
          ).map(([label, items]) => (
            <Dropdown key={label} menu={{ items: items as MenuProps['items'] }} trigger={['click']}>
              <span style={menuStyle} onMouseEnter={e => hov(e, true)} onMouseLeave={e => hov(e, false)}>
                {label}
              </span>
            </Dropdown>
          ))}
        </div>
        <input ref={fileInputRef} type="file" accept=".tif,.tiff,.geotiff" style={{ display: 'none' }}
          onChange={e => { const f = e.target.files?.[0]; if (f) { handleFileSelect(f); e.target.value = ''; } }} />
      </Header>

      {/* 主布局 */}
      <div style={{ flex: 1, overflow: 'hidden' }}>
        <PanelGroup direction="horizontal">

          {/* 左侧：3D + 俯视 */}
          <Panel defaultSize={25} minSize={15} maxSize={40}>
            <PanelGroup direction="vertical">
              <Panel defaultSize={50} minSize={20}>
                <CenterPanel
                  terrainData={terrainData}
                  title="3D 视图"
                  exaggeration={terrainSettings.exaggeration}
                  colorScheme={terrainSettings.colorScheme}
                  renderQuality={renderQuality}
                  onColorSchemeChange={s => handleSettingsChange({ colorScheme: s as TerrainSettings['colorScheme'] })}
                />
              </Panel>
              <PanelResizeHandle style={resH}
                onMouseEnter={e => { e.currentTarget.style.background = '#888'; }}
                onMouseLeave={e => { e.currentTarget.style.background = '#D0D0D0'; }} />
              <Panel defaultSize={50} minSize={20}>
                <TopViewPanel terrainData={terrainData} settings={terrainSettings} onSettingsChange={handleSettingsChange} />
              </Panel>
            </PanelGroup>
          </Panel>

          <PanelResizeHandle style={resV}
            onMouseEnter={e => { e.currentTarget.style.background = '#888'; }}
            onMouseLeave={e => { e.currentTarget.style.background = '#D0D0D0'; }} />

          {/* 中间：主视图 + 剖面 */}
          <Panel defaultSize={50} minSize={30}>
            <PanelGroup direction="vertical">
              <Panel defaultSize={75} minSize={40}>
                <MainDisplayArea
                  terrainData={terrainData}
                  settings={terrainSettings}
                  pathData={pathData}
                  drawPolygonMode={coverageWorkflow === 'draw'}
                  confirmedPolygon={
                    ['params', 'planning', 'done'].includes(coverageWorkflow) ? polygonInfo?.points : undefined
                  }
                  onPolygonConfirmed={handlePolygonConfirmed}
                  onPolygonClear={handlePolygonClear}
                />
              </Panel>
              <PanelResizeHandle style={resH}
                onMouseEnter={e => { e.currentTarget.style.background = '#888'; }}
                onMouseLeave={e => { e.currentTarget.style.background = '#D0D0D0'; }} />
              <Panel defaultSize={25} minSize={10}>
                <BottomChartPanel pathData={pathData} />
              </Panel>
            </PanelGroup>
          </Panel>

          <PanelResizeHandle style={resV}
            onMouseEnter={e => { e.currentTarget.style.background = '#888'; }}
            onMouseLeave={e => { e.currentTarget.style.background = '#D0D0D0'; }} />

          {/* 右侧：控制面板 */}
          <Panel defaultSize={25} minSize={20} maxSize={40}>
            <ControlPanel
              onSettingsChange={handleSettingsChange}
              onRenderQualityChange={handleRenderQualityChange}
              currentSettings={terrainSettings}
              currentRenderQuality={renderQuality}
              selectedRegion={null}
              coverageParams={coverageParams}
              onCoverageParamsChange={handleCoverageParamsChange}
              pathData={pathData}
            />
          </Panel>
        </PanelGroup>
      </div>

      {/* ── 导出弹窗 ────────────────────────────────────────────────────────── */}
      <ExportModal open={showExport} onClose={() => setShowExport(false)} />

      {/* ── 选择区域引导 Modal ──────────────────────────────────────────────── */}
      <Modal
        title={<><AimOutlined style={{ marginRight: 8 }} />选择规划区域</>}
        open={coverageWorkflow === 'preselect'}
        onCancel={handleCoverageCancel}
        footer={
          <Space>
            <Button onClick={handleCoverageCancel}>取消</Button>
            <Button type="primary" icon={<AimOutlined />} onClick={handleStartDraw}>
              开始绘制区域
            </Button>
          </Space>
        }
        width={420}
        maskClosable={false}
      >
        <Space direction="vertical" size={12} style={{ width: '100%' }}>
          <Text>请在 <Text strong>主视图</Text> 中绘制飞行任务区域多边形：</Text>
          <ul style={{ paddingLeft: 20, margin: 0, color: '#555', fontSize: 13 }}>
            <li>左键单击添加顶点</li>
            <li>点击起点（红色点）或已有 3 个顶点后自动闭合</li>
            <li>拖拽顶点可调整位置</li>
            <li>右键 / ESC 清除重新绘制</li>
          </ul>
          <Text type="secondary" style={{ fontSize: 12 }}>
            完成后点击主视图顶部「确认区域」按钮进入下一步。
          </Text>
        </Space>
      </Modal>

      {/* ── 正在计算 ────────────────────────────────────────────────────────── */}
      <Modal title="处理中" open={coverageWorkflow === 'calculating'}
        footer={null} closable={false} maskClosable={false} width={300} centered>
        <div style={{ textAlign: 'center', padding: '24px 0' }}>
          <Spin size="large" />
          <div style={{ marginTop: 14, color: '#555', fontSize: 14 }}>正在计算区域信息…</div>
        </div>
      </Modal>

      {/* ── 规划参数 Modal ───────────────────────────────────────────────────── */}
      <Modal
        title="全覆盖规划配置"
        open={coverageWorkflow === 'params'}
        onOk={handleParamsConfirm}
        onCancel={handleCoverageCancel}
        okText="开始规划"
        cancelText="取消"
        width={520}
        maskClosable={false}
      >
        {polygonInfo && (
          <>
            {/* 区域信息 */}
            <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 8, color: '#333' }}>区域信息</div>
            <Descriptions size="small" bordered column={2}>
              <Descriptions.Item label="顶点数">{polygonInfo.vertexCount} 个</Descriptions.Item>
              <Descriptions.Item label="覆盖面积">{fmtArea(polygonInfo.areaMsq)}</Descriptions.Item>
              <Descriptions.Item label="周长" span={2}>{fmtDist(polygonInfo.perimeter)}</Descriptions.Item>
            </Descriptions>

            <Divider style={{ margin: '16px 0' }} />

            {/* 规划参数 */}
            <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 12, color: '#333' }}>规划参数</div>
            <Form layout="vertical" size="small">
              <Space direction="vertical" size={2} style={{ width: '100%' }}>

                <Form.Item label="防地高度" style={{ marginBottom: 8 }}>
                  <InputNumber min={10} max={500} value={modalParams.minAltitude}
                    onChange={v => setModalParams(p => ({ ...p, minAltitude: v ?? 50 }))}
                    style={{ width: '100%' }} addonAfter="m" />
                </Form.Item>

                <Form.Item label="覆盖宽度" style={{ marginBottom: 8 }}>
                  <InputNumber min={5} max={500} value={modalParams.coverageWidth}
                    onChange={v => setModalParams(p => ({ ...p, coverageWidth: v ?? 50 }))}
                    style={{ width: '100%' }} addonAfter="m" />
                </Form.Item>

                <Form.Item label="重叠率" style={{ marginBottom: 8 }}>
                  <InputNumber min={0} max={80}
                    value={Math.round(modalParams.overlapRate * 100)}
                    onChange={v => setModalParams(p => ({ ...p, overlapRate: (v ?? 20) / 100 }))}
                    style={{ width: '100%' }} addonAfter="%" />
                </Form.Item>

                <Form.Item label="规划算法" style={{ marginBottom: modalAlgorithm === 'custom' ? 8 : 4 }}>
                  <Select
                    value={modalAlgorithm}
                    onChange={setModalAlgorithm}
                    style={{ width: '100%' }}
                    options={[
                      { value: 'boustrophedon', label: '牛耕式（Boustrophedon）' },
                      { value: 'custom', label: <span><CodeOutlined style={{ marginRight: 6 }} />自定义算法（Python）</span> },
                    ]}
                  />
                </Form.Item>

                {/* 自定义算法配置区 */}
                {modalAlgorithm === 'custom' && (
                  <div style={{ background: '#F8F9FA', border: '1px solid #E8E8E8', borderRadius: 4, padding: '10px 12px' }}>
                    <Form.Item
                      label={<Space><CodeOutlined />Python 脚本路径</Space>}
                      style={{ marginBottom: 8 }}
                    >
                      <Input
                        placeholder="例：C:/my_algorithm.py"
                        value={customScriptPath}
                        onChange={e => setCustomScriptPath(e.target.value)}
                      />
                    </Form.Item>

                    <Collapse ghost size="small" items={[{
                      key: 'api',
                      label: <Text style={{ fontSize: 12 }}><CodeOutlined style={{ marginRight: 6 }} />接口规范（展开查看）</Text>,
                      children: (
                        <Space direction="vertical" size={8} style={{ width: '100%' }}>
                          <pre style={{
                            background: '#1E1E1E', color: '#D4D4D4',
                            padding: '10px 12px', borderRadius: 4,
                            fontSize: 11, margin: 0, overflowX: 'auto',
                            fontFamily: 'Consolas, monospace',
                          }}>
                            {CUSTOM_API_DOC}
                          </pre>
                          <Button
                            size="small"
                            icon={<DownloadOutlined />}
                            onClick={() => {
                              // 下载模板文件
                              const a = document.createElement('a');
                              a.href = '/custom_algorithm_template.py';
                              a.download = 'custom_algorithm_template.py';
                              a.click();
                            }}
                          >
                            下载算法模板
                          </Button>
                          <div>
                            <Tag color="blue">提示</Tag>
                            <Text type="secondary" style={{ fontSize: 11 }}>
                              需启动 render_server.py 才能执行自定义算法
                            </Text>
                          </div>
                        </Space>
                      ),
                    }]} />
                  </div>
                )}
              </Space>
            </Form>
          </>
        )}
      </Modal>

      {/* ── 规划中 ──────────────────────────────────────────────────────────── */}
      <Modal title="路径规划中" open={coverageWorkflow === 'planning'}
        footer={null} closable={false} maskClosable={false} width={300} centered>
        <div style={{ textAlign: 'center', padding: '24px 0' }}>
          <Spin size="large" />
          <div style={{ marginTop: 14, color: '#555', fontSize: 14 }}>
            {modalAlgorithm === 'custom' ? '正在执行自定义算法…' : '正在规划全覆盖路径，请稍候…'}
          </div>
        </div>
      </Modal>

    </Layout>
  );
};

export default App;
