import React, { useRef, useEffect } from 'react';
import { Empty, Typography } from 'antd';
import { LineChartOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface BottomChartPanelProps {
  pathData?: any;
}

const BottomChartPanel: React.FC<BottomChartPanelProps> = ({ pathData }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const container = canvas.parentElement;
    if (container) {
      canvas.width = container.clientWidth;
      canvas.height = container.clientHeight;
      drawChart(ctx, canvas.width, canvas.height);
    }
  }, [pathData]);

  const drawChart = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
    ctx.clearRect(0, 0, width, height);

    if (!pathData || !pathData.altitudeProfile) {
      return;
    }

    const { distances, altitudes, minAlt, maxAlt } = pathData.altitudeProfile;

    const padding = { left: 60, right: 30, top: 30, bottom: 50 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    const maxDistance = distances[distances.length - 1] || 100;
    const altRange = maxAlt - minAlt || 1;

    // Draw background
    ctx.fillStyle = '#FAFAFA';
    ctx.fillRect(padding.left, padding.top, chartWidth, chartHeight);

    // Draw grid
    ctx.strokeStyle = '#E8E8E8';
    ctx.lineWidth = 1;

    // Horizontal grid lines
    for (let i = 0; i <= 5; i++) {
      const y = padding.top + (chartHeight * i) / 5;
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(padding.left + chartWidth, y);
      ctx.stroke();
    }

    // Vertical grid lines
    for (let i = 0; i <= 10; i++) {
      const x = padding.left + (chartWidth * i) / 10;
      ctx.beginPath();
      ctx.moveTo(x, padding.top);
      ctx.lineTo(x, padding.top + chartHeight);
      ctx.stroke();
    }

    // Draw axes
    ctx.strokeStyle = '#333333';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding.left, padding.top);
    ctx.lineTo(padding.left, padding.top + chartHeight);
    ctx.lineTo(padding.left + chartWidth, padding.top + chartHeight);
    ctx.stroke();

    // Draw line chart
    ctx.strokeStyle = '#0066FF';
    ctx.lineWidth = 2;
    ctx.beginPath();

    for (let i = 0; i < distances.length; i++) {
      const x = padding.left + (distances[i] / maxDistance) * chartWidth;
      const y = padding.top + chartHeight - ((altitudes[i] - minAlt) / altRange) * chartHeight;

      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }
    ctx.stroke();

    // Fill area under curve
    ctx.lineTo(padding.left + chartWidth, padding.top + chartHeight);
    ctx.lineTo(padding.left, padding.top + chartHeight);
    ctx.closePath();
    ctx.fillStyle = 'rgba(0, 102, 255, 0.1)';
    ctx.fill();

    // Draw labels
    ctx.fillStyle = '#333333';
    ctx.font = '12px Times New Roman';
    ctx.textAlign = 'center';

    // X-axis labels
    for (let i = 0; i <= 10; i++) {
      const x = padding.left + (chartWidth * i) / 10;
      const distance = (maxDistance * i) / 10;
      ctx.fillText(distance.toFixed(0) + 'm', x, height - padding.bottom + 20);
    }

    // Y-axis labels
    ctx.textAlign = 'right';
    for (let i = 0; i <= 5; i++) {
      const y = padding.top + (chartHeight * i) / 5;
      const alt = maxAlt - (altRange * i) / 5;
      ctx.fillText(alt.toFixed(1) + 'm', padding.left - 10, y + 4);
    }

    // Axis titles
    ctx.font = 'bold 14px Times New Roman';
    ctx.textAlign = 'center';
    ctx.fillText('Distance', width / 2, height - 10);

    ctx.save();
    ctx.translate(15, height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Flight Altitude', 0, 0);
    ctx.restore();

    // Title
    ctx.font = 'bold 16px Times New Roman';
    ctx.fillText('Distance - Flight Altitude Profile', width / 2, 20);
  };

  const hasData = pathData && pathData.altitudeProfile;

  return (
    <div className="panel-container">
      <div className="panel-header">
        <h3>
          <LineChartOutlined style={{ marginRight: 6 }} />
          Flight Profile
        </h3>
      </div>
      <div className="panel-content" style={{ padding: 0, background: '#FFFFFF' }}>
        {!hasData ? (
          <div className="empty-panel">
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description="No path data. Please run coverage planning first."
            />
          </div>
        ) : (
          <canvas
            ref={canvasRef}
            style={{
              width: '100%',
              height: '100%',
              display: 'block',
            }}
          />
        )}
      </div>
    </div>
  );
};

export default BottomChartPanel;
