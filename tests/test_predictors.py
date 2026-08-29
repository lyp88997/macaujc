"""predictors (composite/hot/cold/omission 打分 + pick) 合成数据测试。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, predictors, picker_engine

DB = "/tmp/macaujc_test_pred.db"
if os.path.exists(DB):
    os.remove(DB)
conn = db.connect(DB)
db.init_schema(conn)

# 构造 60 期: 特码 1-20 循环 → 热/冷差异明显; 日期跨 2026 (马年)
import random
random.seed(7)
recs = []
for i in range(60):
    sp = (i % 20) + 1
    six = random.sample([n for n in range(1, 50) if n != sp], 6)
    recs.append({
        "expect": f"2026{i+1:03d}",
        "openTime": f"2026-01-{(i % 28) + 1:02d} 21:32:32",
        "openCode": ",".join(f"{n:02d}" for n in six) + f",{sp:02d}",
    })
db.upsert_draws(recs)

# --- composite ---
p = predictors.predict(conn, "composite", "special", 10, 100)
assert p["mode"] == "composite" and p["scope"] == "special" and p["window"] == 60
assert p["disclaimer"] == "统计分析仅供参考,不构成任何中奖承诺"
assert len(p["items"]) == 10
assert p["items"][0]["rank"] == 1
first = p["items"][0]
assert set(first["attrs"]) == {"wave", "zodiac", "wuxing", "head", "tail", "he"}
assert 0 <= first["score"] <= 100, first["score"]
assert isinstance(first["reasons"], list) and len(first["reasons"]) >= 2
for r in first["reasons"]:
    assert isinstance(r, str) and r
# generated_at 当天固定
assert p["generated_at"].startswith(predictors.today_str())
print("predict composite OK, top3:", [(it["number"], it["score"]) for it in p["items"][:3]])

# --- 日种子稳定性: 同一天重复打分结果一致 ---
p2 = predictors.predict(conn, "composite", "special", 10, 100)
assert [it["number"] for it in p["items"]] == [it["number"] for it in p2["items"]]
assert [it["score"] for it in p["items"]] == [it["score"] for it in p2["items"]]
print("day-seed stability OK")

# 无历史号码也应获得遗漏压力, 不能因 avg=None 被错误压成 0
_, boundary_feat = predictors.composite_scores(conn, "special", 100)
unseen = [x for x in boundary_feat["num_omission"] if boundary_feat["appear_count"].get(int(x), 0) == 0]
assert unseen
boundary_scores, _ = predictors.composite_scores(conn, "special", 100)
by_num = {x["number"]: x for x in boundary_scores}
assert all(by_num[x]["feat"]["omit_norm"] > 0 for x in unseen)
print("unseen omission pressure OK")

# --- hot / cold / omission ---
ph = predictors.predict(conn, "hot", "special", 5, 100)
# 1-20 各出现 3 次(60期循环) → 全部并列, tiebreak 用 score
assert len(ph["items"]) == 5
pc = predictors.predict(conn, "cold", "special", 5, 100)
assert len(pc["items"]) == 5
po = predictors.predict(conn, "omission", "special", 5, 100)
# 21-49 从未出现 (omission=60) 排最前
assert int(po["items"][0]["number"]) > 20, po["items"][0]
print("hot/cold/omission OK")

# --- scope=normal ---
pn = predictors.predict(conn, "composite", "normal", 10, 100)
assert pn["scope"] == "normal" and len(pn["items"]) == 10
print("scope=normal OK")

# --- 参数边界 ---
pe = predictors.predict(conn, "composite", "special", 200, 100)  # count 截到 49
assert len(pe["items"]) == 49
print("param clamp OK")

# --- pick count=7 ---
pk = predictors.pick_sets(conn, 7, "composite", None, 100)
assert pk["strategy_note"] == "前6=推荐池按分取,第7=特码推荐"
assert len(pk["sets"]) == 1 and len(pk["sets"][0]) == 7
s = pk["sets"][0]
assert len(set(s)) == 7, s  # 不重复
assert all(len(x) == 2 for x in s)
print("pick composite OK:", s)

# pick + filters (生肖马: 池只有 5 个号 → 7 位不可满足, 返回不重复的最大可用集合)
pk2 = predictors.pick_sets(conn, 7, "all", {"zodiac": ["馬"]}, 100)
s2 = pk2["sets"][0]
zm = picker_engine.zodiac_numbers()
assert set(s2) <= {f"{n:02d}" for n in zm["馬"]}, s2
assert len(set(s2)) == len(s2) == 5, s2  # 5 独立号全取, 无重复
print("pick all+filter (pool<7 degrade) OK:", s2)

# pick hot pool
pk3 = predictors.pick_sets(conn, 7, "hot", {"wave": ["红"]}, 100)
s3 = pk3["sets"][0]
RED = {1,2,7,8,12,13,18,19,23,24,29,30,34,35,40,45,46}
assert set(int(x) for x in s3) <= RED, s3
print("pick hot+wave OK:", s3)

# pick 的前六位按平码 scope, 末位按特码 scope; 两个池都必须遵守筛选条件
normal_pred = predictors.predict(conn, "composite", "normal", 49, 100)
special_pred = predictors.predict(conn, "composite", "special", 49, 100)
pk_scope = predictors.pick_sets(conn, 7, "composite", None, 100)
assert pk_scope["sets"]
assert pk_scope["sets"][0][:6] == [x["number"] for x in normal_pred["items"][:6]]
assert pk_scope["sets"][0][-1] == next(
    x["number"] for x in special_pred["items"] if x["number"] not in pk_scope["sets"][0][:6]
)
print("pick normal/special scope separation OK")

print("ALL PREDICTOR TESTS PASSED")
