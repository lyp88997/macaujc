"""stats_engine + db 层合成数据测试。"""
import sys, os, sqlite3, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, stats_engine

DB = "/tmp/macaujc_test_stats.db"
if os.path.exists(DB):
    os.remove(DB)
conn = db.connect(DB)
db.init_schema(conn)

# 构造 20 期合成数据: 特码已知序列, 校验遗漏/统计
# expect 2001001..2001020, special = 5,5,5,9,9,1,... (可推算)
import random
random.seed(42)
recs = []
specials = [5,5,5,9,9,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
for i in range(20):
    sp = specials[i]
    six = [n for n in range(1, 50) if n != sp][:6]
    recs.append({
        "expect": f"2001{i+1:03d}",
        "openTime": f"2001-01-{i+1:02d} 21:32:32",
        "openCode": ",".join(f"{n:02d}" for n in six) + f",{sp:02d}",
    })
db.upsert_draws(recs)

# --- stats: special_number, window=20 ---
st = stats_engine.calc_stats(conn, "special", "number", 20)
assert st["window"] == 20
items = {it["key"]: it for it in st["items"]}
assert len(items) == 49, len(items)  # 全域 49
assert items["05"]["count"] == 4
assert items["05"]["rate"] == 0.2
assert items["05"]["last_expect"] == "2001010"  # 第10期
assert items["05"]["omission"] == 10  # 20-10
assert items["49"]["count"] == 0 and items["49"]["omission"] == 20
# count 降序
counts = [it["count"] for it in st["items"]]
assert counts == sorted(counts, reverse=True)
print("stats special_number OK")

# --- stats: special_wave, window=20 ---
stw = stats_engine.calc_stats(conn, "special", "wave", 20)
itw = {it["key"]: it for it in stw["items"]}
assert set(itw) == {"红", "蓝", "绿"}
# 5绿,9红; 1蓝,3蓝? 1蓝? wave_of:1红,2蓝,3蓝,4蓝,6蓝,7红,8红,10蓝...
# 手工: specials 5,5,5,9,9,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
# 红: 5,5,5,9,9,1,7,9,13 = 9 ; 蓝: 2,3,4,6,10,14 = 6 ; 绿: 5(第10),8,11,12,15 = 5 → 合计20
# specials 波色实测: 红6 蓝8 绿6
assert itw["红"]["count"] == 6, itw["红"]
assert itw["蓝"]["count"] == 8
assert itw["绿"]["count"] == 6
print("stats special_wave OK")

# --- stats: normal_number (6 平码/期) ---
stn = stats_engine.calc_stats(conn, "normal", "number", 20)
itn = {it["key"]: it for it in stn["items"]}
# 平码 = 1..6 中除特码外的号码, 每期 6 个 → 总 120 槽
assert sum(it["count"] for it in stn["items"]) == 120
# 号码 1: 除 sp=1 (第6期) 外每期都在平码 → 19 次
assert itn["01"]["count"] == 19, itn["01"]
# 号码 7: six=前6个非特码; specials 中 sp>=7 且 sp!=7 的期数 = 期 12..20 (9 期)
assert itn["07"]["count"] == 9, itn["07"]
print("stats normal_number OK")

# --- omit: special ---
om = stats_engine.calc_omit(conn, "special")
assert set(om) == {"number", "wave", "zodiac", "tail", "head", "wuxing"}
omn = {it["key"]: it for it in om["number"]}
assert len(omn) == 49
assert omn["05"]["omission"] == 10
# positions(idx) 0,1,2,9 → gaps 0,0,6 → max=6, avg=2.0
assert omn["05"]["max_omission"] == 6, omn["05"]
# 平均: (0+0+6)/3 = 2.0
assert omn["05"]["avg_omission"] == 2.0, omn["05"]
# 49 从未出现
assert omn["49"]["omission"] == 20 and omn["49"]["max_omission"] == 20 and omn["49"]["avg_omission"] is None
# tail
omt = {it["key"]: it for it in om["tail"]}
assert len(omt) == 10
print("omit OK")

# --- 边界: 空库 ---
DB2 = "/tmp/macaujc_test_empty.db"
if os.path.exists(DB2):
    os.remove(DB2)
conn2 = db.connect(DB2)
db.init_schema(conn2)
st2 = stats_engine.calc_stats(conn2, "special", "number", 100)
assert st2 == {"window": 0, "from_expect": None, "to_expect": None, "items": []}
om2 = stats_engine.calc_omit(conn2, "special")
assert om2["number"][0]["omission"] == 0  # n_total=0
print("empty-db edge OK")
print("ALL STATS TESTS PASSED")
