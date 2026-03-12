import React from 'react';
import {
  Button,
  Space,
  Divider,
  Slider,
  Switch,
  Typography,
  message,
  Collapse,
  Badge,
  InputNumber,
  Statistic,
  Row,
  Col,
} from 'antd';
import {
  SettingOutlined,
  EyeOutlined,
  ThunderboltOutlined,
  ExpandAltOutlined,
  EnvironmentOutlined,
  RocketOutlined,
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
  selectedRegion,
  coverageParams,
  onCoverageParamsChange,
  pathData,
}) => {
  const qualityPercentage = Math.round(((currentRenderQuality.pixelRatio - 0.5) / 4.5) * 100);

  return (
    <div className="panel-container">
      <div className="panel-header">
        <h3>
          <SettingOutlined style={{ marginRight: 6 }} />
          Control Panel
        </h3>
        <Badge status="success" text="Ready" />
      </div>
      <div className="panel-content" style={{ padding: '10px' }}>
        <Space direction="vertical" size="small" style={{ width: '100%' }}>
          {/* 3D Render Quality */}
          <Collapse
            defaultActiveKey={['1']}
            ghost
            size="small"
            items={[
              {
                key: '1',
                label: (
                  <Text strong style={{ fontSize: '12px' }}>
                    <ThunderboltOutlined style={{ marginRight: 6 }} />
                    3D Render Quality
                  </Text>
                ),
                children: (
                  <Space direction="vertical" size="small" style={{ width: '100%' }}>
                    <div>
                      <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                        <Text type="secondary" style={{ fontSize: 11 }}>
                          Quality Level
                        </Text>
                        <Text code style={{ fontSize: 10 }}>
                          {qualityPercentage}%
                        </Text>
                      </Space>
                      <Slider
                        min={0.5}
                        max={5}
                        step={0.1}
                        value={currentRenderQuality.pixelRatio}
                        onChange={(value) => {
                          onRenderQualityChange?.({ pixelRatio: value });
                          if (value < 1) {
                            onRenderQualityChange?.({ antialias: false, shadows: false });
                          } else if (value >= 1 && value < 2) {
                            onRenderQualityChange?.({ antialias: true, shadows: false });
                          } else {
                            onRenderQualityChange?.({ antialias: true, shadows: true });
                          }
                        }}
                        marks={{
                          0.5: { label: 'Low', style: { fontSize: 9 } },
                          2: { label: 'Med', style: { fontSize: 9 } },
                          3.5: { label: 'High', style: { fontSize: 9 } },
                          5: { label: 'Ultra', style: { fontSize: 9 } },
                        }}
                      />
                      <Text type="secondary" style={{ fontSize: 10 }}>
                        Pixel Ratio: {currentRenderQuality.pixelRatio.toFixed(1)}x
                      </Text>
                    </div>

                    <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                      <Text style={{ fontSize: 12 }}>Anti-aliasing</Text>
                      <Switch
                        size="small"
                        checked={currentRenderQuality.antialias}
                        onChange={(checked) => onRenderQualityChange?.({ antialias: checked })}
                      />
                    </Space>

                    <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                      <Text style={{ fontSize: 12 }}>Shadows</Text>
                      <Switch
                        size="small"
                        checked={currentRenderQuality.shadows}
                        onChange={(checked) => onRenderQualityChange?.({ shadows: checked })}
                      />
                    </Space>
                  </Space>
                ),
              },
            ]}
          />

          <Divider style={{ margin: '6px 0' }} />

          {/* Elevation Exaggeration */}
          <Collapse
            defaultActiveKey={['2']}
            ghost
            size="small"
            items={[
              {
                key: '2',
                label: (
                  <Text strong style={{ fontSize: '12px' }}>
                    <ExpandAltOutlined style={{ marginRight: 6 }} />
                    Elevation Scale
                  </Text>
                ),
                children: (
                  <div>
                    <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                      <Text type="secondary" style={{ fontSize: 11 }}>
                        Vertical Exaggeration
                      </Text>
                      <Text code style={{ fontSize: 10 }}>{currentSettings.exaggeration}</Text>
                    </Space>
                    <Slider
                      min={0}
                      max={100}
                      step={1}
                      value={currentSettings.exaggeration}
                      onChange={(value) => onSettingsChange?.({ exaggeration: value })}
                      marks={{
                        0: { label: '0', style: { fontSize: 9 } },
                        25: { label: '25', style: { fontSize: 9 } },
                        50: { label: '50', style: { fontSize: 9 } },
                        75: { label: '75', style: { fontSize: 9 } },
                        100: { label: '100', style: { fontSize: 9 } },
                      }}
                    />
                  </div>
                ),
              },
            ]}
          />

          <Divider style={{ margin: '6px 0' }} />

          {/* Region Parameters (shown when region is selected) */}
          {selectedRegion && (
            <>
              <Collapse
                defaultActiveKey={['3']}
                ghost
                size="small"
                items={[
                  {
                    key: '3',
                    label: (
                      <Text strong style={{ fontSize: '12px' }}>
                        <EnvironmentOutlined style={{ marginRight: 6 }} />
                        Selected Region
                      </Text>
                    ),
                    children: (
                      <Space direction="vertical" size="small" style={{ width: '100%' }}>
                        <Row gutter={8}>
                          <Col span={12}>
                            <Statistic
                              title="Width"
                              value={Math.abs(selectedRegion.x2 - selectedRegion.x1)}
                              suffix="px"
                              valueStyle={{ fontSize: 14 }}
                            />
                          </Col>
                          <Col span={12}>
                            <Statistic
                              title="Height"
                              value={Math.abs(selectedRegion.y2 - selectedRegion.y1)}
                              suffix="px"
                              valueStyle={{ fontSize: 14 }}
                            />
                          </Col>
                        </Row>
                        <Text type="secondary" style={{ fontSize: 10 }}>
                          Region coordinates: ({selectedRegion.x1.toFixed(0)}, {selectedRegion.y1.toFixed(0)}) to ({selectedRegion.x2.toFixed(0)}, {selectedRegion.y2.toFixed(0)})
                        </Text>
                      </Space>
                    ),
                  },
                ]}
              />

              <Divider style={{ margin: '6px 0' }} />

              {/* Coverage Parameters */}
              <Collapse
                defaultActiveKey={['4']}
                ghost
                size="small"
                items={[
                  {
                    key: '4',
                    label: (
                      <Text strong style={{ fontSize: '12px' }}>
                        <RocketOutlined style={{ marginRight: 6 }} />
                        Coverage Parameters
                      </Text>
                    ),
                    children: (
                      <Space direction="vertical" size="small" style={{ width: '100%' }}>
                        <div>
                          <Text type="secondary" style={{ fontSize: 11 }}>
                            Flight Height (m)
                          </Text>
                          <InputNumber
                            size="small"
                            min={10}
                            max={500}
                            value={coverageParams.flightHeight}
                            onChange={(value) => onCoverageParamsChange?.({ flightHeight: value || 100 })}
                            style={{ width: '100%', marginTop: 4 }}
                          />
                        </div>

                        <div>
                          <Text type="secondary" style={{ fontSize: 11 }}>
                            Coverage Width (m)
                          </Text>
                          <InputNumber
                            size="small"
                            min={5}
                            max={200}
                            value={coverageParams.coverageWidth}
                            onChange={(value) => onCoverageParamsChange?.({ coverageWidth: value || 50 })}
                            style={{ width: '100%', marginTop: 4 }}
                          />
                        </div>

                        <div>
                          <Text type="secondary" style={{ fontSize: 11 }}>
                            Overlap Rate
                          </Text>
                          <Slider
                            min={0}
                            max={0.5}
                            step={0.05}
                            value={coverageParams.overlapRate}
                            onChange={(value) => onCoverageParamsChange?.({ overlapRate: value })}
                            marks={{
                              0: { label: '0%', style: { fontSize: 9 } },
                              0.2: { label: '20%', style: { fontSize: 9 } },
                              0.5: { label: '50%', style: { fontSize: 9 } },
                            }}
                          />
                        </div>

                        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                          <Text style={{ fontSize: 12 }}>Terrain Following</Text>
                          <Switch
                            size="small"
                            checked={coverageParams.terrainFollowing}
                            onChange={(checked) => onCoverageParamsChange?.({ terrainFollowing: checked })}
                          />
                        </Space>
                      </Space>
                    ),
                  },
                ]}
              />

              <Divider style={{ margin: '6px 0' }} />
            </>
          )}

          {/* Path Statistics (shown when path is generated) */}
          {pathData && pathData.statistics && (
            <>
              <Collapse
                defaultActiveKey={['5']}
                ghost
                size="small"
                items={[
                  {
                    key: '5',
                    label: (
                      <Text strong style={{ fontSize: '12px' }}>
                        Path Statistics
                      </Text>
                    ),
                    children: (
                      <Space direction="vertical" size="small" style={{ width: '100%' }}>
                        <Row gutter={8}>
                          <Col span={12}>
                            <Statistic
                              title="Total Distance"
                              value={pathData.statistics.totalDistance.toFixed(0)}
                              suffix="m"
                              valueStyle={{ fontSize: 14 }}
                            />
                          </Col>
                          <Col span={12}>
                            <Statistic
                              title="Lines"
                              value={pathData.statistics.totalLines}
                              valueStyle={{ fontSize: 14 }}
                            />
                          </Col>
                        </Row>
                        <Row gutter={8}>
                          <Col span={12}>
                            <Statistic
                              title="Coverage"
                              value={pathData.statistics.coverageArea.toFixed(2)}
                              suffix="km²"
                              valueStyle={{ fontSize: 14 }}
                            />
                          </Col>
                          <Col span={12}>
                            <Statistic
                              title="Est. Time"
                              value={Math.round(pathData.statistics.estimatedTime)}
                              suffix="s"
                              valueStyle={{ fontSize: 14 }}
                            />
                          </Col>
                        </Row>
                      </Space>
                    ),
                  },
                ]}
              />

              <Divider style={{ margin: '6px 0' }} />
            </>
          )}

          {/* Additional Options */}
          <Collapse
            ghost
            size="small"
            items={[
              {
                key: '6',
                label: (
                  <Text strong style={{ fontSize: '12px' }}>
                    <EyeOutlined style={{ marginRight: 6 }} />
                    Additional Options
                  </Text>
                ),
                children: (
                  <Space direction="vertical" size="small" style={{ width: '100%' }}>
                    <Text type="secondary" style={{ fontSize: 11 }}>
                      Top View display options can be toggled using the icons in the Top View panel header.
                    </Text>
                  </Space>
                ),
              },
            ]}
          />

          {/* Reset Button */}
          <div style={{ marginTop: 10 }}>
            <Button
              type="default"
              block
              size="small"
              onClick={() => {
                onSettingsChange?.({
                  exaggeration: 70,
                  colorScheme: 'terrain',
                  showGrid: true,
                  showScale: true,
                  showCompass: true,
                  showContours: true,
                });
                onRenderQualityChange?.({
                  pixelRatio: 0.5,
                  antialias: false,
                  shadows: false,
                });
                message.success('Settings reset to default');
              }}
            >
              Reset to Default
            </Button>
          </div>
        </Space>
      </div>
    </div>
  );
};

export default ControlPanel;
