# BATCH-019 编辑脚本(历史页: 特码球对齐平码+生肖中心线+电脑端左靠期号)
P = "/opt/data/workspace/macaujc-predictor/web/index.html"
src = open(P, encoding="utf-8").read()
n0 = len(src)
edits = []

def rep(old, new, tag):
    global src
    n = src.count(old)
    assert n == 1, f"[{tag}] 命中{n}次, 应为1"
    src = src.replace(old, new)
    edits.append(tag)

# --- 1) 电脑端: 球行左对齐贴期号列(center→flex-start) ---
rep('.his-row{display:flex;flex-wrap:wrap;justify-content:center;align-items:flex-start;gap:clamp(8px,1vw,16px) clamp(8px,1vw,16px)}',
    '.his-row{display:flex;flex-wrap:wrap;justify-content:flex-start;align-items:flex-start;gap:clamp(8px,1vw,16px) clamp(8px,1vw,16px)}',
    "电脑端球行左对齐")

# --- 2) 特码球对齐平码(桌面): 48→48已是cap, 但起点36改42与sm一致, 字号同步 ---
# 注: .his-row .ball.sm 是 33..42, 特码 .ball 36..48 → 统一 clamp(33px,2.7vw,42px)
rep('.his-row .ball{width:clamp(36px,3vw,48px);height:clamp(36px,3vw,48px);font-size:clamp(14px,1.2vw,18px)}',
    '.his-row .ball{width:clamp(33px,2.7vw,42px);height:clamp(33px,2.7vw,42px);font-size:clamp(13px,1.1vw,16.5px)}',
    "桌面特码球对齐平码")

# --- 3) 手机端特码球对齐平码: 26..32 → 24..29 ---
rep('.his-row .ball{width:clamp(26px,7.3vw,32px);height:clamp(26px,7.3vw,32px);font-size:clamp(11.5px,3.1vw,13.5px)}',
    '.his-row .ball{width:clamp(24px,6.8vw,29px);height:clamp(24px,6.8vw,29px);font-size:clamp(10.5px,2.9vw,12.5px)}',
    "手机特码球对齐平码")

# --- 4) 手机端球行居中保持(520档, 不回退018) ---
rep('.his-row{flex-wrap:nowrap;gap:1.2vw;align-items:flex-start}',
    '.his-row{flex-wrap:nowrap;gap:1.2vw;justify-content:center;align-items:flex-start}',
    "手机端球行保持居中")

# --- 5) 桌面间距: 行gap首值(clamp 8,1vw,16)是纵向gap, 保留; 确保对齐后生肖行齐 ---
# (无改动, 生肖行齐平由2/3刀达成)

# --- 6) 生肖字: 特码列与平码列同字号(桌面17/手机12), 已由 .zlabel clamp 统一, 无需改 ---

open(P, "w", encoding="utf-8").write(src)
print(f"共 {len(edits)} 刀全部落盘: {'、'.join(edits)}")
print(f"体积 {n0} → {len(src)} ({len(src)-n0:+d})")