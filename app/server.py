"""macaujc-predictor — 澳门六合彩号码统计分析服务

Python 3.11+ 标准库实现 (http.server + sqlite3 + urllib)。
按 tasks/api_contract.md v1.0 实现:

    python3 server.py [--port 8000] [--db /app/data/macaujc.db]

容器内监听 0.0.0.0:8000; GET / → web/index.html 静态服务; GET /api/* → JSON;
全部响应带 CORS: *。首次启动后台线程批量采集 2020..2026 历史并每 300s 增量同步。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
from datetime import datetime, timedelta, timezone

# 保证 `python3 app/server.py` 与 `python3 -m app.server` 均可用
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import config, db, fetcher, http_api, predictors, stats_engine, zodiac_wuxing

__version__ = "1.1.9"


def main() -> None:
    ap = argparse.ArgumentParser(description="macaujc-predictor backend")
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")))
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--db", default=None, help="SQLite 路径, 默认 /app/data/macaujc.db")
    args = ap.parse_args()

    config.init_paths()
    db_path = args.db or config.DB_PATH
    conn = db.connect(db_path)
    db.init_schema(conn)

    http_api.set_shared_state(conn, db_path)
    fetcher.start(conn)
    srv = http_api.make_server(args.host, args.port)
    print(f"[server] listening on http://{args.host}:{args.port}  db={db_path}", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        fetcher.stop()
        srv.server_close()
        conn.close()


if __name__ == "__main__":
    main()
