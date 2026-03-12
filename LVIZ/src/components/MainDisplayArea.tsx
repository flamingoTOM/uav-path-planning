import React, { useRef, useEffect, useState } from 'react';
import { Button, Space, Typography, message } from 'antd';
import { AimOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface MainDisplayAreaProps {
  terrainData?: any;
  settings: any;
  onRegionSelected?: (region: { x1: number; y1: number; x2: number; y2: number }) => void;
  pathData?: any;
}

const MainDisplayArea: React.FC<MainDisplayAreaProps> = ({
  terrainData,
  settings,
  onRegionSelected,
  pathData,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const baseImageRef = useRef<ImageData | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isSelecting, setIsSelecting] = useState(false);
  const [selectionStart, setSelectionStart] = useState<{ x: number; y: number } | null>(null);
  const [selectionCurrent, setSelectionCurrent] = useState<{ x: number; y: number } | null>(null);
  const [confirmedRegion, setConfirmedRegion] = useState<any>(null);

  // Initialize canvas and generate base image
  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    if (!ctx) return;

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

      // Draw base terrain
      drawBaseTerrain(ctx, canvasWidth, canvasHeight);

      // Save as ImageData for fast redraw
      baseImageRef.current = ctx.getImageData(0, 0, canvasWidth, canvasHeight);

      // Initial draw with overlays
      redrawOverlays();
    } else {
      canvas.width = containerWidth;
      canvas.height = containerHeight;

      ctx.fillStyle = '#F5F5F5';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.strokeStyle = '#D0D0D0';
      ctx.lineWidth = 1;
      ctx.strokeRect(0, 0, canvas.width, canvas.height);
    }
  }, [terrainData, settings.colorScheme, settings.showContours]);

  // Redraw overlays when they change
  useEffect(() => {
    redrawOverlays();
  }, [confirmedRegion, pathData, isSelecting, selectionStart, selectionCurrent]);

  const getColorFromScheme = (normalized: number): string => {
    const scheme = settings.colorScheme || 'terrain';

    if (scheme === 'heatmap') {
      const hue = 240 - normalized * 240;
      return `hsl(${hue}, 100%, 50%)`;
    } else if (scheme === 'grayscale') {
      const gray = Math.round(normalized * 255);
      return `rgb(${gray}, ${gray}, ${gray})`;
    } else if (scheme === 'rainbow') {
      const hue = normalized * 360;
      return `hsl(${hue}, 100%, 50%)`;
    } else if (scheme === 'viridis') {
      const hue = 280 - normalized * 200;
      return `hsl(${hue}, 70%, ${30 + normalized * 50}%)`;
    } else {
      // terrain
      if (normalized < 0.2) return `hsl(210, 100%, ${40 + normalized * 100}%)`;
      if (normalized < 0.4) return `hsl(120, 70%, ${30 + normalized * 100}%)`;
      if (normalized < 0.6) return `hsl(120, 100%, 70%)`;
      if (normalized < 0.8) return `hsl(30, 90%, ${50 + normalized * 30}%)`;
      return `hsl(30, 50%, ${60 + normalized * 40}%)`;
    }
  };

  const drawBaseTerrain = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
    const { width: dataWidth, height: dataHeight, elevationData, minElevation, maxElevation } = terrainData;

    const cellWidth = width / dataWidth;
    const cellHeight = height / dataHeight;
    const range = maxElevation - minElevation || 1;

    // Draw elevation data
    for (let y = 0; y < dataHeight; y++) {
      for (let x = 0; x < dataWidth; x++) {
        const idx = y * dataWidth + x;
        const elevation = elevationData[idx];
        const normalized = (elevation - minElevation) / range;

        ctx.fillStyle = getColorFromScheme(normalized);
        ctx.fillRect(x * cellWidth, y * cellHeight, cellWidth, cellHeight);
      }
    }

    // Draw contours
    if (settings.showContours) {
      ctx.strokeStyle = 'rgba(0, 0, 0, 0.4)';
      ctx.lineWidth = 1;

      const contourLevels = 10;

      for (let level = 1; level < contourLevels; level++) {
        const targetElevation = minElevation + (range * level) / contourLevels;

        for (let y = 0; y < dataHeight - 1; y++) {
          for (let x = 0; x < dataWidth - 1; x++) {
            const idx = y * dataWidth + x;
            const e1 = elevationData[idx];
            const e2 = elevationData[idx + 1];
            const e3 = elevationData[idx + dataWidth];

            if ((e1 <= targetElevation && e2 >= targetElevation) || (e1 >= targetElevation && e2 <= targetElevation)) {
              ctx.beginPath();
              ctx.moveTo(x * cellWidth, y * cellHeight);
              ctx.lineTo((x + 1) * cellWidth, y * cellHeight);
              ctx.stroke();
            }

            if ((e1 <= targetElevation && e3 >= targetElevation) || (e1 >= targetElevation && e3 <= targetElevation)) {
              ctx.beginPath();
              ctx.moveTo(x * cellWidth, y * cellHeight);
              ctx.lineTo(x * cellWidth, (y + 1) * cellHeight);
              ctx.stroke();
            }
          }
        }
      }
    }
  };

  const redrawOverlays = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Restore base image
    if (baseImageRef.current) {
      ctx.putImageData(baseImageRef.current, 0, 0);
    }

    // Draw confirmed region
    if (confirmedRegion) {
      ctx.strokeStyle = '#00FF00';
      ctx.lineWidth = 3;
      ctx.setLineDash([]);
      ctx.strokeRect(
        confirmedRegion.x1,
        confirmedRegion.y1,
        confirmedRegion.x2 - confirmedRegion.x1,
        confirmedRegion.y2 - confirmedRegion.y1
      );
    }

    // Draw path
    if (pathData && pathData.path && terrainData) {
      const { width: dataWidth, height: dataHeight } = terrainData;

      ctx.strokeStyle = '#FF0000';
      ctx.lineWidth = 2;
      ctx.setLineDash([]);

      ctx.beginPath();
      for (let i = 0; i < pathData.path.length; i++) {
        const point = pathData.path[i];
        const x = (point.x / dataWidth) * canvas.width;
        const y = (point.y / dataHeight) * canvas.height;

        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      ctx.stroke();

      // Draw sample waypoints
      ctx.fillStyle = '#FF0000';
      const step = Math.max(1, Math.floor(pathData.path.length / 50));
      for (let i = 0; i < pathData.path.length; i += step) {
        const point = pathData.path[i];
        const x = (point.x / dataWidth) * canvas.width;
        const y = (point.y / dataHeight) * canvas.height;
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // Draw current selection
    if (isSelecting && selectionStart && selectionCurrent) {
      ctx.strokeStyle = '#0066FF';
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 5]);
      ctx.strokeRect(
        selectionStart.x,
        selectionStart.y,
        selectionCurrent.x - selectionStart.x,
        selectionCurrent.y - selectionStart.y
      );
      ctx.setLineDash([]);
    }
  };

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!terrainData) {
      message.warning('Please import a TIF file first');
      return;
    }

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    setIsSelecting(true);
    setSelectionStart({ x, y });
    setSelectionCurrent({ x, y });
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isSelecting || !selectionStart) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    setSelectionCurrent({ x, y });
  };

  const handleMouseUp = () => {
    if (isSelecting) {
      setIsSelecting(false);
    }
  };

  const handleConfirm = () => {
    if (selectionStart && selectionCurrent) {
      const region = {
        x1: Math.min(selectionStart.x, selectionCurrent.x),
        y1: Math.min(selectionStart.y, selectionCurrent.y),
        x2: Math.max(selectionStart.x, selectionCurrent.x),
        y2: Math.max(selectionStart.y, selectionCurrent.y),
      };

      setConfirmedRegion(region);

      if (onRegionSelected) {
        onRegionSelected(region);
      }

      message.success('Region confirmed');
    }
  };

  const handleCancel = () => {
    setSelectionStart(null);
    setSelectionCurrent(null);
    setConfirmedRegion(null);
    setIsSelecting(false);
  };

  const hasData = terrainData && terrainData.elevationData;
  const hasSelection = selectionStart && selectionCurrent && !isSelecting;

  return (
    <div className="panel-container">
      <div className="panel-header">
        <h3>
          <AimOutlined style={{ marginRight: 6 }} />
          Main Display Area
        </h3>
        {hasSelection && !confirmedRegion && (
          <Space size={4}>
            <Button
              type="primary"
              size="small"
              icon={<CheckOutlined />}
              onClick={handleConfirm}
            >
              Confirm
            </Button>
            <Button
              size="small"
              icon={<CloseOutlined />}
              onClick={handleCancel}
            >
              Cancel
            </Button>
          </Space>
        )}
        {confirmedRegion && (
          <Button size="small" onClick={handleCancel}>
            Clear Selection
          </Button>
        )}
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
        {!hasData ? (
          <div className="empty-panel">
            <Text type="secondary">No terrain data. Please import a TIF file via FILE menu.</Text>
          </div>
        ) : (
          <canvas
            ref={canvasRef}
            style={{
              display: 'block',
              border: '1px solid #D0D0D0',
              cursor: isSelecting ? 'crosshair' : confirmedRegion ? 'default' : 'crosshair',
            }}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
          />
        )}
      </div>
    </div>
  );
};

export default MainDisplayArea;
