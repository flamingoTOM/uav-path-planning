#!/usr/bin/env python3
"""
TIF DSM → Octree → Web Viewer

将 DSM/ 目录下的 .tif 高程图转化为八叉树地图，并在浏览器中可视化。

用法:
    python test/tif_octree_viewer.py
然后在浏览器中访问 http://localhost:8765
"""

import os
import sys
import json
import threading
import webbrowser
import time
import math
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import numpy as np
import rasterio
from rasterio.enums import Resampling

# ── 路径配置 ──────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DSM_DIR  = os.path.join(BASE_DIR, "DSM")
HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tif_octree_viewer.html")
PORT = 8765


# ── 高程图加载 ────────────────────────────────────────────────────────────────

def load_tif(fpath: str, target_res: float):
    """
    读取 .tif 文件并降采样到目标分辨率。
    返回 (elev: np.ndarray[H,W] float64, actual_res: float)
    """
    with rasterio.open(fpath) as src:
        native_res = abs(src.transform.a)   # 原始像素大小 (m)
        # 只允许降采样，不放大
        scale = min(1.0, native_res / target_res)
        out_h = max(1, round(src.height * scale))
        out_w = max(1, round(src.width  * scale))
        data  = src.read(
            1,
            out_shape=(out_h, out_w),
            resampling=Resampling.average,
        )
        actual_res = native_res / scale
        nodata = src.nodata

    data = data.astype(np.float64)
    if nodata is not None:
        data[data == nodata] = np.nan
    data[data < -1e10] = np.nan          # 兜底过滤异常 nodata
    return data, float(actual_res)


# ── 八叉树构建 ────────────────────────────────────────────────────────────────

def build_octree(elev: np.ndarray, res: float, min_size: float, max_nodes: int = 300_000):
    """
    从 2D 高程网格构建（四叉树/八叉树退化）叶子节点。

    每个叶子节点表示一块 XY 地面区域，其 Z 范围覆盖该区域内的高程。
    这与 OctoMap 对地形的处理方式一致（XY 细分 + Z 由高程决定）。

    返回:
        nodes: list of [gx, gy, gs, z_lo, z_mid, z_hi]
            gx, gy  — 网格列/行起点（整数）
            gs      — 网格边长（整数格数）
            z_lo/z_mid/z_hi — 该区域最低/平均/最高高程 (m)
    """
    H, W = elev.shape
    mc   = max(1, round(min_size / res))   # 最小叶子格数

    nodes     = []
    truncated = False
    stack     = [(0, W, 0, H)]

    while stack:
        x0, x1, y0, y1 = stack.pop()
        sub   = elev[y0:y1, x0:x1]
        valid = sub[~np.isnan(sub)]
        if len(valid) == 0:
            continue

        z_lo = float(np.min(valid))
        z_hi = float(np.max(valid))
        z_md = float(np.mean(valid))
        dx, dy = x1 - x0, y1 - y0

        if dx <= mc and dy <= mc:
            nodes.append([x0, y0, max(dx, dy), round(z_lo, 2), round(z_md, 2), round(z_hi, 2)])
            if len(nodes) >= max_nodes:
                truncated = True
                break
            continue

        mx = (x0 + x1) // 2
        my = (y0 + y1) // 2
        stack.append((x0, mx, y0, my))
        stack.append((mx, x1, y0, my))
        stack.append((x0, mx, my, y1))
        stack.append((mx, x1, my, y1))

    return nodes, truncated


# ── 工具函数 ──────────────────────────────────────────────────────────────────

def list_tif_files():
    if not os.path.isdir(DSM_DIR):
        return []
    return sorted(f for f in os.listdir(DSM_DIR) if f.lower().endswith(".tif"))


def make_heightmap(elev: np.ndarray, max_w: int = 512):
    """生成俯视图用的降采样高程矩阵 (JSON 可序列化)。"""
    H, W = elev.shape
    step = max(1, W // max_w)
    hm   = elev[::step, ::step]
    # 将 nan 转为 None，保留 1 位小数
    result = []
    for row in hm:
        result.append([None if np.isnan(v) else round(float(v), 1) for v in row])
    return result, list(hm.shape), step


# ── HTTP 处理器 ───────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)
        path   = parsed.path

        if path == "/" or path == "/index.html":
            self._serve_html()
        elif path == "/files":
            self._json(list_tif_files())
        elif path == "/data":
            self._serve_data(parse_qs(parsed.query))
        else:
            self.send_error(404)

    # ── 路由实现 ──────────────────────────────────────────────────────────────

    def _serve_html(self):
        try:
            with open(HTML_PATH, "rb") as f:
                body = f.read()
        except FileNotFoundError:
            self.send_error(404, "HTML file not found")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_data(self, qs):
        files = list_tif_files()
        fname = qs.get("file", [files[0] if files else ""])[0]
        res   = max(1.0, float(qs.get("res",   ["20"])[0]))
        msize = max(1.0, float(qs.get("msize", [str(res)])[0]))

        fpath = os.path.join(DSM_DIR, fname)
        if not os.path.isfile(fpath):
            self._json({"error": f"File not found: {fname}"})
            return

        t0 = time.time()
        elev, actual_res      = load_tif(fpath, res)
        nodes, truncated      = build_octree(elev, actual_res, msize)
        hm, hm_shape, hm_step = make_heightmap(elev)
        elapsed = round(time.time() - t0, 2)

        H, W = elev.shape
        resp = {
            "meta": {
                "file":      fname,
                "res":       round(actual_res, 2),
                "grid":      [H, W],
                "z_min":     round(float(np.nanmin(elev)), 2),
                "z_max":     round(float(np.nanmax(elev)), 2),
                "nodes":     len(nodes),
                "truncated": truncated,
                "elapsed_s": elapsed,
            },
            "nodes":    nodes,      # [[gx,gy,gs,z_lo,z_md,z_hi], ...]
            "hm":       hm,         # [[elev|None, ...], ...]
            "hm_shape": hm_shape,   # [H, W]
            "hm_step":  hm_step,
            "res":      round(actual_res, 2),
        }
        self._json(resp)

    # ── 响应工具 ──────────────────────────────────────────────────────────────

    def _json(self, data):
        body = json.dumps(data, separators=(",", ":")).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        # 只打印错误，不刷屏
        if args and str(args[1]) not in ("200", "304"):
            super().log_message(fmt, *args)


# ── 入口 ──────────────────────────────────────────────────────────────────────

def main():
    files = list_tif_files()
    if not files:
        print(f"[警告] DSM 目录未找到 .tif 文件: {DSM_DIR}")
    else:
        print(f"[信息] 找到 {len(files)} 个 TIF 文件: {', '.join(files)}")

    if not os.path.isfile(HTML_PATH):
        print(f"[错误] 未找到 HTML 文件: {HTML_PATH}")
        sys.exit(1)

    server = HTTPServer(("localhost", PORT), Handler)
    url    = f"http://localhost:{PORT}"
    print(f"[服务] 运行中: {url}  (Ctrl+C 停止)")

    threading.Timer(0.5, webbrowser.open, args=[url]).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[信息] 服务已停止")


if __name__ == "__main__":
    main()
