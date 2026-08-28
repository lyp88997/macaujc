import sys
sys.path.insert(0, ".")
from app import picker_engine as pe
from app import zodiac_wuxing as zw

ctx = {"zodiac": pe.zodiac_numbers(), "wuxing": pe.wuxing_numbers()}
zm = ctx["zodiac"]; wm = ctx["wuxing"]

# 1) 生肖 2026 马年槽位验证
assert zm["馬"] == {1,13,25,37,49} and zm["蛇"] == {2,14,26,38} and zm["羊"] == {12,24,36,48}, zm
assert len(zm) == 12 and sum(len(v) for v in zm.values()) == 49
print("zodiac map OK")

# 2) 五行 2026 表 (wuxing_numbers 返回零填充字符串)
assert wm["金"] == {"04","05","12","13","26","27","34","35","42","43"}, wm["金"]
assert sum(len(v) for v in wm.values()) == 49
print("wuxing map OK")

# 3) 家野
fam = set().union(*[zm[z] for z in ("牛","馬","羊","雞","狗","豬")])
wild = set().union(*[zm[z] for z in ("兔","虎","鼠","猴","蛇","龍")])
assert len(fam | wild) == 49 and not (fam & wild)
print("family/wild OK", len(fam), len(wild))

# 4) filter 验证
r = pe.apply_groups({"zodiac": ["馬","蛇"]})
assert r == sorted({"01","13","25","37","49","02","14","26","38"}), r
r2 = pe.apply_groups({"zodiac": ["馬","蛇"], "wave": ["红"]})
exp = {"01","13","25","37","49","02","14","26","38"} & {"01","02","07","08","12","13","18","19","23","24","29","30","34","35","40","45","46"}
assert r2 == sorted(exp), (r2, sorted(exp))
r3 = pe.apply_groups({"tail": ["5"], "odd_even": ["单"]})
exp3 = {n for n in range(1,50) if n % 10 == 5 and n % 2 == 1}
assert r3 == sorted(f"{n:02d}" for n in exp3), r3
r4 = pe.apply_groups({"big_small": ["大"], "head": ["4"]})
assert r4 == sorted(f"{n:02d}" for n in range(40,50))
r5 = pe.apply_groups({})
assert len(r5) == 49, r5
r6 = pe.apply_groups({"big_small": ["大","小"]})
assert len(r6) == 49
r7 = pe.apply_groups({"big_small": ["小"], "head": ["4"]})  # 40-49 全为大 → 空
assert r7 == [], r7
r8 = pe.apply_groups({"wuxing": ["金"]})
assert r8 == sorted(wm["金"])
r9 = pe.apply_groups({"family_wild": ["家"]})
assert r9 == sorted(f"{n:02d}" for n in fam)
u = pe.union_view({"zodiac": ["馬"], "tail": ["5"]})
assert u["zodiac"] == sorted(f"{n:02d}" for n in zm["馬"])
print("filter OK")

# 5) 合数组
rh = pe.apply_groups({"he_sum": ["合单"]})
HE_DAN = {1,3,5,7,9,10,12,14,16,18,21,23,25,27,29,30,32,34,36,38,41,43,45,47,49}
assert rh == sorted(f"{n:02d}" for n in HE_DAN)
print("he_sum group OK")
print("ALL PICKER TESTS PASSED")
