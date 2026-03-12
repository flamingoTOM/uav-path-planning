import React, { useState, useRef } from 'react';
import { Layout, Typography, Dropdown, MenuProps, message, Modal } from 'antd';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import TopViewPanel from './components/TopViewPanel';
import CenterPanel from './components/CenterPanel';
import ControlPanel from './components/ControlPanel';
import MainDisplayArea from './components/MainDisplayArea';
import BottomChartPanel from './components/BottomChartPanel';
import { fromBlob } from 'geotiff';
import { generateCoveragePath, CoverageParams } from './utils/coveragePlanner';
import logoSrc from './assets/logo.svg';

const { Header } = Layout;
const { Title } = Typography;

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

const App: React.FC = () => {
  const [terrainData, setTerrainData] = useState<any>(null);
  const [terrainSettings, setTerrainSettings] = useState<TerrainSettings>({
    exaggeration: 70,
    colorScheme: 'terrain',
    showGrid: true,
    showScale: true,
    showCompass: true,
    showContours: true,
  });
  const [renderQuality, setRenderQuality] = useState<RenderQuality>({
    pixelRatio: 0.5,
    antialias: false,
    shadows: false,
  });
  const [selectedRegion, setSelectedRegion] = useState<any>(null);
  const [pathData, setPathData] = useState<any>(null);
  const [coverageParams, setCoverageParams] = useState<CoverageParams>({
    flightHeight: 100,
    coverageWidth: 50,
    overlapRate: 0.2,
    terrainFollowing: true,
  });

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleTerrainDataLoaded = (data: any) => {
    setTerrainData(data);
    setSelectedRegion(null);
    setPathData(null);
  };

  const handleSettingsChange = (settings: Partial<TerrainSettings>) => {
    setTerrainSettings(prev => ({ ...prev, ...settings }));
  };

  const handleRenderQualityChange = (quality: Partial<RenderQuality>) => {
    setRenderQuality(prev => ({ ...prev, ...quality }));
  };

  const handleRegionSelected = (region: any) => {
    setSelectedRegion(region);
  };

  const handleCoverageParamsChange = (params: Partial<CoverageParams>) => {
    setCoverageParams(prev => ({ ...prev, ...params }));
  };

  const handleFileSelect = async (file: File) => {
    message.loading({ content: 'Parsing TIF file...', key: 'tif-upload', duration: 0 });

    try {
      const tiff = await fromBlob(file);
      const image = await tiff.getImage();
      const rasters = await image.readRasters();

      const width = image.getWidth();
      const height = image.getHeight();
      const elevationData = rasters[0] as Float32Array;

      let minElevation = Infinity;
      let maxElevation = -Infinity;

      for (let i = 0; i < elevationData.length; i++) {
        const value = elevationData[i];
        if (value !== null && value !== undefined && !isNaN(value)) {
          if (value < minElevation) minElevation = value;
          if (value > maxElevation) maxElevation = value;
        }
      }

      const terrainData = {
        width,
        height,
        elevationData,
        minElevation,
        maxElevation,
        fileName: file.name,
      };

      handleTerrainDataLoaded(terrainData);

      message.success({
        content: `Successfully loaded ${file.name}! Size: ${width}x${height}`,
        key: 'tif-upload',
        duration: 3,
      });
    } catch (error) {
      console.error('TIF parsing failed:', error);
      message.error({
        content: `TIF parsing failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        key: 'tif-upload',
        duration: 5,
      });
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const handleRunFullCoverage = () => {
    if (!terrainData) {
      message.warning('Please import a TIF file first');
      return;
    }

    if (!selectedRegion) {
      message.warning('Please select a region in the Main Display Area first');
      return;
    }

    message.loading({ content: 'Generating coverage path...', key: 'coverage', duration: 0 });

    try {
      const result = generateCoveragePath(terrainData, selectedRegion, coverageParams);
      setPathData(result);

      message.success({
        content: `Path generated! ${result.statistics.totalLines} lines, ${result.statistics.totalDistance.toFixed(0)}m total distance`,
        key: 'coverage',
        duration: 3,
      });
    } catch (error) {
      message.error({
        content: `Failed to generate path: ${error instanceof Error ? error.message : 'Unknown error'}`,
        key: 'coverage',
        duration: 5,
      });
    }
  };

  const handleRunOctree = () => {
    message.info('Octree planning (In development)');
  };

  // Menu items
  const fileMenuItems: MenuProps['items'] = [
    {
      key: 'open',
      label: 'Open TIF File',
      onClick: triggerFileInput,
    },
    {
      type: 'divider',
    },
    {
      key: 'export-png',
      label: 'Export as PNG',
      onClick: () => message.info('Export as PNG (In development)'),
    },
    {
      key: 'export-glb',
      label: 'Export as GLB',
      onClick: () => message.info('Export as GLB (In development)'),
    },
    {
      key: 'export-stl',
      label: 'Export as STL',
      onClick: () => message.info('Export as STL (In development)'),
    },
  ];

  const editMenuItems: MenuProps['items'] = [
    {
      key: 'reset',
      label: 'Reset Settings',
      onClick: () => {
        handleSettingsChange({
          exaggeration: 70,
          colorScheme: 'terrain',
          showGrid: true,
          showScale: true,
          showCompass: true,
          showContours: true,
        });
        handleRenderQualityChange({
          pixelRatio: 0.5,
          antialias: false,
          shadows: false,
        });
        message.success('Settings reset to default');
      },
    },
  ];

  const viewMenuItems: MenuProps['items'] = [
    {
      key: 'grid',
      label: terrainSettings.showGrid ? '✓ Show Grid' : 'Show Grid',
      onClick: () => handleSettingsChange({ showGrid: !terrainSettings.showGrid }),
    },
    {
      key: 'scale',
      label: terrainSettings.showScale ? '✓ Show Scale Bar' : 'Show Scale Bar',
      onClick: () => handleSettingsChange({ showScale: !terrainSettings.showScale }),
    },
    {
      key: 'compass',
      label: terrainSettings.showCompass ? '✓ Show Compass' : 'Show Compass',
      onClick: () => handleSettingsChange({ showCompass: !terrainSettings.showCompass }),
    },
    {
      key: 'contours',
      label: terrainSettings.showContours ? '✓ Show Contours' : 'Show Contours',
      onClick: () => handleSettingsChange({ showContours: !terrainSettings.showContours }),
    },
    {
      type: 'divider',
    },
    {
      key: 'shadows',
      label: renderQuality.shadows ? '✓ Enable Shadows' : 'Enable Shadows',
      onClick: () => handleRenderQualityChange({ shadows: !renderQuality.shadows }),
    },
    {
      key: 'antialias',
      label: renderQuality.antialias ? '✓ Enable Anti-aliasing' : 'Enable Anti-aliasing',
      onClick: () => handleRenderQualityChange({ antialias: !renderQuality.antialias }),
    },
  ];

  const runMenuItems: MenuProps['items'] = [
    {
      key: 'full-coverage',
      label: 'Full Coverage',
      onClick: handleRunFullCoverage,
    },
    {
      key: 'octree',
      label: 'Octree Planning',
      onClick: handleRunOctree,
    },
  ];

  return (
    <Layout style={{ height: '100vh', background: '#F0F0F0', display: 'flex', flexDirection: 'column' }}>
      {/* Single Header Bar with Title + Menu */}
      <Header
        style={{
          background: '#FFFFFF',
          padding: '0 16px',
          borderBottom: '1px solid #D0D0D0',
          display: 'flex',
          alignItems: 'center',
          height: '40px',
          flexShrink: 0,
          zIndex: 1000,
        }}
      >
        <img src={logoSrc} alt="Momenta Logo" style={{ width: 28, height: 28, marginRight: 12 }} />
        <Title level={5} style={{ margin: 0, color: '#333333', fontSize: '14px', fontWeight: 600, marginRight: 24 }}>
          LVIZ Visualization Platform
        </Title>

        {/* Menu Bar in same row */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 0, fontSize: '13px' }}>
          <Dropdown menu={{ items: fileMenuItems }} trigger={['click']}>
            <span style={{ padding: '0 12px', height: '40px', lineHeight: '40px', cursor: 'pointer', transition: 'background 0.2s' }}
              onMouseEnter={(e) => e.currentTarget.style.background = '#E8E8E8'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}>
              FILE
            </span>
          </Dropdown>
          <Dropdown menu={{ items: editMenuItems }} trigger={['click']}>
            <span style={{ padding: '0 12px', height: '40px', lineHeight: '40px', cursor: 'pointer', transition: 'background 0.2s' }}
              onMouseEnter={(e) => e.currentTarget.style.background = '#E8E8E8'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}>
              EDIT
            </span>
          </Dropdown>
          <Dropdown menu={{ items: viewMenuItems }} trigger={['click']}>
            <span style={{ padding: '0 12px', height: '40px', lineHeight: '40px', cursor: 'pointer', transition: 'background 0.2s' }}
              onMouseEnter={(e) => e.currentTarget.style.background = '#E8E8E8'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}>
              VIEW
            </span>
          </Dropdown>
          <Dropdown menu={{ items: runMenuItems }} trigger={['click']}>
            <span style={{ padding: '0 12px', height: '40px', lineHeight: '40px', cursor: 'pointer', transition: 'background 0.2s' }}
              onMouseEnter={(e) => e.currentTarget.style.background = '#E8E8E8'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}>
              RUN
            </span>
          </Dropdown>
        </div>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".tif,.tiff,.geotiff"
          style={{ display: 'none' }}
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) {
              handleFileSelect(file);
              e.target.value = '';
            }
          }}
        />
      </Header>

      {/* Main Layout */}
      <div style={{ flex: 1, overflow: 'hidden', position: 'relative' }}>
        <PanelGroup direction="horizontal">
          {/* Left Panel: 3D View + Top View */}
          <Panel defaultSize={25} minSize={15} maxSize={40}>
            <PanelGroup direction="vertical">
              {/* Area 1: 3D View */}
              <Panel defaultSize={50} minSize={25}>
                <CenterPanel
                  terrainData={terrainData}
                  title="3D View"
                  exaggeration={terrainSettings.exaggeration}
                  colorScheme={terrainSettings.colorScheme}
                  renderQuality={renderQuality}
                  onColorSchemeChange={(scheme) => handleSettingsChange({ colorScheme: scheme })}
                />
              </Panel>

              <PanelResizeHandle
                style={{
                  height: '4px',
                  background: '#D0D0D0',
                  cursor: 'row-resize',
                  transition: 'background 0.2s',
                }}
                onMouseEnter={(e) => { e.currentTarget.style.background = '#888888'; }}
                onMouseLeave={(e) => { e.currentTarget.style.background = '#D0D0D0'; }}
              />

              {/* Area 2: Top View */}
              <Panel defaultSize={50} minSize={25}>
                <TopViewPanel
                  terrainData={terrainData}
                  settings={terrainSettings}
                  onSettingsChange={handleSettingsChange}
                />
              </Panel>
            </PanelGroup>
          </Panel>

          <PanelResizeHandle
            style={{
              width: '4px',
              background: '#D0D0D0',
              cursor: 'col-resize',
              transition: 'background 0.2s',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.background = '#888888'; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = '#D0D0D0'; }}
          />

          {/* Middle Panel: Main Display + Bottom Chart */}
          <Panel defaultSize={50} minSize={30}>
            <PanelGroup direction="vertical">
              {/* Area 4: Main Display Area with Selection */}
              <Panel defaultSize={75} minSize={40}>
                <MainDisplayArea
                  terrainData={terrainData}
                  settings={terrainSettings}
                  onRegionSelected={handleRegionSelected}
                  pathData={pathData}
                />
              </Panel>

              <PanelResizeHandle
                style={{
                  height: '4px',
                  background: '#D0D0D0',
                  cursor: 'row-resize',
                  transition: 'background 0.2s',
                }}
                onMouseEnter={(e) => { e.currentTarget.style.background = '#888888'; }}
                onMouseLeave={(e) => { e.currentTarget.style.background = '#D0D0D0'; }}
              />

              {/* Area 3: Bottom Chart Panel */}
              <Panel defaultSize={25} minSize={10}>
                <BottomChartPanel pathData={pathData} />
              </Panel>
            </PanelGroup>
          </Panel>

          <PanelResizeHandle
            style={{
              width: '4px',
              background: '#D0D0D0',
              cursor: 'col-resize',
              transition: 'background 0.2s',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.background = '#888888'; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = '#D0D0D0'; }}
          />

          {/* Right Panel: Control Panel */}
          <Panel defaultSize={25} minSize={20} maxSize={40}>
            <ControlPanel
              onSettingsChange={handleSettingsChange}
              onRenderQualityChange={handleRenderQualityChange}
              currentSettings={terrainSettings}
              currentRenderQuality={renderQuality}
              selectedRegion={selectedRegion}
              coverageParams={coverageParams}
              onCoverageParamsChange={handleCoverageParamsChange}
              pathData={pathData}
            />
          </Panel>
        </PanelGroup>
      </div>
    </Layout>
  );
};

export default App;
