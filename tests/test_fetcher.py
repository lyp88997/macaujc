"""fetcher 解析逻辑测试(离线, 用 macaujc-analysis 保存的真实响应样本)。"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, fetcher

RAW = "/opt/data/workspace/macaujc-analysis/context/raw"

# --- 历史响应解析: code==200 且 data 非空才算成功 ---
y2026 = json.load(open(f"{RAW}/history_y2026.json"))
recs = fetcher.parse_history_payload(y2026)
assert len(recs) > 300, len(recs)
assert all(r["expect"] and r["openCode"] for r in recs)

# 未命中: code=0 / data=null
assert fetcher.parse_history_payload({"code": 0, "data": None}) == []
assert fetcher.parse_history_payload({"code": 200, "data": []}) == []
assert fetcher.parse_history_payload({"result": True, "message": "x"}) == []
assert fetcher.parse_history_payload(None) == []
assert fetcher.parse_history_payload([]) == []  # 顶层不是 dict
print("history parse OK")

# --- latest 解析: 顶层 JSON 数组 ---
latest = json.load(open(f"{RAW}/latest.json"))
lrecs = fetcher.parse_latest_payload(latest)
assert len(lrecs) == 1
assert lrecs[0]["expect"] == "2026239"
assert lrecs[0]["openCode"] == "47,43,34,17,22,07,05"
assert fetcher.parse_latest_payload({"code": 200}) == []  # 非数组
assert fetcher.parse_latest_payload(None) == []
print("latest parse OK")

# --- 入库 + 排序方向不稳定防护 ---
DB = "/tmp/macaujc_test_fetch.db"
if os.path.exists(DB):
    os.remove(DB)
conn = db.connect(DB)
db.init_schema(conn)

# y2026 样本本身降序; 再混入 y2025 与 y2023 头部混装样本模拟全局去重
y2025 = json.load(open(f"{RAW}/history_y2025.json"))
r25 = fetcher.parse_history_payload(y2025)
seen = {}
for r in recs + r25:
    seen[str(r["expect"])] = r
added = db.upsert_draws(seen.values())
assert added == len(seen), (added, len(seen))
first, last = db.expect_range(conn)
assert first == "2025001" and last == "2026239", (first, last)
total = db.total_draws(conn)
assert total == len(seen) == 604, total  # 366 + 365 - 127 (y2026 尾部混装 2025 的 127 条重叠)

# newest / draws_desc
nd = db.newest_draw(conn)
assert nd["expect"] == "2026239" and nd["special"] == 5
d0 = db.draws_desc(conn, 5, 0)[0]
assert d0["expect"] == "2026239"
d6 = db.draws_asc_limit(conn, 6)
assert d6[-1]["expect"] == "2026239" and d6[0]["expect"] == "2026234"
# n1..n6 原始顺序: 47,43,34,17,22,07 + 特 05
assert [nd[f"n{i}"] for i in range(1, 7)] == [47, 43, 34, 17, 22, 7]
print("db upsert/dedupe/order OK")

# has_expect / meta
assert db.has_expect(conn, "2026239") and not db.has_expect(conn, "2026240")
db.set_meta(conn, "backfill_done", "1")
assert db.get_meta(conn, "backfill_done") == "1"
print("meta OK")
print("ALL FETCHER TESTS PASSED")
