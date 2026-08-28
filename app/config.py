"""路径 / 常量 / 一次性静态数据加载(波色表等)。"""

from __future__ import annotations

import json
import os
import threading

# 本模块变量在首次启动时由 init_paths() 填充
BASE_DIR = ""          # 项目根(含 app/, web/, data/)
DATA_DIR = ""          # 默认 /app/data (SQLite 数据目录), 与项目内 data/ 复用
DB_PATH = ""           # SQLite 绝对路径
INITED = False
_LOCK = threading.Lock()

# ---------- 官方固定波色表 (api_contract.md 属性派生规则) ----------
WAVE_RED = {1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46}
WAVE_BLUE = {3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48}
WAVE_GREEN = {5, 6, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49}


def init_paths() -> None:
    """解析项目路径; 幂等。

    DB 路径优先级: $MACAUJC_DB(文件) > /app/data(若已存在, 契约路径) > <base>/data。
    注意 <base>/data 中 base=server.py 上两级目录: 容器内 COPY app/→/app/app/,
    base=/app → <base>/data=/app/data(契约路径, compose 卷挂载点); 本地开发则落在仓库 data/。
    """
    global BASE_DIR, DATA_DIR, DB_PATH, INITED
    with _LOCK:
        if INITED:
            return
        # server.py 位于 <base>/app/ 下 (容器: /app/app/server.py → base=/app)
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        BASE_DIR = base
        env_db = os.environ.get("MACAUJC_DB")
        if env_db:
            db_file = env_db
            data_dir = os.path.dirname(db_file)
        elif os.path.isdir("/app/data"):
            data_dir = "/app/data"  # 契约默认路径
        else:
            data_dir = os.path.join(base, "data")
        os.makedirs(data_dir, exist_ok=True)
        DATA_DIR = data_dir
        DB_PATH = db_file if env_db else os.path.join(data_dir, "macaujc.db")
        INITED = True


def lunar_table_path() -> str:
    # 优先 app/data/ (任务说明: raw 表已复制进 app/data/), 兜底 data/ 与 context/raw/
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (
        os.path.join(here, "data", "lunar_table_1900_2100.json"),
        os.path.join(BASE_DIR, "data", "lunar_table_1900_2100.json"),
        os.path.join(BASE_DIR, "context", "raw", "lunar_table_1900_2100.json"),
    ):
        if os.path.exists(p):
            return p
    return os.path.join(here, "data", "lunar_table_1900_2100.json")


def wuxing_table_path() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (
        os.path.join(here, "data", "wuxing_table.json"),
        os.path.join(BASE_DIR, "data", "wuxing_table.json"),
        os.path.join(BASE_DIR, "context", "raw", "wuxing_table.json"),
    ):
        if os.path.exists(p):
            return p
    return os.path.join(here, "data", "wuxing_table.json")


def _load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_lunar_table():
    return _load_json(lunar_table_path())


def load_wuxing_table():
    return _load_json(wuxing_table_path())
