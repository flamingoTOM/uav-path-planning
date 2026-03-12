import React, { useRef, useEffect, useState } from 'react';
import { Empty, Spin, Typography, Switch, Space, Tooltip } from 'antd';
import { EyeOutlined, BorderOutlined, CompassOutlined, ColumnHeightOutlined, AimOutlined } from '@ant-design/icons';
import type { TerrainSettings } from '../App';

const { Text } = Typography;

interface TopViewPanelProps {
  terrainData?: any;
  settings: TerrainSettings;
  onSettingsChange?: (settings: Partial<TerrainSettings>) => void;
}

// Color schemes
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

const TopViewPanel: React.FC<TopViewPanelProps> = ({ terrainData, settings, onSettingsChange }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [loading] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resizeCanvas = () => {
      if (!container || !canvas) return;

      const containerWidth = container.clientWidth;
      const containerHeight = container.clientHeight;

      if (terrainData && terrainData.elevationData) {
        const dataAspectRatio = terrainData.width / terrainData.height;
        const containerAspectRatio = containerWidth / containerHeight;

        let canvasWidth, canvasHeight;

        if (containerAspectRatio > dataAspectRatio) {
          canvasHeight = containerHeight;
          canvasWidth = canvasHeight * dataAspectRatio;
        } else {
          canvasWidth = containerWidth;
          canvasHeight = canvasWidth / dataAspectRatio;
        }

        canvas.width = canvasWidth;
        canvas.height = canvasHeight;
      } else {
        canvas.width = containerWidth;
        canvas.height = containerHeight;
      }

      drawTopView(ctx, canvas.width, canvas.height);
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    return () => {
      window.removeEventListener('resize', resizeCanvas);
    };
  }, [terrainData, settings]);

  const getColorFromScheme = (normalized: number, scheme: string): string => {
    const colors = colorSchemes[scheme as keyof typeof colorSchemes] || colorSchemes.terrain;

    let startColor = colors[0];
    let endColor = colors[colors.length - 1];

    for (let i = 0; i < colors.length - 1; i++) {
      if (normalized >= colors[i].stop && normalized <= colors[i + 1].stop) {
        startColor = colors[i];
        endColor = colors[i + 1];
        break;
      }
    }

    const range = endColor.stop - startColor.stop;
    const t = range === 0 ? 0 : (normalized - startColor.stop) / range;

    const start = hexToRgb(startColor.color);
    const end = hexToRgb(endColor.color);

    const r = Math.round(start.r + (end.r - start.r) * t);
    const g = Math.round(start.g + (end.g - start.g) * t);
    const b = Math.round(start.b + (end.b - start.b) * t);

    return `rgb(${r},${g},${b})`;
  };

  const hexToRgb = (hex: string) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result
      ? {
          r: parseInt(result[1], 16),
          g: parseInt(result[2], 16),
          b: parseInt(result[3], 16),
        }
      : { r: 0, g: 0, b: 0 };
  };

  const drawTopView = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
    ctx.clearRect(0, 0, width, height);

    if (terrainData && terrainData.elevationData) {
      const { width: dataWidth, height: dataHeight, elevationData, minElevation, maxElevation } = terrainData;

      const cellWidth = width / dataWidth;
      const cellHeight = height / dataHeight;
      const range = maxElevation - minElevation || 1;

      for (let y = 0; y < dataHeight; y++) {
        for (let x = 0; x < dataWidth; x++) {
          const idx = y * dataWidth + x;
          const elevation = elevationData[idx];
          const normalized = (elevation - minElevation) / range;

          ctx.fillStyle = getColorFromScheme(normalized, settings.colorScheme);
          ctx.fillRect(x * cellWidth, y * cellHeight, cellWidth, cellHeight);
        }
      }

      if (settings.showGrid) {
        ctx.strokeStyle = 'rgba(0, 0, 0, 0.15)';
        ctx.lineWidth = 0.5;

        const gridSpacing = Math.max(20, Math.min(width, height) / 20);
        for (let x = 0; x < width; x += gridSpacing) {
          ctx.beginPath();
          ctx.moveTo(x, 0);
          ctx.lineTo(x, height);
          ctx.stroke();
        }
        for (let y = 0; y < height; y += gridSpacing) {
          ctx.beginPath();
          ctx.moveTo(0, y);
          ctx.lineTo(width, y);
          ctx.stroke();
        }
      }

      if (settings.showContours) {
        const contourLevels = 10;
        ctx.strokeStyle = 'rgba(0, 0, 0, 0.3)';
        ctx.lineWidth = 1;

        for (let level = 1; level < contourLevels; level++) {
          const targetElevation = minElevation + (range * level) / contourLevels;

          for (let y = 0; y < dataHeight - 1; y++) {
            for (let x = 0; x < dataWidth - 1; x++) {
              const idx = y * dataWidth + x;
              const e1 = elevationData[idx];
              const e2 = elevationData[idx + 1];
              const e3 = elevationData[idx + dataWidth];

              if (
                (e1 <= targetElevation && e2 >= targetElevation) ||
                (e1 >= targetElevation && e2 <= targetElevation)
              ) {
                ctx.beginPath();
                ctx.moveTo(x * cellWidth, y * cellHeight);
                ctx.lineTo((x + 1) * cellWidth, y * cellHeight);
                ctx.stroke();
              }

              if (
                (e1 <= targetElevation && e3 >= targetElevation) ||
                (e1 >= targetElevation && e3 <= targetElevation)
              ) {
                ctx.beginPath();
                ctx.moveTo(x * cellWidth, y * cellHeight);
                ctx.lineTo(x * cellWidth, (y + 1) * cellHeight);
                ctx.stroke();
              }
            }
          }
        }
      }
    } else {
      ctx.strokeStyle = '#EBECF0';
      ctx.lineWidth = 1;

      const gridSize = 40;
      if (settings.showGrid) {
        for (let x = 0; x < width; x += gridSize) {
          ctx.beginPath();
          ctx.moveTo(x, 0);
          ctx.lineTo(x, height);
          ctx.stroke();
        }
        for (let y = 0; y < height; y += gridSize) {
          ctx.beginPath();
          ctx.moveTo(0, y);
          ctx.lineTo(width, y);
          ctx.stroke();
        }
      }

      ctx.strokeStyle = '#888888';
      ctx.lineWidth = 2;

      ctx.beginPath();
      ctx.moveTo(0, height / 2);
      ctx.lineTo(width, height / 2);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(width / 2, 0);
      ctx.lineTo(width / 2, height);
      ctx.stroke();

      ctx.fillStyle = '#555555';
      ctx.beginPath();
      ctx.arc(width / 2, height / 2, 6, 0, Math.PI * 2);
      ctx.fill();
    }
  };

  const hasData = terrainData && terrainData.elevationData;

  return (
    <div className="panel-container">
      <div className="panel-header">
        <h3>
          <EyeOutlined style={{ marginRight: 6 }} />
          Top View (Fixed Aspect Ratio)
        </h3>

        {/* Display Options in Header */}
        <Space size={8}>
          <Tooltip title="Compass">
            <CompassOutlined
              style={{
                fontSize: 16,
                color: settings.showCompass ? '#555555' : '#CCCCCC',
                cursor: 'pointer',
                transition: 'color 0.2s',
              }}
              onClick={() => onSettingsChange?.({ showCompass: !settings.showCompass })}
            />
          </Tooltip>
          <Tooltip title="Scale Bar">
            <AimOutlined
              style={{
                fontSize: 16,
                color: settings.showScale ? '#555555' : '#CCCCCC',
                cursor: 'pointer',
                transition: 'color 0.2s',
              }}
              onClick={() => onSettingsChange?.({ showScale: !settings.showScale })}
            />
          </Tooltip>
          <Tooltip title="Contours">
            <ColumnHeightOutlined
              style={{
                fontSize: 16,
                color: settings.showContours ? '#555555' : '#CCCCCC',
                cursor: 'pointer',
                transition: 'color 0.2s',
              }}
              onClick={() => onSettingsChange?.({ showContours: !settings.showContours })}
            />
          </Tooltip>
          <Tooltip title="Grid">
            <BorderOutlined
              style={{
                fontSize: 16,
                color: settings.showGrid ? '#555555' : '#CCCCCC',
                cursor: 'pointer',
                transition: 'color 0.2s',
              }}
              onClick={() => onSettingsChange?.({ showGrid: !settings.showGrid })}
            />
          </Tooltip>
        </Space>
      </div>
      <div
        className="panel-content"
        ref={containerRef}
        style={{
          padding: 0,
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#F5F5F5',
        }}
      >
        {loading ? (
          <div className="loading-container">
            <Spin size="large" />
            <Text type="secondary">Loading...</Text>
          </div>
        ) : !hasData ? (
          <div className="empty-panel">
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description="No elevation data. Please import a .tif file"
            />
          </div>
        ) : (
          <>
            <canvas
              ref={canvasRef}
              style={{
                display: 'block',
                border: '1px solid #D0D0D0',
              }}
            />

            {/* Compass */}
            {settings.showCompass && (
              <div className="compass">
                N
                <div style={{
                  position: 'absolute',
                  fontSize: '10px',
                  fontWeight: 500,
                  color: '#666',
                  top: '8px',
                }}>
                  ↑
                </div>
              </div>
            )}

            {/* Scale Bar */}
            {settings.showScale && terrainData && (
              <div className="scale-bar">
                <div className="scale-bar-line" />
                <div style={{ textAlign: 'center', fontSize: '10px' }}>
                  {Math.round(terrainData.width / 10)} m
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default TopViewPanel;
