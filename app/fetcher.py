"""后台数据采集线程。

首次启动: GET https://history.macaumarksix.com/history/macaujc2/y/{year}, year=2020..2026
  - 成功判定: code==200 且 data 为非空数组 (HTTP 200 不代表命中; code=0/data=null 判空)
  - 年份间混装/滚动窗: 一律按 expect 全局去重, openCode 两位零填充逗号分隔 7 个
增量: 每 300s GET https://macaumarksix.com/api/macaujc2.com (顶层 JSON 数组, 无包装)
  - 抓 expect/openCode/openTime, 新期号才入库
请求间隔 >=0.5s, 超时 <=10s。
"""

from __future__ import annotations

import json
import threading
import time
import urllib.request
from typing import Dict, List, Optional

from . import config, db

HISTORY_URL = "https://history.macaumarksix.com/history/macaujc2/y/{year}"
LATEST_URL = "https://macaumarksix.com/api/macaujc2.com"
SYNC_INTERVAL = 300.0  # 秒
REQ_INTERVAL = 0.6  # 请求间隔 >= 0.5s
REQ_TIMEOUT = 10.0  # 超时 <= 10s
FIRST_YEARS = list(range(2020, 2027))  # 2020..2026

_state_lock = threading.Lock()
_state = {"running": False, "last_fetch": "", "last_error": None}


def get_state() -> Dict:
    with _state_lock:
        return dict(_state)


def _set_state(**kw) -> None:
    with _state_lock:
        _state.update(kw)


def _http_get_json(url: str):
    req = urllib.request.Request(
        url, headers={"User-Agent": "macaujc-predictor/1.0", "Accept": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=REQ_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_history_payload(payload) -> List[Dict]:
    """历史响应 → 有效记录列表。判空: code==200 且 data 非空。"""
    if not isinstance(payload, dict):
        return []
    if payload.get("code") != 200:
        return []
    data = payload.get("data")
    if not isinstance(data, list) or not data:
        return []
    return [r for r in data if isinstance(r, dict) and r.get("expect") and r.get("openCode")]


def parse_latest_payload(payload) -> List[Dict]:
    """latest 响应为顶层 JSON 数组(无包装)。"""
    if not isinstance(payload, list):
        return []
    return [r for r in payload if isinstance(r, dict) and r.get("expect") and r.get("openCode")]


def _sleep_interval() -> None:
    time.sleep(REQ_INTERVAL)


def initial_backfill(conn) -> None:
    """批量采集 2020..2026, 全局按 expect 去重后入库。"""
    seen: Dict[str, Dict] = {}
    for year in FIRST_YEARS:
        url = HISTORY_URL.format(year=year)
        try:
            payload = _http_get_json(url)
            recs = parse_history_payload(payload)
        except Exception as e:  # 网络异常不中断整体采集
            _set_state(last_error=f"history y{year}: {e}")
            recs = []
        for r in recs:
            seen[str(r["expect"])] = r  # expect 全局去重(年份间混装)
        _set_state(last_fetch=db.datetime_utc8_str())
        _sleep_interval()
    if seen:
        added = db.upsert_draws(seen.values())
        print(f"[fetcher] backfill: {len(seen)} unique expects, {added} new", flush=True)


def sync_latest(conn) -> None:
    """增量: latest 端点, 新期号才入库。"""
    try:
        payload = _http_get_json(LATEST_URL)
        recs = parse_latest_payload(payload)
    except Exception as e:
        _set_state(last_fetch=db.datetime_utc8_str(), last_error=f"latest: {e}")
        return
    _set_state(last_fetch=db.datetime_utc8_str(), last_error=None)
    if not recs:
        return
    try:
        fresh = [r for r in recs if not db.has_expect(conn, str(r["expect"]))]
        if fresh:
            added = db.upsert_draws(fresh)
            print(f"[fetcher] sync: +{added} ({', '.join(str(r['expect']) for r in fresh)})", flush=True)
    except Exception as e:
        _set_state(last_error=f"sync db: {e}")


def _loop(conn) -> None:
    # 首次采集(库空或无 meta 标记时), 之后进入增量循环
    try:
        if db.total_draws(conn) == 0 or not db.get_meta(conn, "backfill_done"):
            initial_backfill(conn)
            if db.total_draws(conn) > 0:
                db.set_meta(conn, "backfill_done", "1")
    except Exception as e:
        _set_state(last_error=f"backfill: {e}")
        if db.total_draws(conn) > 0:
            try:
                db.set_meta(conn, "backfill_done", "1")
            except Exception:
                pass
    while not _stop_event.is_set():
        try:
            sync_latest(conn)
        except Exception as e:
            _set_state(last_error=f"loop: {e}")
        _stop_event.wait(SYNC_INTERVAL)


_stop_event = threading.Event()
_thread: Optional[threading.Thread] = None


def start(conn) -> None:
    global _thread
    if _thread is not None and _thread.is_alive():
        return
    _stop_event.clear()
    _set_state(running=True)
    _thread = threading.Thread(target=_loop, args=(conn,), name="fetcher", daemon=True)
    _thread.start()


def stop() -> None:
    _stop_event.set()
    _set_state(running=False)
