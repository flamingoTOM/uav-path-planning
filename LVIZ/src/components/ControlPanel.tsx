import React from 'react';
import {
  Button, Space, Divider, Slider, Typography,
  message, Collapse, Badge, Statistic, Row, Col,
} from 'antd';
import {
  SettingOutlined, EyeOutlined, ExpandAltOutlined, RocketOutlined,
} from '@ant-design/icons';
import type { TerrainSettings, RenderQuality } from '../App';
import type { CoverageParams } from '../utils/coveragePlanner';

const { Text } = Typography;

interface ControlPanelProps {
  onSettingsChange?: (settings: Partial<TerrainSettings>) => void;
  onRenderQualityChange?: (quality: Partial<RenderQuality>) => void;
  currentSettings: TerrainSettings;
  currentRenderQuality: RenderQuality;
  selectedRegion?: any;
  coverageParams: CoverageParams;
  onCoverageParamsChange?: (params: Partial<CoverageParams>) => void;
  pathData?: any;
}

const ControlPanel: React.FC<ControlPanelProps> = ({
  onSettingsChange,
  onRenderQualityChange,
  currentSettings,
  currentRenderQuality,
  coverageParams,
  onCoverageParamsChange,
  pathData,
}) => {
  return (
    <div className="panel-container">
      <div className="panel-header">
        <h3><SettingOutlined style={{ marginRight: 6 }} />控制面板</h3>
        <Badge status="success" text="就绪" />
      </div>
      <div className="panel-content" style={{ padding: '10px' }}>
        <Space direction="vertical" size="small" style={{ width: '100%' }}>

          {/* 3D 视图设置（渲染质量 + 高程缩放合并） */}
          <Collapse defaultActiveKey={['1']} ghost size="small" items={[{
            key: '1',
            label: <Text strong style={{ fontSize: '12px' }}><ExpandAltOutlined style={{ marginRight: 6 }} />3D 视图设置</Text>,
            children: (
              <Space direction="vertical" size="small" style={{ width: '100%' }}>
                {/* 高程夸大 */}
                <div>
                  <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                    <Text type="secondary" style={{ fontSize: 11 }}>高程夸大</Text>
                    <Text code style={{ fontSize: 10 }}>{currentSettings.exaggeration}</Text>
                  </Space>
                  <Slider
                    min={0} max={100} step={1}
                    value={currentSettings.exaggeration}
                    onChange={v => onSettingsChange?.({ exaggeration: v })}
                    marks={{
                      0: { label: '0', style: { fontSize: 9 } },
                      50: { label: '50', style: { fontSize: 9 } },
                      100: { label: '100', style: { fontSize: 9 } },
                    }}
                  />
                </div>
              </Space>
            ),
          }]} />

          <Divider style={{ margin: '6px 0' }} />

          {/* 路径统计（规划完成后显示） */}
          {pathData?.statistics && (
            <>
              <Collapse defaultActiveKey={['5']} ghost size="small" items={[{
                key: '5',
                label: <Text strong style={{ fontSize: '12px' }}><RocketOutlined style={{ marginRight: 6 }} />路径统计</Text>,
                children: (
                  <Space direction="vertical" size="small" style={{ width: '100%' }}>
                    <Row gutter={8}>
                      <Col span={12}>
                        <Statistic title="总航程" value={pathData.statistics.totalDistance.toFixed(0)} suffix="m" valueStyle={{ fontSize: 14 }} />
                      </Col>
                      <Col span={12}>
                        <Statistic title="航线数" value={pathData.statistics.totalLines} valueStyle={{ fontSize: 14 }} />
                      </Col>
                    </Row>
                    <Row gutter={8}>
                      <Col span={12}>
                        <Statistic
                          title="覆盖面积"
                          value={pathData.statistics.coverageAreaM2
                            ? (pathData.statistics.coverageAreaM2 / 10000).toFixed(2)
                            : (pathData.statistics.coverageArea || 0).toFixed(2)}
                          suffix="hm²"
                          valueStyle={{ fontSize: 14 }}
                        />
                      </Col>
                      <Col span={12}>
                        <Statistic title="预计时间" value={Math.round(pathData.statistics.estimatedTime)} suffix="s" valueStyle={{ fontSize: 14 }} />
                      </Col>
                    </Row>
                    <Row gutter={8}>
                      <Col span={12}>
                        <Statistic title="航点数" value={pathData.statistics.waypointCount || pathData.path?.length || 0} valueStyle={{ fontSize: 14 }} />
                      </Col>
                      <Col span={12}>
                        <Statistic title="航线间距" value={pathData.statistics.lineSpacing || '--'} suffix="m" valueStyle={{ fontSize: 14 }} />
                      </Col>
                    </Row>
                    <Row gutter={8}>
                      <Col span={12}>
                        <Statistic
                          title="最低高度"
                          value={pathData.statistics.planMinAlt != null ? pathData.statistics.planMinAlt.toFixed(1) : '--'}
                          suffix="m" valueStyle={{ fontSize: 14 }}
                        />
                      </Col>
                      <Col span={12}>
                        <Statistic
                          title="最高高度"
                          value={pathData.statistics.planMaxAlt != null ? pathData.statistics.planMaxAlt.toFixed(1) : '--'}
                          suffix="m" valueStyle={{ fontSize: 14 }}
                        />
                      </Col>
                    </Row>
                  </Space>
                ),
              }]} />
              <Divider style={{ margin: '6px 0' }} />
            </>
          )}

          {/* 附加选项 */}
          <Collapse ghost size="small" items={[{
            key: '6',
            label: <Text strong style={{ fontSize: '12px' }}><EyeOutlined style={{ marginRight: 6 }} />附加选项</Text>,
            children: (
              <Text type="secondary" style={{ fontSize: 11 }}>
                俯视图的显示选项可在俯视图面板头部图标切换。
              </Text>
            ),
          }]} />

          {/* 重置按钮 */}
          <div style={{ marginTop: 10 }}>
            <Button type="default" block size="small"
              onClick={() => {
                onSettingsChange?.({ exaggeration: 70, colorScheme: 'terrain', showGrid: true, showScale: true, showCompass: true, showContours: true });
                onRenderQualityChange?.({ pixelRatio: 0.5, antialias: false, shadows: false });
                message.success('已重置为默认设置');
              }}
            >
              重置默认
            </Button>
          </div>
        </Space>
      </div>
    </div>
  );
};

export default ControlPanel;
