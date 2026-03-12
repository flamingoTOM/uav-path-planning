/**
 * Coverage Path Planning Algorithm
 * 全覆盖路径规划算法
 */

export interface CoverageParams {
  flightHeight: number;      // 飞行高度 (m)
  coverageWidth: number;      // 覆盖宽度 (m)
  overlapRate: number;        // 重叠率 (0-1)
  terrainFollowing: boolean;  // 是否仿地飞行
}

export interface PathPoint {
  x: number;
  y: number;
  altitude: number;
  distance: number;
}

export interface CoverageResult {
  path: PathPoint[];
  altitudeProfile: {
    distances: number[];
    altitudes: number[];
    minAlt: number;
    maxAlt: number;
  };
  statistics: {
    totalDistance: number;
    totalLines: number;
    coverageArea: number;
    estimatedTime: number;
  };
}

/**
 * Generate coverage path for selected region
 */
export function generateCoveragePath(
  terrainData: any,
  region: { x1: number; y1: number; x2: number; y2: number },
  params: CoverageParams
): CoverageResult {
  const { elevationData, width, height, minElevation, maxElevation } = terrainData;
  const { flightHeight, coverageWidth, overlapRate, terrainFollowing } = params;

  // Convert canvas coordinates to data coordinates
  const canvas = document.querySelector('canvas');
  if (!canvas) throw new Error('Canvas not found');

  const canvasWidth = canvas.width;
  const canvasHeight = canvas.height;

  const x1 = Math.floor((region.x1 / canvasWidth) * width);
  const y1 = Math.floor((region.y1 / canvasHeight) * height);
  const x2 = Math.ceil((region.x2 / canvasWidth) * width);
  const y2 = Math.ceil((region.y2 / canvasHeight) * height);

  const regionWidth = x2 - x1;
  const regionHeight = y2 - y1;

  // Calculate line spacing based on coverage width and overlap
  const lineSpacing = Math.max(1, Math.floor(coverageWidth * (1 - overlapRate)));

  // Generate boustrophedon (zigzag) path
  const path: PathPoint[] = [];
  let totalDistance = 0;
  let direction = 1; // 1 for right, -1 for left

  for (let y = y1; y < y2; y += lineSpacing) {
    if (direction === 1) {
      // Left to right
      for (let x = x1; x <= x2; x++) {
        const idx = Math.min(y * width + x, elevationData.length - 1);
        const terrainAlt = elevationData[idx] || minElevation;

        const altitude = terrainFollowing
          ? terrainAlt + flightHeight
          : flightHeight;

        if (path.length > 0) {
          const prev = path[path.length - 1];
          const dx = x - prev.x;
          const dy = y - prev.y;
          totalDistance += Math.sqrt(dx * dx + dy * dy);
        }

        path.push({
          x,
          y,
          altitude,
          distance: totalDistance,
        });
      }
    } else {
      // Right to left
      for (let x = x2; x >= x1; x--) {
        const idx = Math.min(y * width + x, elevationData.length - 1);
        const terrainAlt = elevationData[idx] || minElevation;

        const altitude = terrainFollowing
          ? terrainAlt + flightHeight
          : flightHeight;

        if (path.length > 0) {
          const prev = path[path.length - 1];
          const dx = x - prev.x;
          const dy = y - prev.y;
          totalDistance += Math.sqrt(dx * dx + dy * dy);
        }

        path.push({
          x,
          y,
          altitude,
          distance: totalDistance,
        });
      }
    }

    direction *= -1; // Alternate direction
  }

  // Generate altitude profile
  const distances: number[] = [];
  const altitudes: number[] = [];
  let minAlt = Infinity;
  let maxAlt = -Infinity;

  for (const point of path) {
    distances.push(point.distance);
    altitudes.push(point.altitude);
    if (point.altitude < minAlt) minAlt = point.altitude;
    if (point.altitude > maxAlt) maxAlt = point.altitude;
  }

  // Calculate statistics
  const totalLines = Math.ceil(regionHeight / lineSpacing);
  const coverageArea = (regionWidth * regionHeight) / 100; // in km²
  const estimatedTime = totalDistance / 10; // assuming 10 m/s speed, in seconds

  return {
    path,
    altitudeProfile: {
      distances,
      altitudes,
      minAlt,
      maxAlt,
    },
    statistics: {
      totalDistance,
      totalLines,
      coverageArea,
      estimatedTime,
    },
  };
}
