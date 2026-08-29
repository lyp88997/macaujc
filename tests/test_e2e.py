#!/usr/bin/env python3
"""端到端验收: 启动服务(合成数据) → 7 个端点全部请求 → 校验契约结构。"""
import json
import os
import signal
import subprocess
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8990
BASE = f"http://127.0.0.1:{PORT}"

# 预置合成库: 3 期
sys.path.insert(0, ROOT)
from app import db as dbm  # noqa: E402

DBP = "/tmp/macaujc_e2e.db"
for suf in ("", "-wal", "-shm"):
    p = DBP + suf
    if os.path.exists(p):
        os.remove(p)
conn = dbm.connect(DBP)
dbm.init_schema(conn)
dbm.upsert_draws([
    {"expect": "2026001", "openTime": "2026-01-01 21:32:32", "openCode": "01,02,03,04,05,06,07"},
    {"expect": "2026002", "openTime": "2026-01-02 21:32:32", "openCode": "10,11,12,13,14,15,16"},
    {"expect": "2026003", "openTime": "2026-01-03 21:32:32", "openCode": "40,41,42,43,44,45,46"},
])
conn.close()

env = dict(os.environ)
proc = subprocess.Popen(
    [sys.executable, os.path.join(ROOT, "app", "server.py"),
     "--port", str(PORT), "--db", DBP],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env,
)
try:
    for _ in range(40):
        time.sleep(0.5)
        try:
            urllib.request.urlopen(f"{BASE}/api/status", timeout=2)
            break
        except Exception:
            continue
    results = {}

    def get(path):
        with urllib.request.urlopen(f"{BASE}{path}", timeout=10) as r:
            return r.status, dict(r.headers), json.loads(r.read().decode())

    def post(path, body):
        req = urllib.request.Request(
            f"{BASE}{path}", data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, dict(r.headers), json.loads(r.read().decode())

    # 1 status
    st, hd, d = get("/api/status")
    assert st == 200 and d["ok"] and d["service"] == "macaujc-predictor"
    import re as _re, pathlib as _pl
    _ver = _re.search(r'__version__\s*=\s*"(\d+\.\d+\.\d+)"', _pl.Path(__file__).resolve().parents[1].joinpath("app/server.py").read_text(encoding="utf-8"))
    assert _ver, "server.py 中未找到 __version__"
    assert d["version"] == _ver.group(1)
    assert d["last_draw"]["expect"] == "2026003"
    assert d["last_draw"]["codes"] == ["40", "41", "42", "43", "44", "45"]
    assert d["last_draw"]["special"] == "46"
    assert d["db"]["total_draws"] == 3
    assert d["fetcher"]["running"] is True
    assert d["next_draw_at"].endswith("21:32:32")
    assert hd.get("Access-Control-Allow-Origin") == "*"
    results["status"] = "PASS"

    # 2 draws
    st, hd, d = get("/api/draws?limit=2&offset=0")
    assert st == 200 and d["ok"] and d["total"] == 3
    assert [it["expect"] for it in d["items"]] == ["2026003", "2026002"]  # newest first
    it = d["items"][0]
    for k in ("wave", "zodiac", "wuxing", "odd_even", "big_small", "head", "tail", "he_sum"):
        assert isinstance(it[k], list) and len(it[k]) == 7, k
    assert it["wave"] == ["红", "蓝", "蓝", "绿", "绿", "红", "红"]
    assert it["big_small"] == ["大", "大", "大", "大", "大", "大", "大"]
    results["draws"] = "PASS"

    # 3 stats
    st, hd, d = get("/api/stats?window=3&dim=special_number")
    assert st == 200 and d["window"] == 3
    assert len(d["items"]) == 49
    m = {x["key"]: x for x in d["items"]}
    assert m["07"]["count"] == 1 and m["07"]["last_expect"] == "2026001"
    assert m["46"]["count"] == 1 and m["46"]["omission"] == 0
    assert sum(x["count"] for x in d["items"]) == 3
    results["stats"] = "PASS"

    st, hd, d = get("/api/stats?window=3&dim=special_wave")
    assert len(d["items"]) == 3
    st, hd, d = get("/api/stats?window=3&dim=normal_zodiac")
    assert len(d["items"]) == 12
    st, hd, d = get("/api/stats?window=3&dim=normal_he_sum")
    assert len(d["items"]) == 13
    results["stats dims"] = "PASS"

    # 4 omit
    st, hd, d = get("/api/omit?scope=special")
    assert st == 200
    assert set(d) == {"number", "wave", "zodiac", "tail", "head", "wuxing"}
    assert len(d["number"]) == 49 and len(d["wave"]) == 3
    om = {x["key"]: x for x in d["number"]}
    assert om["46"]["omission"] == 0
    assert om["20"]["omission"] == 3  # 从未出现
    results["omit"] = "PASS"

    # 5 predict
    st, hd, d = get("/api/predict?mode=composite&count=5&window=3&scope=special")
    assert st == 200 and len(d["items"]) == 5
    assert d["items"][0]["rank"] == 1
    assert set(d["items"][0]["attrs"]) == {"wave", "zodiac", "wuxing", "head", "tail", "he"}
    assert d["items"][0]["reasons"]
    assert d["disclaimer"] == "统计分析仅供参考,不构成任何中奖承诺"
    for mode in ("hot", "cold", "omission"):
        st, hd, d2 = get(f"/api/predict?mode={mode}&count=3&window=3")
        assert st == 200 and len(d2["items"]) == 3
    results["predict"] = "PASS"

    # 6 filter
    st, hd, d = post("/api/filter", {"groups": {"wave": ["红"], "big_small": ["大"]}})
    assert st == 200 and d["count"] == len(d["remaining"])
    assert d["remaining"] == ["29", "30", "34", "35", "40", "45", "46"], d["remaining"]
    assert d["union"]["wave"][0] == "01"
    results["filter"] = "PASS"

    # 7 pick
    st, hd, d = post("/api/pick", {"count": 7, "pool": "all", "filters": {}})
    assert st == 200 and len(d["sets"][0]) == 7
    assert len(set(d["sets"][0])) == 7
    assert d["strategy_note"] == "前6=推荐池按分取,第7=特码推荐"
    results["pick"] = "PASS"

    print(json.dumps(results, ensure_ascii=False, indent=2))
    print("E2E ALL PASS")
finally:
    proc.send_signal(signal.SIGTERM)
    try:
        proc.wait(5)
    except subprocess.TimeoutExpired:
        proc.kill()
