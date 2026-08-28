"""SQLite 存储层。

主表 draws(expect TEXT PK, open_time TEXT, n1..n6 INT, special INT, synced_at TEXT)
n1..n6 保留开奖原始顺序(平一~平六), special = 特码(第 7 位)。
"""

from __future__ import annotations

import os
import sqlite3
import threading
from typing import Dict, Iterable, List, Optional, Tuple

from . import config

# sqlite3 连接跨线程使用(check_same_thread=False) + 进程内互斥; WAL 提升读并发
_conn: Optional[sqlite3.Connection] = None
_lock = threading.RLock()


def connect(path: str) -> sqlite3.Connection:
    global _conn
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    _conn = sqlite3.connect(path, check_same_thread=False, timeout=30)
    _conn.row_factory = sqlite3.Row
    _conn.execute("PRAGMA journal_mode=WAL")
    _conn.execute("PRAGMA synchronous=NORMAL")
    return _conn


def get_conn() -> sqlite3.Connection:
    assert _conn is not None, "db.connect() not called"
    return _conn


def get_lock() -> threading.RLock:
    return _lock


def init_schema(conn: sqlite3.Connection) -> None:
    with _lock:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS draws (
                expect    TEXT PRIMARY KEY,
                open_time TEXT NOT NULL,
                n1 INT NOT NULL, n2 INT NOT NULL, n3 INT NOT NULL,
                n4 INT NOT NULL, n5 INT NOT NULL, n6 INT NOT NULL,
                special INT NOT NULL,
                synced_at TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_draws_open_time ON draws(open_time)")
        conn.commit()


def _row_to_tuple(r: Dict) -> Tuple:
    codes = [int(x) for x in str(r["openCode"]).split(",")]
    if len(codes) != 7 or any(not (1 <= n <= 49) for n in codes):
        # 上游实测: expect=2022132 openCode 含重复对 '33,33', 放宽不判重复,
        # 仅校验 7 位且 1-49; 唯一性以 expect 主键保证
        raise ValueError(f"bad openCode for expect={r.get('expect')}: {r.get('openCode')!r}")
    now = datetime_utc8_str()
    return (str(r["expect"]), str(r["openTime"]), *codes[:6], codes[6], now)


UPSERT_SQL = (
    "INSERT INTO draws(expect, open_time, n1,n2,n3,n4,n5,n6, special, synced_at) "
    "VALUES (?,?,?,?,?,?,?,?,?,?) "
    "ON CONFLICT(expect) DO UPDATE SET open_time=excluded.open_time, "
    "n1=excluded.n1, n2=excluded.n2, n3=excluded.n3, n4=excluded.n4, n5=excluded.n5, "
    "n6=excluded.n6, special=excluded.special, synced_at=excluded.synced_at"
)


def upsert_draws(records: Iterable[Dict]) -> int:
    """批量入库(INSERT OR REPLACE 语义), 返回实际新增期数。

    单条格式非法时跳过并打日志, 不中断整批。
    """
    conn = get_conn()
    rows = []
    skipped = 0
    for r in records:
        try:
            rows.append(_row_to_tuple(r))
        except ValueError as e:
            skipped += 1
            print(f"[db] skip invalid record: {e}", flush=True)
    with _lock:
        before = conn.execute("SELECT COUNT(*) FROM draws").fetchone()[0]
        conn.executemany(UPSERT_SQL, rows)
        conn.commit()
        after = conn.execute("SELECT COUNT(*) FROM draws").fetchone()[0]
    return after - before


def total_draws(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) FROM draws").fetchone()[0]


def expect_range(conn: sqlite3.Connection) -> Tuple[Optional[str], Optional[str]]:
    row = conn.execute("SELECT MIN(expect), MAX(expect) FROM draws").fetchone()
    return row[0], row[1]


def newest_draw(conn: sqlite3.Connection) -> Optional[Dict]:
    """最新一期(按 expect 排序, expect=YYYYNNN 字典序即时间序)。"""
    row = conn.execute(
        "SELECT * FROM draws ORDER BY expect DESC LIMIT 1"
    ).fetchone()
    return dict(row) if row else None


def draws_desc(conn: sqlite3.Connection, limit: int, offset: int) -> List[Dict]:
    return [
        dict(r)
        for r in conn.execute(
            "SELECT * FROM draws ORDER BY expect DESC LIMIT ? OFFSET ?", (limit, offset)
        )
    ]


def draws_asc(conn: sqlite3.Connection) -> List[Dict]:
    """全部历史升序(统计/遗漏计算用)。"""
    return [dict(r) for r in conn.execute("SELECT * FROM draws ORDER BY expect ASC")]


def draws_asc_limit(conn: sqlite3.Connection, limit: int) -> List[Dict]:
    """最近 N 期升序。"""
    return [
        dict(r)
        for r in conn.execute(
            "SELECT * FROM (SELECT * FROM draws ORDER BY expect DESC LIMIT ?) "
            "ORDER BY expect ASC",
            (limit,),
        )
    ]


def has_expect(conn: sqlite3.Connection, expect: str) -> bool:
    return conn.execute("SELECT 1 FROM draws WHERE expect=?", (expect,)).fetchone() is not None


def set_meta(conn: sqlite3.Connection, key: str, value: str) -> None:
    with _lock:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT NOT NULL)"
        )
        conn.execute(
            "INSERT INTO meta(k,v) VALUES(?,?) "
            "ON CONFLICT(k) DO UPDATE SET v=excluded.v",
            (key, value),
        )
        conn.commit()


def get_meta(conn: sqlite3.Connection, key: str, default: str = "") -> str:
    try:
        row = conn.execute("SELECT v FROM meta WHERE k=?", (key,)).fetchone()
    except sqlite3.OperationalError:
        return default
    return row[0] if row else default


def datetime_utc8_str() -> str:
    from datetime import datetime, timezone, timedelta

    return datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
