import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Button, Space, Typography } from 'antd';
import { AimOutlined, CheckOutlined, DeleteOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface Point { x: number; y: number; }

interface MainDisplayAreaProps {
  terrainData?: any;
  settings: any;
  pathData?: any;
  drawPolygonMode?: boolean;
  confirmedPolygon?: Point[];
  onPolygonConfirmed?: (pts: Point[], canvasW: number, canvasH: number) => void;
  onPolygonClear?: () => void;
}

// ── same color scheme table as TopViewPanel ──────────────────────────────────
const colorSchemes = {
  terrain: [
    { stop: 0.0, color: '#0077BE' },
    { stop: 0.2, color: '#00A86B' },
    { stop: 0.4, color: '#90EE90' },
    { stop: 0.6, color: '#F4A460' },
    { stop: 0.8, color: '#8B4513' },
    { stop: 1.0, color: '#FFFFFF' },
  ],
  heatmap: [
    { stop: 0.0, color: '#0000FF' },
    { stop: 0.25, color: '#00FFFF' },
    { stop: 0.5, color: '#00FF00' },
    { stop: 0.75, color: '#FFFF00' },
    { stop: 1.0, color: '#FF0000' },
  ],
  grayscale: [
    { stop: 0.0, color: '#000000' },
    { stop: 1.0, color: '#FFFFFF' },
  ],
  rainbow: [
    { stop: 0.0, color: '#9400D3' },
    { stop: 0.17, color: '#0000FF' },
    { stop: 0.33, color: '#00FF00' },
    { stop: 0.5, color: '#FFFF00' },
    { stop: 0.67, color: '#FF7F00' },
    { stop: 0.83, color: '#FF0000' },
    { stop: 1.0, color: '#8B0000' },
  ],
  viridis: [
    { stop: 0.0, color: '#440154' },
    { stop: 0.25, color: '#31688E' },
    { stop: 0.5, color: '#35B779' },
    { stop: 0.75, color: '#FDE724' },
    { stop: 1.0, color: '#FFFF00' },
  ],
};

function hexToRgb(hex: string) {
  const r = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return r ? { r: parseInt(r[1], 16), g: parseInt(r[2], 16), b: parseInt(r[3], 16) } : { r: 0, g: 0, b: 0 };
}

function getColorFromScheme(normalized: number, scheme: string): string {
  const colors = colorSchemes[scheme as keyof typeof colorSchemes] || colorSchemes.terrain;
  let start = colors[0], end = colors[colors.length - 1];
  for (let i = 0; i < colors.length - 1; i++) {
    if (normalized >= colors[i].stop && normalized <= colors[i + 1].stop) {
      start = colors[i]; end = colors[i + 1]; break;
    }
  }
  const range = end.stop - start.stop;
  const t = range === 0 ? 0 : (normalized - start.stop) / range;
  const s = hexToRgb(start.color), e = hexToRgb(end.color);
  return `rgb(${Math.round(s.r + (e.r - s.r) * t)},${Math.round(s.g + (e.g - s.g) * t)},${Math.round(s.b + (e.b - s.b) * t)})`;
}
// ─────────────────────────────────────────────────────────────────────────────

const VERTEX_RADIUS = 7;
const CLOSE_THRESHOLD = 15;
const DRAG_THRESHOLD = 4;

const MainDisplayArea: React.FC<MainDisplayAreaProps> = ({
  terrainData,
  settings,
  pathData,
  drawPolygonMode = false,
  confirmedPolygon,
  onPolygonConfirmed,
  onPolygonClear,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const baseImageRef = useRef<ImageData | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const [polyPoints, setPolyPoints] = useState<Point[]>([]);
  const [polyClosed, setPolyClosed] = useState(false);
  const [mousePos, setMousePos] = useState<Point | null>(null);

  const dragIndexRef = useRef<number | null>(null);
  const mouseDownPosRef = useRef<Point | null>(null);
  const didDragRef = useRef(false);

  // ── clear callback ref (avoids stale closure in ESC listener) ────────────
  const handleClearRef = useRef<() => void>(() => {});

  // ── base terrain draw ─────────────────────────────────────────────────────

  const drawBaseTerrain = useCallback(
    (ctx: CanvasRenderingContext2D, cW: number, cH: number) => {
      if (!terrainData?.elevationData) {
        ctx.fillStyle = '#F5F5F5';
        ctx.fillRect(0, 0, cW, cH);
        return;
      }
      const { width: dW, height: dH, elevationData, minElevation, maxElevation } = terrainData;
      const cellW = cW / dW;
      const cellH = cH / dH;
      const range = maxElevation - minElevation || 1;
      const scheme = settings.colorScheme || 'terrain';

      for (let y = 0; y < dH; y++) {
        for (let x = 0; x < dW; x++) {
          const n = (elevationData[y * dW + x] - minElevation) / range;
          ctx.fillStyle = getColorFromScheme(n, scheme);
          ctx.fillRect(x * cellW, y * cellH, cellW + 0.5, cellH + 0.5);
        }
      }

      // Contours — always shown when setting is on (same as TopViewer)
      if (settings.showContours) {
        ctx.strokeStyle = 'rgba(0,0,0,0.3)';
        ctx.lineWidth = 1;
        for (let level = 1; level < 10; level++) {
          const target = minElevation + (range * level) / 10;
          for (let y = 0; y < dH - 1; y++) {
            for (let x = 0; x < dW - 1; x++) {
              const idx = y * dW + x;
              const e1 = elevationData[idx], e2 = elevationData[idx + 1], e3 = elevationData[idx + dW];
              if ((e1 <= target) !== (e2 <= target)) {
                ctx.beginPath(); ctx.moveTo(x * cellW, y * cellH);
                ctx.lineTo((x + 1) * cellW, y * cellH); ctx.stroke();
              }
              if ((e1 <= target) !== (e3 <= target)) {
                ctx.beginPath(); ctx.moveTo(x * cellW, y * cellH);
                ctx.lineTo(x * cellW, (y + 1) * cellH); ctx.stroke();
              }
            }
          }
        }
      }
    },
    [terrainData, settings.colorScheme, settings.showContours]
  );

  // ── canvas init ───────────────────────────────────────────────────────────

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    if (!ctx) return;

    const cW = container.clientWidth;
    const cH = container.clientHeight;

    if (terrainData?.elevationData) {
      const ar = terrainData.width / terrainData.height;
      const cAR = cW / cH;
      canvas.width = cAR > ar ? cH * ar : cW;
      canvas.height = cAR > ar ? cH : cW / ar;
    } else {
      canvas.width = cW;
      canvas.height = cH;
    }

    drawBaseTerrain(ctx, canvas.width, canvas.height);
    baseImageRef.current = ctx.getImageData(0, 0, canvas.width, canvas.height);
  }, [terrainData, settings.colorScheme, settings.showContours, drawBaseTerrain]);

  // ── polygon overlay helpers ───────────────────────────────────────────────

  const drawEdgeLabel = (ctx: CanvasRenderingContext2D, p1: Point, p2: Point, canvas: HTMLCanvasElement) => {
    if (!terrainData) return;
    const sx = terrainData.width / canvas.width;
    const sy = terrainData.height / canvas.height;
    const dist = Math.sqrt(((p2.x - p1.x) * sx) ** 2 + ((p2.y - p1.y) * sy) ** 2);
    const label = dist < 1000 ? dist.toFixed(1) + ' m' : (dist / 1000).toFixed(2) + ' km';
    const mx = (p1.x + p2.x) / 2, my = (p1.y + p2.y) / 2;

    ctx.font = 'bold 11px Arial';
    const tw = ctx.measureText(label).width;
    ctx.fillStyle = 'rgba(0,0,0,0.72)';
    ctx.beginPath();
    ctx.roundRect(mx - tw / 2 - 4, my - 10, tw + 8, 18, 3);
    ctx.fill();
    ctx.fillStyle = '#FFFFFF';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, mx, my);
  };

  const drawPolygonOverlay = (
    ctx: CanvasRenderingContext2D, pts: Point[], closed: boolean,
    hover: Point | null, canvas: HTMLCanvasElement, readOnly = false
  ) => {
    if (pts.length === 0) return;

    ctx.beginPath();
    ctx.moveTo(pts[0].x, pts[0].y);
    for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i].x, pts[i].y);
    if (closed) {
      ctx.closePath();
      ctx.fillStyle = 'rgba(255,102,0,0.13)';
      ctx.fill();
    }
    ctx.strokeStyle = '#FF6600';
    ctx.lineWidth = 2.5;
    ctx.setLineDash([]);
    ctx.stroke();

    if (!closed && !readOnly && hover) {
      ctx.strokeStyle = 'rgba(255,102,0,0.5)';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([6, 4]);
      ctx.beginPath();
      ctx.moveTo(pts[pts.length - 1].x, pts[pts.length - 1].y);
      ctx.lineTo(hover.x, hover.y);
      ctx.stroke();
      ctx.setLineDash([]);
    }

    for (let i = 0; i < pts.length - 1; i++) drawEdgeLabel(ctx, pts[i], pts[i + 1], canvas);
    if (closed && pts.length >= 3) drawEdgeLabel(ctx, pts[pts.length - 1], pts[0], canvas);
    if (!closed && !readOnly && hover && pts.length > 0) drawEdgeLabel(ctx, pts[pts.length - 1], hover, canvas);

    for (let i = 0; i < pts.length; i++) {
      ctx.beginPath();
      ctx.arc(pts[i].x, pts[i].y, i === 0 ? VERTEX_RADIUS : 5, 0, Math.PI * 2);
      ctx.fillStyle = i === 0 ? '#FF2200' : '#FF6600';
      ctx.fill();
      ctx.strokeStyle = '#FFFFFF';
      ctx.lineWidth = 2;
      ctx.stroke();
    }

    if (!closed && !readOnly && pts.length >= 3 && hover &&
        Math.hypot(hover.x - pts[0].x, hover.y - pts[0].y) < CLOSE_THRESHOLD) {
      ctx.beginPath();
      ctx.arc(pts[0].x, pts[0].y, CLOSE_THRESHOLD, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(255,34,0,0.5)';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 4]);
      ctx.stroke();
      ctx.setLineDash([]);
    }
  };

  // ── redraw ────────────────────────────────────────────────────────────────

  const redrawOverlays = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    if (baseImageRef.current) ctx.putImageData(baseImageRef.current, 0, 0);

    if (pathData?.path && terrainData) {
      const { width: dW, height: dH } = terrainData;
      ctx.strokeStyle = '#FF0000';
      ctx.lineWidth = 2;
      ctx.setLineDash([]);
      ctx.beginPath();
      for (let i = 0; i < pathData.path.length; i++) {
        const pt = pathData.path[i];
        const x = (pt.x / dW) * canvas.width, y = (pt.y / dH) * canvas.height;
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      }
      ctx.stroke();
      ctx.fillStyle = 'rgba(255,0,0,0.7)';
      const step = Math.max(1, Math.floor(pathData.path.length / 60));
      for (let i = 0; i < pathData.path.length; i += step) {
        const pt = pathData.path[i];
        ctx.beginPath();
        ctx.arc((pt.x / dW) * canvas.width, (pt.y / dH) * canvas.height, 2.5, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    if (!drawPolygonMode && confirmedPolygon && confirmedPolygon.length >= 3)
      drawPolygonOverlay(ctx, confirmedPolygon, true, null, canvas, true);

    if (drawPolygonMode)
      drawPolygonOverlay(ctx, polyPoints, polyClosed, mousePos, canvas, false);
  }, [pathData, terrainData, drawPolygonMode, confirmedPolygon, polyPoints, polyClosed, mousePos]);

  useEffect(() => { redrawOverlays(); }, [redrawOverlays]);

  // ── reset when polygon mode off ───────────────────────────────────────────

  useEffect(() => {
    if (!drawPolygonMode) {
      setPolyPoints([]);
      setPolyClosed(false);
      setMousePos(null);
      dragIndexRef.current = null;
    }
  }, [drawPolygonMode]);

  // ── clear handler (stable ref for ESC listener) ───────────────────────────

  const handleClear = useCallback(() => {
    setPolyPoints([]);
    setPolyClosed(false);
    setMousePos(null);
    dragIndexRef.current = null;
    onPolygonClear?.();
  }, [onPolygonClear]);

  handleClearRef.current = handleClear;

  // ── ESC key to exit polygon drawing ──────────────────────────────────────

  useEffect(() => {
    if (!drawPolygonMode) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') handleClearRef.current();
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [drawPolygonMode]);

  // ── mouse helpers ─────────────────────────────────────────────────────────

  const getPos = (e: React.MouseEvent<HTMLCanvasElement>): Point => {
    const r = canvasRef.current!.getBoundingClientRect();
    return { x: e.clientX - r.left, y: e.clientY - r.top };
  };
  const nearPt = (a: Point, b: Point, r: number) => Math.hypot(a.x - b.x, a.y - b.y) < r;

  // ── mouse events ──────────────────────────────────────────────────────────

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!drawPolygonMode) return;
    const pos = getPos(e);
    mouseDownPosRef.current = pos;
    didDragRef.current = false;
    for (let i = 0; i < polyPoints.length; i++) {
      if (nearPt(pos, polyPoints[i], VERTEX_RADIUS + 6)) { dragIndexRef.current = i; return; }
    }
    dragIndexRef.current = null;
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!drawPolygonMode) return;
    const pos = getPos(e);
    setMousePos(pos);
    if (dragIndexRef.current !== null) {
      const d = mouseDownPosRef.current;
      if (d && Math.hypot(pos.x - d.x, pos.y - d.y) > DRAG_THRESHOLD) didDragRef.current = true;
      setPolyPoints(prev => { const u = [...prev]; u[dragIndexRef.current!] = pos; return u; });
    }
  };

  const handleMouseUp = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!drawPolygonMode) return;
    const pos = getPos(e);
    const d = mouseDownPosRef.current;
    const wasDrag = didDragRef.current || (d !== null && Math.hypot(pos.x - d.x, pos.y - d.y) > DRAG_THRESHOLD);
    dragIndexRef.current = null;
    mouseDownPosRef.current = null;
    didDragRef.current = false;
    if (wasDrag || polyClosed) return;
    if (polyPoints.length >= 3 && nearPt(pos, polyPoints[0], CLOSE_THRESHOLD)) {
      setPolyClosed(true); return;
    }
    setPolyPoints(prev => [...prev, pos]);
  };

  const handleMouseLeave = () => {
    setMousePos(null);
    dragIndexRef.current = null;
  };

  // ── right-click: clear polygon ────────────────────────────────────────────

  const handleContextMenu = (e: React.MouseEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    if (drawPolygonMode) handleClear();
  };

  // ── confirm ───────────────────────────────────────────────────────────────

  const handleConfirm = () => {
    const canvas = canvasRef.current;
    if (!canvas || polyPoints.length < 3) return;
    onPolygonConfirmed?.(polyPoints, canvas.width, canvas.height);
  };

  // ── cursor ────────────────────────────────────────────────────────────────

  const getCursor = (): string => {
    if (!drawPolygonMode) return 'default';
    if (!mousePos) return 'crosshair';
    if (polyClosed) {
      for (const pt of polyPoints) if (nearPt(mousePos, pt, VERTEX_RADIUS + 6)) return 'move';
      return 'default';
    }
    if (polyPoints.length >= 3 && nearPt(mousePos, polyPoints[0], CLOSE_THRESHOLD)) return 'pointer';
    return 'crosshair';
  };

  const getHintText = (): string => {
    if (polyClosed) return '多边形已闭合 · 可拖拽顶点调整 · 右键或 ESC 清除';
    if (polyPoints.length === 0) return '左键添加顶点 · 右键 / ESC 退出';
    if (polyPoints.length < 3) return `已绘 ${polyPoints.length} 点 · 继续添加（至少 3 个）· 右键 / ESC 退出`;
    return `${polyPoints.length} 个顶点 · 点击红色起点闭合 · 右键 / ESC 清除`;
  };

  const hasData = terrainData?.elevationData;

  return (
    <div className="panel-container">
      <div className="panel-header">
        <h3>
          <AimOutlined style={{ marginRight: 6 }} />
          Main Display Area
        </h3>
        {drawPolygonMode && (
          <Space size={6}>
            <Text type="secondary" style={{ fontSize: 11 }}>{getHintText()}</Text>
            {polyPoints.length >= 3 && (
              <Button type="primary" size="small" icon={<CheckOutlined />} onClick={handleConfirm}>
                确认区域
              </Button>
            )}
            <Button size="small" icon={<DeleteOutlined />} onClick={handleClear}>清除</Button>
          </Space>
        )}
      </div>

      <div
        className="panel-content"
        ref={containerRef}
        style={{ padding: 0, position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#F5F5F5' }}
      >
        {!hasData ? (
          <div className="empty-panel">
            <Text type="secondary">
              {drawPolygonMode ? '请先通过 FILE 菜单导入 TIF 地形文件' : '暂无地形数据，请通过 FILE 菜单导入 TIF 文件'}
            </Text>
          </div>
        ) : (
          <canvas
            id="main-display-canvas"
            ref={canvasRef}
            style={{ display: 'block', border: '1px solid #D0D0D0', cursor: getCursor() }}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseLeave}
            onContextMenu={handleContextMenu}
          />
        )}
      </div>
    </div>
  );
};

export default MainDisplayArea;
