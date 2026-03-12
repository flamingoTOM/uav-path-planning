/**
 * CenterPanel — Matplotlib 3D 地形视图
 * 优先调用 Python 渲染服务 /render-3d；服务离线时退化为 Canvas 2D 等轴测图
 */
import React, { useRef, useEffect, useState, useCallback, useMemo } from 'react';
import { Select, Tooltip, Typography, Spin } from 'antd';
import { BoxPlotOutlined, EyeOutlined, EyeInvisibleOutlined, ReloadOutlined } from '@ant-design/icons';

const { Text } = Typography;

// ── 备用色彩方案（Canvas 2D fallback 用） ─────────────────────────────────────
const FALLBACK_SCHEMES: Record<string, { stop: number; color: string }[]> = {
  terrain: [
    { stop: 0.0, color: '#1A6EA8' }, { stop: 0.2, color: '#2E9E5B' },
    { stop: 0.4, color: '#7DC879' }, { stop: 0.6, color: '#D4A45A' },
    { stop: 0.8, color: '#8B5E3C' }, { stop: 1.0, color: '#F0ECE4' },
  ],
  heatmap: [
    { stop: 0.0, color: '#0000CC' }, { stop: 0.5, color: '#00CC00' }, { stop: 1.0, color: '#CC0000' },
  ],
  grayscale: [{ stop: 0.0, color: '#1A1A1A' }, { stop: 1.0, color: '#E8E8E8' }],
  rainbow: [
    { stop: 0.0, color: '#9400D3' }, { stop: 0.33, color: '#00BB00' },
    { stop: 0.67, color: '#FF7F00' }, { stop: 1.0, color: '#660000' },
  ],
  viridis: [
    { stop: 0.0, color: '#440154' }, { stop: 0.5, color: '#35B779' }, { stop: 1.0, color: '#FFFF55' },
  ],
};

function hexToRgb(hex: string): [number, number, number] {
  const m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return m ? [parseInt(m[1], 16), parseInt(m[2], 16), parseInt(m[3], 16)] : [128, 128, 128];
}

function lerpColor(n: number, scheme: string): [number, number, number] {
  const stops = FALLBACK_SCHEMES[scheme] ?? FALLBACK_SCHEMES.terrain;
  let s = stops[0], e = stops[stops.length - 1];
  for (let i = 0; i < stops.length - 1; i++) {
    if (n >= stops[i].stop && n <= stops[i + 1].stop) { s = stops[i]; e = stops[i + 1]; break; }
  }
  const t = s.stop === e.stop ? 0 : (n - s.stop) / (e.stop - s.stop);
  const [r1, g1, b1] = hexToRgb(s.color);
  const [r2, g2, b2] = hexToRgb(e.color);
  return [Math.round(r1 + (r2 - r1) * t), Math.round(g1 + (g2 - g1) * t), Math.round(b1 + (b2 - b1) * t)];
}

// ── 内置示例地形（服务离线时展示） ────────────────────────────────────────────
const DEMO_RES = 40;
const demoTerrain = (() => {
  const data = new Float32Array(DEMO_RES * DEMO_RES);
  for (let y = 0; y < DEMO_RES; y++) {
    for (let x = 0; x < DEMO_RES; x++) {
      const nx = x / DEMO_RES, ny = y / DEMO_RES;
      data[y * DEMO_RES + x] =
        Math.sin(nx * Math.PI * 4) * 28 + Math.cos(ny * Math.PI * 3) * 22 +
        Math.sin((nx + ny) * Math.PI * 2.5) * 16 + 120;
    }
  }
  return { width: DEMO_RES, height: DEMO_RES, elevationData: data, minElevation: 44, maxElevation: 196, isDemo: true };
})();

const MAX_RES = 56;

const COLOR_OPTIONS = [
  { label: '地形', value: 'terrain' }, { label: '热力图', value: 'heatmap' },
  { label: '灰度', value: 'grayscale' }, { label: '彩虹', value: 'rainbow' },
  { label: '绿紫', value: 'viridis' },
];

interface CenterPanelProps {
  terrainData?: any;
  title?: string;
  exaggeration?: number;
  colorScheme?: string;
  renderQuality?: any;
  onColorSchemeChange?: (s: string) => void;
}

const CenterPanel: React.FC<CenterPanelProps> = ({
  terrainData,
  title = '3D 视图',
  exaggeration = 50,
  colorScheme = 'terrain',
  onColorSchemeChange,
}) => {
  const [contentVisible, setContentVisible] = useState(true);
  const [imgSrc, setImgSrc] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [serverOnline, setServerOnline] = useState<boolean | null>(null); // null=未知
  const canvasRef    = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const abortRef     = useRef<AbortController | null>(null);

  const activeData = useMemo(
    () => (terrainData?.elevationData ? terrainData : demoTerrain),
    [terrainData]
  );
  const isDemo = !terrainData?.elevationData;

  // ── 向 Python 服务器请求渲染 ─────────────────────────────────────────────
  const fetchRender = useCallback(async () => {
    if (!contentVisible) return;

    // 取消上一次请求
    abortRef.current?.abort();
    abortRef.current = new AbortController();

    setLoading(true);

    try {
      // 降采样后再发送，减小 payload
      const { width: dW, height: dH, elevationData, minElevation, maxElevation } = activeData;
      const stepX = Math.max(1, Math.ceil(dW / 100));
      const stepY = Math.max(1, Math.ceil(dH / 100));
      const sampledW = Math.ceil(dW / stepX);
      const sampledH = Math.ceil(dH / stepY);
      const sampled: number[] = [];
      for (let y = 0; y < dH; y += stepY) {
        for (let x = 0; x < dW; x += stepX) {
          const v = elevationData[y * dW + x];
          sampled.push(isFinite(v) ? v : minElevation);
        }
      }

      const res = await fetch('/render-3d', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          width: sampledW,
          height: sampledH,
          elevationData: sampled,
          minElevation,
          maxElevation,
          colorScheme,
          exaggeration,
        }),
        signal: abortRef.current.signal,
      });

      if (!res.ok) throw new Error(`服务器响应 ${res.status}`);
      const json = await res.json();
      if (json.error) throw new Error(json.error);

      setImgSrc(`data:image/png;base64,${json.image}`);
      setServerOnline(true);
    } catch (err: any) {
      if (err.name === 'AbortError') return; // 被主动取消，忽略
      console.warn('[CenterPanel] Matplotlib 服务不可用，切换为 Canvas 2D 备用渲染:', err.message);
      setServerOnline(false);
      setImgSrc(null);
    } finally {
      setLoading(false);
    }
  }, [activeData, exaggeration, colorScheme, contentVisible]);

  useEffect(() => { fetchRender(); }, [fetchRender]);

  // ── Canvas 2D 备用渲染（Matplotlib 服务不可用时） ────────────────────────
  const drawFallback = useCallback(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;
    const cW = container.clientWidth, cH = container.clientHeight;
    if (cW < 20 || cH < 20) return;
    canvas.width = cW; canvas.height = cH;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const bg = ctx.createLinearGradient(0, 0, 0, cH);
    bg.addColorStop(0, '#B8D4E8'); bg.addColorStop(1, '#EBF4FB');
    ctx.fillStyle = bg; ctx.fillRect(0, 0, cW, cH);

    const { width: dW, height: dH, elevationData, minElevation, maxElevation } = activeData;
    const range = maxElevation - minElevation || 1;
    const stepX = Math.max(1, Math.ceil(dW / MAX_RES));
    const stepY = Math.max(1, Math.ceil(dH / MAX_RES));
    const gridW = Math.ceil(dW / stepX), gridH = Math.ceil(dH / stepY);

    const exagg = Math.max(0.05, exaggeration / 100);
    const twW = (cW * 0.90) / (gridW + gridH);
    const hCoeff = (gridW + gridH) * 0.5 + 4 * exagg + 0.8;
    const twH = (cH * 0.86) / hCoeff;
    const tileHW = Math.max(1.5, Math.min(twW, twH));
    const tileHH = tileHW * 0.5;
    const elevScale = tileHH * 8 * exagg;
    const wallH = Math.max(1.5, tileHH * 0.80);
    const originX = cW / 2;
    const originY = cH * 0.93 - (gridW + gridH) * tileHH - wallH;

    for (let d = 0; d < gridW + gridH - 1; d++) {
      for (let gy = Math.max(0, d - gridW + 1); gy <= Math.min(d, gridH - 1); gy++) {
        const gx = d - gy;
        const dy = Math.min(gy * stepY, dH - 1), dx = Math.min(gx * stepX, dW - 1);
        const n = Math.max(0, Math.min(1, ((elevationData[dy * dW + dx] as number) - minElevation) / range));
        const sx = originX + (gx - gy) * tileHW;
        const sy = originY + (gx + gy) * tileHH - n * elevScale;
        const [r, g, b] = lerpColor(n, colorScheme);

        ctx.beginPath();
        ctx.moveTo(sx, sy); ctx.lineTo(sx + tileHW, sy + tileHH);
        ctx.lineTo(sx, sy + tileHH * 2); ctx.lineTo(sx - tileHW, sy + tileHH);
        ctx.closePath(); ctx.fillStyle = `rgb(${r},${g},${b})`; ctx.fill();

        ctx.beginPath();
        ctx.moveTo(sx - tileHW, sy + tileHH); ctx.lineTo(sx, sy + tileHH * 2);
        ctx.lineTo(sx, sy + tileHH * 2 + wallH); ctx.lineTo(sx - tileHW, sy + tileHH + wallH);
        ctx.closePath(); ctx.fillStyle = `rgb(${Math.round(r*.62)},${Math.round(g*.62)},${Math.round(b*.62)})`; ctx.fill();

        ctx.beginPath();
        ctx.moveTo(sx, sy + tileHH * 2); ctx.lineTo(sx + tileHW, sy + tileHH);
        ctx.lineTo(sx + tileHW, sy + tileHH + wallH); ctx.lineTo(sx, sy + tileHH * 2 + wallH);
        ctx.closePath(); ctx.fillStyle = `rgb(${Math.round(r*.40)},${Math.round(g*.40)},${Math.round(b*.40)})`; ctx.fill();
      }
    }

    ctx.fillStyle = 'rgba(0,0,0,0.4)';
    ctx.font = `${Math.max(9, Math.round(cH * 0.055))}px Arial`;
    ctx.textAlign = 'left'; ctx.textBaseline = 'bottom';
    ctx.fillText('Canvas 备用渲染（启动 render_server.py 以使用 Matplotlib）', 6, cH - 4);
  }, [activeData, exaggeration, colorScheme]);

  useEffect(() => {
    if (serverOnline === false && contentVisible) drawFallback();
  }, [serverOnline, contentVisible, drawFallback]);

  useEffect(() => {
    if (serverOnline !== false) return;
    const el = containerRef.current;
    if (!el) return;
    const obs = new ResizeObserver(() => { if (contentVisible) drawFallback(); });
    obs.observe(el);
    return () => obs.disconnect();
  }, [serverOnline, contentVisible, drawFallback]);

  // ── JSX ──────────────────────────────────────────────────────────────────
  const showImg    = serverOnline === true && imgSrc;
  const showCanvas = serverOnline === false;

  return (
    <div className="panel-container">
      <div className="panel-header">
        <h3><BoxPlotOutlined style={{ marginRight: 6 }} />{title}</h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {/* 手动刷新 */}
          <Tooltip title="重新渲染">
            <span
              style={{ cursor: 'pointer', fontSize: 14, color: '#777', lineHeight: 1 }}
              onClick={fetchRender}
            >
              <ReloadOutlined spin={loading} />
            </span>
          </Tooltip>
          <Select size="small" value={colorScheme} onChange={onColorSchemeChange}
            options={COLOR_OPTIONS} style={{ minWidth: 90 }} />
          <Tooltip title={contentVisible ? '隐藏 3D 内容' : '显示 3D 内容'}>
            <span
              style={{ cursor: 'pointer', fontSize: 15, color: contentVisible ? '#555' : '#BBB', lineHeight: 1 }}
              onClick={() => setContentVisible(v => !v)}
            >
              {contentVisible ? <EyeOutlined /> : <EyeInvisibleOutlined />}
            </span>
          </Tooltip>
        </div>
      </div>

      <div
        className="panel-content"
        ref={containerRef}
        style={{ padding: 0, position: 'relative', overflow: 'hidden', background: '#B8D4E8',
          display: 'flex', alignItems: 'center', justifyContent: 'center' }}
      >
        {!contentVisible ? (
          <Text type="secondary" style={{ fontSize: 12 }}>3D 视图已隐藏</Text>
        ) : loading ? (
          /* 加载中 */
          <div style={{ textAlign: 'center' }}>
            <Spin size="large" />
            <div style={{ marginTop: 10, color: '#555', fontSize: 12 }}>Matplotlib 渲染中…</div>
          </div>
        ) : showImg ? (
          /* Matplotlib 渲染图 */
          <img
            src={imgSrc!}
            alt="3D terrain"
            style={{ width: '100%', height: '100%', objectFit: 'contain', display: 'block' }}
          />
        ) : showCanvas ? (
          /* Canvas 2D 备用 */
          <canvas
            ref={canvasRef}
            style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}
          />
        ) : (
          /* 初始等待 */
          <Text type="secondary" style={{ fontSize: 12 }}>正在连接渲染服务…</Text>
        )}

        {/* 示例地形水印 */}
        {contentVisible && !loading && isDemo && (showImg || showCanvas) && (
          <div style={{
            position: 'absolute', bottom: 6, left: 6, fontSize: 10,
            color: 'rgba(0,0,0,0.45)', pointerEvents: 'none',
          }}>
            示例地形（加载 TIF 后显示真实数据）
          </div>
        )}
      </div>
    </div>
  );
};

export default CenterPanel;
