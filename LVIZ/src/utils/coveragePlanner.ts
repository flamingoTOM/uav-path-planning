/**
 * Coverage Path Planning Algorithm
 * 全覆盖路径规划算法 (Boustrophedon / Lawn-mower pattern)
 */

export interface CoverageParams {
  minAltitude: number;        // 防低高度 / terrain clearance (m)
  coverageWidth: number;      // 覆盖宽度 (m)
  overlapRate: number;        // 重叠率 (0-1)
  terrainFollowing: boolean;  // 仿地飞行
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
    coverageAreaM2: number;   // 覆盖面积 m²
    estimatedTime: number;    // 预计飞行时间 s
    waypointCount: number;    // 航点数量
    planMinAlt: number;       // 最低飞行高度 m
    planMaxAlt: number;       // 最高飞行高度 m
    lineSpacing: number;      // 航线间距 m
  };
}

/** Ray-casting point-in-polygon test */
function pointInPolygon(
  px: number,
  py: number,
  polygon: { x: number; y: number }[]
): boolean {
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const xi = polygon[i].x, yi = polygon[i].y;
    const xj = polygon[j].x, yj = polygon[j].y;
    const intersect =
      yi > py !== yj > py &&
      px < ((xj - xi) * (py - yi)) / (yj - yi) + xi;
    if (intersect) inside = !inside;
  }
  return inside;
}

/**
 * Generate boustrophedon coverage path for a polygon region.
 * @param terrainData   - loaded terrain data (width, height, elevationData, minElevation, maxElevation)
 * @param polygonCanvas - polygon vertices in canvas pixel coordinates
 * @param canvasWidth   - canvas width in pixels
 * @param canvasHeight  - canvas height in pixels
 * @param params        - coverage planning parameters
 */
export function generateCoveragePath(
  terrainData: any,
  polygonCanvas: { x: number; y: number }[],
  canvasWidth: number,
  canvasHeight: number,
  params: CoverageParams
): CoverageResult {
  const { elevationData, width, height, minElevation } = terrainData;
  const { minAltitude, coverageWidth, overlapRate, terrainFollowing } = params;

  // Scale: terrain data pixels per canvas pixel
  const scaleX = width / canvasWidth;
  const scaleY = height / canvasHeight;

  // Convert polygon to terrain data coordinates
  const polyTerrain = polygonCanvas.map((p) => ({
    x: p.x * scaleX,
    y: p.y * scaleY,
  }));

  // Bounding box in terrain coords
  const xs = polyTerrain.map((p) => p.x);
  const ys = polyTerrain.map((p) => p.y);
  const x1 = Math.max(0, Math.floor(Math.min(...xs)));
  const y1 = Math.max(0, Math.floor(Math.min(...ys)));
  const x2 = Math.min(width - 1, Math.ceil(Math.max(...xs)));
  const y2 = Math.min(height - 1, Math.ceil(Math.max(...ys)));

  // Line spacing (terrain pixels ≈ meters assuming 1px = 1m)
  const lineSpacing = Math.max(1, Math.floor(coverageWidth * (1 - overlapRate)));

  const path: PathPoint[] = [];
  let totalDistance = 0;
  let direction = 1;
  let lineCount = 0;

  for (let y = y1; y <= y2; y += lineSpacing) {
    // Collect points on this scanline inside the polygon
    const rowPoints: { x: number; y: number }[] = [];
    for (let x = x1; x <= x2; x++) {
      if (pointInPolygon(x + 0.5, y + 0.5, polyTerrain)) {
        rowPoints.push({ x, y });
      }
    }
    if (rowPoints.length === 0) continue;

    if (direction === -1) rowPoints.reverse();
    lineCount++;

    for (const pt of rowPoints) {
      const idx = Math.min(
        Math.round(pt.y) * width + Math.round(pt.x),
        elevationData.length - 1
      );
      const terrainAlt = (elevationData[idx] as number) || minElevation;
      const altitude = terrainFollowing ? terrainAlt + minAltitude : minAltitude;

      if (path.length > 0) {
        const prev = path[path.length - 1];
        const dx = pt.x - prev.x;
        const dy = pt.y - prev.y;
        totalDistance += Math.sqrt(dx * dx + dy * dy);
      }

      path.push({ x: pt.x, y: pt.y, altitude, distance: totalDistance });
    }

    direction *= -1;
  }

  // Altitude profile arrays
  const distances = path.map((p) => p.distance);
  const altitudes = path.map((p) => p.altitude);
  const planMinAlt = altitudes.length > 0 ? Math.min(...altitudes) : minAltitude;
  const planMaxAlt = altitudes.length > 0 ? Math.max(...altitudes) : minAltitude;

  // Polygon area using shoelace formula in terrain coords (m²)
  let polyArea = 0;
  for (let i = 0, j = polyTerrain.length - 1; i < polyTerrain.length; j = i++) {
    polyArea += polyTerrain[i].x * polyTerrain[j].y;
    polyArea -= polyTerrain[j].x * polyTerrain[i].y;
  }
  const coverageAreaM2 = Math.abs(polyArea) / 2;

  const estimatedTime = totalDistance / 10; // assume 10 m/s cruise speed

  return {
    path,
    altitudeProfile: {
      distances,
      altitudes,
      minAlt: planMinAlt,
      maxAlt: planMaxAlt,
    },
    statistics: {
      totalDistance,
      totalLines: lineCount,
      coverageAreaM2,
      estimatedTime,
      waypointCount: path.length,
      planMinAlt,
      planMaxAlt,
      lineSpacing,
    },
  };
}
