# BATCH-017 编辑脚本(预测页摘要中文化+窗口带期+历史页响应式缩放)
P = "/opt/data/workspace/macaujc-predictor/web/index.html"
src = open(P, encoding="utf-8").read()
n0 = len(src)
edits = []

def rep(old, new, tag):
    global src
    n = src.count(old)
    assert n == 1, f"[{tag}] 命中 {n} 次(须唯一): {old[:60]}"
    src = src.replace(old, new)
    edits.append(tag)

# ===== 预测推荐页 =====
# 1) 模式中文映射表(PD_LAST 声明旁)
rep("let PD_LAST=null;",
    'let PD_LAST=null;const MODE_TXT={composite:"综合模式",hot:"热号模式",cold:"冷号模式",omission:"遗漏模式"};',
    "模式映射表")

# 2) 推荐组合结果摘要中文化(四模式全覆盖, 用户示例逐字)
rep('${r.mode} · ${r.scope==="special"?"特码":"平码"} · window ${r.window} · ${items.length} 个号码（单击号码复制全部）',
    '${MODE_TXT[r.mode]||r.mode} · ${r.scope==="special"?"特码":"平码"} · 窗口 ${r.window}期 · ${items.length} 个号码（单击号码复制全部）',
    "摘要中文化")

# 3) 复制文案里夹英文的 mode 同步治
rep("【预测推荐组合】模式:${p.mode} 范围:",
    "【预测推荐组合】模式:${MODE_TXT[p.mode]||p.mode} 范围:",
    "复制文案中文化")

# 4) 预测页窗口选项带"期"(value 保数字, API 参数不受影响)
rep('<option>50</option><option selected>100</option><option>200</option></select>',
    '<option value="50">50期</option><option selected value="100">100期</option><option value="200">200期</option></select>',
    "pd-win带期")

# 5) 统计页窗口选项同步带"期"(显示一致性)
rep('<option>50</option><option selected>100</option><option>200</option><option>500</option></select>',
    '<option value="50">50期</option><option selected value="100">100期</option><option value="200">200期</option><option value="500">500期</option></select>',
    "st-win带期")

# 6) 统计页区间文案 (window 100) → 窗口 100期
rep("(window ${st.window})", "窗口 ${st.window}期", "st-range中文化")

# ===== 历史开奖页: 响应式连续缩放(仅 .his-row 作用域, 不动其他页) =====
# 7) 桌面端: 球体/生肖/间距随视口放大(cap 44px/16px/14px)
rep(".his-row{display:flex;flex-wrap:wrap;justify-content:center;align-items:flex-start;gap:8px 8px}",
    ".his-row{display:flex;flex-wrap:wrap;justify-content:center;align-items:flex-start;gap:clamp(7px,0.8vw,14px) clamp(7px,0.8vw,14px)}\n"
    "/* 历史页球体/生肖随视口连续缩放(宽屏放大; 手机端在520档另控) */\n"
    ".his-row .ball{width:clamp(34px,2.6vw,44px);height:clamp(34px,2.6vw,44px);font-size:clamp(13.5px,1.05vw,17px)}\n"
    ".his-row .ball.sm{width:clamp(31px,2.35vw,40px);height:clamp(31px,2.35vw,40px);font-size:clamp(12.5px,0.98vw,15.5px)}\n"
    ".his-row .zlabel{font-size:clamp(12.5px,0.95vw,16px)}\n"
    ".his-row .ball-col{gap:clamp(3px,0.35vw,6px)}",
    "桌面连续缩放")

# 8) 桌面加号原地改 clamp(223 行有后置定义, 必须原位改否则被覆盖)
rep(".his-row .plus{font-size:22px;margin:0 2px}",
    ".his-row .plus{font-size:clamp(22px,1.8vw,30px);margin:0 2px}",
    "加号clamp")

# 9) 手机端(≤520px): 历史页球体/间距/生肖整体缩小(窄屏一行更从容)
rep(".his-row{flex-wrap:nowrap;gap:1.4vw;align-items:flex-start}",
    ".his-row{flex-wrap:nowrap;gap:1.2vw;align-items:flex-start}\n"
    "  /* 历史页手机端: 球体/间距缩小 */\n"
    "  .his-row .ball{width:clamp(22px,6.4vw,28px);height:clamp(22px,6.4vw,28px);font-size:clamp(10px,2.6vw,12px)}\n"
    "  .his-row .ball.sm{width:clamp(20px,5.9vw,26px);height:clamp(20px,5.9vw,26px);font-size:clamp(9.5px,2.4vw,11.5px)}\n"
    "  .his-row .ball-col{gap:3px}",
    "手机端历史缩小")

# 10) 手机端生肖字号缩小(历史页作用域)
rep(".zlabel{font-size:3vw;line-height:1.2}",
    ".zlabel{font-size:3vw;line-height:1.2}\n  .his-row .zlabel{font-size:clamp(8.5px,2.6vw,10.5px)}",
    "手机端生肖缩小")

open(P, "w", encoding="utf-8").write(src)
print(f"共 {len(edits)} 刀全部落盘: {'、'.join(edits)}")
print(f"体积 {n0} → {len(src)} ({len(src)-n0:+d})")
