"""HTTP 层: http.server + 7 个 API 端点 + 静态文件服务 + CORS。

路由:
  GET  /                → web/index.html (默认回退)
  GET  /api/status      → 服务状态
  GET  /api/draws       → 开奖历史 + 全 7 位属性
  GET  /api/stats       → 窗口统计
  GET  /api/omit        → 遗漏分析
  GET  /api/predict     → 预测推荐
  POST /api/filter      → 挑码过滤
  POST /api/pick        → 组号推荐
"""

from __future__ import annotations

import json
import os
import socketserver
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Optional
from urllib.parse import urlparse, parse_qs

from . import config, db, fetcher, picker_engine, predictors, stats_engine, zodiac_wuxing as zw

_conn = None
_db_path = ""
_srv: Optional[ThreadingHTTPServer] = None


def set_shared_state(conn, db_path: str) -> None:
    global _conn, _db_path
    _conn = conn
    _db_path = db_path


def make_server(host: str, port: int) -> ThreadingHTTPServer:
    global _srv
    config.init_paths()
    _srv = ThreadingHTTPServer((host, port), Handler)
    _srv.daemon_threads = True
    return _srv


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "macaujc-predictor/1.1.9"

    # ---------- 基础输出 ----------

    def _send(self, code: int, body: bytes, ctype: str = "application/json; charset=utf-8",
              extra: Optional[dict] = None) -> None:
        try:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _json(self, obj, code: int = 200) -> None:
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def _err(self, code: int, msg: str) -> None:
        self._json({"ok": False, "error": msg}, code)

    # ---------- HTTP 方法 ----------

    def do_OPTIONS(self) -> None:
        self._send(204, b"", extra={
            "Access-Control-Max-Age": "86400",
        })

    def do_GET(self) -> None:
        try:
            self._route_get()
        except BrokenPipeError:
            pass
        except Exception as e:  # noqa: BLE001
            self._err(500, f"internal error: {e}")

    def do_POST(self) -> None:
        try:
            self._route_post()
        except BrokenPipeError:
            data = b""
        except Exception as e:  # noqa: BLE001
            self._err(500, f"internal error: {e}")

    def log_message(self, fmt, *args) -> None:
        pass  # 静默访问日志

    # ---------- 参数工具 ----------

    def _query(self):
        return parse_qs(urlparse(self.path).query)

    def _qget(self, q, key: str, default: str = "") -> str:
        vals = q.get(key)
        return vals[0] if vals else default

    def _read_body(self) -> dict:
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        if not raw:
            return {}
        try:
            data = json.loads(raw.decode("utf-8"))
            return data if isinstance(data, dict) else {}
        except (ValueError, UnicodeDecodeError):
            return {}

    # ---------- 路由 ----------

    def _route_get(self) -> None:
        path = urlparse(self.path).path
        if path == "/" or not path.startswith("/api/"):
            self._serve_static(path)
            return
        q = self._query()
        if path == "/api/status":
            self._api_status()
        elif path == "/api/draws":
            self._api_draws(q)
        elif path == "/api/stats":
            self._api_stats(q)
        elif path == "/api/omit":
            self._api_omit(q)
        elif path == "/api/predict":
            self._api_predict(q)
        else:
            self._err(404, f"not found: {path}")

    def _route_post(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/filter":
            self._api_filter()
        elif path == "/api/pick":
            self._api_pick()
        else:
            self._err(404, f"not found: {path}")

    # ---------- 端点实现 ----------

    def _api_status(self) -> None:
        from datetime import datetime, timedelta

        conn = _conn
        config.init_paths()
        newest = db.newest_draw(conn)
        first_expect, last_expect = db.expect_range(conn)
        fstate = fetcher.get_state()
        now_dt = datetime_now_utc8()
        today = now_dt.strftime("%Y-%m-%d")
        draw_dt = datetime.strptime(f"{today} 21:32:32", "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=now_dt.tzinfo
        )
        if draw_dt <= now_dt:
            draw_dt += timedelta(days=1)
        codes = [f"{newest[f'n{i}']:02d}" for i in range(1, 7)] if newest else []
        special = f"{newest['special']:02d}" if newest else None
        self._json({
            "ok": True,
            "service": "macaujc-predictor",
            "version": "1.1.9",
            "last_draw": {
                "expect": newest["expect"] if newest else None,
                "open_time": newest["open_time"] if newest else None,
                "codes": codes,
                "special": special,
            },
            "db": {
                "total_draws": db.total_draws(conn),
                "first_expect": first_expect,
                "last_expect": last_expect,
                "last_sync": fstate.get("last_fetch") or None,
            },
            "fetcher": {
                "running": fstate.get("running", False),
                "last_fetch": fstate.get("last_fetch") or None,
                "last_error": fstate.get("last_error"),
            },
            "next_draw_at": draw_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "server_time": now_dt.strftime("%Y-%m-%d %H:%M:%S"),
        })

    def _api_draws(self, q) -> None:
        try:
            limit = max(0, min(int(self._qget(q, "limit", "50")), 1000))
            offset = max(0, int(self._qget(q, "offset", "0")))
        except ValueError:
            self._err(400, "limit/offset must be integers")
            return
        conn = _conn
        rows = db.draws_desc(conn, limit, offset)
        items = []
        for d in rows:
            open_date = str(d["open_time"])[:10]
            year = int(open_date[:4])
            nums = [int(d[f"n{i}"]) for i in range(1, 7)] + [int(d["special"])]
            attrs7 = [zw.attrs_for_number(n, open_date, year) for n in nums]
            items.append({
                "expect": d["expect"],
                "open_time": d["open_time"],
                "codes": [f"{n:02d}" for n in nums[:6]],
                "special": f"{nums[6]:02d}",
                "wave":   [a["wave"] for a in attrs7],
                "zodiac": [a["zodiac"] for a in attrs7],
                "wuxing": [a["wuxing"] for a in attrs7],
                "odd_even": [a["odd_even"] for a in attrs7],
                "big_small": [a["big_small"] for a in attrs7],
                "head": [a["head"] for a in attrs7],
                "tail": [a["tail"] for a in attrs7],
                "he_sum": [a["he_sum"] for a in attrs7],
            })
        self._json({
            "ok": True,
            "total": db.total_draws(conn),
            "limit": limit,
            "offset": offset,
            "items": items,
        })

    def _api_stats(self, q) -> None:
        dim_param = self._qget(q, "dim", "")
        try:
            window = max(1, min(int(self._qget(q, "window", "100")), 5000))
        except ValueError:
            self._err(400, "window must be an integer")
            return
        resolved = stats_engine.resolve_dim(dim_param)
        if not resolved:
            self._err(400, "invalid dim, expect special_*|normal_* with "
                           "number|wave|zodiac|wuxing|odd_even|big_small|head|tail|he_sum")
            return
        scope, dim = resolved
        self._json(stats_engine.calc_stats(_conn, scope, dim, window))

    def _api_omit(self, q) -> None:
        scope = self._qget(q, "scope", "special")
        if scope not in ("special", "normal"):
            self._err(400, "scope must be special|normal")
            return
        self._json(stats_engine.calc_omit(_conn, scope))

    def _api_predict(self, q) -> None:
        mode = self._qget(q, "mode", "composite")
        scope = self._qget(q, "scope", "special")
        if mode not in predictors.MODES:
            self._err(400, f"mode must be one of {list(predictors.MODES)}")
            return
        if scope not in predictors.SCOPES:
            self._err(400, f"scope must be one of {list(predictors.SCOPES)}")
            return
        try:
            count = max(1, min(int(self._qget(q, "count", "10")), 49))
            window = max(1, min(int(self._qget(q, "window", "100")), 5000))
        except ValueError:
            self._err(400, "count/window must be integers")
            return
        self._json(predictors.predict(_conn, mode, scope, count, window))

    def _api_filter(self) -> None:
        body = self._read_body()
        groups = body.get("groups")
        if groups is None:
            groups = {}
        if not isinstance(groups, dict):
            self._err(400, "groups must be an object")
            return
        union = picker_engine.union_view(groups)
        remaining = picker_engine.apply_groups(groups)
        self._json({
            "union": union,
            "remaining": remaining,
            "count": len(remaining),
        })

    def _api_pick(self) -> None:
        body = self._read_body()
        try:
            count = int(body.get("count", 7))
        except (TypeError, ValueError):
            count = 7
        count = max(1, min(count, 7))
        pool = str(body.get("pool", "composite"))
        filters = body.get("filters") or {}
        if not isinstance(filters, dict):
            self._err(400, "filters must be an object")
            return
        try:
            window = int(body.get("window", 100))
        except (TypeError, ValueError):
            window = 100
        window = max(1, min(window, 5000))
        self._json(predictors.pick_sets(_conn, count, pool, filters, window))

    # ---------- 静态文件 ----------

    def _serve_static(self, path: str) -> None:
        config.init_paths()
        web_root = os.path.join(config.BASE_DIR, "web")
        if path in ("", "/"):
            path = "/index.html"
        rel = os.path.normpath(path.lstrip("/"))
        if rel.startswith(".."):
            self._err(403, "forbidden")
            return
        full = os.path.join(web_root, rel)
        if not os.path.isfile(full):
            # SPA 回退到 index.html
            full = os.path.join(web_root, "index.html")
            if not os.path.isfile(full):
                self._send(200, _FALLBACK_HTML.encode("utf-8"),
                           ctype="text/html; charset=utf-8")
                return
        ctype = _guess_type(full)
        with open(full, "rb") as f:
            body = f.read()
        self._send(200, body, ctype=ctype)


_FALLBACK_HTML = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>macaujc-predictor</title></head>
<body style="font-family:sans-serif;max-width:640px;margin:40px auto">
<h1>macaujc-predictor 后端已启动</h1>
<p>web/index.html 尚未部署。API 端点:</p>
<ul>
<li>GET /api/status</li><li>GET /api/draws?limit=50</li>
<li>GET /api/stats?window=100&amp;dim=special_number</li>
<li>GET /api/omit?scope=special</li><li>GET /api/predict?mode=composite</li>
<li>POST /api/filter</li><li>POST /api/pick</li>
</ul>
</body></html>"""

_MIME = {
    ".html": "text/html; charset=utf-8",
    ".htm": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".mjs": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".ttf": "font/ttf",
    ".map": "application/json",
    ".txt": "text/plain; charset=utf-8",
}


def _guess_type(path: str) -> str:
    return _MIME.get(os.path.splitext(path)[1].lower(), "application/octet-stream")


def datetime_now_utc8():
    from datetime import datetime, timedelta, timezone

    return datetime.now(timezone(timedelta(hours=8)))


from datetime import datetime, timedelta  # noqa: E402  (_api_status 用)
