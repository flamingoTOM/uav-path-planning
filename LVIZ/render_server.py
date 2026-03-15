#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LVIZ Matplotlib 3D render server
Listen: http://localhost:5001/render-3d
Receive terrain JSON, generate 3D surface with Matplotlib, return base64 PNG
"""
import sys, io as _io
sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
import base64
import io
import math
from http.server import HTTPServer, BaseHTTPRequestHandler

import numpy as np
import matplotlib
matplotlib.use('Agg')          # 非交互后端，无需显示器
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

PORT = 5001

# Matplotlib 色彩映射对应关系
CMAP_MAP = {
    'terrain':  'terrain',
    'heatmap':  'RdYlBu_r',
    'grayscale': 'gray',
    'rainbow':  'gist_rainbow',
    'viridis':  'viridis',
}


def render_3d(data: dict) -> str:
    """渲染地形 3D 曲面，返回 base64 编码的 PNG 字符串"""

    width        = int(data['width'])
    height       = int(data['height'])
    elev_flat    = data['elevationData']
    min_elev     = float(data.get('minElevation', 0))
    max_elev     = float(data.get('maxElevation', 100))
    color_scheme = data.get('colorScheme', 'terrain')
    exaggeration = float(data.get('exaggeration', 50)) / 100.0

    # 重建高程矩阵
    Z = np.array(elev_flat, dtype=np.float32).reshape(height, width)
    Z = np.where(np.isfinite(Z), Z, min_elev)   # 清除 NaN/inf

    elev_range = max(max_elev - min_elev, 1.0)

    rows, cols = Z.shape
    X, Y = np.meshgrid(np.arange(cols), np.arange(rows))

    # Z 用于高度（考虑高程夸大）
    Z_height = (Z - min_elev) / elev_range * exaggeration * min(rows, cols) * 0.18

    # Z 用于颜色（归一化 0-1）
    Z_color  = (Z - min_elev) / elev_range
    Z_color  = np.clip(Z_color, 0, 1)

    cmap = CMAP_MAP.get(color_scheme, 'terrain')
    face_colors = plt.get_cmap(cmap)(Z_color)   # RGBA array

    # ── 绘图 ─────────────────────────────────────────────────────────────────
    bg = '#C8DCF0'
    fig = plt.figure(figsize=(5, 4), dpi=120)
    fig.patch.set_facecolor(bg)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor(bg)

    ax.plot_surface(
        X, Y, Z_height,
        facecolors=face_colors,
        linewidth=0,
        antialiased=True,
        shade=False,           # 颜色已由 facecolors 指定，关闭自动着色
    )

    # 视角：俯仰 40°，方位 225°（东南方向俯视）
    ax.view_init(elev=40, azim=225)

    # 宽高深比
    depth_ratio = max(0.3, exaggeration * 0.6)
    ax.set_box_aspect([cols, rows, max(cols, rows) * depth_ratio])

    ax.set_axis_off()
    fig.tight_layout(pad=0.2)

    # ── 输出为 PNG ────────────────────────────────────────────────────────────
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight',
                facecolor=bg, dpi=120)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def run_custom_algorithm(data: dict) -> dict:
    """
    加载并执行用户自定义算法脚本。
    data = {
        script_path: str,        # 算法脚本文件路径
        width: int, height: int,
        elevationData: list,     # 降采样后的高程数据（float list）
        minElevation: float, maxElevation: float,
        polygon: [[x,y], ...],   # 多边形顶点（地形坐标）
        params: {minAltitude, coverageWidth, overlapRate}
    }
    """
    import os

    script_path = data.get('scriptPath', '')
    if not script_path or not os.path.isfile(script_path):
        raise FileNotFoundError(f'Script not found: {script_path}')

    # 用 exec 加载用户脚本（比 importlib 更稳定，避免长运行进程中的 spec 缓存问题）
    script_path = os.path.abspath(script_path)
    namespace = {'__file__': script_path, '__name__': 'custom_algo'}
    with open(script_path, 'r', encoding='utf-8') as f:
        source = f.read()
    exec(compile(source, script_path, 'exec'), namespace)

    if 'generate_path' not in namespace:
        raise AttributeError('Custom script must define generate_path(terrain_data, polygon, params)')

    width  = int(data['width'])
    height = int(data['height'])
    elev   = np.array(data['elevationData'], dtype=np.float32).reshape(height, width)

    terrain_data = {
        'elevation':     elev,
        'width':         width,
        'height':        height,
        'min_elevation': float(data.get('minElevation', 0)),
        'max_elevation': float(data.get('maxElevation', 100)),
    }

    polygon = [(float(p[0]), float(p[1])) for p in data.get('polygon', [])]

    p = data.get('params', {})
    params = {
        'min_altitude':   float(p.get('minAltitude',   50)),
        'coverage_width': float(p.get('coverageWidth',  50)),
        'overlap_rate':   float(p.get('overlapRate',   0.2)),
    }

    return namespace['generate_path'](terrain_data, polygon, params)


# ── HTTP 请求处理 ──────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self._set_cors()
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body   = self.rfile.read(length)
            data   = json.loads(body)

            if self.path == '/render-3d':
                result = {'image': render_3d(data)}
            elif self.path == '/run-custom':
                result = run_custom_algorithm(data)
            else:
                self.send_response(404)
                self.end_headers()
                return

            resp = json.dumps(result).encode()
            self.send_response(200)
            self._set_cors()
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)

        except Exception as e:
            err = json.dumps({'error': str(e)}).encode()
            self.send_response(500)
            self._set_cors()
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(err)))
            self.end_headers()
            self.wfile.write(err)

    def _set_cors(self):
        self.send_header('Access-Control-Allow-Origin',  '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def log_message(self, fmt, *args):
        print(f'[render_server] {fmt % args}', flush=True)


if __name__ == '__main__':
    server = HTTPServer(('localhost', PORT), Handler)
    print(f'[OK] Matplotlib render server: http://localhost:{PORT}')
    print('     Waiting for /render-3d requests ...')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n服务已停止')
