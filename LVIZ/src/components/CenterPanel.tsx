import React, { Suspense, useRef, useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid, Environment } from '@react-three/drei';
import { Empty, Spin, Typography, Select } from 'antd';
import { BoxPlotOutlined } from '@ant-design/icons';
import * as THREE from 'three';

const { Text } = Typography;

interface CenterPanelProps {
  terrainData?: any;
  title?: string;
  exaggeration?: number;
  colorScheme?: string;
  renderQuality?: {
    pixelRatio: number;
    antialias: boolean;
    shadows: boolean;
  };
  onColorSchemeChange?: (scheme: string) => void;
}

// Color schemes
const getColorFromScheme = (normalized: number, scheme: string): THREE.Color => {
  const colorSchemes: Record<string, Array<{stop: number, color: string}>> = {
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

  const colors = colorSchemes[scheme] || colorSchemes.terrain;

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

  const start = new THREE.Color(startColor.color);
  const end = new THREE.Color(endColor.color);

  return start.lerp(end, t);
};

// Terrain Mesh Component
const TerrainMesh: React.FC<{
  terrainData?: any;
  exaggeration: number;
  colorScheme: string;
  shadows: boolean;
}> = ({ terrainData, exaggeration, colorScheme, shadows }) => {
  const meshRef = useRef<THREE.Mesh>(null);

  const { geometry } = useMemo(() => {
    // Convert exaggeration from 0-100 to multiplier
    const exaggerationMultiplier = exaggeration / 10;

    if (terrainData && terrainData.elevationData) {
      const { width, height, elevationData, minElevation, maxElevation } = terrainData;

      const geometry = new THREE.PlaneGeometry(width / 10, height / 10, width - 1, height - 1);
      const vertices = geometry.attributes.position.array as Float32Array;
      const colors = new Float32Array(vertices.length);

      const range = maxElevation - minElevation || 1;

      for (let i = 0; i < elevationData.length; i++) {
        const elevation = elevationData[i];
        const normalized = (elevation - minElevation) / range;

        vertices[i * 3 + 2] = normalized * 10 * exaggerationMultiplier;

        const color = getColorFromScheme(normalized, colorScheme);
        colors[i * 3] = color.r;
        colors[i * 3 + 1] = color.g;
        colors[i * 3 + 2] = color.b;
      }

      geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
      geometry.computeVertexNormals();

      return { geometry };
    } else {
      const geometry = new THREE.PlaneGeometry(20, 20, 32, 32);
      const vertices = geometry.attributes.position.array as Float32Array;
      const colors = new Float32Array(vertices.length);

      for (let i = 0; i < vertices.length; i += 3) {
        const x = vertices[i];
        const y = vertices[i + 1];
        const z = Math.sin(x * 0.5) * Math.cos(y * 0.5) * 2 * exaggerationMultiplier;
        vertices[i + 2] = z;

        const normalized = (z + 2 * exaggerationMultiplier) / (4 * exaggerationMultiplier);
        const color = getColorFromScheme(normalized, colorScheme);
        colors[i] = color.r;
        colors[i + 1] = color.g;
        colors[i + 2] = color.b;
      }

      geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
      geometry.computeVertexNormals();

      return { geometry };
    }
  }, [terrainData, exaggeration, colorScheme]);

  return (
    <mesh
      ref={meshRef}
      geometry={geometry}
      rotation={[-Math.PI / 2, 0, 0]}
      castShadow={shadows}
      receiveShadow={shadows}
    >
      <meshStandardMaterial
        vertexColors
        side={THREE.DoubleSide}
        metalness={0.2}
        roughness={0.8}
      />
    </mesh>
  );
};

// 3D Scene
const Scene: React.FC<{
  terrainData?: any;
  exaggeration: number;
  colorScheme: string;
  shadows: boolean;
}> = ({ terrainData, exaggeration, colorScheme, shadows }) => {
  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight
        position={[10, 10, 5]}
        intensity={1}
        castShadow={shadows}
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
      />
      <pointLight position={[-10, -10, -5]} intensity={0.5} />

      <Suspense fallback={null}>
        <TerrainMesh
          terrainData={terrainData}
          exaggeration={exaggeration}
          colorScheme={colorScheme}
          shadows={shadows}
        />
        <Grid
          args={[30, 30]}
          cellSize={1}
          cellThickness={0.5}
          cellColor="#6B778C"
          sectionSize={5}
          sectionThickness={1}
          sectionColor="#888888"
          fadeDistance={50}
          fadeStrength={1}
          followCamera={false}
          infiniteGrid={false}
        />
        <Environment preset="sunset" />
      </Suspense>

      <OrbitControls
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        minDistance={0.5}
        maxDistance={200}
        maxPolarAngle={Math.PI / 2}
      />
    </>
  );
};

const CenterPanel: React.FC<CenterPanelProps> = ({
  terrainData,
  title = "3D Rendering View",
  exaggeration = 50,
  colorScheme = 'terrain',
  renderQuality = {
    pixelRatio: 2,
    antialias: true,
    shadows: true,
  },
  onColorSchemeChange,
}) => {
  const colorSchemeOptions = [
    { label: 'Terrain', value: 'terrain' },
    { label: 'Heatmap', value: 'heatmap' },
    { label: 'Grayscale', value: 'grayscale' },
    { label: 'Rainbow', value: 'rainbow' },
    { label: 'Viridis', value: 'viridis' },
  ];

  return (
    <div className="panel-container">
      <div className="panel-header">
        <h3>
          <BoxPlotOutlined style={{ marginRight: 6 }} />
          {title}
        </h3>
        <Select
          size="small"
          value={colorScheme}
          onChange={onColorSchemeChange}
          options={colorSchemeOptions}
          className="color-scheme-selector"
          style={{ minWidth: 110 }}
        />
      </div>
      <div className="panel-content" style={{ padding: 0 }}>
        <div className="three-canvas-container">
          <Suspense
            fallback={
              <div className="loading-container">
                <Spin size="large" />
                <Text style={{ color: '#FFFFFF' }}>Loading 3D scene...</Text>
              </div>
            }
          >
            <Canvas
              camera={{ position: [40, 40, 40], fov: 50 }}
              shadows={renderQuality.shadows}
              dpr={renderQuality.pixelRatio}
              gl={{ antialias: renderQuality.antialias }}
            >
              <Scene
                terrainData={terrainData}
                exaggeration={exaggeration}
                colorScheme={colorScheme}
                shadows={renderQuality.shadows}
              />
            </Canvas>
          </Suspense>
        </div>
      </div>
    </div>
  );
};

export default CenterPanel;
