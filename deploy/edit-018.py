# BATCH-018 编辑脚本(历史页: 五行并入球行+手机加大+桌面极限+居中)
P = "/opt/data/workspace/macaujc-predictor/web/index.html"
src = open(P, encoding="utf-8").read()
n0 = len(src)
edits = []

def rep(old, new, tag):
    global src
    n = src.count(old)
    assert n == 1, f"[{tag}] 命中 {n} 次(须唯一)"
    src = src.replace(old, new)
    edits.append(tag)

# 1) 表头合并: 三列→两列
rep("<th>开奖号码（号码下方为生肖）</th><th>特码五行</th>",
    "<th>开奖号码（号码下方为生肖 · 右侧为特码五行）</th>", "表头两列化")

# 2) 行模板: 特码球后加五行章(水平排列), 删第三列td
rep("""<span class="zlabel">${esc(zodiacOf(it,it.special)||"-")}</span></span></div></td>
        <td>${esc(it.wuxing?.[6]||"-")}</td></tr>`}""",
    """<span class="zlabel">${esc(zodiacOf(it,it.special)||"-")}</span></span><span class="wx-chip">${esc(it.wuxing?.[6]||"-")}</span></div></td></tr>`}""",
    "行模板五行章")

# 3) 错误行 colspan 3→2
rep('<tr><td colspan="3" class="muted">加载失败', '<tr><td colspan="2" class="muted">加载失败', "错误行colspan")

# 4) 桌面: 间距cap 16
rep(".his-row{display:flex;flex-wrap:wrap;justify-content:center;align-items:flex-start;gap:clamp(7px,0.8vw,14px) clamp(7px,0.8vw,14px)}",
    ".his-row{display:flex;flex-wrap:wrap;justify-content:center;align-items:flex-start;gap:clamp(8px,1vw,16px) clamp(8px,1vw,16px)}", "桌面间距极限")

# 5) 桌面: 球 cap 48
rep(".his-row .ball{width:clamp(34px,2.6vw,44px);height:clamp(34px,2.6vw,44px);font-size:clamp(13.5px,1.05vw,17px)}",
    ".his-row .ball{width:clamp(36px,3vw,48px);height:clamp(36px,3vw,48px);font-size:clamp(14px,1.2vw,18px)}", "桌面球48")

# 6) 桌面: sm 球 cap 42
rep(".his-row .ball.sm{width:clamp(31px,2.35vw,40px);height:clamp(31px,2.35vw,40px);font-size:clamp(12.5px,0.98vw,15.5px)}",
    ".his-row .ball.sm{width:clamp(33px,2.7vw,42px);height:clamp(33px,2.7vw,42px);font-size:clamp(13px,1.1vw,16.5px)}", "桌面sm球42")

# 7) 桌面: 生肖字放大
rep(".his-row .zlabel{font-size:clamp(12.5px,0.95vw,16px)}",
    ".his-row .zlabel{font-size:clamp(13px,1.05vw,17px)}", "桌面生肖字")

# 8) 五行章样式(桌面基准)
rep(".his-row .ball-col{gap:clamp(3px,0.35vw,6px)}",
    ".his-row .ball-col{gap:clamp(3px,0.35vw,6px)}\n/* 特码五行章: 与特码球水平排列 */\n.his-row .wx-chip{align-self:center;flex:none;padding:7px 13px;border-radius:11px;background:rgba(127,127,127,.10);border:1px solid var(--border);font-weight:800;font-size:clamp(12px,1vw,15px);color:var(--gold);white-space:nowrap}", "五行章样式")

# 9) 手机: 球加大 6.4→7.3vw
rep(".his-row .ball{width:clamp(22px,6.4vw,28px);height:clamp(22px,6.4vw,28px);font-size:clamp(10px,2.6vw,12px)}",
    ".his-row .ball{width:clamp(26px,7.3vw,32px);height:clamp(26px,7.3vw,32px);font-size:clamp(11.5px,3.1vw,13.5px)}", "手机球加大")

# 10) 手机: sm球/加号/生肖字加大
rep(""".his-row .ball.sm{width:clamp(20px,5.9vw,26px);height:clamp(20px,5.9vw,26px);font-size:clamp(9.5px,2.4vw,11.5px)}""",
    """.his-row .ball.sm{width:clamp(24px,6.8vw,29px);height:clamp(24px,6.8vw,29px);font-size:clamp(10.5px,2.9vw,12.5px)}""", "手机sm球")
rep(".his-row .plus{font-size:5vw;margin:0 .2vw}", ".his-row .plus{font-size:5.5vw;margin:0 .2vw}", "手机加号")
rep(".his-row .zlabel{font-size:clamp(8.5px,2.6vw,10.5px)}", ".his-row .zlabel{font-size:clamp(9.5px,3vw,12px)}", "手机生肖字")

# 11) 手机: 五行章+整行居中不遮挡
rep("""  #ov-balls .zlabel{font-size:3.5vw}""",
    """  #ov-balls .zlabel{font-size:3.5vw}
  /* 历史页手机端: 五行章缩小+全行居中不遮挡 */
  .his-row .wx-chip{padding:5px 9px;font-size:11px;border-radius:9px}
  #dr-body td{text-align:center;vertical-align:middle}
  #dr-body td.num b{font-size:13.5px}""", "手机居中+五行章")

open(P, "w", encoding="utf-8").write(src)
print(f"共 {len(edits)} 刀全部落盘: " + "、".join(edits))
print(f"体积 {n0} → {len(src)} ({len(src)-n0:+d})")
